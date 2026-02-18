import importlib
import platform
import time

import ray

# 1. Logic to check for Pi environment
IS_PI = platform.system() == "Linux" and platform.machine() in ["aarch64", "armv7l"]

def get_class(module_path, class_name):
    """Dynamically loads a class if it exists and dependencies are met."""
    try:
        module = importlib.import_module(module_path)
        return getattr(module, class_name)
    except (ImportError, AttributeError, ModuleNotFoundError):
        return None

# 2. Attempt to load Hardware classes, fallback to Mocks
# Format: (module_path, class_name)
HWCamera = get_class("src.producers.camera", "HWCamera") if IS_PI else None
HWLidar = get_class("src.producers.lidar", "HWLidar") if IS_PI else None
HWLED = get_class("src.consumers.hardware", "HWLEDHandler") if IS_PI else None
HWHaptic = get_class("src.consumers.hardware", "HWHapticHandler") if IS_PI else None

from src.consumers.hardware import MockHapticHandler, MockLEDHandler
from src.consumers.inference import MLInference
from src.consumers.interpreter import Interpreter
# 3. Always import Mocks (they should be platform-agnostic)
from src.producers.camera import MockCamera
from src.producers.lidar import MockLidar


def main():
    ray.init(ignore_reinit_error=True, include_dashboard=True)

    # --- Hardware Selection Logic ---
    # We use HW version ONLY if we are on a Pi AND the class was successfully loaded
    selected_camera = HWCamera if (IS_PI and HWCamera) else MockCamera
    selected_lidar = HWLidar if (IS_PI and HWLidar) else MockLidar
    selected_led = HWLED if (IS_PI and HWLED) else MockLEDHandler
    selected_haptic = HWHaptic if (IS_PI and HWHaptic) else MockHapticHandler

    print(f"--- Initialization ---")
    print(f"Environment: {'Raspberry Pi' if IS_PI else 'Laptop/Dev'}")
    print(f"Using Camera: {selected_camera.name}")
    print(f"Using LiDAR:  {selected_lidar.name}")

    # --- Orchestration ---
    led = selected_led.remote()
    haptic = selected_haptic.remote()
    
    interp = Interpreter.remote({"led": led, "haptic": haptic})
    model = MLInference.remote(interp)

    camera = selected_camera.remote(model)
    lidar = selected_lidar.remote(model)

    # Start sensing
    camera.start_sensing.remote()
    lidar.start_sensing.remote()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")
        ray.shutdown()

if __name__ == '__main__':
    main()
