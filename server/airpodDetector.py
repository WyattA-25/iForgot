import os
from ultralytics import YOLO

base_dir = os.path.dirname(os.path.dirname(__file__))  # one folder up from /server
data_path = os.path.join(base_dir, "airpod", "data.yaml")
print("Base directory:", base_dir)
print("Data path:", data_path)

print("Using data.yaml from:", data_path)

model = YOLO("yolov8n.pt")
model.train(data=data_path, epochs=50, imgsz=640, batch=8, name="glasses-detector-local6")

# Load a pretrained YOLOv8 model (for example, YOLOv8n)
model = YOLO("yolov8n.pt")  # You can also try yolov8s.pt for a stronger model

# # Train the model
model.train(
    data=data_path,
    epochs=50,
    imgsz=640,
    batch=8,
    name="airpod-detector-local"
)

# Optional: Evaluate or visualize
metrics = model.val()
print(metrics)
