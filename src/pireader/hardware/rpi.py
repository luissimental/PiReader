import threading
from typing import TYPE_CHECKING, Self, override

import gpiozero
import smbus2
import spidev

from pireader.hardware import hal

if TYPE_CHECKING:
    from collections.abc import Sequence


I2C_BUS = 3


class RaspberryPi(hal.PlatformHAL):
    """Manage hardware resources for the Raspberry Pi platform."""

    def __init__(self) -> None:
        self._spi = spidev.SpiDev()
        self._i2c = smbus2.SMBus()
        self._devices: dict[
            int, gpiozero.DigitalInputDevice | gpiozero.DigitalOutputDevice
        ] = {}

        self._spi_enabled = False
        self._i2c_enabled = False

        self._spi_lock = threading.Lock()
        self._i2c_lock = threading.Lock()
        self._pin_lock = threading.Lock()

    @override
    def enable_spi(self) -> None:
        with self._spi_lock:
            if self._spi_enabled:
                return

            self._spi.open(0, 0)  # bus=0, device=0
            self._spi.max_speed_hz = 4000000
            self._spi.mode = 0b00
            self._spi_enabled = True

    @override
    def close_spi(self) -> None:
        with self._spi_lock:
            if not self._spi_enabled:
                return

            self._spi.close()
            self._spi_enabled = False

    @override
    def spi_write_bytes(self, data: list[int]) -> None:
        if len(data) == 0:
            return

        with self._spi_lock:
            if not self._spi_enabled:
                msg = "SPI is not enabled."
                raise RuntimeError(msg)

            self._spi.writebytes(data)

    @override
    def spi_write_bytes2(self, data: Sequence[int]) -> None:
        if len(data) == 0:
            return

        with self._spi_lock:
            if not self._spi_enabled:
                msg = "SPI is not enabled."
                raise RuntimeError(msg)

            self._spi.writebytes2(data)

    @override
    def enable_i2c(self) -> None:
        with self._i2c_lock:
            if self._i2c_enabled:
                return

            self._i2c.open(I2C_BUS)
            self._i2c_enabled = True

    @override
    def close_i2c(self) -> None:
        with self._i2c_lock:
            if not self._i2c_enabled:
                return

            self._i2c.close()
            self._i2c_enabled = False

    @override
    def i2c_read_byte_data(self, i2c_addr: int, reg: int) -> int:
        with self._i2c_lock:
            if not self._i2c_enabled:
                msg = "I2C is not enabled."
                raise RuntimeError(msg)

            return self._i2c.read_byte_data(i2c_addr, reg)

    @override
    def i2c_read_block_data(
        self, i2c_addr: int, reg: int, length: int = 1
    ) -> list[int]:
        if length < 1:
            msg = "Length of block must be at least 1."
            raise ValueError(msg)

        with self._i2c_lock:
            if not self._i2c_enabled:
                msg = "I2C is not enabled."
                raise RuntimeError(msg)

            return self._i2c.read_i2c_block_data(i2c_addr, reg, length)

    @override
    def i2c_write(
        self, i2c_addr: int, reg: int, data: int | Sequence[int]
    ) -> None:
        with self._i2c_lock:
            if not self._i2c_enabled:
                msg = "I2C is not enabled."
                raise RuntimeError(msg)

            if isinstance(data, int):
                self._i2c.write_byte_data(i2c_addr, reg, data)
            else:
                self._i2c.write_block_data(i2c_addr, reg, data)

    @override
    def request_input_pin(
        self, pin: int, *, pull_up: bool = False
    ) -> gpiozero.DigitalInputDevice:
        with self._pin_lock:
            if pin in self._devices:
                msg = f"Input pin is already allocated: {pin}"
                raise RuntimeError(msg)

            device = gpiozero.DigitalInputDevice(pin, pull_up=pull_up)
            self._devices[pin] = device

        return device

    @override
    def request_output_pin(self, pin: int) -> gpiozero.DigitalOutputDevice:
        with self._pin_lock:
            if pin in self._devices:
                msg = f"Output pin is already allocated: {pin}"
                raise RuntimeError(msg)

            device = gpiozero.DigitalOutputDevice(pin)
            self._devices[pin] = device

        return device

    @override
    def release_pin(self, pin: int) -> None:
        with self._pin_lock:
            if pin not in self._devices:
                msg = f"Cannot release a non-existant pin: {pin}"
                raise RuntimeError(msg)

            device = self._devices.pop(pin)

        device.close()

    @override
    def clean_up(self) -> None:
        with self._spi_lock:
            if self._spi_enabled:
                self._spi.close()
                self._spi_enabled = False

        with self._i2c_lock:
            if self._i2c_enabled:
                self._i2c.close()
                self._i2c_enabled = False

        with self._pin_lock:
            pins = list(self._devices.values())
            self._devices.clear()

        for pin in pins:
            pin.close()

    @override
    def __enter__(self) -> Self:
        self.enable_spi()
        self.enable_i2c()
        return self

    @override
    def __exit__(self, exc_type, exc, tb) -> None:  # noqa: ANN001
        self.clean_up()
