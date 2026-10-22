import pytest
lazy import pytest_mock

from pireader.hardware import rpi


@pytest.fixture
def mock_gpiozero(mocker: pytest_mock.MockerFixture) -> pytest_mock.MockType:
    """Mock the gpiozero package."""
    return mocker.patch("pireader.hardware.rpi.gpiozero")


@pytest.fixture
def mock_spidev(mocker: pytest_mock.MockerFixture) -> pytest_mock.MockType:
    """Mock spidev.Spidev."""
    return mocker.patch("pireader.hardware.rpi.spidev.SpiDev")


class TestRaspberryPiEnableSpi:
    """RaspberryPi enable_spi."""

    def test_enable_spi_success(
        self, mock_spidev: pytest_mock.MockType
    ) -> None:
        """SPI is enabled successfully."""
        platform = rpi.RaspberryPi()

        platform.enable_spi()

        mock_spidev.return_value.open.assert_called_once()
        assert platform._spi_enabled

    def test_spi_already_enabled(
        self, mock_spidev: pytest_mock.MockType
    ) -> None:
        """SPI is already enabled."""
        platform = rpi.RaspberryPi()
        platform._spi_enabled = True

        platform.enable_spi()

        mock_spidev.return_value.open.assert_not_called()
        assert platform._spi_enabled


class TestRaspberryPiCloseSpi:
    """RaspberryPi close_spi."""

    def test_close_spi_success(
        self, mock_spidev: pytest_mock.MockType
    ) -> None:
        """SPI is closed successfully."""
        platform = rpi.RaspberryPi()
        platform._spi_enabled = True

        platform.close_spi()

        mock_spidev.return_value.close.assert_called_once()
        assert not platform._spi_enabled

    def test_spi_is_already_closed(
        self, mock_spidev: pytest_mock.MockType
    ) -> None:
        """SPI is already closed."""
        platform = rpi.RaspberryPi()

        platform.close_spi()

        mock_spidev.return_value.close.assert_not_called()
        assert not platform._spi_enabled


class TestRaspberryPiSpiWriteBytes:
    """RaspberryPi spi_write_bytes."""

    def test_spi_write_bytes_successful(
        self, mock_spidev: pytest_mock.MockType
    ) -> None:
        """SPI writebytes is successful."""
        platform = rpi.RaspberryPi()
        platform._spi_enabled = True
        mock_data = [0x03, 0x04, 0x05]

        platform.spi_write_bytes(mock_data)

        mock_spidev.return_value.writebytes.assert_called_once_with(mock_data)

    def test_spi_write_bytes_skips_on_empty_data(
        self, mock_spidev: pytest_mock.MockType
    ) -> None:
        """SPI writebytes skips when data is empty."""
        platform = rpi.RaspberryPi()
        platform._spi_enabled = True

        platform.spi_write_bytes([])

        mock_spidev.return_value.writebytes.assert_not_called()

    def test_spi_write_bytes_fails_on_closed_spi(
        self, mock_spidev: pytest_mock.MockType
    ) -> None:
        """SPI writebytes fails when SPI is closed."""
        platform = rpi.RaspberryPi()
        mock_data = [0x03, 0x04, 0x05]

        with pytest.raises(RuntimeError):
            platform.spi_write_bytes(mock_data)

        mock_spidev.return_value.writebytes.assert_not_called()


class TestRaspberryPiSpiWriteBytes2:
    """RaspberryPi spi_write_bytes2."""

    def test_spi_write_bytes2_successful(
        self, mock_spidev: pytest_mock.MockType
    ) -> None:
        """SPI writebytes2 is successful."""
        platform = rpi.RaspberryPi()
        platform._spi_enabled = True
        mock_data = [0x03, 0x04, 0x05]

        platform.spi_write_bytes2(mock_data)

        mock_spidev.return_value.writebytes2.assert_called_once_with(mock_data)

    def test_spi_write_bytes2_skips_on_empty_data(
        self, mock_spidev: pytest_mock.MockType
    ) -> None:
        """SPI writebytes2 skips when data is empty."""
        platform = rpi.RaspberryPi()
        platform._spi_enabled = True

        platform.spi_write_bytes2([])

        mock_spidev.return_value.writebytes2.assert_not_called()

    def test_spi_write_bytes2_fails_on_closed_spi(
        self, mock_spidev: pytest_mock.MockType
    ) -> None:
        """SPI writebytes2 fails when SPI is closed."""
        platform = rpi.RaspberryPi()
        mock_data = [0x03, 0x04, 0x05]

        with pytest.raises(RuntimeError):
            platform.spi_write_bytes2(mock_data)

        mock_spidev.return_value.writebytes2.assert_not_called()


