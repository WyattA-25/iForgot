# iForgot - AI-Powered Lost Item Finder

A complete system for finding lost items using computer vision and AI chat interface.

## System Overview

```
┌─────────────────┐        ┌──────────────────┐        ┌─────────────────────┐
│   Frontend      │        │   Middleware     │        │   CV Models         │
│   (HTML/JS)     │───────▶│   (Python)       │───────▶│   (PyTorch/TF)      │
│                 │        │                  │        │                     │
│  • Chat UI      │        │  • Model Router  │        │  • Keys Model       │
│  • Image Upload │        │  • API Endpoints │        │  • Wallet Model     │
│  • Display      │        │  • Annotation    │        │  • Headphones Model │
│                 │◀───────│                  │◀───────│  • Glasses Model    │
└─────────────────┘        └──────────────────┘        └─────────────────────┘
     User Query                 Routes to                 Returns Detections
     + Image                    Right Model               + Bounding Boxes
```

## Features

### Frontend
- ✅ Modern ChatGPT-like interface
- ✅ Dark/Light mode toggle
- ✅ Image upload with preview
- ✅ Responsive design (mobile & desktop)
- ✅ Modal prompt for image upload
- ✅ Real-time chat interaction

### Backend Middleware
- ✅ Intelligent model routing based on item type
- ✅ Keyword parsing from user queries
- ✅ Multiple CV model support
- ✅ Bounding box annotation
- ✅ Confidence score reporting
- ✅ RESTful API
- ✅ CORS enabled for frontend

### Computer Vision
- ✅ Modular architecture for different item types
- ✅ Support for PyTorch, TensorFlow, YOLO
- ✅ Bounding box detection
- ✅ Confidence scoring
- ✅ Easy to add new item categories

## Quick Start

### 1. Frontend Setup

Simply open `lost-item-chat.html` in a web browser:

```bash
# Option 1: Open directly
open lost-item-chat.html

# Option 2: Serve with Python
python -m http.server 8080
# Then visit http://localhost:8080/lost-item-chat.html
```

### 2. Backend Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Start the server
python backend_middleware.py

# Server runs on http://localhost:5000
```

### 3. Test the System

1. Open the frontend in your browser
2. Type a message: "I lost my keys"
3. Upload an image when prompted
4. The system will:
   - Route to the keys detection model
   - Analyze the image
   - Return annotated image with bounding boxes
   - Display confidence scores

## File Structure

```
iForgot/
├── lost-item-chat.html          # Frontend interface
├── backend_middleware.py         # Backend API server
├── requirements.txt              # Python dependencies
├── INTEGRATION_GUIDE.md          # Detailed integration docs
├── README.md                     # This file
└── models/                       # Your CV models go here
    ├── keys_yolo_v8.pt
    ├── wallet_fasterrcnn.pth
    ├── headphones_model.h5
    └── ...
```

## Supported Item Types

The system currently supports detection of:

- 🔑 **Keys** - Detects various types of keys and keychains
- 👛 **Wallet** - Identifies wallets and purses
- 🎧 **Headphones** - Finds headphones, earbuds, AirPods
- 👓 **Glasses** - Detects glasses and sunglasses
- 📱 **Phone** - Locates mobile phones and smartphones
- 🎒 **Backpack** - Identifies bags and backpacks
- 💻 **Laptop** - Finds laptops and notebooks
- ⌚ **Watch** - Detects watches and smartwatches

## API Documentation

### POST /api/find-item

Main endpoint for item detection.

**Request:**
```json
{
  "image": "data:image/jpeg;base64,/9j/4AAQSkZJRg...",
  "query": "I lost my keys"
}
```

**Response (Success):**
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
  "annotated_image": "data:image/png;base64,iVBORw0KGg...",
  "message": "Found keys with 95.0% confidence"
}
```

**Response (Not Found):**
```json
{
  "success": true,
  "item_type": "keys",
  "model_used": "keys_detection_model",
  "found": false,
  "detections": [],
  "message": "No keys detected in the image"
}
```

### GET /api/models

List all available detection models.

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

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "iForgot Backend Middleware"
}
```

## How It Works

### 1. User Interaction
- User types: "I lost my wallet"
- System prompts for image upload
- User uploads photo

### 2. Model Routing
```python
Query: "I lost my wallet"
   ↓
Keyword Parser: Identifies "wallet"
   ↓
Model Router: Routes to wallet_detection_model
   ↓
CV Model: Runs inference on image
```

### 3. Detection & Response
```python
Model Output:
{
  "bbox": [x1, y1, x2, y2],
  "confidence": 0.92
}
   ↓
Image Annotator: Draws bounding box
   ↓
Response: Returns annotated image + metadata
   ↓
