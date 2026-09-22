import cv2
from typing import Optional, Callable
import logging

from .person_detection import PersonDetection

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("pipline")


class CameraPipeline:
    def __init__(
        self,
        source: int = 0,
        model_path: str = "yolo11n.pt",
        on_persons_detected: Optional[Callable] = None,
        draw: bool = True,
        window_name: str = "Person Detection",
    ):
        self.source = source
        self.draw = draw
        self.window_name = window_name
        self.on_persons_detected = on_persons_detected
        self.detector = PersonDetection(model_path=model_path)
        self.cap: Optional[cv2.VideoCapture] = None

    def open(self) -> bool:
        self.cap = cv2.VideoCapture(self.source)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        if not self.cap.isOpened():
            logger.info(f"[CameraPipeline] Cannot open source {self.source}")
            return False
        return True

    def _draw_results(self, frame, persons):
        for person in persons:
            x1, y1, x2, y2 = person["bbox"]
            conf = person["confidence"]
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(
                frame,
                f"Person {conf:.2f}",
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                2,
            )
        return frame

    def run(self):
        if not self.open():
            return

        logger.info("[CameraPipeline] Нажмите «q», чтобы выйти.")

        while True:
            ret, frame = self.cap.read()
            if not ret:
                logger.info("[CameraPipeline] Конец потока или невозможно получить кадр.")
                break

            persons = self.detector.detect(frame)

            if self.on_persons_detected is not None:
                self.on_persons_detected(persons, frame)

            if self.draw:
                frame = self._draw_results(frame, persons)
                cv2.imshow(self.window_name, frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        self.release()

    def release(self):
        if self.cap is not None:
            self.cap.release()
        cv2.destroyAllWindows()
