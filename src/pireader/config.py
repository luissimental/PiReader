# pragma: exclude file
"""System-wide hardware topology and constants."""

import dataclasses
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pireader.common import models


# Raspberry Pi Wiring
RPI_I2C_BUS = 3


# Touch Controller Wiring
TOUCH_I2C_ADDR = 0x38
TOUCH_RST_PIN = 26
TOUCH_INT_PIN = 19


# Gesture Configuration
@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class FastTapConfig:
    """Threshold constants for the FAST TAP gesture."""

    max_px: int = 10
    max_sec: float = 0.1

    def threshold_is_met(self, distance: float, duration: float) -> bool:
        """Determine whether the distance and duration meet the threshold."""
        return distance < self.max_px and duration < self.max_sec


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class SwipeConfig:
    """Threshold constants for the SWIPE gesture."""

    min_px: int = 50
    max_sec: float = 0.2

    def threshold_is_met(self, distance: float, duration: float) -> bool:
        """Determine whether the distance and duration meet the threshold."""
        return distance >= self.min_px and duration < self.max_sec


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class HoldConfig:
    """Threshold constants for the HOLD gesture."""

    max_px: int = 10
    min_sec: float = 0.25

    def threshold_is_met(self, distance: float, duration: float) -> bool:
        """Determine whether the distance and duration meet the threshold."""
        return distance < self.max_px and duration >= self.min_sec


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class DragConfig:
    """Threshold constants for the DRAG gesture."""

    min_px: int = 10

    def threshold_is_met(self, distance: float) -> bool:
        """Determine whether the distance meets the threshold."""
        return distance >= self.min_px


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class PanConfig:
    """Threshold constants for the PAN gesture."""

    min_px: int = 10

    def threshold_is_met(
        self,
        start_midpoint: models.TouchEvent,
        current_midpoint: models.TouchEvent,
    ) -> bool:
        """Determine whether the midpoints meet the threshold."""
        distance = start_midpoint.distance_to(current_midpoint)
        return distance >= self.min_px


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class ZoomConfig:
    """Threshold constants for the ZOOM gesture."""

    min_px: int = 10

    def threshold_is_met(self, distance: float) -> bool:
        """Determine whether the distance meets the threshold."""
        return distance >= self.min_px


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class RotateConfig:
    """Threshold constants for the ROTATE gesture."""

    min_deg: float = 5.0

    def threshold_is_met(self, angular_diff: float) -> bool:
        """Determine whether the angle in degrees meets the threshold."""
        return angular_diff >= self.min_deg


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class GestureConfig:
    """The configurations for each gesture."""

    # Single-touch gestures
    fast_tap: FastTapConfig = FastTapConfig()
    swipe: SwipeConfig = SwipeConfig()
    hold: HoldConfig = HoldConfig()
    drag: DragConfig = DragConfig()

    # Multi-touch gestures
    pan: PanConfig = PanConfig()
    zoom: ZoomConfig = ZoomConfig()
    rotate: RotateConfig = RotateConfig()


GESTURE_CONFIG = GestureConfig()
