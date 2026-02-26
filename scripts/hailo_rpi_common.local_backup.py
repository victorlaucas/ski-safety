import gi
gi.require_version("Gst", "1.0")
from gi.repository import Gst
import numpy as np
import argparse

def get_default_parser():
    """
    Matches the flags used by the Hailo RPi examples.
    detection_pipeline.py expects this to exist.
    """
    p = argparse.ArgumentParser()

    # Common example flags (seen in your consumer-tracking-infer.sh)
    p.add_argument("-i", "--input", default="rpi",
                   help="Input source preset (e.g., rpi, file, usb).")
    p.add_argument("-f", "--use-frame", action="store_true",
                   help="If set, map frames into numpy in the callback.")
    p.add_argument("--hef-path", default="yolov8m.hef",
                   help="Path to the HEF model file.")
    p.add_argument("--labels-json", default="yolov8.json",
                   help="Path to labels json file.")

    # Your pipeline uses shm sockets; these defaults match your .sh scripts
    p.add_argument("--shm-in", default="/tmp/feed.raw",
                   help="Input shmsrc socket path.")
    p.add_argument("--shm-out", default="/tmp/infered.feed",
                   help="Output shmsink socket path.")

    # Optional knobs that examples often have
    p.add_argument("--fps", type=int, default=30, help="Target FPS.")
    p.add_argument("--width", type=int, default=1920, help="Frame width.")
    p.add_argument("--height", type=int, default=1080, help="Frame height.")

    return p


def get_caps_from_pad(pad):
    """
    Returns (format, width, height) from a GstPad's caps.
    """
    caps = pad.get_current_caps() or pad.get_allowed_caps()
    if not caps or caps.get_size() == 0:
        return None, None, None

    s = caps.get_structure(0)
    fmt = s.get_string("format")
    width = s.get_value("width") if s.has_field("width") else None
    height = s.get_value("height") if s.has_field("height") else None
    return fmt, width, height


def get_numpy_from_buffer(buffer, fmt, width, height):
    """
    Maps a GstBuffer to numpy.
    This is only needed if you actually use frames in Python.
    For now we support common raw formats enough to avoid crashes.
    """
    ok, mapinfo = buffer.map(Gst.MapFlags.READ)
    if not ok:
        return None
    try:
        data = mapinfo.data  # bytes-like
        if fmt in ("RGB", "BGR"):
            arr = np.frombuffer(data, dtype=np.uint8)
            return arr.reshape((height, width, 3))
        if fmt == "GRAY8":
            arr = np.frombuffer(data, dtype=np.uint8)
            return arr.reshape((height, width))
        if fmt == "NV12":
            # NV12 is Y plane (H*W) + interleaved UV plane (H/2 * W)
            arr = np.frombuffer(data, dtype=np.uint8)
            return arr.reshape((int(height * 3 / 2), width))
        # Unknown format: return a flat array (still useful for debugging)
        return np.frombuffer(data, dtype=np.uint8)
    finally:
        buffer.unmap(mapinfo)


class app_callback_class:
    """
    Minimal replacement for the helper class your script expects.
    """
    def __init__(self, use_frame: bool = False):
        self.use_frame = use_frame
        self._frame_count = 0

    def increment(self):
        self._frame_count += 1

    @property
    def frame_count(self):
        return self._frame_count
