#!/usr/bin/env python3
import subprocess
from datetime import datetime
from pathlib import Path

# Based on https://docs.arducam.com/Raspberry-Pi-Camera/Native-camera/16MP-IMX519/#raspberry-pi-compute-module-3-4_1
# Live preview (Ctrl+C to exit):
    # rpicam-still -t 0

# Capture image with 5-second preview:
    # rpicam-still -t 5000 -o test.jpg

def main():
    out_dir = Path("cam_tests")
    out_dir.mkdir(exist_ok=True)

    fname = out_dir / f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    cmd = ["rpicam-still", "-o", str(fname), "--timeout", "10000"] # 10 seconds

    subprocess.run(cmd, check=True)
    print(f"Saved: {fname}")

if __name__ == "__main__":
    main()
