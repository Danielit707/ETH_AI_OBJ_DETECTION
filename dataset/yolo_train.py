from ultralytics import YOLO

# Load YOLOv8 nano model
model = YOLO("yolov8n.pt")

# Train on your dataset
model.train(
    data="data.yaml",  # path to your dataset yaml
    epochs=50,
    imgsz=640
)

