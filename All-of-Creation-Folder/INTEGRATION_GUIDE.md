# iForgot Backend Middleware - Model Integration Guide

## Overview
This middleware routes images to appropriate computer vision models based on item type and returns annotated results with bounding boxes and confidence scores.

## Architecture

```
User Query + Image → Model Router → Specific CV Model → Image Annotator → Response
```

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Server
```bash
python backend_middleware.py
```

Server will start on `http://localhost:5000`

### 3. Test the API
```bash
curl -X POST http://localhost:5000/api/find-item \
  -H "Content-Type: application/json" \
  -d '{
    "image": "base64_encoded_image_here",
    "query": "I lost my keys"
  }'
```

## Integrating Real CV Models

### Replace Simulated Detection

In `backend_middleware.py`, locate the `CVModelInterface` class and replace the `predict` method:

```python
class CVModelInterface:
    def __init__(self):
        # Load your actual models here
        self.models = {
            'keys_detection_model': self.load_keys_model(),
            'wallet_detection_model': self.load_wallet_model(),
            'headphones_detection_model': self.load_headphones_model(),
            # ... add all your models
        }
    
    def load_keys_model(self):
        # Example: Load YOLO model
        from ultralytics import YOLO
        return YOLO('models/keys_yolo_v8.pt')
    
    def predict(self, image: Image.Image, model_name: str) -> Dict:
        """Run actual model inference"""
        model = self.models.get(model_name)
        
        if not model:
            raise ValueError(f"Model {model_name} not found")
        
        # Convert PIL Image to format your model expects
        image_array = np.array(image)
        
        # Run inference (example with YOLO)
        results = model(image_array)
        
        # Parse results into our format
        detections = []
        for result in results:
            boxes = result.boxes
            for box in boxes:
                detections.append({
                    'bbox': box.xyxy[0].tolist(),  # [x1, y1, x2, y2]
                    'confidence': float(box.conf[0]),
                    'class': result.names[int(box.cls[0])]
                })
        
        return {
            'detections': detections,
            'found': len(detections) > 0
        }
```

## Example: PyTorch Model Integration

```python
import torch
import torchvision.transforms as transforms
from torchvision.models.detection import fasterrcnn_resnet50_fpn

class CVModelInterface:
    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Load models
        self.models = {
            'keys_detection_model': self.load_pytorch_model('models/keys_fasterrcnn.pth'),
            'wallet_detection_model': self.load_pytorch_model('models/wallet_fasterrcnn.pth'),
            # ... more models
        }
    
    def load_pytorch_model(self, model_path):
        model = fasterrcnn_resnet50_fpn(pretrained=False, num_classes=2)
        model.load_state_dict(torch.load(model_path, map_location=self.device))
        model.to(self.device)
        model.eval()
        return model
    
    def predict(self, image: Image.Image, model_name: str) -> Dict:
        model = self.models[model_name]
        
        # Preprocess image
        transform = transforms.Compose([
            transforms.ToTensor(),
        ])
        image_tensor = transform(image).to(self.device)
        
        # Run inference
        with torch.no_grad():
            predictions = model([image_tensor])
        
        # Parse predictions
        detections = []
        pred = predictions[0]
        
        for i, score in enumerate(pred['scores']):
            if score > 0.5:  # Confidence threshold
                box = pred['boxes'][i].cpu().numpy()
                detections.append({
                    'bbox': box.tolist(),
                    'confidence': float(score),
                    'class': model_name.replace('_detection_model', '')
                })
        
        return {
            'detections': detections,
            'found': len(detections) > 0
        }
```

## Example: TensorFlow Model Integration

```python
import tensorflow as tf

class CVModelInterface:
    def __init__(self):
        # Load TensorFlow models
        self.models = {
            'keys_detection_model': tf.saved_model.load('models/keys_tf'),
            'wallet_detection_model': tf.saved_model.load('models/wallet_tf'),
            # ... more models
        }
    
    def predict(self, image: Image.Image, model_name: str) -> Dict:
        model = self.models[model_name]
        
        # Preprocess image
        image_array = np.array(image)
        input_tensor = tf.convert_to_tensor(image_array)
        input_tensor = input_tensor[tf.newaxis, ...]
        
        # Run inference
        detections_output = model(input_tensor)
        
        # Parse detections
        detections = []
        boxes = detections_output['detection_boxes'][0].numpy()
        scores = detections_output['detection_scores'][0].numpy()
        classes = detections_output['detection_classes'][0].numpy()
        
        height, width = image.size
        
        for i, score in enumerate(scores):
            if score > 0.5:
                # Convert normalized coordinates to pixel coordinates
                ymin, xmin, ymax, xmax = boxes[i]
                x1 = int(xmin * width)
                y1 = int(ymin * height)
                x2 = int(xmax * width)
                y2 = int(ymax * height)
                
                detections.append({
                    'bbox': [x1, y1, x2, y2],
                    'confidence': float(score),
                    'class': model_name.replace('_detection_model', '')
                })
        
        return {
            'detections': detections,
            'found': len(detections) > 0
        }
```

