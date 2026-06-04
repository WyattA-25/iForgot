# iForgot

An AI-powered lost-item finder. Upload a photo of a room and iForgot locates common misplaced items (keys, wallet, headphones, glasses, earbuds) using a set of custom-trained YOLOv8 object-detection models served behind a chat-style web interface.

## Overview

An uploaded image is routed to the right detection model, scanned with a sliding-window pass so large photos are covered in full, de-duplicated with non-maximum suppression, and returned with the highest-confidence matches drawn as bounding boxes.

## 🌟 System Overview

```
┌─────────────────┐        ┌──────────────────┐        ┌─────────────────────┐
│   Frontend      │        │   Middleware     │        │   YOLO Models       │
│   (HTML/JS)     │───────▶│   (Flask)        │───────▶│   (PyTorch)         │
│                 │        │                  │        │                     │
│  • Chat UI      │        │  • Model Router  │        │  • Keys Model       │
│  • Image Upload │        │  • Sliding Window│        │  • Wallet Model     │
│  • Dark/Light   │        │  • NMS Algorithm │        │  • Headphones Model │
│  • Display      │        │  • Annotation    │        │  • Glasses Model    │
│                 │◀───────│                  │◀───────│  • Earbuds Model    │
└─────────────────┘        └──────────────────┘        └─────────────────────┘
     User Query                 Routes to                 Returns Detections
     + Image                    Right Model               + Bounding Boxes
```

## Features

- Five custom-trained YOLOv8 detectors, one per item type
- Sliding-window detection (640x640 windows, 320px step) so large images are scanned in full
- Non-maximum suppression (IoU threshold 0.4) to remove duplicate boxes
- Confidence filtering (default 0.25) and top-N results per query
- Bounding-box annotation with confidence scores returned to the interface
- Chat-style frontend with image upload and light / dark mode

## Tech Stack

- Python, PyTorch, Ultralytics YOLOv8
- Flask and Flask-CORS (REST API)
- Pillow and NumPy for image handling
- HTML / CSS / JavaScript frontend

## API

The Flask service runs on port 5000 and exposes:

- POST /api/find-item   submit an image and item query, returns detections
- GET  /api/models      list the available detection models
- GET  /api/health      health check

## Running Locally

1. Install dependencies:
   pip install flask flask-cors ultralytics pillow numpy
2. Start the server:
   python All-of-Creation-Folder/backend_middleware.py
3. Open the frontend in a browser and upload an image.

Trained model weights live in server/models/. Datasets were labeled and exported with Roboflow.

## Contributors

- WyattA-25: designed the frontend, built the Flask middleware, and integrated the two.
- Jonathanhsiao123: built the sliding-window detection and the training foundation.
- Model training was split across the team, with each member training one model on their own device to speed up the overall process.
