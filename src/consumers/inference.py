import ray


@ray.remote
class MLInference:
    def __init__(self, interpreter_handle):
        self.interpreter = interpreter_handle
        self.latest_image = None
        self.latest_lidar = None

    def handle_camera_input(self, frame, count):
        print(f'Received new image data. Count: {count}')
        self.latest_image = frame
        self._run_inference()

    def handle_lidar_input(self, point_cloud, ts):
        print(f'Received new lidar data timestampped {ts}')
        self.latest_lidar = point_cloud
        self._run_inference()

    def _run_inference(self):
        # Only run if we have both pieces of data (Sensor Fusion)
        if self.latest_image is not None and self.latest_lidar is not None:
            # logic to detect skiers...
            pass
