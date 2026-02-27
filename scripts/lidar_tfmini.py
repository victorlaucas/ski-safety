# scripts/lidar_tfmini.py
import threading
import time
import serial
import adafruit_tfmini

class TFMiniReader:
    """
    Continuously reads distance from a TFmini/TFmini-Plus over UART (via USB-serial).
    Stores latest distance in meters (float) and a timestamp.
    """
    def __init__(self, port: str, baudrate: int = 115200, timeout: float = 0.2, hz: float = 20.0):
        self._ser = serial.Serial(port, baudrate=baudrate, timeout=timeout)
        self._tf = adafruit_tfmini.TFmini(self._ser, timeout=timeout)
        self._period = 1.0 / max(hz, 1.0)

        self._lock = threading.Lock()
        self._running = False
        self._thread = None

        self._distance_m = None
        self._ts = None

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)
        try:
            self._ser.close()
        except Exception:
            pass

    def latest(self):
        """Returns (distance_m or None, timestamp or None)."""
        with self._lock:
            return self._distance_m, self._ts

    def _run(self):
        while self._running:
            try:
                # Adafruit driver returns distance in cm
                cm = self._tf.distance
                if cm and cm > 0:
                    with self._lock:
                        self._distance_m = cm / 100.0
                        self._ts = time.time()
            except Exception:
                # If the sensor glitches, keep last good reading
                pass
            time.sleep(self._period)