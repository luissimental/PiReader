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
    return mocker.patch("pireader.hardware.rpi.spidev.SpiDev").return_value


@pytest.fixture
def mock_smbus(mocker: pytest_mock.MockerFixture) -> pytest_mock.MockType:
    """Mock smbus2.SMBus."""
    return mocker.patch("pireader.hardware.rpi.smbus2.SMBus").return_value


class TestRaspberryPiEnableSpi:
    """RaspberryPi enable_spi."""

    def test_enable_spi_success(
        self, mock_spidev: pytest_mock.MockType
    ) -> None:
        """SPI is enabled successfully."""
        platform = rpi.RaspberryPi()

        platform.enable_spi()

        mock_spidev.open.assert_called_once()
        assert platform._spi_enabled

    def test_spi_already_enabled(
        self, mock_spidev: pytest_mock.MockType
    ) -> None:
        """SPI is already enabled."""
        platform = rpi.RaspberryPi()
        platform._spi_enabled = True

        platform.enable_spi()

        mock_spidev.open.assert_not_called()
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

        mock_spidev.close.assert_called_once()
        assert not platform._spi_enabled

    def test_spi_is_already_closed(
        self, mock_spidev: pytest_mock.MockType
    ) -> None:
        """SPI is already closed."""
        platform = rpi.RaspberryPi()

        platform.close_spi()

        mock_spidev.close.assert_not_called()
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

        mock_spidev.writebytes.assert_called_once_with(mock_data)

    def test_spi_write_bytes_skips_on_empty_data(
        self, mock_spidev: pytest_mock.MockType
    ) -> None:
        """SPI writebytes skips when data is empty."""
        platform = rpi.RaspberryPi()
        platform._spi_enabled = True

        platform.spi_write_bytes([])

        mock_spidev.writebytes.assert_not_called()

    def test_spi_write_bytes_fails_on_closed_spi(
        self, mock_spidev: pytest_mock.MockType
    ) -> None:
        """SPI writebytes fails when SPI is closed."""
        platform = rpi.RaspberryPi()
        mock_data = [0x03, 0x04, 0x05]

        with pytest.raises(RuntimeError):
            platform.spi_write_bytes(mock_data)

        mock_spidev.writebytes.assert_not_called()


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

        mock_spidev.writebytes2.assert_called_once_with(mock_data)

    def test_spi_write_bytes2_skips_on_empty_data(
        self, mock_spidev: pytest_mock.MockType
    ) -> None:
        """SPI writebytes2 skips when data is empty."""
        platform = rpi.RaspberryPi()
        platform._spi_enabled = True

        platform.spi_write_bytes2([])

        mock_spidev.writebytes2.assert_not_called()

    def test_spi_write_bytes2_fails_on_closed_spi(
        self, mock_spidev: pytest_mock.MockType
    ) -> None:
        """SPI writebytes2 fails when SPI is closed."""
        platform = rpi.RaspberryPi()
        mock_data = [0x03, 0x04, 0x05]

        with pytest.raises(RuntimeError):
            platform.spi_write_bytes2(mock_data)

        mock_spidev.writebytes2.assert_not_called()


class TestRaspberryPiEnableI2c:
    """RaspberryPi enable_i2c."""

    def test_enable_i2c_success(
        self, mock_smbus: pytest_mock.MockType
    ) -> None:
        """I2C is enabled successfully."""
        platform = rpi.RaspberryPi()

        platform.enable_i2c()

        mock_smbus.open.assert_called_once()
        assert platform._i2c_enabled

    def test_i2c_already_enabled(
        self, mock_smbus: pytest_mock.MockType
    ) -> None:
        """I2C is already enabled."""
        platform = rpi.RaspberryPi()
        platform._i2c_enabled = True

        platform.enable_i2c()

        mock_smbus.open.assert_not_called()
        assert platform._i2c_enabled


class TestRaspberryPiCloseI2c:
    """RaspberryPi close_i2c."""

    def test_close_i2c_success(self, mock_smbus: pytest_mock.MockType) -> None:
        """I2C is closed successfully."""
        platform = rpi.RaspberryPi()
        platform._i2c_enabled = True

        platform.close_i2c()

        mock_smbus.close.assert_called_once()
        assert not platform._i2c_enabled

    def test_i2c_already_closed(
        self, mock_smbus: pytest_mock.MockType
    ) -> None:
        """I2C is already closed."""
        platform = rpi.RaspberryPi()

        platform.close_i2c()

        mock_smbus.close.assert_not_called()
        assert not platform._i2c_enabled


class TestRaspberryPiI2cReadByteData:
    """RaspberryPi i2c_read_byte_data."""

    def test_i2c_read_byte_data_success(
        self, mock_smbus: pytest_mock.MockType
    ) -> None:
        """I2C read_byte_data is successful."""
        mock_smbus.read_byte_data.return_value = 0x45
        platform = rpi.RaspberryPi()
        platform._i2c_enabled = True

        result = platform.i2c_read_byte_data(0x10, 0x05)

        mock_smbus.read_byte_data.assert_called_once_with(0x10, 0x05)
        assert result == 0x45

    def test_i2c_read_byte_data_fails_on_closed_i2c(
        self, mock_smbus: pytest_mock.MockType
    ) -> None:
        """I2C read_byte_data fails when I2C is closed."""
        platform = rpi.RaspberryPi()

        with pytest.raises(RuntimeError):
            platform.i2c_read_byte_data(0x10, 0x05)

        mock_smbus.read_byte_data.assert_not_called()


