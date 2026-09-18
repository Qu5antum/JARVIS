import cv2
import numpy as np
import pyautogui
from pathlib import Path
from datetime import datetime
import threading

from src.tts.tts import speak

class ScreenRecorder:
    def __init__(self):
        self.is_recording = False
        self.thread = None

    def start(self):
        if self.is_recording:
            speak("Запись уже идёт")
            return

        self.is_recording = True

        self.thread = threading.Thread(
            target=self._record,
            daemon=True
        )

        self.thread.start()

    def stop(self):
        if not self.is_recording:
            speak("Запись не запущена")
            return

        self.is_recording = False

    def _record(self):
        screen_size = pyautogui.size()

        fourcc = cv2.VideoWriter_fourcc(*"XVID")

        videos_dir = Path.home() / "Videos" / "JARVIS"
        videos_dir.mkdir(parents=True, exist_ok=True)

        output_file = videos_dir / (
            f"video_{datetime.now():%Y-%m-%d_%H-%M-%S}.mp4"
        )

        fps = 30.0

        out = cv2.VideoWriter(
            str(output_file),
            fourcc,
            fps,
            screen_size
        )

        if not out.isOpened():
            self.is_recording = False
            print("Не удалось открыть VideoWriter")
            return

        speak("Запись началась")

        cv2.namedWindow("Live Preview", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Live Preview", 640, 360)

        try:
            while self.is_recording:
                img = pyautogui.screenshot()

                frame = np.array(img)

                frame = cv2.cvtColor(
                    frame,
                    cv2.COLOR_RGB2BGR
                )

                out.write(frame)

                cv2.imshow("Live Preview", frame)

                if cv2.waitKey(1) & 0xFF == ord("q"):
                    self.is_recording = False

        finally:
            out.release()
            cv2.destroyAllWindows()

            print(f"Запись сохранена: {output_file}")

            speak(f"Запись сохранена в видео файл: {output_file}")