Frontend: Displays result in chat
```

## Adding New Item Types

### Step 1: Train Your Model
Train a computer vision model for your new item type (e.g., "umbrella")

### Step 2: Add to Model Registry
```python
# In backend_middleware.py
self.model_registry['umbrella'] = 'umbrella_detection_model'
```

### Step 3: Add Keywords
```python
self.keyword_mapping['umbrella'] = 'umbrella'
self.keyword_mapping['parasol'] = 'umbrella'
```

### Step 4: Load Model
```python
def __init__(self):
    self.models = {
        'umbrella_detection_model': self.load_umbrella_model(),
        # ... other models
    }
```

### Step 5: Update Frontend (Optional)
Add suggestion card in `lost-item-chat.html`:
```html
<div class="suggestion-card" onclick="useSuggestion('I lost my umbrella')">
    <strong>Lost Umbrella</strong>
    <span>Find my umbrella</span>
</div>
```

## Integrating Real CV Models

The backend currently uses simulated detections. To integrate real models:

### Option 1: YOLO (Recommended)
```python
from ultralytics import YOLO

def load_keys_model(self):
    return YOLO('models/keys_yolo_v8.pt')

def predict(self, image, model_name):
    model = self.models[model_name]
    results = model(np.array(image))
    # Parse and return detections
```

### Option 2: PyTorch Faster R-CNN
```python
import torch
from torchvision.models.detection import fasterrcnn_resnet50_fpn

def load_pytorch_model(self, path):
    model = fasterrcnn_resnet50_fpn(pretrained=False, num_classes=2)
    model.load_state_dict(torch.load(path))
    return model
```

### Option 3: TensorFlow
```python
import tensorflow as tf

def load_tf_model(self, path):
    return tf.saved_model.load(path)
```

See `INTEGRATION_GUIDE.md` for detailed examples.

## Development Mode

When the backend is not running, the frontend shows:
- Connection error message
- Instructions to start backend
- Simulated demo results

This allows frontend development without backend dependency.

## Production Deployment

### Frontend
```bash
# Serve with nginx, Apache, or any static file server
# Update API endpoint from localhost to production URL
```

### Backend
```bash
# Use production WSGI server
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 backend_middleware:app

# Or use Docker
docker build -t iforgot-backend .
docker run -p 5000:5000 iforgot-backend
```

### Environment Variables
```bash
export FLASK_ENV=production
export MODEL_DIR=/path/to/models
export CONFIDENCE_THRESHOLD=0.5
```

## Performance Optimization

### Image Processing
- Resize large images before processing
- Use GPU acceleration when available
- Implement image caching

### Model Loading
- Load all models at startup (not per request)
- Use model quantization for faster inference
- Consider model pruning for edge devices

### API
- Implement rate limiting
- Add request caching
- Use async workers (Celery, RQ)
- Add monitoring and logging

## Troubleshooting

### Frontend doesn't connect to backend
- Ensure backend is running on `http://localhost:5000`
- Check CORS settings
- Verify firewall rules

### Low detection accuracy
- Increase training data
- Adjust confidence threshold
- Improve image quality
- Fine-tune model hyperparameters

### Slow inference
- Enable GPU (CUDA)
- Reduce image resolution
- Use lighter model architecture
- Implement batch processing

## Tech Stack

**Frontend:**
- HTML5
- CSS3 (Custom styles)
- Vanilla JavaScript (ES6+)

**Backend:**
- Python 3.8+
- Flask (Web framework)
- Pillow (Image processing)
- NumPy (Array operations)

**Computer Vision:**
- PyTorch / TensorFlow / YOLO (Your choice)
- OpenCV (Optional)
- Custom trained models

## Security Considerations

- ✅ Input validation on all endpoints
- ✅ File size limits on uploads
- ✅ Image format validation
- ⚠️ Add authentication for production
- ⚠️ Implement rate limiting
- ⚠️ Sanitize user queries
- ⚠️ Use HTTPS in production

## Future Enhancements

- [ ] Real-time camera feed detection
- [ ] Multiple item detection in single image
- [ ] Location tracking integration
- [ ] Database of lost items
- [ ] User accounts and history
- [ ] Mobile app (React Native / Flutter)
- [ ] Push notifications
- [ ] Map integration for found items

## Contributing

To contribute:

1. Fork the repository
2. Create feature branch
3. Add your CV models to `models/` directory
4. Update model registry
5. Test thoroughly
6. Submit pull request

## License

[Your License Here]

## Support

For questions or issues:
- Check `INTEGRATION_GUIDE.md` for detailed docs
- Open an issue on GitHub
- Contact the development team

## Acknowledgments

Built with modern web technologies and computer vision frameworks to help people find their lost items quickly and easily.

---

**iForgot** - Never lose anything again! 🔍
