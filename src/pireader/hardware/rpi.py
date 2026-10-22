from typing import Self
lazy from collections.abc import Sequence

import gpiozero
import spidev


class RaspberryPi:
    """Manage hardware resources for the Raspberry Pi platform."""

    def __init__(self) -> None:
        self._spi = spidev.SpiDev()
        self._devices: dict[
            int, gpiozero.DigitalInputDevice | gpiozero.DigitalOutputDevice
        ] = {}
        self._spi_enabled = False

    def enable_spi(self) -> None:
        """Enable SPI communication."""
        if self._spi_enabled:
            return

        self._spi.open(0, 0)  # bus=0, device=0
        self._spi.max_speed_hz = 4000000
        self._spi.mode = 0b00
        self._spi_enabled = True

    def close_spi(self) -> None:
        """Close SPI communication."""
        if not self._spi_enabled:
            return

        self._spi.close()
        self._spi_enabled = False

    def spi_write_bytes(self, data: list[int]) -> None:
        """Write a block of data to the SPI interface."""
        if not self._spi_enabled:
            msg = "SPI is not enabled."
            raise RuntimeError(msg)

        if len(data) == 0:
            return

        self._spi.writebytes(data)

    def spi_write_bytes2(self, data: Sequence[int]) -> None:
        """Write an arbitrary large block of data to the SPI interface."""
        if not self._spi_enabled:
            msg = "SPI is not enabled."
            raise RuntimeError(msg)

        if len(data) == 0:
            return

        self._spi.writebytes2(data)

    def request_input_pin(
        self, pin: int, *, pull_up: bool = False
    ) -> gpiozero.DigitalInputDevice:
        """Allocate an input pin from the Raspberry Pi."""
        if pin in self._devices:
            msg = f"Input pin is already allocated: {pin}"
            raise RuntimeError(msg)

        device = gpiozero.DigitalInputDevice(pin, pull_up=pull_up)
        self._devices[pin] = device
        return device

    def request_output_pin(self, pin: int) -> gpiozero.DigitalOutputDevice:
        """Allocate an output pin from the Raspberry Pi."""
        if pin in self._devices:
            msg = f"Output pin is already allocated: {pin}"
            raise RuntimeError(msg)

        device = gpiozero.DigitalOutputDevice(pin)
        self._devices[pin] = device
        return device

    def release_pin(self, pin: int) -> None:
        """Release and close a pin from the Raspberry Pi."""
        if pin not in self._devices:
            msg = f"Cannot release a non-existant pin: {pin}"
            raise RuntimeError(msg)

        device = self._devices.pop(pin)
        device.close()

    def clean_up(self) -> None:
        """Release and close all Raspberry Pi interfaces in use."""
        if self._spi_enabled:
            self._spi.close()
            self._spi_enabled = False

        for pin in list(self._devices):
            self._devices.pop(pin).close()

    def __enter__(self) -> Self:  # noqa: D105
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # noqa: ANN001, D105
        self.clean_up()
