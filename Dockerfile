# iForgot - Flask + YOLOv8 lost-item detector, single CPU-only container.
# Builds an image that serves both the chat frontend and the detection API.

FROM python:3.11-slim

# System libraries:
#   libgl1        -> provides libGL.so.1; ultralytics pulls the non-headless
#                    opencv-python, which links libGL, so slim needs this
#   libglib2.0-0  -> also required by OpenCV at runtime
#   libgomp1      -> OpenMP runtime used by numpy / torch / ultralytics
#   fonts-dejavu-core -> provides DejaVuSans-Bold.ttf for box label rendering
RUN apt-get update && apt-get install -y --no-install-recommends \
        libgl1 \
        libglib2.0-0 \
        libgomp1 \
        fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install CPU-only PyTorch FIRST from the PyTorch CPU index. The default PyPI
# wheels on Linux are the CUDA build (multi-GB) and would blow past free-tier
# image-size and memory limits. Installing the exact pinned versions here means
# the later "pip install -r requirements.txt" sees torch as already satisfied.
RUN pip install --no-cache-dir \
        torch==2.1.0 torchvision==0.16.0 \
        --index-url https://download.pytorch.org/whl/cpu

# Remaining Python dependencies.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code, frontend, and the five trained weight files.
COPY backend_middleware.py lost-item-chat.html ./
COPY models/ ./models/

# Give ultralytics / matplotlib writable config dirs. Hugging Face Spaces runs
# the container as a non-root user whose HOME is not writable, so point these
# at /tmp to avoid permission errors on first model load.
ENV YOLO_CONFIG_DIR=/tmp/Ultralytics \
    MPLCONFIGDIR=/tmp/matplotlib

# Hugging Face Spaces expects 7860. Render / Railway / Fly inject their own $PORT,
# which the start command below honors via ${PORT:-7860}.
ENV PORT=7860
EXPOSE 7860

# One worker keeps memory bounded (each worker loads all five models). Two
# threads keep /api/health and the frontend responsive while an inference runs.
# The long timeout covers slow sliding-window CPU inference on large photos.
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-7860} --workers 1 --threads 2 --timeout 180 backend_middleware:app"]