class TestRaspberryPiI2cReadBlockData:
    """RaspberryPi i2c_read_block_data."""

    def test_i2c_read_block_data_success(
        self, mock_smbus: pytest_mock.MockType
    ) -> None:
        """I2C read_block_data is successful."""
        mock_result = [0x45, 0x47, 0x48]
        mock_smbus.read_i2c_block_data.return_value = mock_result
        platform = rpi.RaspberryPi()
        platform._i2c_enabled = True

        result = platform.i2c_read_block_data(0x10, 0x05, 15)

        mock_smbus.read_i2c_block_data.assert_called_once_with(0x10, 0x05, 15)
        assert result is mock_result

    def test_i2c_read_block_data_fails_on_closed_spi(
        self, mock_smbus: pytest_mock.MockType
    ) -> None:
        """I2C read_block_data fails when I2C is closed."""
        platform = rpi.RaspberryPi()

        with pytest.raises(RuntimeError):
            platform.i2c_read_block_data(0x10, 0x05, 15)

        mock_smbus.read_i2c_block_data.assert_not_called()

    def test_i2c_read_block_data_fails_on_invalid_length(
        self, mock_smbus: pytest_mock.MockType
    ) -> None:
        """I2C read_block_data fails when length is less than 1."""
        platform = rpi.RaspberryPi()
        platform._i2c_enabled = True

        with pytest.raises(
            ValueError, match=r"Length of block must be at least 1."
        ):
            platform.i2c_read_block_data(0x10, 0x05, 0)

        mock_smbus.read_i2c_block_data.assert_not_called()


class TestRaspberryPiI2cWrite:
    """RaspberryPi i2c_write."""

    def test_i2c_write_byte_success(
        self, mock_smbus: pytest_mock.MockType
    ) -> None:
        """I2C write byte is successful."""
        platform = rpi.RaspberryPi()
        platform._i2c_enabled = True

        platform.i2c_write(0x10, 0x05, 0x45)

        mock_smbus.write_byte_data.assert_called_once_with(0x10, 0x05, 0x45)

    def test_i2c_write_block_success(
        self, mock_smbus: pytest_mock.MockType
    ) -> None:
        """I2C write block is successful."""
        platform = rpi.RaspberryPi()
        platform._i2c_enabled = True
        mock_data = [0x03, 0x04, 0x05]

        platform.i2c_write(0x10, 0x05, mock_data)

        mock_smbus.write_block_data.assert_called_once_with(
            0x10, 0x05, mock_data
        )

    def test_i2c_write_fails_on_closed_spi(
        self, mock_smbus: pytest_mock.MockType
    ) -> None:
        """I2C write fails when I2C is closed."""
        platform = rpi.RaspberryPi()

        with pytest.raises(RuntimeError):
            platform.i2c_write(0x10, 0x05, 0x45)

        mock_smbus.write_byte_data.assert_not_called()

        with pytest.raises(RuntimeError):
            platform.i2c_write(0x10, 0x05, [0x03, 0x04, 0x05])

        mock_smbus.write_block_data.assert_not_called()


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
        mock_smbus: pytest_mock.MockType,
    ) -> None:
        """Close all pins and devices dict is empty."""
        mock_pin1 = mocker.Mock()
        mock_pin2 = mocker.Mock()
        platform = rpi.RaspberryPi()
        platform._devices = {10: mock_pin1, 11: mock_pin2}
        platform._spi_enabled = True
        platform._i2c_enabled = True

        platform.clean_up()

        mock_spidev.close.assert_called_once()
        mock_smbus.close.assert_called_once()
        mock_pin1.close.assert_called_once()
        mock_pin2.close.assert_called_once()
        assert len(platform._devices) == 0
        assert not platform._spi_enabled
        assert not platform._i2c_enabled

    def test_clean_up_skips_spi_close(
        self, mock_spidev: pytest_mock.MockType
    ) -> None:
        """SPI is already closed."""
        platform = rpi.RaspberryPi()

        platform.clean_up()

        mock_spidev.close.assert_not_called()
        assert not platform._spi_enabled

    def test_clean_up_skips_i2c_closed(
        self, mock_smbus: pytest_mock.MockType
    ) -> None:
        """I2C is already closed."""
        platform = rpi.RaspberryPi()

        platform.clean_up()

        mock_smbus.close.assert_not_called()
        assert not platform._i2c_enabled


class TestRaspberryPiAsContextManager:
    """RaspberryPi as context manager."""

    def test_enter_context_manager(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """RaspberryPi enters context manager correctly."""
        mocker.patch.object(rpi.RaspberryPi, "enable_spi")
        mocker.patch.object(rpi.RaspberryPi, "enable_i2c")

        with rpi.RaspberryPi() as platform:
            assert isinstance(platform, rpi.RaspberryPi)

    def test_exit_context_manager(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """RaspberryPi is cleaned up after exit."""
        mocker.patch.object(rpi.RaspberryPi, "enable_spi")
        mocker.patch.object(rpi.RaspberryPi, "enable_i2c")

        with rpi.RaspberryPi() as platform:
            mock_clean_up = mocker.patch.object(platform, "clean_up")

        mock_clean_up.assert_called_once()
