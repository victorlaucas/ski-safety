Look into  Segment Anything Model (SAM) 

<!-- Documentation -->
https://cdn.sparkfun.com/assets/1/4/2/1/9/TFmini_Plus_A02_Product_Manual_EN.pdf

<!-- Dependencies -->
https://github.com/adafruit/Adafruit_CircuitPython_TFmini

<!-- Todo -->
Update readme

<!-- Document new script startup procedure -->
1) Terminal A: start the camera producer

From repo root:

./src/producers/producer-camera.sh

Confirm it created the socket:

ls -l /tmp/feed.raw*

You should see /tmp/feed.raw (and maybe .shm side files).
2) Terminal B: confirm the raw feed is readable

If you have a display attached to the Pi:

./src/consumers/consumer-raw-fpsdisplaysink.sh

If you’re SSH’d in and don’t have GUI/video output, use a headless check:

gst-launch-1.0 shmsrc socket-path=/tmp/feed.raw is-live=true ! \
  fpsdisplaysink video-sink=fakesink text-overlay=false sync=false

If this shows FPS updating, the producer side is solid.

3) Terminal C: activate the right env and source setup

From repo root:

source venv_hailo_rpi5_examples/bin/activate
source setup_env.sh

Quick checks:

python -c "from gi.repository import Gst; import hailo; print('python+hailo+gst ok')"
4) Terminal C: run detection

Run your detection script:

python scripts/detection.py

Now confirm the inferred socket appears:

ls -l /tmp/infered.feed*

If it appears, detection is producing output.

Update: How to run:
cd ~/Documents/ski-safety
source venv_hailo_rpi5_examples/bin/activate
source setup_env.sh
python scripts/detection.py -i rpi -f --hef-path ./resources/yolov8m.hef

5) Terminal D: view inferred output
./src/consumers/consumer-infered-fpsdisplaysink.sh

That should show the annotated stream + FPS.

<!-- Debugging -->