## API Endpoints

### POST /api/find-item
Main detection endpoint

**Request:**
```json
{
  "image": "data:image/jpeg;base64,/9j/4AAQSkZJRg...",
  "query": "I lost my keys"
}
```

**Response:**
```json
{
  "success": true,
  "item_type": "keys",
  "model_used": "keys_detection_model",
  "found": true,
  "detections": [
    {
      "bbox": [150, 200, 350, 400],
      "confidence": 0.95,
      "class": "keys"
    }
  ],
  "annotated_image": "data:image/png;base64,iVBORw0KGgoAAAANS...",
  "message": "Found keys with 95.0% confidence"
}
```

### GET /api/models
List available models

**Response:**
```json
{
  "available_models": ["keys", "wallet", "headphones", "glasses"],
  "keyword_mappings": {
    "key": "keys",
    "keys": "keys",
    "wallet": "wallet",
    ...
  }
}
```

### GET /api/health
Health check

## Adding New Item Types

1. **Add to Model Registry** (`ModelRouter.__init__`):
```python
self.model_registry['umbrella'] = 'umbrella_detection_model'
```

2. **Add Keywords** (`ModelRouter.__init__`):
```python
self.keyword_mapping['umbrella'] = 'umbrella'
self.keyword_mapping['parasol'] = 'umbrella'
```

3. **Load Model** (`CVModelInterface.__init__`):
```python
self.models['umbrella_detection_model'] = self.load_umbrella_model()
```

## Frontend Integration

Update your HTML/JavaScript to call the backend:

```javascript
async function detectItem(imageData, userQuery) {
    const response = await fetch('http://localhost:5000/api/find-item', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            image: imageData,  // base64 encoded image
            query: userQuery   // e.g., "I lost my keys"
        })
    });
    
    const result = await response.json();
    
    if (result.success && result.found) {
        // Display annotated image
        displayImage(result.annotated_image);
        
        // Show detection info
        showMessage(result.message);
        
        // Display confidence scores
        result.detections.forEach(det => {
            console.log(`Found ${det.class} with ${det.confidence * 100}% confidence`);
        });
    } else {
        showMessage(result.message || 'Item not found');
    }
}
```

## Model Training Tips

### Dataset Structure
```
datasets/
├── keys/
│   ├── images/
│   ├── labels/
│   └── train.txt
├── wallet/
│   ├── images/
│   ├── labels/
│   └── train.txt
└── ...
```

### Recommended Frameworks
- **YOLO v8**: Best for real-time detection
- **Faster R-CNN**: Better accuracy, slower
- **SSD**: Good balance of speed and accuracy
- **EfficientDet**: Efficient for mobile deployment

## Production Considerations

1. **Model Loading**: Load models once at startup, not per request
2. **GPU Support**: Use CUDA if available for faster inference
3. **Caching**: Cache model outputs for identical requests
4. **Rate Limiting**: Implement rate limiting for API
5. **Image Size**: Resize large images before processing
6. **Async Processing**: Use async workers for concurrent requests
7. **Monitoring**: Log detection metrics and model performance

## Example Production Config

```python
# config.py
import os

class Config:
    # Server
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    DEBUG = os.getenv('DEBUG', 'False') == 'True'
    
    # Models
    MODEL_DIR = os.getenv('MODEL_DIR', 'models/')
    CONFIDENCE_THRESHOLD = float(os.getenv('CONFIDENCE_THRESHOLD', 0.5))
    
    # Image Processing
    MAX_IMAGE_SIZE = (1920, 1080)
    
    # GPU
    USE_GPU = torch.cuda.is_available()
    DEVICE = 'cuda' if USE_GPU else 'cpu'
```

## Troubleshooting

### Model not loading
- Check model file paths
- Verify model format matches framework
- Check Python environment has correct packages

### Low accuracy
- Adjust confidence threshold
- Retrain model with more data
- Check image preprocessing steps

### Slow inference
- Enable GPU acceleration
- Reduce image resolution
- Use lighter model architecture
- Implement batch processing

## Support

For issues or questions, check the documentation or contact the development team.
