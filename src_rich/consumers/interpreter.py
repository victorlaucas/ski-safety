import ray


@ray.remote
class Interpreter:
    def __init__(self, hardware_handles: dict):
        # hardware_handles = {"led": led_actor, "haptic": haptic_actor}
        self.hw = hardware_handles

    def evaluate_threat(self, prediction):
        # Example logic: Only warn if confidence > 85% and distance < 5m
        if prediction['label'] == 'skier' and prediction['distance'] < 5.0:
            print(f"[Interpreter] THREAT DETECTED at {prediction['distance']}m")
            
            # Dispatch to multiple hardware outputs in parallel
            self.hw['led'].trigger.remote("RED", "BLINK")
            self.hw['haptic'].vibrate.remote(intensity=1.0)
        else:
            self.hw['led'].trigger.remote("GREEN", "SOLID")
