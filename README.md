# Ski Safety Vision System

Rear-facing computer vision system for detecting approaching skiers and providing LED-based warnings.

Designed for:
- Raspberry Pi 5  
- Raspberry Pi AI HAT+ (Hailo)  
- Arducam camera  
- TFMini Plus  
- Addressable LED strip  

---

# Repository Structure

```
ski-safety/
  src/                     # Core pipelines and producer/consumer scripts
  scripts/                 # Detection entrypoints and hardware tests
  resources/               # HEF files and inference assets
  third_party/             # External dependencies (ignored by git)
  data/                    # Local captures (ignored)
  venv_hailo_rpi5_examples/ # Python virtual environment (ignored)
```

---

# Raspberry Pi Setup (Clean Install)

This project is intended to run directly on a Raspberry Pi 5.

## 1. Update System

```bash
sudo apt update
sudo apt upgrade -y
```

---

## 2. Install Required System Packages

```bash
sudo apt install -y \
  git \
  python3-venv \
  python3-pip \
  gstreamer1.0-tools \
  gstreamer1.0-plugins-base \
  gstreamer1.0-plugins-good \
  gstreamer1.0-plugins-bad \
  gstreamer1.0-libav
```

Install Picamera2 (if using CSI camera):

```bash
sudo apt install python3-picamera2 -y
```

---

## 3. Clone Repository

```bash
git clone https://github.com/victorlaucas/ski-safety.git
cd ski-safety
```

---

## 4. Create Python Virtual Environment

If not already created:

```bash
python3 -m venv venv_hailo_rpi5_examples
source venv_hailo_rpi5_examples/bin/activate
pip install --upgrade pip
```

Install required Python packages:

```bash
pip install -r requirements.txt
```

If Hailo SDK packages are installed via their installer, ensure they are accessible in this venv.

---

# Runtime Pipeline Overview

The system uses a shared-memory producer → inference → consumer pipeline.

Terminal layout:

- Terminal A – Camera Producer  
- Terminal B – Raw Feed Validation  
- Terminal C – Detection  
- Terminal D – Inference Viewer  

---

# Startup Procedure

Always run from repository root:

```bash
cd ~/Documents/ski-safety
```

---

## 1️⃣ Terminal A – Start Camera Producer

```bash
./src/producers/producer-camera.sh
```

Confirm shared memory socket:

```bash
ls -l /tmp/feed.raw*
```

You should see `/tmp/feed.raw`.

---

## 2️⃣ Terminal B – Confirm Raw Feed is Readable

If Pi has display:

```bash
./src/consumers/consumer-raw-fpsdisplaysink.sh
```

If SSH / headless:

```bash
gst-launch-1.0 shmsrc socket-path=/tmp/feed.raw is-live=true ! \
  fpsdisplaysink video-sink=fakesink text-overlay=false sync=false
```

If FPS is updating, camera + producer pipeline is healthy.

---

## 3️⃣ Terminal C – Activate Environment

```bash
source venv_hailo_rpi5_examples/bin/activate
source setup_env.sh
```

Quick validation:

```bash
python -c "from gi.repository import Gst; import hailo; print('python+hailo+gst ok')"
```

---

## 4️⃣ Terminal C – Run Detection

```bash
python scripts/detection.py -i rpi -f --hef-path ./resources/yolov8m.hef
```

Confirm inferred output socket:

```bash
ls -l /tmp/infered.feed*
```

If this appears, inference is producing output.

---

## 5️⃣ Terminal D – View Inference Output

```bash
./src/consumers/consumer-infered-fpsdisplaysink.sh
```

You should see annotated detections and live FPS.

---

# Quick Health Checklist

If something fails, check in this order:

1. `/tmp/feed.raw` exists  
2. Raw pipeline shows FPS  
3. Python + Hailo imports succeed  
4. `/tmp/infered.feed` appears  
5. Inference viewer shows FPS  

To reset sockets:

```bash
rm -f /tmp/feed.raw*
rm -f /tmp/infered.feed*
```

Then restart from Terminal A.

---

# Git Notes

Add to `.gitignore`:

```
venv_hailo_rpi5_examples/
data/
third_party/
*.hef
```

Do not commit:
- Virtual environments  
- Large model weights  
- Hailo SDK binaries  

---

## How It Works

This system detects people in a live camera feed and measures their distance using a LiDAR sensor, running entirely on a Raspberry Pi 5 with a Hailo AI HAT+.

---

### System Architecture

