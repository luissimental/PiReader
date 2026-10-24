import enum
import time
from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from pireader import config
from pireader.common import models

if TYPE_CHECKING:
    from pireader.hardware import hal

_AcceptsTouchEvents = Callable[[list[models.TouchEvent]], Any]


class PowerMode(enum.Enum):
    """The power mode of the touch controller mapped to register values."""

    ACTIVE = 0x00
    MONITOR = 0x01
    HIBERNATE = 0x03


class _TouchRegisters:
    REG_POWER_MODE = 0xA5
    REG_TD_STATUS = 0x02
    TOUCH_POINTS = 2

    # Offsets relative to TD_STATUS (0x02) when doing a single block read
    STRIDE = 6  # bytes per touch point
    BLOCK_LENGTH = 1 + TOUCH_POINTS * STRIDE
    XH = 1
    XL = 2
    YH = 3
    YL = 4

    # Masks
    TOUCH_POINTS_MASK = 0x0F
    ID_MASK = 0xF0
    X_HIGH_MASK = 0x0F
    Y_HIGH_MASK = 0x0F


class TouchDriver:
    """Driver for the FT6336U touch controller."""

    def __init__(
        self,
        hardware: hal.PlatformHAL,
        /,
        *,
        on_touch: _AcceptsTouchEvents | None,
        initialize: bool = True,
        i2c_addr: int = config.TOUCH_I2C_ADDR,
        rst_pin: int = config.TOUCH_RST_PIN,
        int_pin: int = config.TOUCH_INT_PIN,
    ) -> None:
        """Initialize the FT6336U touch controller hardware.

        Args:
          hardware:
            The platform's hardware manager.
          on_touch:
            The callback function to handle touch interrupts.
            This function must accept a list of `TouchEvent` objects.
          initialize:
            If True, the reset and interrupt pins are initialized, then a
            hardware reset is performed.
          i2c_addr:
            The touch controller's I2C slave address.
          rst_pin:
            The reset pin number.
          int_pin:
            The interrupt pin number.

        """
        self._hw = hardware
        self._on_touch = on_touch
        self._is_active = False

        self._i2c_addr = i2c_addr
        self._rst_pin_num = rst_pin
        self._int_pin_num = int_pin

        if initialize:
            self.initialize()

    @property
    def on_touch(self) -> _AcceptsTouchEvents | None:
        """The callback handler of a touch event."""
        return self._on_touch

    @on_touch.setter
    def on_touch(self, callback: _AcceptsTouchEvents | None) -> None:
        self._on_touch = callback

    def initialize(self) -> None:
        """Enable pins and perform a hardware reset."""
        if not self._is_active:
            self._reset_pin = self._hw.request_output_pin(self._rst_pin_num)
            self._int_pin = self._hw.request_input_pin(
                self._int_pin_num, pull_up=True
            )
            self._int_pin.when_activated = self._on_touch_interrupt
            self._is_active = True

        self.hardware_reset()

    def hardware_reset(self) -> None:
        """Perform a hardware reset on the touch controller."""
        if not self._is_active:
            msg = "Touch driver is not active."
            raise RuntimeError(msg)

        self._reset_pin.off()
        time.sleep(0.01)  # 10 ms
        self._reset_pin.on()
        time.sleep(0.2)  # 200 ms

    def set_power_mode(self, mode: PowerMode) -> None:
        """Change the power mode of the touch controller.

        Monitor mode scans at a reduced speed and power. When a touch
        is detected, the controller automatically enters active mode.

        Hibernate mode powers down the touch controller, so `hardware_reset`
        must be called to wake the device up and start receiving touch input.
        """
        if not self._is_active:
            msg = "Touch driver is not active."
            raise RuntimeError(msg)

        if not isinstance(mode, PowerMode):  # pragma: no cover
            msg = f"Unknown power mode: {mode!r}"
            raise TypeError(msg)

        self._hw.i2c_write(
            self._i2c_addr, _TouchRegisters.REG_POWER_MODE, mode.value
        )
        time.sleep(0.05)  # 50 ms

    def clean_up(self) -> None:
        """Clean up the touch controller's hardware resources."""
        if not self._is_active:
            return

        self._int_pin.when_activated = None
        self._hw.release_pin(self._rst_pin_num)
        self._hw.release_pin(self._int_pin_num)
        self._is_active = False

    def _on_touch_interrupt(self) -> None:
        """Interrupt pin callback when a touch event is detected."""
        if self._on_touch is not None:
            touches = self._read_touches()
            self._on_touch(touches)

    def _read_touches(self) -> list[models.TouchEvent]:
        """Acquire touch coordinates."""
        if not self._is_active:
            msg = "Touch driver is not active."
            raise RuntimeError(msg)

        now = time.time()
        data = self._hw.i2c_read_block_data(
            self._i2c_addr,
            _TouchRegisters.REG_TD_STATUS,
            _TouchRegisters.BLOCK_LENGTH,
        )

        touch_count = data[0] & _TouchRegisters.TOUCH_POINTS_MASK
        if touch_count == 0 or touch_count > _TouchRegisters.TOUCH_POINTS:
            return []

        touches: list[models.TouchEvent] = []
        for i in range(touch_count):
            offset = i * _TouchRegisters.STRIDE

            xh = data[offset + _TouchRegisters.XH]
            xl = data[offset + _TouchRegisters.XL]
            yh = data[offset + _TouchRegisters.YH]
            yl = data[offset + _TouchRegisters.YL]

            touch_id = (yh & _TouchRegisters.ID_MASK) >> 4
            x = ((xh & _TouchRegisters.X_HIGH_MASK) << 8) | xl
            y = ((yh & _TouchRegisters.Y_HIGH_MASK) << 8) | yl

            point = models.TouchEvent(touch_id, x, y, now)
            touches.append(point)

        return touches
