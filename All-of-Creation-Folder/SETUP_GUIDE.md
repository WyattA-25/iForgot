# iForgot - Complete Setup Guide

This guide will walk you through setting up the iForgot system with the included YOLO models.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- 4GB+ RAM
- 2GB free disk space

## Step-by-Step Setup

### Step 1: Verify Your Files

First, make sure you have all the necessary files:

```bash
# Check for required files
ls -lh

# You should see:
# - backend_middleware.py
# - lost-item-chat.html
# - requirements.txt
# - keys.pt
# - wallets.pt
# - headphones.pt
# - glasses.pt
# - earbuds.pt
# - README.md
# - INTEGRATION_GUIDE.md
# - QUICKSTART.md
# - test_api.py
```

### Step 2: Create Project Directory

```bash
# Create a dedicated directory for the project
mkdir -p iForgot
cd iForgot

# Move all project files here (if not already in a project directory)
```

### Step 3: Set Up Python Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate

# You should see (venv) in your terminal prompt
```

### Step 4: Install Dependencies

```bash
# Update pip
pip install --upgrade pip

# Install core dependencies
pip install Flask==3.0.0
pip install flask-cors==4.0.0
pip install Pillow==10.1.0
pip install numpy==1.24.3

# Install YOLO and computer vision dependencies
pip install ultralytics==8.0.200
pip install opencv-python==4.8.1.78

# Install PyTorch (this may take a few minutes)
pip install torch==2.1.0 torchvision==0.16.0

# Verify installation
python -c "import torch; print(f'PyTorch installed: {torch.__version__}')"
python -c "from ultralytics import YOLO; print('Ultralytics YOLO installed!')"
python -c "import cv2; print(f'OpenCV installed: {cv2.__version__}')"
```

**Note:** PyTorch installation is ~500MB. Be patient!

### Step 5: Create Models Directory

```bash
# Create models directory
mkdir -p models

# Verify it was created
ls -d models/
```

### Step 6: Copy Model Files

```bash
# Copy all .pt model files to the models directory
cp keys.pt models/
cp wallets.pt models/
cp headphones.pt models/
cp glasses.pt models/
cp earbuds.pt models/

# Verify all models are in place
ls -lh models/

# You should see:
# keys.pt (6MB)
# wallets.pt (6MB)
# headphones.pt (18MB)
# glasses.pt (6MB)
# earbuds.pt (6MB)
```

### Step 7: Verify Backend Configuration

```bash
# Check that backend_middleware.py points to correct model paths
grep "models/" backend_middleware.py

# You should see lines like:
# 'keys_detection_model': YOLO('models/keys.pt'),
# 'wallet_detection_model': YOLO('models/wallets.pt'),
# etc.
```

### Step 8: Test Backend Startup

```bash
# Start the backend server
python backend_middleware.py

# You should see:
# Loading YOLO models with sliding window detection...
# ✅ All models loaded successfully with sliding window detection!
# * Running on http://127.0.0.1:5000
```

**If you see errors:**
- "Model not found" → Check models/ directory has all .pt files
- "No module named 'ultralytics'" → Reinstall: `pip install ultralytics`
- "No module named 'cv2'" → Reinstall: `pip install opencv-python`

**If successful, press Ctrl+C to stop the server (we'll restart it after testing)**

### Step 9: Test API Endpoints

Open a new terminal window (keep the backend running in the first terminal):

```bash
# Activate virtual environment (if using one)
source venv/bin/activate

# Test health check
curl http://localhost:5000/api/health

# Expected response:
# {"status":"healthy","service":"iForgot Backend Middleware"}

# Test list models
curl http://localhost:5000/api/models

# Expected response:
# {"available_models":["keys","wallet","headphones","glasses","earbuds"],...}
```

### Step 10: Run Test Script

```bash
# Run the API test script
python test_api.py

# You should see:
# ========================================
# iForgot Backend API Test Suite
# ========================================
# 
# Health Check
# ✅ Server is healthy
# 
# Listing Available Models
# Available Models:
#   • keys
#   • wallet
#   • headphones
#   • glasses
#   • earbuds
```

### Step 11: Open the Frontend

**Option 1: Direct Open (Simple)**
```bash
# Open in default browser
# On Mac:
open lost-item-chat.html

# On Linux:
xdg-open lost-item-chat.html

