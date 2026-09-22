from src.detection.camera_pipeline import CameraPipeline

if __name__ == "__main__":
    pipeline = CameraPipeline(source=0)
    pipeline.run()