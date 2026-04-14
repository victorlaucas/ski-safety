import time
import board
import neopixel

PIXEL_PIN = board.D18
NUM_PIXELS = 30
BRIGHTNESS = 0.1

pixels = neopixel.NeoPixel(
    PIXEL_PIN,
    NUM_PIXELS,
    brightness=BRIGHTNESS,
    auto_write=True,
)

try:
    while True:
        pixels.fill((255, 0, 0))
        time.sleep(1)
        pixels.fill((0, 255, 0))
        time.sleep(1)
        pixels.fill((0, 0, 255))
        time.sleep(1)
        pixels.fill((0, 0, 0))
        time.sleep(1)
except KeyboardInterrupt:
    pixels.fill((0, 0, 0))