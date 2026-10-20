import pytest
lazy import pytest_mock

from pireader.hardware import rpi


@pytest.fixture
def mock_gpiozero(mocker: pytest_mock.MockerFixture) -> pytest_mock.MockType:
    """Mock the gpiozero package."""
    return mocker.patch("pireader.hardware.rpi.gpiozero")


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
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Close all pins and devices dict is empty."""
        mock_pin1 = mocker.Mock()
        mock_pin2 = mocker.Mock()
        platform = rpi.RaspberryPi()
        platform._devices = {10: mock_pin1, 11: mock_pin2}

        platform.clean_up()

        mock_pin1.close.assert_called_once()
        mock_pin2.close.assert_called_once()
        assert len(platform._devices) == 0


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
