from typing import TYPE_CHECKING

import pytest

from pireader.drivers import touch

if TYPE_CHECKING:
    import pytest_mock

    from pireader.common import models

CallbackType = touch._AcceptsTouchEvents | None


def _test_callback(_: list[models.TouchEvent]) -> None: ...


@pytest.fixture
def mock_time(mocker: pytest_mock.MockerFixture) -> pytest_mock.MockType:
    """Return a time mock."""
    return mocker.patch("pireader.drivers.touch.time")


@pytest.fixture
def mock_driver(
    mocker: pytest_mock.MockerFixture,
    mock_time: pytest_mock.MockType,  # noqa: ARG001
) -> touch.TouchDriver:
    """Return a TouchDriver with mocked init values."""
    driver = touch.TouchDriver(mocker.Mock(), on_touch=None, initialize=False)
    driver._reset_pin = mocker.Mock()
    driver._int_pin = mocker.Mock()
    return driver


class TestTouchDriverInit:
    """TouchDriver __init__."""

    def test_init_sets_hardware(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Init sets hardware."""
        mock_hardware = mocker.Mock()

        driver = touch.TouchDriver(
            mock_hardware, on_touch=None, initialize=False
        )

        assert driver._hw is mock_hardware

    @pytest.mark.parametrize("callback", [_test_callback, None])
    def test_init_sets_on_touch_callback(
        self, mocker: pytest_mock.MockerFixture, callback: CallbackType
    ) -> None:
        """Init sets on_touch callback."""
        driver = touch.TouchDriver(
            mocker.Mock(), on_touch=callback, initialize=False
        )

        assert driver._on_touch is callback

    def test_init_calls_initialize(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Init calls initialize when bool is True."""
        mock_initialize = mocker.patch.object(touch.TouchDriver, "initialize")

        touch.TouchDriver(mocker.Mock(), on_touch=None, initialize=True)

        mock_initialize.assert_called_once()

    def test_init_skips_initialize(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Init skips initialize when bool is False."""
        mock_initialize = mocker.patch.object(touch.TouchDriver, "initialize")

        touch.TouchDriver(mocker.Mock(), on_touch=None, initialize=False)

        mock_initialize.assert_not_called()


class TestTouchDriverOnTouchProperty:
    """TouchDriver on_touch property."""

    @pytest.mark.parametrize("callback", [_test_callback, None])
    def test_on_touch_getter_returns_callback(
        self, mock_driver: touch.TouchDriver, callback: CallbackType
    ) -> None:
        """Return callback function."""
        mock_driver._on_touch = callback

        assert mock_driver.on_touch is callback

    @pytest.mark.parametrize("callback", [_test_callback, None])
    def test_on_touch_setter_sets_callback(
        self, mock_driver: touch.TouchDriver, callback: CallbackType
    ) -> None:
        """Set callback function."""
        mock_driver.on_touch = callback

        assert mock_driver._on_touch is callback


class TestTouchDriverInitialize:
    """TouchDriver initialize."""

    def test_initialize_enables_pins_and_resets(
        self, mocker: pytest_mock.MockerFixture, mock_driver: touch.TouchDriver
    ) -> None:
        """Enable pins and perform a hardware reset."""
        hw_spy = mocker.spy(mock_driver, "_hw")
        mock_hw_reset = mocker.patch.object(mock_driver, "hardware_reset")

        mock_driver.initialize()

        hw_spy.request_output_pin.assert_called_once()
        hw_spy.request_input_pin.assert_called_once()
        mock_hw_reset.assert_called_once()
        assert (
            hw_spy.request_input_pin.return_value.when_activated
            == mock_driver._on_touch_interrupt
        )
        assert mock_driver._is_active is True

    def test_initialize_only_resets(
        self, mocker: pytest_mock.MockerFixture, mock_driver: touch.TouchDriver
    ) -> None:
        """Pins are already enabled so only perform a hardware reset."""
        hw_spy = mocker.spy(mock_driver, "_hw")
        mock_hw_reset = mocker.patch.object(mock_driver, "hardware_reset")
        mock_driver._is_active = True

        mock_driver.initialize()

        hw_spy.request_output_pin.assert_not_called()
        hw_spy.request_input_pin.assert_not_called()
        mock_hw_reset.assert_called_once()
        assert mock_driver._is_active is True


class TestTouchDriverHardwareReset:
    """TouchDriver hardware_reset."""

    def test_reset_performs_successfully(
        self, mocker: pytest_mock.MockerFixture, mock_driver: touch.TouchDriver
    ) -> None:
        """A hardware reset is performed."""
        spy_reset_pin = mocker.spy(mock_driver, "_reset_pin")
        mock_driver._is_active = True

        mock_driver.hardware_reset()

        spy_reset_pin.on.assert_called_once()
        spy_reset_pin.off.assert_called_once()

    def test_reset_fails_on_inactive_driver(
        self, mocker: pytest_mock.MockerFixture, mock_driver: touch.TouchDriver
    ) -> None:
        """The hardware reset fails due to inactive driver."""
        spy_reset_pin = mocker.spy(mock_driver, "_reset_pin")

        with pytest.raises(RuntimeError):
            mock_driver.hardware_reset()

        spy_reset_pin.on.assert_not_called()
        spy_reset_pin.off.assert_not_called()


class TestTouchDriverSetPowerMode:
    """TouchDriver set_power_mode."""

    @pytest.mark.parametrize(
        "mode",
        [
            touch.PowerMode.ACTIVE,
            touch.PowerMode.MONITOR,
            touch.PowerMode.HIBERNATE,
        ],
    )
    def test_set_power_mode_successfully(
        self,
        mocker: pytest_mock.MockerFixture,
        mock_driver: touch.TouchDriver,
        mode: touch.PowerMode,
    ) -> None:
        """Set power mode successfully."""
        hw_spy = mocker.spy(mock_driver, "_hw")
        mock_driver._is_active = True

        mock_driver.set_power_mode(mode)

        hw_spy.i2c_write.assert_called_once_with(
            mock_driver._i2c_addr,
            touch._TouchRegisters.REG_POWER_MODE,
            mode.value,
        )

    def test_set_power_mode_fails_on_inactive_driver(
        self, mocker: pytest_mock.MockerFixture, mock_driver: touch.TouchDriver
    ) -> None:
        """Set power mode fails due to inactive driver."""
        hw_spy = mocker.spy(mock_driver, "_hw")

        with pytest.raises(RuntimeError):
            mock_driver.set_power_mode(touch.PowerMode.HIBERNATE)

        hw_spy.i2c_write.assert_not_called()


class TestTouchDriverCleanUp:
    """TouchDriver clean_up."""

    def test_clean_up_successfully(
        self, mocker: pytest_mock.MockerFixture, mock_driver: touch.TouchDriver
    ) -> None:
        """Clean up resources."""
        hw_spy = mocker.spy(mock_driver, "_hw")
        mock_driver._is_active = True

        mock_driver.clean_up()

        expected = [
            mocker.call(mock_driver._rst_pin_num),
            mocker.call(mock_driver._int_pin_num),
        ]
        hw_spy.release_pin.assert_has_calls(expected, any_order=True)
        assert mock_driver._is_active is False

    def test_clean_up_is_skipped(
        self, mocker: pytest_mock.MockerFixture, mock_driver: touch.TouchDriver
    ) -> None:
        """Skip clean up due to inactive driver."""
        hw_spy = mocker.spy(mock_driver, "_hw")

        mock_driver.clean_up()

        hw_spy.release_pin.assert_not_called()
        assert mock_driver._is_active is False


class TestTouchDriverOnTouchInterrupt:
    """TouchDriver _on_touch_interrupt."""

    def test_interrupt_successfully(
        self, mocker: pytest_mock.MockerFixture, mock_driver: touch.TouchDriver
    ) -> None:
        """Interrupt reads touches and calls callback."""
        mock_read_touches = mocker.patch.object(mock_driver, "_read_touches")
        mock_on_touch = mocker.Mock()
        mock_driver._on_touch = mock_on_touch

        mock_driver._on_touch_interrupt()

        mock_read_touches.assert_called_once()
        mock_on_touch.assert_called_once_with(mock_read_touches.return_value)

    def test_interrupt_skips_on_no_callback(
        self, mocker: pytest_mock.MockerFixture, mock_driver: touch.TouchDriver
    ) -> None:
        """Interrupt is skipped due to a None callback."""
        mock_read_touches = mocker.patch.object(mock_driver, "_read_touches")

        mock_driver._on_touch_interrupt()

        mock_read_touches.assert_not_called()


class TestTouchDriverReadTouches:
    """TouchDriver _read_touches."""

    def test_read_touches_returns_empty_list(
        self, mocker: pytest_mock.MockerFixture, mock_driver: touch.TouchDriver
    ) -> None:
        """Return an empty list."""
        spy_hw = mocker.spy(mock_driver, "_hw")
        spy_hw.i2c_read_block_data.return_value = [0x00]
        mock_driver._is_active = True

        result = mock_driver._read_touches()

        spy_hw.i2c_read_block_data.assert_called_once()
        assert len(result) == 0

    def test_read_touches_single_touch(
        self,
        mocker: pytest_mock.MockerFixture,
        mock_time: pytest_mock.MockType,
        mock_driver: touch.TouchDriver,
    ) -> None:
        """Return a list with a single touch."""
        mock_time.time.return_value = 15
        spy_hw = mocker.spy(mock_driver, "_hw")
        spy_hw.i2c_read_block_data.return_value = [
            0b0000_0001,
            # Touch 1
            0b0000_1011,
            0b0010_0010,
            0b0001_0101,
            0b1000_1001,
        ]
        mock_driver._is_active = True

        result = mock_driver._read_touches()

        spy_hw.i2c_read_block_data.assert_called_once()
        assert len(result) == 1
        point = result[0]
        assert point.id == 0b0001
        assert point.x == 0b1011_0010_0010
        assert point.y == 0b0101_1000_1001
        assert point.timestamp == 15

    def test_read_touches_multi_touch(
        self,
        mocker: pytest_mock.MockerFixture,
        mock_time: pytest_mock.MockType,
        mock_driver: touch.TouchDriver,
    ) -> None:
        """Return a list with two touches."""
        mock_time.time.return_value = 10
        spy_hw = mocker.spy(mock_driver, "_hw")
        spy_hw.i2c_read_block_data.return_value = [
            0b0000_0010,
            # Touch 1
            0b0000_1011,
            0b0010_0010,
            0b0001_0101,
            0b1000_1001,
            0,
            0,
            # Touch 2
            0b0000_0110,
            0b1100_0101,
            0b0010_0001,
            0b0100_1101,
        ]
        mock_driver._is_active = True

        result = mock_driver._read_touches()

        spy_hw.i2c_read_block_data.assert_called_once()
        assert len(result) == 2
        point1 = result[0]
        assert point1.id == 0b0001
        assert point1.x == 0b1011_0010_0010
        assert point1.y == 0b0101_1000_1001
        assert point1.timestamp == 10
        point2 = result[1]
        assert point2.id == 0b0010
        assert point2.x == 0b0110_1100_0101
        assert point2.y == 0b0001_0100_1101
        assert point2.timestamp == 10

    def test_read_touches_fails_on_inactive_driver(
        self, mocker: pytest_mock.MockerFixture, mock_driver: touch.TouchDriver
    ) -> None:
        """Read touches fails due to inactive driver."""
        spy_hw = mocker.spy(mock_driver, "_hw")

        with pytest.raises(RuntimeError):
            mock_driver._read_touches()

        spy_hw.i2c_read_block_data.assert_not_called()
