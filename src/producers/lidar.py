import time

import numpy as np
import ray


@ray.remote
class MockLidar:
    def __init__(self, model_handle):
        self.model = model_handle
        self.running = True

    def start_sensing(self):
        print('LiDAR started')
        while self.running:
            # Generate mock XYZ data
            mock_data = np.random.rand(3, 1024)
            ts = time.time()
            
            # Use a specific method for LiDAR data
            self.model.handle_lidar_input.remote(mock_data, ts)
            
            time.sleep(0.1) # 10Hz is a standard LiDAR rate

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
