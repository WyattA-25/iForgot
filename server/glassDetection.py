from ultralytics import YOLO

# Path to your dataset YAML (adjust if needed)
data_path = r"C:\Users\DELL\Downloads\archive\new dataset 640x640\data.yaml"

# Load a pretrained YOLOv8 model (for example, YOLOv8n)
model = YOLO("yolov8n.pt")  # You can also try yolov8s.pt for a stronger model

# Train the model
model.train(
    data=data_path,
    epochs=50,
    imgsz=640,
    batch=8,
    name="glasses-detector-local"
)

# Optional: Evaluate or visualize
metrics = model.val()
print(metrics)
