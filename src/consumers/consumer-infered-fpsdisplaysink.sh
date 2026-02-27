#!/usr/bin/env bash
set -e

gst-launch-1.0 -v \
  shmsrc socket-path=/tmp/infered.feed is-live=true do-timestamp=true ! \
  video/x-raw,format=RGB,width=1920,height=1080,framerate=30/1 ! \
  queue max-size-buffers=30 leaky=downstream ! \
  videoconvert ! \
  fpsdisplaysink video-sink=autovideosink text-overlay=true sync=false