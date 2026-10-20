from typing import Self

import gpiozero


class RaspberryPi:
    """Manage hardware resources for the Raspberry Pi platform."""

    def __init__(self) -> None:
        self._devices: dict[
            int, gpiozero.DigitalInputDevice | gpiozero.DigitalOutputDevice
        ] = {}

    def request_input_pin(
        self, pin: int, *, pull_up: bool = False
    ) -> gpiozero.DigitalInputDevice:
        """Allocate an input pin from the Raspberry Pi."""
        if pin in self._devices:
            raise RuntimeError

        device = gpiozero.DigitalInputDevice(pin, pull_up=pull_up)
        self._devices[pin] = device
        return device

    def request_output_pin(self, pin: int) -> gpiozero.DigitalOutputDevice:
        """Allocate an output pin from the Raspberry Pi."""
        if pin in self._devices:
            raise RuntimeError

        device = gpiozero.DigitalOutputDevice(pin)
        self._devices[pin] = device
        return device

    def release_pin(self, pin: int) -> None:
        """Release and close a pin from the Raspberry Pi."""
        if pin not in self._devices:
            raise RuntimeError

        device = self._devices.pop(pin)
        device.close()

    def clean_up(self) -> None:
        """Release and close all pins in use."""
        for pin in list(self._devices):
            self._devices.pop(pin).close()

    def __enter__(self) -> Self:  # noqa: D105
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # noqa: ANN001, D105
        self.clean_up()
