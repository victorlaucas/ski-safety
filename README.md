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

# Development Notes

This project is designed primarily for Raspberry Pi deployment.

If developing off-device:
- Use recorded video files  
- Mock hardware interfaces  
- Keep hardware logic isolated  

---

# Recommended Practices

- Always activate the virtual environment before running scripts.
- Avoid running multiple producers simultaneously.
- Use shared memory inspection (`ls /tmp`) for debugging.
- Log FPS to detect performance regressions.

---

# License

Add license here if publishing.