The system is built as a multi-process pipeline where video data flows through shared memory segments, allowing each stage to run independently without blocking one another.
```
Arducam (1080p/30fps)
    │
    ▼  [GStreamer, NV12 format]
/tmp/feed.raw  ◀──── shared memory socket
    │
    ▼  [GStreamer inference pipeline]
Hailo AI HAT+  ◀──── runs YOLOv8m neural network
  detects persons, positions, confidence scores
    │
    ▼  [Python callback fires per frame]
detection.py
  ├── filters detections to 'person' class only
  ├── selects best candidate (nearest to frame center)
  └── attaches LiDAR distance reading as label
    │
    ▼  [hailooverlay renders bounding boxes + labels]
/tmp/infered.feed  ◀──── second shared memory socket
    │
    ▼
Display (annotated video with FPS counter)
```

---

### Components

**`producer-camera.sh`**
A GStreamer pipeline that captures frames from the Arducam at 1920×1080, 30fps in NV12 format and writes them to a shared memory socket at `/tmp/feed.raw`. Using `leaky=downstream` queuing ensures old frames are dropped if a downstream stage falls behind, keeping the feed real-time.

**`detection_pipeline.py`**
Defines the full GStreamer inference pipeline. It reads from `/tmp/feed.raw`, converts frames to RGB, passes them through the Hailo NPU for inference, runs object tracking, overlays bounding boxes, and writes the annotated output to `/tmp/infered.feed`. Key stages:
- `hailocropper` — tiles the 1080p frame into 640×640 crops suitable for the model
- `hailonet` — executes the YOLOv8 `.hef` model on the Hailo AI HAT+
- `hailofilter` — decodes raw model outputs and applies Non-Maximum Suppression (NMS)
- `hailotracker` — assigns consistent tracking IDs to the same person across frames
- `hailooverlay` — draws bounding boxes and labels onto each frame

**`detection.py`**
The Python callback that fires on every frame after inference. It:
1. Extracts all detections from the frame buffer
2. Filters to the `person` class only
3. Selects the best detection (prefers whoever overlaps the frame center beam point; falls back to nearest by center distance)
4. Reads the latest LiDAR distance and attaches it as a `range: X.X m` label to the chosen detection

**`lidar_tfmini.py`**
Runs a background thread that continuously polls the TFMini Plus sensor over UART/USB-serial at 20Hz. Distance readings (in cm, converted to meters) are stored with a timestamp and accessed thread-safely by the detection callback. Readings older than 0.5 seconds are treated as invalid.

**`consumer-infered-fpsdisplaysink.sh`** / **`consumer-raw-fpsdisplaysink.sh`**
GStreamer consumer pipelines for displaying video output. The raw consumer is used as a health check to confirm the camera is streaming before inference starts. The inferred consumer displays the final annotated output with FPS overlay.

---

### Object Detection — How YOLOv8 Classifies Objects

The file `yolov8m.hef` is a pre-trained YOLOv8 neural network compiled into Hailo's Executable Format. It was trained on the COCO dataset (80 object classes). When a frame arrives:

1. The image is resized to 640×640 and divided into a grid of cells
2. Each cell predicts candidate bounding boxes, class probabilities, and confidence scores
3. Non-Maximum Suppression (NMS) removes overlapping duplicate boxes
4. The result is a list of detections: `[label, confidence, x1, y1, x2, y2]`

The Hailo AI HAT+ is a Neural Processing Unit (NPU) — dedicated hardware for the matrix operations that power neural networks. It runs inference far faster and more efficiently than the Pi's CPU, with the Pi handling all surrounding logic.

Detection is filtered to the `person` class only (configurable via `target_classes` in `detection.py`). All other COCO classes are ignored at the callback level, though they still appear as bounding boxes in the raw overlay.

---

### Startup Procedure

> Always run from the repository root: `cd ~/Documents/ski-safety`

| Terminal | Command | Purpose |
|----------|---------|---------|
| A | `./src/producers/producer-camera.sh` | Start camera feed |
| B | `./src/consumers/consumer-raw-fpsdisplaysink.sh` | Verify raw feed (optional) |
| C | `source venv_hailo_rpi5_examples/bin/activate && source setup_env.sh` | Activate environment |
| C | `python scripts/detection.py -i rpi -f --hef-path ./resources/yolov8m.hef` | Run inference |
| D | `./src/consumers/consumer-infered-fpsdisplaysink.sh` | View annotated output |

Confirm shared memory sockets exist before proceeding to the next step:
- After Terminal A: `ls -l /tmp/feed.raw*`
- After Terminal C (inference): `ls -l /tmp/infered.feed*`