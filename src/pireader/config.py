# pragma: exclude file
"""System-wide hardware topology and constants."""

import dataclasses

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
class GestureConfig:
    """The configurations for each gesture."""

    fast_tap: FastTapConfig = FastTapConfig()
    swipe: SwipeConfig = SwipeConfig()
    hold: HoldConfig = HoldConfig()
    drag: DragConfig = DragConfig()


GESTURE_CONFIG = GestureConfig()
