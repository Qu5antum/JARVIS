import cv2
import mediapipe as mp
import numpy as np
import pyautogui
import time
import platform
import threading
from pathlib import Path

pyautogui.FAILSAFE = False


class HandTracker:
    def __init__(
        self,
        model_path="models/hand_landmarker.task",
        cooldown=0.4,
        complexity=1,
        click_radius=20,
        hover_radius=25,
        right_click_radius=50,
        right_hover_radius=60,
        hold_click_radius=30,
        hold_hover_radius=35,
        scroll_radius=25,
        scroll_hover_radius=30,
        scroll_speed=60,
        smoothing=0.25,
    ):
        self.model_path = Path(model_path)
        if not self.model_path.exists():
            raise FileNotFoundError(f"MediaPipe model not found: {self.model_path}")

        BaseOptions = mp.tasks.BaseOptions
        HandLandmarker = mp.tasks.vision.HandLandmarker
        HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
        RunningMode = mp.tasks.vision.RunningMode

        options = HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=str(self.model_path)),
            running_mode=RunningMode.VIDEO,
            num_hands=1,
            min_hand_detection_confidence=0.5,
            min_hand_presence_confidence=0.5,
            min_tracking_confidence=0.5,
        )

        self.hands = HandLandmarker.create_from_options(options)

        self.cooldown = cooldown
        self.click_radius = click_radius
        self.hover_radius = hover_radius
        self.right_click_radius = right_click_radius
        self.right_hover_radius = right_hover_radius
        self.hold_click_radius = hold_click_radius
        self.hold_hover_radius = hold_hover_radius
        self.scroll_radius = scroll_radius
        self.scroll_hover_radius = scroll_hover_radius
        self.scroll_speed = scroll_speed

        self.smoothing = smoothing
        self.prev_cursor_x = None
        self.prev_cursor_y = None

        self.last_click_time = 0
        self.last_right_click_time = 0

        self.landmark_colors = [(0, 255, 0)] * 21
        self.tracked_landmarks = [0, 3, 4, 5, 6, 7, 8, 9, 12, 20]

        self.is_holding = False
        self.hold_start_time = 0

        self.is_scrolling = False
        self.scroll_direction = None
        self.scroll_interval = 0.1
        self.scroll_thread = None
        self.scroll_active = False
        self.scroll_lock = threading.Lock()

        self.start_time = time.monotonic()
        self.last_timestamp_ms = 0

    def process_frame(self, frame):
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb_frame,
        )

        timestamp_ms = int((time.monotonic() - self.start_time) * 1000)
        if timestamp_ms <= self.last_timestamp_ms:
            timestamp_ms = self.last_timestamp_ms + 1
        self.last_timestamp_ms = timestamp_ms

        try:
            results = self.hands.detect_for_video(mp_image, timestamp_ms)
        except Exception as e:
            print(f"MediaPipe processing error: {e}")
            return frame

        current_time = time.time()

        if results.hand_landmarks:
            for hand_landmarks in results.hand_landmarks:
                self.landmark_colors = [(0, 255, 0)] * 21
                landmarks = []

                for lm in hand_landmarks:
                    cx = int(lm.x * w)
                    cy = int(lm.y * h)
                    landmarks.append((cx, cy))

                if len(landmarks) > 8:
                    self.move_cursor(landmarks[8], w, h)

                self.detect_scroll(landmarks)
                self.detect_click_and_hold(landmarks, current_time)

                if not self.is_holding and self.detect_thumb_index_contact(landmarks, current_time):
                    pyautogui.click()

                if self.detect_pinky_wrist_contact(landmarks, current_time):
                    pyautogui.rightClick()

                self.draw_points_only(frame, landmarks)
        else:
            if self.is_holding:
                pyautogui.mouseUp()
                self.is_holding = False
            self.stop_scrolling()

        return frame

    def move_cursor(self, index_tip, frame_width, frame_height):
        screen_w, screen_h = pyautogui.size()

        target_x = np.interp(
            index_tip[0],
            [0, frame_width],
            [0, screen_w],
        )
        target_y = np.interp(
            index_tip[1],
            [0, frame_height],
            [0, screen_h],
        )

        if self.prev_cursor_x is None:
            self.prev_cursor_x = target_x
            self.prev_cursor_y = target_y
        else:
            self.prev_cursor_x = (
                self.prev_cursor_x * (1 - self.smoothing)
                + target_x * self.smoothing
            )
            self.prev_cursor_y = (
                self.prev_cursor_y * (1 - self.smoothing)
                + target_y * self.smoothing
            )

        pyautogui.moveTo(
            int(self.prev_cursor_x),
            int(self.prev_cursor_y),
            _pause=False,
        )

    def detect_scroll(self, landmarks):
        if len(landmarks) < 13:
            self.stop_scrolling()
            return

        index_tip = landmarks[8]
        middle_tip = landmarks[12]
        middle_base = landmarks[9]

        distance = (
            abs(index_tip[0] - middle_tip[0])
            + abs(index_tip[1] - middle_tip[1])
        )

        mid_y = (index_tip[1] + middle_tip[1]) // 2
        vertical_diff = mid_y - middle_base[1]

        direction = None
        if vertical_diff < -15:
            direction = "up"
        elif vertical_diff > 15:
            direction = "down"

        if distance < self.scroll_hover_radius:
            self.landmark_colors[8] = (0, 255, 255)
            self.landmark_colors[12] = (0, 255, 255)
            self.landmark_colors[9] = (0, 255, 255)

            if distance < self.scroll_radius and direction:
                self.landmark_colors[8] = (255, 0, 255)
                self.landmark_colors[12] = (255, 0, 255)
                self.landmark_colors[9] = (255, 0, 255)
                self.start_scrolling(direction)
            else:
                self.stop_scrolling()
        else:
            self.stop_scrolling()

    def start_scrolling(self, direction):
        self.is_scrolling = True
        self.scroll_direction = direction

        with self.scroll_lock:
            if not self.scroll_active:
                self.scroll_active = True
                self.scroll_thread = threading.Thread(
                    target=self._scroll_worker,
                    daemon=True,
                )
                self.scroll_thread.start()

    def stop_scrolling(self):
        self.is_scrolling = False

    def _scroll_worker(self):
        while self.scroll_active:
            if self.is_scrolling:
                self._perform_scroll()
            time.sleep(self.scroll_interval)

    def _perform_scroll(self):
        os_name = platform.system()

        if os_name == "Windows":
            self._windows_scroll()
        elif os_name == "Linux":
            self._linux_scroll()
        else:
            self._default_scroll()

    def _windows_scroll(self):
        try:
            import ctypes
            scroll_amount = 120 if self.scroll_direction == "up" else -120
            ctypes.windll.user32.mouse_event(
                0x0800,
                0,
                0,
                scroll_amount,
                0,
            )
        except Exception as e:
            print(f"Windows scroll error: {e}")
            self._default_scroll()

    def _linux_scroll(self):
        try:
            from Xlib import X, display
            from Xlib.ext.xtest import fake_input

            d = display.Display()
            event_direction = 4 if self.scroll_direction == "up" else 5

            fake_input(d, X.ButtonPress, event_direction)
            d.sync()
            fake_input(d, X.ButtonRelease, event_direction)
            d.sync()
        except ImportError:
            self._default_scroll()
        except Exception as e:
            print(f"Linux scroll error: {e}")
            self._default_scroll()

    def _default_scroll(self):
        scroll_amount = self.scroll_speed if self.scroll_direction == "up" else -self.scroll_speed
        pyautogui.scroll(scroll_amount // 3)

    def detect_click_and_hold(self, landmarks, current_time):
        if len(landmarks) < 9:
            return

        thumb_tip = landmarks[4]
        index_tip = landmarks[8]

        distance = np.linalg.norm(
            np.array(thumb_tip) - np.array(index_tip)
        )

        if distance < self.hold_hover_radius:
            self.landmark_colors[4] = (0, 255, 255)
            self.landmark_colors[8] = (0, 255, 255)

            if distance < self.hold_click_radius:
                self.landmark_colors[4] = (0, 0, 255)
                self.landmark_colors[8] = (0, 0, 255)

                if not self.is_holding:
                    self.hold_start_time = current_time
                    self.is_holding = True
                    pyautogui.mouseDown()
            elif self.is_holding:
                pyautogui.mouseUp()
                self.is_holding = False
        elif self.is_holding:
            pyautogui.mouseUp()
            self.is_holding = False

    def detect_thumb_index_contact(self, landmarks, current_time):
        if (
            len(landmarks) < 9
            or current_time - self.last_click_time < self.cooldown
            or self.is_holding
        ):
            return False

        thumb_tip = landmarks[4]
        contact_detected = False

        for idx in [5, 6, 7, 8]:
            distance = np.linalg.norm(
                np.array(thumb_tip) - np.array(landmarks[idx])
            )

            if distance < self.hover_radius:
                self.landmark_colors[4] = (0, 255, 255)
                self.landmark_colors[idx] = (0, 255, 255)

                if distance < self.click_radius:
                    self.landmark_colors[4] = (255, 0, 0)
                    self.landmark_colors[idx] = (255, 0, 0)
                    contact_detected = True

        if contact_detected:
            self.last_click_time = current_time
            return True

        return False

    def detect_pinky_wrist_contact(self, landmarks, current_time):
        if (
            len(landmarks) < 21
            or current_time - self.last_right_click_time < self.cooldown
        ):
            return False

        pinky_tip = landmarks[20]
        wrist = landmarks[0]

        distance = np.linalg.norm(
            np.array(pinky_tip) - np.array(wrist)
        )

        if distance < self.right_hover_radius:
            self.landmark_colors[20] = (0, 255, 255)
            self.landmark_colors[0] = (0, 255, 255)

            if distance < self.right_click_radius:
                self.landmark_colors[20] = (255, 0, 0)
                self.landmark_colors[0] = (255, 0, 0)
                self.last_right_click_time = current_time
                return True

        return False

    def draw_points_only(self, frame, landmarks):
        for idx in self.tracked_landmarks:
            if idx >= len(landmarks):
                continue

            cx, cy = landmarks[idx]
            color = self.landmark_colors[idx]
            cv2.circle(frame, (cx, cy), 6, color, -1)

    def release(self):
        if self.is_holding:
            try:
                pyautogui.mouseUp()
            except Exception:
                pass
            self.is_holding = False

        with self.scroll_lock:
            self.scroll_active = False
            self.is_scrolling = False

        if self.scroll_thread and self.scroll_thread.is_alive():
            self.scroll_thread.join(timeout=0.5)

        try:
            self.hands.close()
        except Exception:
            pass