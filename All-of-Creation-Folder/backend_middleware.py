"""
iForgot Backend Middleware
Routes images to appropriate computer vision models based on item type
Returns annotated images with bounding boxes and confidence scores
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
import io
import json
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from typing import Dict, List, Tuple, Optional

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication


class ModelRouter:
    """Routes requests to appropriate CV models based on item type"""
    
    def __init__(self):
        # Map item types to their corresponding model endpoints
        self.model_registry = {
            'keys': 'keys_detection_model',
            'wallet': 'wallet_detection_model',
            'headphones': 'headphones_detection_model',
            'glasses': 'glasses_detection_model',
            'phone': 'phone_detection_model',
            'tablet': 'tablet_detection_model',
            'watch': 'watch_detection_model',
            'laptop': 'laptop_detection_model',
            'earbuds': 'earbud_detection_model',
        }
        
        # Keywords that map to item types
        self.keyword_mapping = {
            'key': 'keys',
            'keys': 'keys',
            'keychain': 'keys',
            'wallet': 'wallet',
            'purse': 'wallet',
            'headphone': 'headphones',
            'headphones': 'headphones',
            'earbuds': 'earbuds',
            'airpods': 'earbuds',
            'glasses': 'glasses',
            'sunglasses': 'glasses',
            'spectacles': 'glasses',
            'phone': 'phone',
            'mobile': 'phone',
            'cellphone': 'phone',
            'smartphone': 'phone',
            'backpack': 'backpack',
            'bag': 'backpack',
            'laptop': 'laptop',
            'computer': 'laptop',
            'notebook': 'laptop',
            'watch': 'watch',
            'smartwatch': 'watch',
        }
    
    def identify_item_type(self, user_query: str) -> Optional[str]:
        """
        Parse user query to identify what item they're looking for
        
        Args:
            user_query: User's text description of the lost item
            
        Returns:
            Item type string or None if not recognized
        """
        query_lower = user_query.lower()
        
        for keyword, item_type in self.keyword_mapping.items():
            if keyword in query_lower:
                return item_type
        
        return None
    
    def get_model_endpoint(self, item_type: str) -> Optional[str]:
        """Get the model endpoint for a specific item type"""
        return self.model_registry.get(item_type)


class CVModelInterface:
    """Interface for computer vision model predictions with sliding window + NMS"""
    
    def __init__(self):
        from ultralytics import YOLO
        import os
        
        # Configuration
        self.window_size = 640  # Size of sliding window
        self.step_size = 320    # Step size for sliding window
        self.conf_thresh = 0.25 # Confidence threshold
        self.nms_iou_thresh = 0.4  # IoU threshold for NMS
        self.top_n = 2  # Number of top detections to return
        
        # Check models directory exists
        if not os.path.exists('models'):
            os.makedirs('models')
            print("⚠️  Created models/ directory. Please add your model files.")
        
        # TODO: Replace these paths with your actual model file names
        print("Loading YOLO models with sliding window detection...")
        self.models = {
            'keys_detection_model': YOLO('models/keys.pt'),              # ← YOUR MODEL HERE
            'wallet_detection_model': YOLO('models/wallets.pt'),          # ← YOUR MODEL HERE
            #'headphones_detection_model': YOLO('models/headphones.pt'),  # ← YOUR MODEL HERE
            'glasses_detection_model': YOLO('models/glasses.pt'),        # ← YOUR MODEL HERE
            #'phone_detection_model': YOLO('models/phone.pt'),            # ← YOUR MODEL HERE
            #'backpack_detection_model': YOLO('models/backpack.pt'),      # ← YOUR MODEL HERE
            #'laptop_detection_model': YOLO('models/laptop.pt'),          # ← YOUR MODEL HERE
            #'watch_detection_model': YOLO('models/watch.pt'),            # ← YOUR MODEL HERE
            'earbud_detection_model': YOLO('models/earbuds.pt'),            # ← YOUR MODEL HERE
        }
        print("✅ All models loaded successfully with sliding window detection!")
    
    def apply_nms(self, detections, iou_threshold=0.4):
        """Apply Non-Maximum Suppression to remove overlapping boxes"""
        import cv2
        import numpy as np
        
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
    
    def predict(self, image: Image.Image, model_name: str) -> Dict:
        """
        Run inference using YOLO model with sliding window + NMS
        
        This method:
        1. Splits large images into sliding windows
        2. Runs detection on each window
        3. Combines results from all windows
        4. Applies NMS to remove overlaps
        5. Returns top N highest confidence detections
        """
        import numpy as np
        import cv2
        
        model = self.models.get(model_name)
        if not model:
            raise ValueError(f"Model {model_name} not found")
        
        # Convert PIL Image to numpy array (OpenCV format)
        image_array = np.array(image)
        
        # Convert RGB to BGR (OpenCV uses BGR)
        if len(image_array.shape) == 3 and image_array.shape[2] == 3:
            image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
        
        H, W = image_array.shape[:2]
        
        detections = []
        
        # --- SLIDING WINDOW DETECTION ---
        print(f"Processing image {W}x{H} with sliding window (window={self.window_size}, step={self.step_size})...")
        
        for y in range(0, H, self.step_size):
            for x in range(0, W, self.step_size):
                x_end = min(x + self.window_size, W)
                y_end = min(y + self.window_size, H)
                sub_img = image_array[y:y_end, x:x_end]
                
                # Run YOLO on this window
                results = model.predict(sub_img, conf=self.conf_thresh, verbose=False)
                
                # Extract detections from this window
                for box in results[0].boxes:
                    conf = float(box.conf)
                    cls = int(box.cls)
                    (x1, y1, x2, y2) = box.xyxy[0].tolist()
                    
                    # Convert local coordinates to global image coordinates
                    global_box = [x + x1, y + y1, x + x2, y + y2]
                    detections.append((global_box, conf, cls))
        
        print(f"Found {len(detections)} raw detections before NMS")
        
        # --- APPLY NMS ---
        detections_nms = self.apply_nms(detections, self.nms_iou_thresh)
        print(f"After NMS: {len(detections_nms)} detections remaining")
        
        # --- GET TOP N DETECTIONS ---
        if len(detections_nms) > 0:
            # Sort by confidence (highest first) and take top N
            sorted_detections = sorted(detections_nms, key=lambda d: d[1], reverse=True)
            top_detections = sorted_detections[:self.top_n]
            
            # Format results
            result_detections = []
            for i, (box, conf, cls) in enumerate(top_detections):
                x1, y1, x2, y2 = map(int, box)
                
                # Get class name
                class_name = model.names.get(cls, 'unknown') if hasattr(model, 'names') else 'object'
                
                result_detections.append({
                    'bbox': [x1, y1, x2, y2],
                    'confidence': float(conf),
                    'class': class_name,
                    'rank': i + 1  # Add rank for reference
                })
                
                print(f"   Top #{i+1}: Confidence {conf:.3f}, Box [{x1}, {y1}, {x2}, {y2}]")
            
            return {
                'detections': result_detections,
                'found': True,
                'stats': {
                    'raw_detections': len(detections),
                    'after_nms': len(detections_nms),
                    'returned': len(result_detections)
                }
            }
        else:
            print("No detections found above confidence threshold")
            return {
                'detections': [],
                'found': False,
                'stats': {
                    'raw_detections': len(detections),
                    'after_nms': 0,
                    'returned': 0
                }
            }
    


class ImageAnnotator:
    """Annotate images with bounding boxes and labels"""
    
    @staticmethod
    def draw_bounding_boxes(image: Image.Image, detections: List[Dict]) -> Image.Image:
        """
        Draw bounding boxes on image
        
        Args:
            image: PIL Image object
            detections: List of detection dictionaries with bbox and confidence
            
        Returns:
            Annotated PIL Image
        """
        # Create a copy to avoid modifying original
        annotated_image = image.copy()
        draw = ImageDraw.Draw(annotated_image)
        
        # Try to load a font, fallback to default if not available
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
        except:
            font = ImageFont.load_default()
        
        for detection in detections:
            bbox = detection['bbox']
            confidence = detection['confidence']
            class_name = detection['class']
            
            # Draw bounding box
            x1, y1, x2, y2 = bbox
            
            # Draw rectangle with thick lines
            line_width = 10
            draw.rectangle(
                [(x1, y1), (x2, y2)],
                outline='#667eea',
                width=line_width
            )
            
            # Prepare label text
            label = f"{class_name} {confidence*100:.1f}%"
            
            # Get text bounding box for background
            bbox_text = draw.textbbox((x1, y1 - 30), label, font=font)
            
            # Draw label background
            draw.rectangle(
                [(bbox_text[0] - 5, bbox_text[1] - 5), 
                 (bbox_text[2] + 5, bbox_text[3] + 5)],
                fill='#667eea'
            )
            
            # Draw label text
            draw.text((x1, y1 - 30), label, fill='white', font=font)
        
        return annotated_image


# Initialize components
model_router = ModelRouter()
cv_interface = CVModelInterface()
image_annotator = ImageAnnotator()


@app.route('/api/find-item', methods=['POST'])
def find_item():
    """
    Main endpoint for item detection
    
    Expected JSON payload:
    {
        "image": "base64_encoded_image_string",
        "query": "I lost my keys"
    }
    
    Returns:
    {
        "success": true,
        "item_type": "keys",
        "model_used": "keys_detection_model",
        "found": true,
        "detections": [
            {
                "bbox": [x1, y1, x2, y2],
                "confidence": 0.95,
                "class": "keys"
            }
        ],
        "annotated_image": "base64_encoded_annotated_image",
        "message": "Found keys with 95.0% confidence"
    }
    """
    try:
        # Parse request
        data = request.get_json()
        
        if not data or 'image' not in data or 'query' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing image or query in request'
            }), 400
        
        # Decode image
        image_data = data['image']
        if 'base64,' in image_data:
            image_data = image_data.split('base64,')[1]
        
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))
        
        # Identify item type from query
        user_query = data['query']
        item_type = model_router.identify_item_type(user_query)
        
        if not item_type:
            return jsonify({
                'success': False,
                'error': 'Could not identify item type from query',
                'message': 'Please specify what item you are looking for (keys, wallet, headphones, glasses, etc.)'
            }), 400
        
        # Get appropriate model
        model_name = model_router.get_model_endpoint(item_type)
        
        if not model_name:
            return jsonify({
                'success': False,
                'error': f'No model available for item type: {item_type}'
            }), 400
        
        # Run detection
        detection_result = cv_interface.predict(image, model_name)
        
        # Prepare response
        response_data = {
            'success': True,
            'item_type': item_type,
            'model_used': model_name,
            'found': detection_result['found'],
            'detections': detection_result['detections']
        }
        
        # If item found, annotate image
        if detection_result['found'] and detection_result['detections']:
            annotated_image = image_annotator.draw_bounding_boxes(
                image, 
                detection_result['detections']
            )
            
            # Convert annotated image to base64
            buffered = io.BytesIO()
            annotated_image.save(buffered, format="PNG")
            annotated_image_base64 = base64.b64encode(buffered.getvalue()).decode()
            
            response_data['annotated_image'] = f"data:image/png;base64,{annotated_image_base64}"
            
            # Generate message
            max_confidence = max(d['confidence'] for d in detection_result['detections'])
            response_data['message'] = f"Found {item_type} with {max_confidence*100:.1f}% confidence"
            
        else:
            response_data['message'] = f"No {item_type} detected in the image"
        
        return jsonify(response_data), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/models', methods=['GET'])
def list_models():
    """List all available models"""
    return jsonify({
        'available_models': list(model_router.model_registry.keys()),
        'keyword_mappings': model_router.keyword_mapping
    })


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'iForgot Backend Middleware'
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
