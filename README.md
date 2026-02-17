# Ski Safety Vision System

Rear-facing computer vision system for detecting approaching skiers and providing LED-based warnings.

Designed for:
- Raspberry Pi 5  
- Raspberry Pi AI HAT+
- Arducam camera  
- TFMini Plus
- Addressable LED strip  

---

## Repository Structure

```
ski-safety/
  src/              # Core application code
  scripts/          # Hardware smoke tests (camera, LEDs)
  data/             # Local captures (ignored by git)
  models/           # Model files (do not commit large weights)
  environment.yml   # Conda environment spec
```

---

# Development Setup (macOS)

This setup is for development and testing non-hardware code.

## 1. Install Conda (Recommended: Miniforge)

```bash
brew install --cask miniforge
conda init zsh
```

Restart your terminal.

Disable auto-activating base (recommended):

```bash
conda config --set auto_activate_base false
```

---

## 2. Create Environment

From the project root:

```bash
conda env create -f environment.yml
conda activate ski
```

Verify:

```bash
python --version
```

---

## 3. Run Code

Example:

```bash
python src/main.py
```

Note:
- Camera and GPIO/LED features are Raspberry Pi–specific.
- On macOS, use test images or video files instead of live camera input.

---

# Development Setup (Windows)

This setup is for development on Windows systems.

## 1. Install Miniforge or Miniconda

Download and install one of the following:

- Miniforge: https://github.com/conda-forge/miniforge
- Miniconda: https://docs.conda.io/en/latest/miniconda.html

During installation:
- Allow it to initialize your shell.
- Install for "Just Me" unless you have a specific reason otherwise.

Open **Anaconda Prompt** (recommended) after installation.

Disable auto-activating base (recommended):

```bash
conda config --set auto_activate_base false
```

Close and reopen Anaconda Prompt.

---

## 2. Create Environment

Navigate to your cloned repository:

```bash
cd path\to\ski-safety
```

Create the environment:

```bash
conda env create -f environment.yml
conda activate ski
```

Verify:

```bash
python --version
```

---

## 3. Run Code

```bash
python src\main.py
```

Notes:
- Raspberry Pi camera and GPIO libraries will not run on Windows.
- Use video files or test images for development.
- Keep hardware-specific code modular to avoid import errors.

---

# Raspberry Pi Setup

This setup is for deployment on the Raspberry Pi 5.

## 1. System Update

```bash
sudo apt update
sudo apt upgrade -y
```

---

## 2. Install Git

```bash
sudo apt install git -y
```

Clone the repository:

```bash
git clone https://github.com/victorlaucas/ski-safety.git
cd ski-safety
```

---

## 3. Install Conda (Miniconda ARM64)

```bash
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-aarch64.sh
bash Miniconda3-latest-Linux-aarch64.sh
source ~/.bashrc
```

Disable auto base activation (recommended):

```bash
conda config --set auto_activate_base false
```

---

## 4. Create Environment

```bash
conda env create -f environment.yml
conda activate ski
```

---

## 5. Raspberry Pi–Specific Dependencies

Camera stack (if using CSI Arducam):

```bash
sudo apt install python3-picamera2 -y
```

LED libraries (example for WS2812/NeoPixel):

```bash
pip install rpi_ws281x adafruit-circuitpython-neopixel
```

Adjust depending on LED hardware.

---

## 6. Test Hardware

Camera test:

```bash
python scripts/test_camera.py
```

---

# Git Workflow

## First-time push

```bash
git push -u origin master
```

After that:

```bash
git push
```

---

# Updating the Environment

If new packages are added:

On development machine:

```bash
conda env export --from-history > environment.yml
git add environment.yml
git commit -m "Update environment"
git push
```

Teammates update with:

```bash
conda env update -f environment.yml --prune
```

---

# Notes

- Do not commit large model weights (>100MB).
- Do not commit installers (Miniconda, etc.).
- `data/` should remain untracked.
- Keep Raspberry Pi–specific dependencies isolated from cross-platform code.