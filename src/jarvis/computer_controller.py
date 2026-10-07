import cv2
import threading

from src.detection.hand_tracker import HandTracker


class ComputerControl:

    def __init__(self):
        self.enabled = False
        self.thread = None
        self.camera = None
        self.tracker = None

    def start(self):
        if self.enabled:
            return

        self.enabled = True

        self.thread = threading.Thread(
            target=self._run,
            daemon=True
        )

        self.thread.start()

    def stop(self):
        self.enabled = False

    def _run(self):
        self.camera = cv2.VideoCapture(0)
        self.tracker = HandTracker()

        while self.enabled:
            success, frame = self.camera.read()

            if not success:
                continue

            frame = self.tracker.process_frame(frame)

            cv2.imshow(
                "JARVIS Hand Control",
                frame
            )

            if cv2.waitKey(1) & 0xFF == 27:
                self.enabled = False

        self.tracker.release()
        self.camera.release()

        cv2.destroyWindow(
            "JARVIS Hand Control"
        )