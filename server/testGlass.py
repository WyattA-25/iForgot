from ultralytics import YOLO
import os

base_dir = os.path.dirname(os.path.dirname(__file__))  # one folder up from /server
data_path = os.path.join(base_dir, "runs\\detect", "glasses-detector-local64", "weights", "best.pt")
print(data_path)


model = YOLO(data_path)

# results = model.predict(source="C:\\Users\\enboy\\Downloads\\IMG_1563.jpeg", show=True, conf=0.5)
results = model.predict(
    source="C:\\Users\\enboy\\Downloads\\IMG_1575.jpeg",
    conf=0.3,      # confidence threshold (try 0.5–0.7)
    iou=0.4,       # IoU threshold for NMS (lower = fewer overlapping boxes)
    show=True,
    save=True
)
results[0].save("C:\\Users\\enboy\\Downloads\\glassResult.jpg")

print("Done")