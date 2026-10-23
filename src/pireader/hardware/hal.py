# pragma: exclude file
import abc
from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:
    from collections.abc import Sequence

    import gpiozero


class PlatformHAL(abc.ABC):
    """Manage hardware resources for the platform."""

    @abc.abstractmethod
    def enable_spi(self) -> None:
        """Enable SPI communication."""

    @abc.abstractmethod
    def close_spi(self) -> None:
        """Close SPI communication."""

    @abc.abstractmethod
    def spi_write_bytes(self, data: list[int]) -> None:
        """Write a block of data to the SPI interface."""

    @abc.abstractmethod
    def spi_write_bytes2(self, data: Sequence[int]) -> None:
        """Write an arbitrary large block of data to the SPI interface."""

    @abc.abstractmethod
    def enable_i2c(self) -> None:
        """Enable I2C communication."""

    @abc.abstractmethod
    def close_i2c(self) -> None:
        """Close I2C communication."""

    @abc.abstractmethod
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

    @abc.abstractmethod
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

    @abc.abstractmethod
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

    @abc.abstractmethod
    def request_input_pin(
        self, pin: int, *, pull_up: bool = False
    ) -> gpiozero.DigitalInputDevice:
        """Allocate an input pin from the platform."""

    @abc.abstractmethod
    def request_output_pin(self, pin: int) -> gpiozero.DigitalOutputDevice:
        """Allocate an output pin from the platform."""

    @abc.abstractmethod
    def release_pin(self, pin: int) -> None:
        """Release and close a pin from the platform."""

    @abc.abstractmethod
    def clean_up(self) -> None:
        """Release and close all platform interfaces in use."""

    @abc.abstractmethod
    def __enter__(self) -> Self: ...  # noqa: D105

    @abc.abstractmethod
    def __exit__(self, exc_type, exc, tb) -> None: ...  # noqa: ANN001, D105