# On Windows:
start lost-item-chat.html
```

**Option 2: Serve with Python (Recommended for testing)**
```bash
# Open a new terminal window
# Start simple HTTP server
python -m http.server 8080

# Then open browser to:
# http://localhost:8080/lost-item-chat.html
```

### Step 12: Test the Complete System

1. **In the browser:**
   - You should see the iForgot chat interface
   - Type: "I lost my keys"
   - Click "Upload Photos" button
   - Select an image with keys (or any test image)
   - Wait for detection results

2. **Expected result:**
   - Annotated image with bounding boxes
   - Confidence scores displayed
   - Message like "Found keys with XX% confidence"

### Step 13: Verify Backend Logs

Switch back to the terminal running the backend. You should see logs like:

```
Processing image 1920x1080 with sliding window (window=640, step=320)...
Found 15 raw detections before NMS
After NMS: 3 detections remaining
   Top #1: Confidence 0.847, Box [234, 567, 456, 789]
   Top #2: Confidence 0.723, Box [890, 234, 1012, 456]
127.0.0.1 - - [26/Oct/2025 12:34:56] "POST /api/find-item HTTP/1.1" 200 -
```

## Troubleshooting Setup Issues

### Issue: "Module not found" errors

```bash
# Solution: Reinstall dependencies
pip uninstall -y Flask flask-cors Pillow numpy ultralytics opencv-python torch torchvision
pip install Flask flask-cors Pillow numpy ultralytics opencv-python torch torchvision
```

### Issue: "Model not found" errors

```bash
# Solution: Verify model files
ls -lh models/

# If files are missing, copy them again
cp *.pt models/
```

### Issue: Backend won't start (port in use)

```bash
# Solution: Kill process on port 5000
# On Linux/Mac:
lsof -ti:5000 | xargs kill -9

# On Windows:
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### Issue: Frontend can't connect to backend

1. Verify backend is running: `curl http://localhost:5000/api/health`
2. Check CORS is enabled (it is by default)
3. Try opening frontend with HTTP server: `python -m http.server 8080`

### Issue: Slow detection

```bash
# Check if GPU is available
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"

# If False, detection will use CPU (slower but works)
# For GPU support, install CUDA-enabled PyTorch:
# pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

## Verification Checklist

- [ ] Python 3.8+ installed
- [ ] Virtual environment created and activated
- [ ] All dependencies installed (no errors)
- [ ] Models directory created
- [ ] All 5 model files copied to models/
- [ ] Backend starts without errors
- [ ] Health check endpoint responds
- [ ] Models endpoint lists 5 models
- [ ] Frontend opens in browser
- [ ] Can upload images and get detections

## Next Steps After Setup

1. **Test with Real Images:**
   - Take photos of items
   - Test detection accuracy
   - Try different angles and lighting

2. **Adjust Configuration (Optional):**
   ```python
   # Edit backend_middleware.py, line ~95-99
   self.conf_thresh = 0.25  # Lower for more detections
   self.step_size = 320     # Lower for better accuracy
   ```

3. **Add More Item Types:**
   - Train new YOLO models
   - Add to model registry
   - See README.md for detailed instructions

4. **Deploy to Production:**
   - See README.md "Production Deployment" section
   - Use Gunicorn for production server
   - Set up Nginx reverse proxy

## Getting Help

If you encounter issues:

1. Check the logs in the terminal running the backend
2. Review the troubleshooting section above
3. Read the full README.md
4. Check INTEGRATION_GUIDE.md for model details

## System Architecture Reminder

```
Your Computer
├── Python Virtual Environment (venv/)
├── Backend Server (http://localhost:5000)
│   ├── Flask Application
│   ├── Model Router
│   ├── YOLO Models (models/*.pt)
│   └── Detection Pipeline
└── Frontend (http://localhost:8080)
    └── Chat Interface (lost-item-chat.html)
```

## Quick Commands Summary

```bash
# Setup
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install Flask flask-cors Pillow numpy ultralytics opencv-python torch torchvision
mkdir -p models
cp *.pt models/

# Run
python backend_middleware.py  # Terminal 1
python -m http.server 8080    # Terminal 2
# Open: http://localhost:8080/lost-item-chat.html

# Test
curl http://localhost:5000/api/health
curl http://localhost:5000/api/models
python test_api.py
```

---

**Congratulations! 🎉**

Your iForgot system is now set up and ready to find lost items!

The system is using real YOLO models with advanced sliding window detection. Test it with different images and items to see it in action!
