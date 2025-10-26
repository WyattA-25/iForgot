from ultralytics import YOLO
import os
import cv2
import numpy as np
import json

# --- CONFIG ---
image_path = r"C:\Users\DELL\Downloads\IMG_1576.jpg" #change this to your image path

base_dir = os.path.dirname(os.path.dirname(__file__))
data_path = os.path.join(base_dir, "server", "models", "airpod.pt")

model_path = data_path
window_size = 640
step_size = 320
conf_thresh = 0.25
nms_iou_thresh = 0.4  # IoU threshold for NMS
top_n = 3  # Number of top detections to display

# --- LOAD MODEL ---
model = YOLO(model_path)

# --- READ IMAGE ---
img = cv2.imread(image_path)
H, W, _ = img.shape

detections = []

# --- SLIDING WINDOW LOOP ---
print(f"Processing image {W}x{H} with sliding window...")
for y in range(0, H, step_size):
    for x in range(0, W, step_size):
        x_end = min(x + window_size, W)
        y_end = min(y + window_size, H)
        sub_img = img[y:y_end, x:x_end]

        results = model.predict(sub_img, conf=conf_thresh, verbose=False)

        # --- EXTRACT DETECTIONS ---
        for box in results[0].boxes:
            conf = float(box.conf)
            cls = int(box.cls)
            (x1, y1, x2, y2) = box.xyxy[0].tolist()
            global_box = [x + x1, y + y1, x + x2, y + y2]
            detections.append((global_box, conf, cls))

print(f"Found {len(detections)} raw detections before NMS")

# --- APPLY NON-MAXIMUM SUPPRESSION ---
def apply_nms(detections, iou_threshold=0.4):
    """Apply Non-Maximum Suppression to remove overlapping boxes"""
    if len(detections) == 0:
        return []
    
    # Convert to arrays for OpenCV NMS
    boxes = np.array([d[0] for d in detections], dtype=np.float32)
    scores = np.array([d[1] for d in detections], dtype=np.float32)
    classes = np.array([d[2] for d in detections], dtype=np.int32)
    
    # Apply NMS per class
    final_detections = []
    for cls_id in np.unique(classes):
        cls_mask = classes == cls_id
        cls_boxes = boxes[cls_mask]
        cls_scores = scores[cls_mask]
        
        # OpenCV NMS
        indices = cv2.dnn.NMSBoxes(
            cls_boxes.tolist(),
            cls_scores.tolist(),
            score_threshold=0.0,  # Already filtered by conf_thresh
            nms_threshold=iou_threshold
        )
        
        if len(indices) > 0:
            indices = indices.flatten()
            for idx in indices:
                original_idx = np.where(cls_mask)[0][idx]
                final_detections.append(detections[original_idx])
    
    return final_detections

detections_nms = apply_nms(detections, nms_iou_thresh)
print(f"After NMS: {len(detections_nms)} detections remaining")

# --- CREATE OUTPUT DIRECTORY ---
output_dir = os.path.join(os.path.dirname(image_path), "detections")
os.makedirs(output_dir, exist_ok=True)

# --- FIND AND SAVE TOP N HIGHEST CONFIDENCE DETECTIONS ---
if len(detections_nms) > 0:
    # Sort by confidence (highest first) and take top N
    sorted_detections = sorted(detections_nms, key=lambda d: d[1], reverse=True)
    top_detections = sorted_detections[:top_n]
    
    img_result = img.copy()
    
    # Define colors for different ranks (BGR format)
    colors = [
        (0, 0, 255),    # Red for #1
        (0, 165, 255),  # Orange for #2
        (0, 255, 255),  # Yellow for #3
        (0, 255, 0),    # Green for #4
        (255, 0, 255),  # Magenta for #5
    ]
    
    # Prepare JSON data
    json_data = {
        "image_path": image_path,
        "image_dimensions": {"width": W, "height": H},
        "total_raw_detections": len(detections),
        "detections_after_nms": len(detections_nms),
        "top_n": top_n,
        "detections": []
    }
    
    print(f"\n🏆 Top {len(top_detections)} detections:")
    for i, (box, conf, cls) in enumerate(top_detections):
        x1, y1, x2, y2 = map(int, box)
        color = colors[i % len(colors)]
        
        # Draw box
        cv2.rectangle(img_result, (x1, y1), (x2, y2), color, 10)
        
        # Draw label with rank and confidence
        label = f"#{i+1}: {conf:.2f}"
        cv2.putText(img_result, label, (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        
        print(f"   #{i+1}: Confidence {conf:.3f}, Box [{x1}, {y1}, {x2}, {y2}]")
        
        # Add to JSON data
        json_data["detections"].append({
            "rank": i + 1,
            "confidence": round(float(conf), 4),
            "class_id": int(cls),
            "bounding_box": {
                "x1": int(x1),
                "y1": int(y1),
                "x2": int(x2),
                "y2": int(y2),
                "width": int(x2 - x1),
                "height": int(y2 - y1)
            }
        })
    
    # Save image
    output_path = os.path.join(output_dir, f"top_{top_n}_detections.png")
    cv2.imwrite(output_path, img_result)
    print(f"\n✅ Saved top {len(top_detections)} detections: {output_path}")
    
    # Save JSON
    json_path = os.path.join(output_dir, f"top_{top_n}_detections.json")
    with open(json_path, 'w') as f:
        json.dump(json_data, f, indent=2)
    print(f"💾 Saved detection data as JSON: {json_path}")
    
else:
    print("⚠️ No detections found above confidence threshold.")

print("\n📊 Summary:")
print(f"   Raw detections: {len(detections)}")
print(f"   After NMS: {len(detections_nms)}")
print(f"   Displayed: {min(top_n, len(detections_nms)) if detections_nms else 0}")