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
            'backpack': 'backpack_detection_model',
            'laptop': 'laptop_detection_model',
            'watch': 'watch_detection_model',
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
            'earbuds': 'headphones',
            'airpods': 'headphones',
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
    """Interface for computer vision model predictions"""
    
    def __init__(self):
        # In production, these would be actual model instances
        # For now, we'll simulate responses
        pass
    
    def predict(self, image: Image.Image, model_name: str) -> Dict:
        """
        Run inference on image using specified model
        
        Args:
            image: PIL Image object
            model_name: Name of the model to use
            
        Returns:
            Dictionary containing bounding boxes and confidence scores
        """
        # SIMULATION: In production, this would call your actual CV models
        # Example: Load model, run inference, return detections
        
        # Simulated detection result
        # In real implementation, replace with actual model inference
        detections = self._simulate_detection(image, model_name)
        
        return detections
    
    def _simulate_detection(self, image: Image.Image, model_name: str) -> Dict:
        """
        Simulate model detection (replace with actual model inference)
        
        Returns format:
        {
            'detections': [
                {
                    'bbox': [x1, y1, x2, y2],  # Bounding box coordinates
                    'confidence': 0.95,         # Confidence score
                    'class': 'keys'             # Detected class
                }
            ],
            'found': True/False
        }
        """
        width, height = image.size
        
        # Simulate finding an object (replace with real model)
        import random
        found = random.random() > 0.3  # 70% chance of finding item
        
        if found:
            # Simulate bounding box coordinates (replace with model output)
            x1 = random.randint(50, width // 2)
            y1 = random.randint(50, height // 2)
            x2 = random.randint(x1 + 100, width - 50)
            y2 = random.randint(y1 + 100, height - 50)
            
            confidence = random.uniform(0.75, 0.99)
            
            return {
                'detections': [
                    {
                        'bbox': [x1, y1, x2, y2],
                        'confidence': confidence,
                        'class': model_name.replace('_detection_model', '')
                    }
                ],
                'found': True
            }
        else:
            return {
                'detections': [],
                'found': False
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
            line_width = 4
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
