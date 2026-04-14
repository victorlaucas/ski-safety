import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import gi
gi.require_version("Gst", "1.0")
gi.require_version("GLib", "2.0")
from gi.repository import Gst, GLib
from lidar_tfmini import TFMiniReader
from src.common.led_strip import LEDStripController, classify_side
import json
import hailo
import time


from hailo_rpi_common import (
    get_caps_from_pad,
    get_numpy_from_buffer,
    app_callback_class,
)

from detection_pipeline import GStreamerDetectionApp

# Set to keep track of emitted tracking IDs
emitted_ids = set()

# Define the target classes for detection
# this should align to the COCO list of objects
# https://github.com/ultralytics/ultralytics/blob/main/ultralytics/cfg/datasets/coco.yaml
# note that this just filters which ones we'll call MQTT on, they'll still appear as bounding boxes because we haven't
# told hailo to exclude them.
target_classes = {"person"}

# LED / warning tuning
LED_ENABLED = os.environ.get("LED_ENABLED", "1") == "1"
LED_COUNT = int(os.environ.get("LED_COUNT", "30"))
LED_BRIGHTNESS = float(os.environ.get("LED_BRIGHTNESS", "0.10"))
WARNING_FAR_M = float(os.environ.get("WARNING_FAR_M", "5.0"))
WARNING_NEAR_M = float(os.environ.get("WARNING_NEAR_M", "2"))
CENTER_BAND_FRACTION = float(os.environ.get("CENTER_BAND_FRACTION", "0.20"))
LIDAR_STALE_SECONDS = float(os.environ.get("LIDAR_STALE_SECONDS", "0.5"))
CENTER_LED_MODE = os.environ.get("CENTER_LED_MODE", "all")  # all or center


# -----------------------------------------------------------------------------------------------
# User-defined class to be used in the callback function
# -----------------------------------------------------------------------------------------------
# Inheritance from the app_callback_class
class user_app_callback_class(app_callback_class):
    def __init__(self):
        super().__init__()
        port = os.environ.get("TFMINI_PORT", "/dev/ttyUSB0")
        self.lidar = TFMiniReader(port=port)
        self.lidar.start()

        self.leds = None
        if LED_ENABLED:
            self.leds = LEDStripController(
                num_pixels=LED_COUNT,
                brightness=LED_BRIGHTNESS,
            )

        # Store what cairooverlay should draw:
        # (x1,y1,x2,y2, distance_m, tracking_id)
        self.lidar_target = None

    def cleanup(self):
        if self.leds is not None:
            try:
                self.leds.off()
            except Exception:
                pass
        try:
            self.lidar.stop()
        except Exception:
            pass


# -----------------------------------------------------------------------------------------------
# User-defined callback function
# -----------------------------------------------------------------------------------------------
def attach_distance_label(detection, dist_m, tracking_id):
    # Clear any old distance classification(s) if you want to avoid duplicates
    # (optional - depends on how hailooverlay behaves in your version)
    try:
        existing = detection.get_objects_typed(hailo.HAILO_CLASSIFICATION)
        for obj in existing:
            # Only remove ones we previously added (prefix match)
            if hasattr(obj, "get_label") and str(obj.get_label()).startswith("range:"):
                detection.remove_object(obj)
    except Exception:
        pass

    if dist_m is None:
        return

    label = f"range: {dist_m:.1f} m"
    try:
        # name, label, confidence
        cls = hailo.HailoClassification("lidar", label, 1.0)
        detection.add_object(cls)
    except Exception as e:
        print(f"Could not attach classification label: {e}")


def normalize_center_side(side: str) -> str:
    if side != "center":
        return side
    return "all" if CENTER_LED_MODE == "all" else "center"


# This is the callback function that will be called when data is available from the pipeline
def app_callback(pad, info, user_data):
    buffer = info.get_buffer()
    if buffer is None:
        return Gst.PadProbeReturn.OK

    user_data.increment()

    format, width, height = get_caps_from_pad(pad)

    frame = None
    if getattr(user_data, "use_frame", False) and format and width and height:
        frame = get_numpy_from_buffer(buffer, format, width, height)

    roi = hailo.get_roi_from_buffer(buffer)
    hailo_detections = roi.get_objects_typed(hailo.HAILO_DETECTION)

    for detection in hailo_detections:
        if detection.get_label() not in target_classes:
            roi.remove_object(detection)

    filtered_detections = [
        detection for detection in hailo_detections
        if detection.get_label() in target_classes
    ]

    beam_x = width * 0.5
    beam_y = height * 0.5

    best = None
    best_score = None

    for detection in filtered_detections:
        uid_objs = detection.get_objects_typed(hailo.HAILO_UNIQUE_ID)
        tracking_id = uid_objs[0].get_id() if uid_objs else -1
        if tracking_id not in emitted_ids:
            print(f"Detection!: {tracking_id} {detection.get_label()} {detection.get_confidence():.2f}\n")
            emitted_ids.add(tracking_id)
            payload = {
                "tracking_id": tracking_id,
                "label": detection.get_label()
            }
            print("Event:", json.dumps(payload))

        if detection.get_label() != "person":
            continue

        bbox = detection.get_bbox()
        x1 = bbox.xmin() * width
        y1 = bbox.ymin() * height
        x2 = bbox.xmax() * width
        y2 = bbox.ymax() * height

        contains = (beam_x >= x1 and beam_x <= x2 and beam_y >= y1 and beam_y <= y2)

        cx = (x1 + x2) * 0.5
        cy = (y1 + y2) * 0.5
        dist2 = (cx - beam_x) ** 2 + (cy - beam_y) ** 2

        score = dist2 - (1e12 if contains else 0)

        if best_score is None or score < best_score:
            best_score = score
            best = (detection, x1, y1, x2, y2, tracking_id)

    dist_m, ts = user_data.lidar.latest()
    if ts is None or (time.time() - ts) > LIDAR_STALE_SECONDS:
        dist_m = None

    user_data.lidar_target = None

    if best is not None:
        det_obj, x1, y1, x2, y2, tracking_id = best
        attach_distance_label(det_obj, dist_m, tracking_id)
        user_data.lidar_target = (x1, y1, x2, y2, dist_m, tracking_id)

        if user_data.leds is not None:
            side = classify_side(
                bbox=(x1, y1, x2, y2),
                frame_width=width,
                center_band_fraction=CENTER_BAND_FRACTION,
            )
            side = normalize_center_side(side)
            user_data.leds.set_warning(
                side=side,
                distance_m=dist_m,
                far_threshold_m=WARNING_FAR_M,
                near_threshold_m=WARNING_NEAR_M,
            )
    else:
        if user_data.leds is not None:
            user_data.leds.off()

    return Gst.PadProbeReturn.OK


if __name__ == "__main__":
    user_data = user_app_callback_class()
    app = GStreamerDetectionApp(app_callback, user_data)
    try:
        app.run()
    finally:
        user_data.cleanup()
