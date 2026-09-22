from ultralytics import YOLO


class PersonDetection:
    def __init__(self, model_path: str = "yolo11n.pt"):
        self.model = YOLO(model_path)

    def detect(self, frame):
        results = self.model(frame)

        persons = []

        for result in results:
            for box in result.boxes:
                class_id = int(box.cls[0])
                confidence = float(box.conf[0])

                if class_id != 0:
                    continue

                x1, y1, x2, y2 = map(int, box.xyxy[0])

                persons.append({
                    "bbox": (x1, y1, x2, y2),
                    "confidence": confidence,
                })

        return persons