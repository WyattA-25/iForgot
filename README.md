# iForgot

An AI-powered lost-item finder. Upload a photo of a room and iForgot locates common misplaced items (keys, wallet, headphones, glasses, earbuds) using a set of custom-trained YOLOv8 object-detection models served behind a chat-style web interface.

## Overview

An uploaded image is routed to the right detection model, scanned with a sliding-window pass so large photos are covered in full, de-duplicated with non-maximum suppression, and returned with the highest-confidence matches drawn as bounding boxes.

## System Overview

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

## Model Performance

Validation metrics recorded from the Ultralytics training logs (runs/detect/*/results.csv). Each row is matched to the exact shipped weight file by hash.

| Model | mAP@0.5 | Precision | Recall | Training |
|---|---|---|---|---|
| keys.pt | 0.993 | 0.962 | 0.981 | YOLOv8n, 50 epochs, 640px |
| glasses.pt | 0.992 | 0.985 | 0.959 | YOLOv8n, 50 epochs, 640px |
| headphones.pt | 0.830 | 0.782 | 0.865 | YOLOv8s, 640px |
| earbuds.pt | pending | - | - | trained off-repo, validation pending |
| wallets.pt | pending | - | - | trained off-repo, validation pending |

Datasets were labeled and exported with Roboflow.

## API

The Flask service runs on port 5000 and exposes:

- POST /api/find-item   submit an image and item query, returns detections
- GET  /api/models      list the available detection models
- GET  /api/health      health check

## Running Locally

1. Install dependencies:
   pip install -r requirements.txt
2. Start the server:
   python backend_middleware.py
3. Open lost-item-chat.html in a browser and upload an image.

A step-by-step walkthrough is in docs/SETUP_GUIDE.md.

## Repository Layout

- backend_middleware.py: Flask API with model routing, sliding-window inference, and NMS
- lost-item-chat.html: chat-style frontend
- models/: the five trained YOLOv8 weight files
- training/: model training and detection scripts
- docs/: setup guide

A live deployed demo (Docker) is in progress; the link will land here.

## Contributors

- @WyattA-25: designed the frontend chat interface, built the Flask middleware and serving API, and integrated the models, frontend, and backend.
- @Jonathanhsiao123: developed the image slicing / sliding-window approach and several detection and training scripts; trained the keys, wallet, airpod, and glasses models.
- @Eyao24: wrote the headphone and glasses detection scripts; trained the headphone and glasses models.
- @FRFS30: trained and contributed the keys model.
- @sfurniss1234: wrote the original project documentation.
