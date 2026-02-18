import time

import numpy as np
import ray


@ray.remote
class MockCamera:
    def __init__(self, model_handle, fps=30):
        self.model = model_handle
        self.fps = fps
        self.running = True

    def start_sensing(self):
        print("Camera feed started...")
        frame_count = 0
        
        while self.running:
            # 1. Simulate capturing a 640x480 RGB image
            mock_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
            
            # 2. Push to the model (Non-blocking)
            # don't 'ray.get()' because you don't want to wait for the ML model 
            # to finish before grabbing the next frame.
            self.model.handle_camera_input.remote(mock_frame, frame_count)
            
            frame_count += 1
            time.sleep(1 / self.fps)

    def stop(self):
        self.running = False

    @property
    def name(self):
        """Safely gets the name of a Ray-decorated or standard class."""
        if hasattr(self, "_remote_class"):
            return self._remote_class.__name__
        elif hasattr(self, "__name__"):
            return self.__name__
        else:
            return 'MockCamera'
