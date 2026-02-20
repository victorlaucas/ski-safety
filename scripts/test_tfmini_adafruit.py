#!/usr/bin/env python3
import time
import serial
import adafruit_tfmini
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

PORT = "/dev/serial/by-id/usb-Prolific_Technology_Inc._USB-Serial_Controller_CAA9o151406-if00-port0"
BAUD = 115200  # TFmini Plus default


def main():
    # Open USB-TTL serial port
    ser = serial.Serial(PORT, baudrate=BAUD, timeout=1)
    ser.reset_input_buffer()
    time.sleep(0.1)

    # Create TFmini object
    tfmini = adafruit_tfmini.TFmini(ser)
   

    print(f"TFmini (Adafruit) reading on {PORT} @ {BAUD}. Ctrl+C to stop.")

    try:
        
        while True:    
            timeStamp = datetime.now(timezone.utc).astimezone(ZoneInfo("America/Denver")).isoformat()
            try:
                d = tfmini.distance   # cm
                s = tfmini.strength
                # print(f"{time.time():.3f}  Distance: {d:4d} cm  Strength: {s:5d}")
                print(f"{timeStamp}  Distance: {d:4d} cm  Strength: {s:5d}")
            except RuntimeError as e:
                # Usually: "Timed out looking for valid data"
                print(f"{timeStamp}  Read error: {e}")
                # Try to recover by clearing buffer
                ser.reset_input_buffer()

            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nStopping...")

    finally:
        ser.close()

if __name__ == "__main__":
    main()