class TestRaspberryPiRequestInputPin:
    """RaspberryPi request_input_pin."""

    def test_successful_request_input_pin(
        self, mock_gpiozero: pytest_mock.MockType
    ) -> None:
        """Pin is successfully allocated."""
        platform = rpi.RaspberryPi()

        result = platform.request_input_pin(10, pull_up=True)

        mock_gpiozero.DigitalInputDevice.assert_called_once_with(
            10, pull_up=True
        )
        assert result is not None
        assert (10, result) in platform._devices.items()

    def test_request_raises_error_on_allocated_pin(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Pin is already allocated."""
        mock_pin = mocker.Mock()
        platform = rpi.RaspberryPi()
        platform._devices[11] = mock_pin

        with pytest.raises(RuntimeError):
            platform.request_input_pin(11, pull_up=True)

        assert (11, mock_pin) in platform._devices.items()


class TestRaspberryPiRequestOutputPin:
    """RaspberryPi request_output_pin."""

    def test_successful_request_output_pin(
        self, mock_gpiozero: pytest_mock.MockType
    ) -> None:
        """Pin is successfully allocated."""
        platform = rpi.RaspberryPi()

        result = platform.request_output_pin(10)

        mock_gpiozero.DigitalOutputDevice.assert_called_once_with(10)
        assert result is not None
        assert (10, result) in platform._devices.items()

    def test_request_raises_error_on_allocated_pin(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Pin is already allocated."""
        mock_pin = mocker.Mock()
        platform = rpi.RaspberryPi()
        platform._devices[11] = mock_pin

        with pytest.raises(RuntimeError):
            platform.request_output_pin(11)

        assert (11, mock_pin) in platform._devices.items()


class TestRaspberryPiReleasePin:
    """RaspberryPi release_pin."""

    def test_successful_release_pin(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Pin is successfully released."""
        mock_pin = mocker.Mock()
        platform = rpi.RaspberryPi()
        platform._devices[10] = mock_pin

        platform.release_pin(10)

        mock_pin.close.assert_called_once()
        assert (10, mock_pin) not in platform._devices.items()

    def test_release_raises_error_on_unallocated_pin(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Pin is not allocated."""
        mock_pin = mocker.Mock()
        platform = rpi.RaspberryPi()
        platform._devices[10] = mock_pin

        with pytest.raises(RuntimeError):
            platform.release_pin(11)

        assert (10, mock_pin) in platform._devices.items()


class TestRaspberryPiCleanUp:
    """RaspberryPi clean_up."""

    def test_clean_up_successfully(
        self,
        mocker: pytest_mock.MockerFixture,
        mock_spidev: pytest_mock.MockType,
    ) -> None:
        """Close all pins and devices dict is empty."""
        mock_pin1 = mocker.Mock()
        mock_pin2 = mocker.Mock()
        platform = rpi.RaspberryPi()
        platform._devices = {10: mock_pin1, 11: mock_pin2}
        platform._spi_enabled = True

        platform.clean_up()

        mock_spidev.return_value.close.assert_called_once()
        mock_pin1.close.assert_called_once()
        mock_pin2.close.assert_called_once()
        assert len(platform._devices) == 0
        assert not platform._spi_enabled

    def test_clean_up_skips_spi_close(
        self, mock_spidev: pytest_mock.MockType
    ) -> None:
        """SPI is already closed."""
        platform = rpi.RaspberryPi()

        platform.clean_up()

        mock_spidev.return_value.close.assert_not_called()
        assert not platform._spi_enabled


class TestRaspberryPiAsContextManager:
    """RaspberryPi as context manager."""

    def test_enter_context_manager(self) -> None:
        """RaspberryPi enters context manager correctly."""
        with rpi.RaspberryPi() as platform:
            assert isinstance(platform, rpi.RaspberryPi)

    def test_exit_context_manager(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """RaspberryPi is cleaned up after exit."""
        with rpi.RaspberryPi() as platform:
            mock_clean_up = mocker.patch.object(platform, "clean_up")

        mock_clean_up.assert_called_once()
