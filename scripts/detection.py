import gi
gi.require_version("Gst", "1.0")
gi.require_version("GLib", "2.0")
from gi.repository import Gst, GLib
from lidar_tfmini import TFMiniReader
import json
import hailo
import os
import time

from hailo_rpi_common import (
    get_caps_from_pad,
    get_numpy_from_buffer,
    app_callback_class,
)

from detection_pipeline import GStreamerDetectionApp

# tracker = sv.ByteTrack()
# label_annotator = sv.LabelAnnotator()

# Set to keep track of emitted tracking IDs
emitted_ids = set()

# Define the target classes for detection
# this should align to the COCO list of objects
# https://github.com/ultralytics/ultralytics/blob/main/ultralytics/cfg/datasets/coco.yaml
# note that this just filters which ones we'll call MQTT on, they'll still appear as bounding boxes because we haven't
# told hailo to exclude them.
# target_classes = {'person', 'car', 'bird'}
target_classes = {'person'}


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

        # Store what cairooverlay should draw:
        # (x1,y1,x2,y2, distance_m, tracking_id)
        self.lidar_target = None

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
        # If this constructor name differs on your installed bindings, print once for debug
        # (better than silently failing)
        print(f"Could not attach classification label: {e}")

# This is the callback function that will be called when data is available from the pipeline
def app_callback(pad, info, user_data):
    # Get the GstBuffer from the probe info
    buffer = info.get_buffer()
    if buffer is None:
        return Gst.PadProbeReturn.OK

    # Increment frame count
    user_data.increment()

    # Get the caps from the pad
    format, width, height = get_caps_from_pad(pad)

    # Retrieve the video frame if required
    frame = None
    if getattr(user_data, "use_frame", False) and format and width and height:
        frame = get_numpy_from_buffer(buffer, format, width, height)

    # Extract detections from the buffer
    roi = hailo.get_roi_from_buffer(buffer)
    hailo_detections = roi.get_objects_typed(hailo.HAILO_DETECTION)

    # Remove all non-person detections so hailooverlay doesn't draw them
    for detection in hailo_detections:
        if detection.get_label() not in target_classes:
            roi.remove_object(detection)

    # Filter detections to include only target classes
    filtered_detections = [
        detection for detection in hailo_detections
        if detection.get_label() in target_classes
    ]

    # Choose a "beam point" in the frame (start with center)
    beam_x = width * 0.5
    beam_y = height * 0.5

    best = None
    best_score = None

    # Prepare detection data for Supervision
    boxes = []
    confidences = []
    class_ids = []

    for detection in filtered_detections:
        uid_objs = detection.get_objects_typed(hailo.HAILO_UNIQUE_ID)
        tracking_id = uid_objs[0].get_id() if uid_objs else -1
        # Emit event only if the tracking ID hasn't been emitted before
        if tracking_id not in emitted_ids:
            print(f"Detection!: {tracking_id} {detection.get_label()} {detection.get_confidence():.2f}\n")
            emitted_ids.add(tracking_id)
            payload = {
                "tracking_id" : tracking_id,
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

        # Prefer "contains", otherwise nearest center
        score = dist2 - (1e12 if contains else 0)

        if best_score is None or score < best_score:
            best_score = score
            best = (detection, x1, y1, x2, y2, tracking_id)

        label = detection.get_label()
        bbox = detection.get_bbox()
        confidence = detection.get_confidence()
        boxes.append([bbox.xmin() * width, bbox.ymin() * height, bbox.xmax() * width, bbox.ymax() * height])
        confidences.append(confidence)
        # class_ids.append(label)  # Ensure label is an integer class ID
    
    dist_m, ts = user_data.lidar.latest()
    # Optional: treat readings older than 0.5s as invalid
    if ts is None or (time.time() - ts) > 0.5:
        dist_m = None

    if best is not None:
        det_obj, x1, y1, x2, y2, tracking_id = best
        attach_distance_label(det_obj, dist_m, tracking_id)
        user_data.lidar_target = (x1, y1, x2, y2, dist_m, tracking_id)

    return Gst.PadProbeReturn.OK


if __name__ == "__main__":
    # Create an instance of the user app callback class
    user_data = user_app_callback_class()
    app = GStreamerDetectionApp(app_callback, user_data)
    app.run()