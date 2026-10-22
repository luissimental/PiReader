import threading
from typing import Self
lazy from collections.abc import Sequence

import gpiozero
import smbus2
import spidev

I2C_BUS = 3


class RaspberryPi:
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

    def enable_spi(self) -> None:
        """Enable SPI communication."""
        with self._spi_lock:
            if self._spi_enabled:
                return

            self._spi.open(0, 0)  # bus=0, device=0
            self._spi.max_speed_hz = 4000000
            self._spi.mode = 0b00
            self._spi_enabled = True

    def close_spi(self) -> None:
        """Close SPI communication."""
        with self._spi_lock:
            if not self._spi_enabled:
                return

            self._spi.close()
            self._spi_enabled = False

    def spi_write_bytes(self, data: list[int]) -> None:
        """Write a block of data to the SPI interface."""
        if len(data) == 0:
            return

        with self._spi_lock:
            if not self._spi_enabled:
                msg = "SPI is not enabled."
                raise RuntimeError(msg)

            self._spi.writebytes(data)

    def spi_write_bytes2(self, data: Sequence[int]) -> None:
        """Write an arbitrary large block of data to the SPI interface."""
        if len(data) == 0:
            return

        with self._spi_lock:
            if not self._spi_enabled:
                msg = "SPI is not enabled."
                raise RuntimeError(msg)

            self._spi.writebytes2(data)

    def enable_i2c(self) -> None:
        """Enable I2C communication."""
        with self._i2c_lock:
            if self._i2c_enabled:
                return

            self._i2c.open(I2C_BUS)
            self._i2c_enabled = True

    def close_i2c(self) -> None:
        """Close I2C communication."""
        with self._i2c_lock:
            if not self._i2c_enabled:
                return

            self._i2c.close()
            self._i2c_enabled = False

    def i2c_read_byte_data(self, i2c_addr: int, reg: int) -> int:
        """Read a single byte from a given register.

        Args:
          i2c_addr:
            The i2c address.
          reg:
            The start register.

        Returns:
            The read byte value.

        """
        with self._i2c_lock:
            if not self._i2c_enabled:
                msg = "I2C is not enabled."
                raise RuntimeError(msg)

            return self._i2c.read_byte_data(i2c_addr, reg)

    def i2c_read_block_data(
        self, i2c_addr: int, reg: int, length: int = 1
    ) -> list[int]:
        """Read a block of byte data from a given register.

        Args:
          i2c_addr:
            The i2c address.
          reg:
            The start register.
          length:
            The desired block length. Must be at least 1.

        Returns:
            The list of bytes.

        """
        if length < 1:
            msg = "Length of block must be at least 1."
            raise ValueError(msg)

        with self._i2c_lock:
            if not self._i2c_enabled:
                msg = "I2C is not enabled."
                raise RuntimeError(msg)

            return self._i2c.read_i2c_block_data(i2c_addr, reg, length)

    def i2c_write(
        self, i2c_addr: int, reg: int, data: int | Sequence[int]
    ) -> None:
        """Write a byte or a block of data to a given register.

        Args:
          i2c_addr:
            The i2c address.
          reg:
            The register to write to.
          data:
            The byte value or list of bytes to transmit.

        """
        with self._i2c_lock:
            if not self._i2c_enabled:
                msg = "I2C is not enabled."
                raise RuntimeError(msg)

            if isinstance(data, int):
                self._i2c.write_byte_data(i2c_addr, reg, data)
            else:
                self._i2c.write_block_data(i2c_addr, reg, data)

    def request_input_pin(
        self, pin: int, *, pull_up: bool = False
    ) -> gpiozero.DigitalInputDevice:
        """Allocate an input pin from the Raspberry Pi."""
        with self._pin_lock:
            if pin in self._devices:
                msg = f"Input pin is already allocated: {pin}"
                raise RuntimeError(msg)

            device = gpiozero.DigitalInputDevice(pin, pull_up=pull_up)
            self._devices[pin] = device

        return device

    def request_output_pin(self, pin: int) -> gpiozero.DigitalOutputDevice:
        """Allocate an output pin from the Raspberry Pi."""
        with self._pin_lock:
            if pin in self._devices:
                msg = f"Output pin is already allocated: {pin}"
                raise RuntimeError(msg)

            device = gpiozero.DigitalOutputDevice(pin)
            self._devices[pin] = device

        return device

    def release_pin(self, pin: int) -> None:
        """Release and close a pin from the Raspberry Pi."""
        with self._pin_lock:
            if pin not in self._devices:
                msg = f"Cannot release a non-existant pin: {pin}"
                raise RuntimeError(msg)

            device = self._devices.pop(pin)

        device.close()

    def clean_up(self) -> None:
        """Release and close all Raspberry Pi interfaces in use."""
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

    def __enter__(self) -> Self:  # noqa: D105
        self.enable_spi()
        self.enable_i2c()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # noqa: ANN001, D105
        self.clean_up()
