#!/usr/bin/env python3
import time
import serial
import argparse
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

# utc_now = datetime.now(timezone.utc).astimezone(ZoneInfo("America/Denver"))



HEADER = b"\x59\x59"
FRAME_LEN = 9

def checksum_ok(frame: bytes) -> bool:
    # frame[8] should equal low 8 bits of sum(frame[0:8])
    return ((sum(frame[0:8]) & 0xFF) == frame[8])

def read_frame(ser: serial.Serial) -> bytes | None:
    """
    Find 0x59 0x59 then read the remaining 7 bytes.
    Returns a 9-byte frame or None on timeout.
    """
    while True:
        b = ser.read(1)
        if not b:
            return None
        if b != b"\x59":
            continue
        b2 = ser.read(1)
        if not b2:
            return None
        if b2 == b"\x59":
            payload = ser.read(FRAME_LEN - 2)
            if len(payload) != FRAME_LEN - 2:
                return None
            return HEADER + payload

def decode(frame: bytes):
    dist = frame[2] | (frame[3] << 8)
    strength = frame[4] | (frame[5] << 8)
    temp_raw = frame[6] | (frame[7] << 8)
    temp_c = temp_raw / 8.0 - 256.0
    return dist, strength, temp_c

def send_cmd(ser: serial.Serial, cmd_bytes: bytes):
    """
    Send a TFmini command frame (starts with 0x5A) and optionally read back an echo.
    Datasheet command frames use: Head=0x5A, Len, ID, Payload..., Checksum
    Checksum = low 8 bits of sum(all bytes except checksum).
    """
    ser.write(cmd_bytes)
    ser.flush()

def build_cmd(head: int, length: int, cmd_id: int, payload: bytes) -> bytes:
    frame_wo_ck = bytes([head, length, cmd_id]) + payload
    ck = sum(frame_wo_ck) & 0xFF
    return frame_wo_ck + bytes([ck])

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", default="/dev/ttyUSB0")
    ap.add_argument("--baud", type=int, default=115200)
    ap.add_argument("--hz", type=float, default=20.0)
    ap.add_argument("--set-unit", choices=["cm", "mm"], default=None,
                    help="Optionally set measurement unit using datasheet command.")
    args = ap.parse_args()

    dt = 1.0 / max(args.hz, 1.0)

    ser = serial.Serial(args.port, args.baud, timeout=1)
    ser.reset_input_buffer()
    time.sleep(0.1)

    # Optional: set measurement unit (datasheet: 01=cm, 06=mm)
    if args.set_unit:
        unit = 0x01 if args.set_unit == "cm" else 0x06
        # Command: Head 0x5A, Len 0x05, ID 0x05, Payload [unit]
        cmd = build_cmd(0x5A, 0x05, 0x05, bytes([unit]))
        print(f"Sending set-unit command: {cmd.hex()}")
        send_cmd(ser, cmd)
        # Recommended by datasheet when modifying parameters: send Save Settings
        # Save settings command (table shows 5A 04 11 6F) — we can build it too:
        save = build_cmd(0x5A, 0x04, 0x11, b"")
        print(f"Sending save-settings command: {save.hex()}")
        send_cmd(ser, save)
        time.sleep(0.2)
        ser.reset_input_buffer()

    print(f"Listening on {args.port} @ {args.baud}. Ctrl+C to stop.")
    print("Columns: time | dist_raw | unit_guess | strength | tempC | frame_hex | ck_ok")

    try:
        while True:
            frame = read_frame(ser)
            timeStamp = datetime.now(timezone.utc).astimezone(ZoneInfo("America/Denver")).isoformat()
            if frame is None:
                print(f"{timeStamp}  TIMEOUT")
                continue

            ok = checksum_ok(frame)
            dist, strength, temp_c = decode(frame)

            # We don't *know* the unit unless we set it; default is typically cm.
            # We'll label the raw value and a "cm guess".
            print(
                f"{timeStamp}  dist={dist:5d}  (~{dist:4d} cm if in cm)  "
                f"str={strength:5d}  temp={temp_c:6.1f}C  "
                f"frame={frame.hex()}"
            )

            time.sleep(dt + .5)

    except KeyboardInterrupt:
        pass
    finally:
        ser.close()

if __name__ == "__main__":
    main()