import time
import serial

PORT = "/dev/serial/by-id/usb-Prolific_Technology_Inc._USB-Serial_Controller_CAA9o151406-if00-port0"
BAUD = 115200

FRAME_HEADER = b"\x59\x59"
FRAME_LEN = 9

def read_tfmini_frame(ser: serial.Serial):
    """
    Read and validate one TFmini frame. Returns (distance_cm, strength, temp_c) or None on timeout.
    """
    # Find header
    while True:
        b = ser.read(1)
        if not b:
            return None  # timeout
        if b == b"\x59":
            b2 = ser.read(1)
            if not b2:
                return None
            if b2 == b"\x59":
                break  # header found

    payload = ser.read(FRAME_LEN - 2)  # remaining 7 bytes
    if len(payload) != FRAME_LEN - 2:
        return None

    frame = FRAME_HEADER + payload

    # checksum: sum of first 8 bytes & 0xFF must equal byte 8
    checksum = sum(frame[0:8]) & 0xFF
    if checksum != frame[8]:
        return None  # bad frame, discard

    dist = frame[2] | (frame[3] << 8)
    strength = frame[4] | (frame[5] << 8)
    temp_raw = frame[6] | (frame[7] << 8)
    temp_c = temp_raw / 8.0 - 256  # common TFmini temp conversion

    return dist, strength, temp_c

def main():
    ser = serial.Serial(PORT, BAUD, timeout=1)
    ser.reset_input_buffer()
    print(f"TFmini listening on {PORT} @ {BAUD}. Ctrl+C to stop.")

    try:
        while True:
            out = read_tfmini_frame(ser)
            if out is None:
                print("Timeout / no valid frame")
                continue

            dist, strength, temp_c = out
            print(f"{time.time():.3f}  Distance: {dist:4d} cm  Strength: {strength:5d}  Temp: {temp_c:6.1f} C")
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        ser.close()

if __name__ == "__main__":
    main()
