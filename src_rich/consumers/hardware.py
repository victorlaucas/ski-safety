import ray


@ray.remote
class MockLEDHandler:
    def trigger(self, color, pattern):
        # This is where you would use RPi.GPIO or similar to activate the LED
        print(f"[Hardware] LED is now {color} ({pattern})")

@ray.remote
class MockHapticHandler:
    def vibrate(self, intensity):
        # Same here, RPi.GPIO or similar to start and stop the haptic motor
        print(f"[Hardware] Haptic motor pulsing at {intensity*100}%")
