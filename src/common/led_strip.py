import board
import neopixel


class LEDStripController:
    """
    Controls a WS2812B / NeoPixel strip connected to GPIO18.

    Assumptions:
    - Data pin: GPIO18 / board.D18 / physical pin 12
    - Strip is arranged linearly
    - Left half of strip represents the left side of the camera frame
    - Right half of strip represents the right side of the camera frame
    """

    def __init__(
        self,
        num_pixels: int,
        brightness: float = 0.15,
        pin=board.D18,
        pixel_order=neopixel.GRB,
    ) -> None:
        if num_pixels <= 0:
            raise ValueError("num_pixels must be greater than 0")

        self.num_pixels = num_pixels
        self.left_end = num_pixels // 2
        self.right_start = self.left_end

        self.pixels = neopixel.NeoPixel(
            pin,
            num_pixels,
            brightness=brightness,
            auto_write=False,
            pixel_order=pixel_order,
        )

        self._last_state = None
        self.off()

    def show(self) -> None:
        self.pixels.show()

    def off(self) -> None:
        if self._last_state == ("off", None):
            return
        self.pixels.fill((0, 0, 0))
        self.pixels.show()
        self._last_state = ("off", None)

    def fill_all(self, color: tuple[int, int, int]) -> None:
        self.pixels.fill(color)
        self.pixels.show()
        self._last_state = ("all", color)

    def fill_left(self, color: tuple[int, int, int]) -> None:
        self.pixels.fill((0, 0, 0))
        for i in range(0, self.left_end):
            self.pixels[i] = color
        self.pixels.show()
        self._last_state = ("left", color)

    def fill_right(self, color: tuple[int, int, int]) -> None:
        self.pixels.fill((0, 0, 0))
        for i in range(self.right_start, self.num_pixels):
            self.pixels[i] = color
        self.pixels.show()
        self._last_state = ("right", color)

    def fill_center(self, color: tuple[int, int, int], width_fraction: float = 0.3) -> None:
        width_fraction = max(0.0, min(1.0, width_fraction))
        center_width = max(1, int(self.num_pixels * width_fraction))
        start = (self.num_pixels - center_width) // 2
        end = start + center_width

        self.pixels.fill((0, 0, 0))
        for i in range(start, end):
            self.pixels[i] = color
        self.pixels.show()
        self._last_state = ("center", color)

    def set_side(self, side: str | None, color: tuple[int, int, int]) -> None:
        if side in (None, "off"):
            self.off()
        elif side == "left":
            self.fill_left(color)
        elif side == "right":
            self.fill_right(color)
        elif side == "center":
            self.fill_center(color)
        elif side == "all":
            self.fill_all(color)
        else:
            raise ValueError(f"Unsupported side: {side}")

    def set_warning(
        self,
        side: str | None,
        distance_m: float | None,
        far_threshold_m: float,
        near_threshold_m: float,
    ) -> None:
        """
        Basic distance-based warning colors:
        - <= near_threshold_m: red
        - <= far_threshold_m: orange
        - otherwise off
        """
        if distance_m is None:
            self.off()
            return

        if distance_m <= near_threshold_m:
            color = (255, 0, 0)
        elif distance_m <= far_threshold_m:
            color = (0, 0, 255)
        else:
            self.off()
            return

        desired_state = (side, color)
        if self._last_state != desired_state:
            self.set_side(side, color)


def get_bbox_center_x(bbox: tuple[float, float, float, float]) -> float:
    x1, _, x2, _ = bbox
    return (x1 + x2) / 2.0


def get_bbox_area(bbox: tuple[float, float, float, float]) -> float:
    x1, y1, x2, y2 = bbox
    return max(0.0, x2 - x1) * max(0.0, y2 - y1)


def classify_side(
    bbox: tuple[float, float, float, float],
    frame_width: int,
    center_band_fraction: float = 0.2,
) -> str:
    """
    Splits the frame into left / center / right.
    center_band_fraction=0.2 means the middle 20% of the frame is treated as center.
    """
    if frame_width <= 0:
        raise ValueError("frame_width must be > 0")

    center_x = get_bbox_center_x(bbox)

    center_band_fraction = max(0.0, min(1.0, center_band_fraction))
    center_band_width = frame_width * center_band_fraction
    center_left = (frame_width / 2.0) - (center_band_width / 2.0)
    center_right = (frame_width / 2.0) + (center_band_width / 2.0)

    if center_x < center_left:
        return "left"
    if center_x > center_right:
        return "right"
    return "center"


def choose_primary_person(detections: list[dict]) -> dict | None:
    """
    Picks the most relevant person detection.
    Current heuristic: largest person bbox.

    Expected detection dict format:
    {
        "label": "person",
        "confidence": 0.87,
        "bbox": (x1, y1, x2, y2),
        ...
    }
    """
    people = []
    for det in detections:
        if det.get("label") != "person":
            continue
        bbox = det.get("bbox")
        if bbox is None:
            continue
        people.append(det)

    if not people:
        return None

    return max(people, key=lambda d: get_bbox_area(d["bbox"]))
