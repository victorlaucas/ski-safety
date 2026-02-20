import ray
from ray.actor import ActorHandle

from src.consumers.hardware import HapticHandler, LEDHandler
from src.consumers.inference import MLInference
from src.consumers.interpreter import Interpreter
from src.producers.camera import MockCamera
from src.producers.lidar import MockLidar


def main():
    ray.init()

    # 1. Start the leaf nodes (Hardware)
    led = LEDHandler.remote()
    haptic = HapticHandler.remote()

    # 2. Start the Interpreter (Needs HW handles)
    interp = Interpreter.remote({"led": led, "haptic": haptic})

    # 3. Start the ML Model (Needs Interpreter handle)
    model = MLInference.remote(interp)

    # 4. Start the Sensors (Needs Model handle)
    camera = MockCamera.remote(model)
    lidar = MockLidar.remote(model)

    # 5. Kick off the continuous loops
    camera.start_sensing.remote()
    lidar.start_sensing.remote()

    # Keep alive logic...
