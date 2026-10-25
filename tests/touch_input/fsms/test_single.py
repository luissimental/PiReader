import pytest

from pireader import config
from pireader.common import enums, models
from pireader.touch_input.fsms import single
from tests import utils


# --- Conditions ---
class TestSingleTouchFSMShouldHold:
    """SingleTouchFSM _should_hold."""

    test_config = config.GestureConfig(
        hold=config.HoldConfig(max_px=100, min_sec=50)
    )

    def test_should_hold_returns_true_on_thresholds(self) -> None:
        """Distance and duration thresholds are met."""
        machine = single.SingleTouchFSM(config=self.test_config)
        machine._start_point = utils.new_touch(0, 100, 100)

        result = machine._should_hold(utils.new_touch(0, 199, 150))

        assert result is True

    @pytest.mark.parametrize(
        "point",
        [
            utils.new_touch(0, 200, 150),  # Distance threshold is not met
            utils.new_touch(0, 199, 149),  # Duration threshold is not met
            utils.new_touch(0, 200, 149),  # Both thresholds are not met
        ],
    )
    def test_should_hold_returns_false_on_thresholds(
        self, point: models.TouchEvent
    ) -> None:
        """Distance or duration thresholds are not met."""
        machine = single.SingleTouchFSM(config=self.test_config)
        machine._start_point = utils.new_touch(0, 100, 100)

        result = machine._should_hold(point)

        assert result is False

    def test_should_hold_returns_false_on_no_start_point(self) -> None:
        """Start point is None."""
        machine = single.SingleTouchFSM()

        result = machine._should_hold(utils.new_touch(-1, -1, -1))

        assert result is False


class TestSingleTouchFSMShouldDrag:
    """SingleTouchFSM _should_drag."""

    test_config = config.GestureConfig(drag=config.DragConfig(min_px=100))

    def test_should_drag_returns_true_on_threshold(self) -> None:
        """Distance threshold is met."""
        machine = single.SingleTouchFSM(config=self.test_config)
        machine._start_point = utils.new_touch(0, 100, 0)

        result = machine._should_drag(utils.new_touch(0, 200, 0))

        assert result is True

    def test_should_drag_returns_true_on_dragging_state(self) -> None:
        """Dragging state is active and points are different."""
        machine = single.SingleTouchFSM(config=self.test_config)
        machine.current_state_value = machine.dragging.value
        machine._start_point = utils.new_touch(-1, -1, -1)
        machine._last_point = utils.new_touch(0, 100, 100)

        result = machine._should_drag(utils.new_touch(0, 101, 100))

        assert result is True

    def test_should_drag_returns_false_on_threshold(self) -> None:
        """Distance threshold is not met."""
        machine = single.SingleTouchFSM(config=self.test_config)
        machine._start_point = utils.new_touch(0, 100, 0)

        result = machine._should_drag(utils.new_touch(0, 199, 0))

        assert result is False

    def test_should_drag_returns_false_on_dragging_state(self) -> None:
        """Dragging state is active and points are the same."""
        machine = single.SingleTouchFSM(config=self.test_config)
        machine.current_state_value = machine.dragging.value
        machine._start_point = utils.new_touch(-1, -1, -1)
        machine._last_point = utils.new_touch(0, 100, 100)

        result = machine._should_drag(utils.new_touch(0, 100, 100))

        assert result is False

    def test_should_drag_returns_false_on_no_start_point(self) -> None:
        """Start point is None."""
        machine = single.SingleTouchFSM()

        result = machine._should_drag(utils.new_touch(-1, -1, -1))

        assert result is False


# --- Action Hooks ---
class TestSingleTouchFSMOnTouchDown:
    """SingleTouchFSM on_touch_down."""

    def test_on_touch_down_creates_down_gesture(self) -> None:
        """Generates a DOWN gesture."""
        machine = single.SingleTouchFSM()
        point = utils.new_touch(-1, -1, -1)

        machine.on_touch_down(point)

        curr_gest = machine._current_gesture
        assert isinstance(curr_gest, models.SingleTouchGesture)
        assert curr_gest.type is enums.SingleTouchType.DOWN
        assert curr_gest.start is point
        assert curr_gest.end is point


class TestSingleTouchFSMOnHold:
    """SingleTouchFSM on_hold."""

    def test_on_hold_creates_hold_gesture(self) -> None:
        """Generates a HOLD gesture."""
        machine = single.SingleTouchFSM()
        machine.current_state_value = machine.down.value
        machine._start_point = utils.new_touch(-1, -1, -1)
        point = utils.new_touch(-1, -1, -1)

        machine.on_hold(point)

        curr_gest = machine._current_gesture
        assert isinstance(curr_gest, models.SingleTouchGesture)
        assert curr_gest.type is enums.SingleTouchType.HOLD
        assert curr_gest.start is machine._start_point
        assert curr_gest.end is point

    def test_on_hold_fails_on_no_start_point(self) -> None:
        """Fails due to no start point."""
        machine = single.SingleTouchFSM()

        with pytest.raises(RuntimeError):
            machine.on_hold(utils.new_touch(-1, -1, -1))

        assert machine._current_gesture is None


class TestSingleTouchFSMOnDrag:
    """SingleTouchFSM on_drag."""

    def test_on_drag_creates_drag_gesture(self) -> None:
        """Generates a DRAG gesture."""
        machine = single.SingleTouchFSM()
        machine.current_state_value = machine.dragging.value
        machine._start_point = utils.new_touch(-1, -1, -1)
        point = utils.new_touch(-1, -1, -1)

        machine.on_drag(point)

        curr_gest = machine._current_gesture
        assert isinstance(curr_gest, models.SingleTouchGesture)
        assert curr_gest.type is enums.SingleTouchType.DRAG
        assert curr_gest.start is machine._start_point
        assert curr_gest.end is point

    def test_on_drag_fails_on_no_start_point(self) -> None:
        """Fails due to no start point."""
        machine = single.SingleTouchFSM()

        with pytest.raises(RuntimeError):
            machine.on_drag(utils.new_touch(-1, -1, -1))

        assert machine._current_gesture is None


class TestSingleTouchFSMOnRelease:
    """SingleTouchFSM on_release."""

    def test_on_release_creates_fast_tap_gesture(self) -> None:
        """Generates a FAST TAP gesture."""
        test_config = config.GestureConfig(
            fast_tap=config.FastTapConfig(max_px=100, max_sec=50),
            swipe=config.SwipeConfig(min_px=1000, max_sec=0),
        )
        machine = single.SingleTouchFSM(config=test_config)
        machine.current_state_value = machine.down.value
        machine._start_point = utils.new_touch(0, 100, 100)
        machine._last_point = utils.new_touch(0, 199, 149)

        machine.on_release()

        curr_gest = machine._current_gesture
        assert isinstance(curr_gest, models.SingleTouchGesture)
        assert curr_gest.type is enums.SingleTouchType.FAST_TAP
        assert curr_gest.start is machine._start_point
        assert curr_gest.end is machine._last_point

    def test_on_release_creates_swipe_gesture(self) -> None:
        """Generates a SWIPE gesture (no direction check)."""
        test_config = config.GestureConfig(
            fast_tap=config.FastTapConfig(max_px=0, max_sec=0),
            swipe=config.SwipeConfig(min_px=100, max_sec=50),
        )
        machine = single.SingleTouchFSM(config=test_config)
        machine.current_state_value = machine.down.value
        machine._start_point = utils.new_touch(0, 100, 100)
        machine._last_point = utils.new_touch(0, 200, 149)

        machine.on_release()

        curr_gest = machine._current_gesture
        assert isinstance(curr_gest, models.SingleTouchGesture)
        assert curr_gest.type is enums.SingleTouchType.SWIPE
        assert curr_gest.start is machine._start_point
        assert curr_gest.end is machine._last_point

    @pytest.mark.parametrize(
        ("x", "y", "direction"),
        [
            (-100, 100, enums.Direction.LEFT),
            (100, 100, enums.Direction.RIGHT),
            (0, 0, enums.Direction.UP),
            (0, 200, enums.Direction.DOWN),
        ],
    )
    def test_on_release_creates_swipe_gesture_check_direction(
        self, x: int, y: int, direction: enums.Direction
    ) -> None:
        """Generates a SWIPE gesture (direction check)."""
        test_config = config.GestureConfig(
            fast_tap=config.FastTapConfig(max_px=0, max_sec=0),
            swipe=config.SwipeConfig(min_px=100, max_sec=50),
        )
        machine = single.SingleTouchFSM(config=test_config)
        machine.current_state_value = machine.down.value
        machine._start_point = utils.new_touch(0, 100, 100)
        machine._last_point = utils.new_touch(x, y, 149)

        machine.on_release()

        curr_gest = machine._current_gesture
        assert isinstance(curr_gest, models.SingleTouchGesture)
        assert curr_gest.type is enums.SingleTouchType.SWIPE
        assert curr_gest.direction is direction

    def test_on_release_creates_release_gesture(self) -> None:
        """Generates a RELEASE gesture."""
        test_config = config.GestureConfig(
            fast_tap=config.FastTapConfig(max_px=0, max_sec=0),
            swipe=config.SwipeConfig(min_px=1000, max_sec=0),
        )
        machine = single.SingleTouchFSM(config=test_config)
        machine.current_state_value = machine.down.value
        machine._start_point = utils.new_touch(0, 100, 100)
        machine._last_point = utils.new_touch(0, 100, 100)

        machine.on_release()

        curr_gest = machine._current_gesture
        assert isinstance(curr_gest, models.SingleTouchGesture)
        assert curr_gest.type is enums.SingleTouchType.RELEASE
        assert curr_gest.start is machine._start_point
        assert curr_gest.end is machine._last_point

    def test_on_release_fails_on_no_start_point(self) -> None:
        """Fails due to no start point."""
        machine = single.SingleTouchFSM()
        machine._last_point = utils.new_touch(-1, -1, -1)

        with pytest.raises(RuntimeError):
            machine.on_release()

        assert machine._current_gesture is None

    def test_on_release_fails_on_no_last_point(self) -> None:
        """Fails due to no last point."""
        machine = single.SingleTouchFSM()
        machine._start_point = utils.new_touch(-1, -1, -1)

        with pytest.raises(RuntimeError):
            machine.on_release()

        assert machine._current_gesture is None


class TestSingleTouchFSMGenerateGesture:
    """SingleTouchFSM generate_gesture."""

    # --- ALL COMBINATIONS ---
    # None -> return

    # DOWN -> return
    # DOWN -> contact (None) -> return
    # DOWN -> contact (None) -> RELEASE -> return
    # DOWN -> contact (None) -> RELEASE -> DOWN -> return (to check cycle)

    # DOWN -> HOLD -> return
    # DOWN -> HOLD -> RELEASE -> return
    # DOWN -> HOLD -> DRAG -> return
    # DOWN -> HOLD -> contact (None) -> return
    # DOWN -> HOLD -> contact (None) -> RELEASE -> return

    # DOWN -> DRAG -> return
    # DOWN -> DRAG -> RELEASE -> return
    # DOWN -> DRAG -> DRAG -> return
    # DOWN -> DRAG -> contact (None) -> return
    # DOWN -> DRAG -> contact (None) -> RELEASE -> return

    # DOWN -> FAST TAP -> return
    # DOWN -> SWIPE -> return

    test_config = config.GestureConfig(
        fast_tap=config.FastTapConfig(max_px=10, max_sec=10),
        swipe=config.SwipeConfig(min_px=30, max_sec=30),
        hold=config.HoldConfig(max_px=50, min_sec=50),
        drag=config.DragConfig(min_px=70),
    )

    def test_generate_none(self) -> None:
        """None -> return."""
        machine = single.SingleTouchFSM()

        result = machine.generate_gesture(None)

        assert machine.idle.is_active
        assert machine._start_point is None
        assert machine._last_point is None
        assert result is None

    def test_generate_down(self) -> None:
        """DOWN -> return."""
        machine = single.SingleTouchFSM()
        down_point = utils.new_touch(0, 100, 100)

        result = machine.generate_gesture(down_point)

        assert machine.down.is_active
        assert machine._start_point is down_point
        assert machine._last_point is down_point
        assert isinstance(result, models.SingleTouchGesture)
        assert result.type is enums.SingleTouchType.DOWN

    def test_generate_down_to_contact(self) -> None:
        """DOWN -> contact (None) -> return."""
        machine = single.SingleTouchFSM(config=self.test_config)
        down_point = utils.new_touch(0, 100, 100)
        contact_point = utils.new_touch(0, 100, 140)

        machine.generate_gesture(down_point)
        result = machine.generate_gesture(contact_point)

        assert machine.down.is_active
        assert machine._start_point is down_point
        assert machine._last_point is contact_point
        assert result is None

    def test_generate_down_to_contact_to_release(self) -> None:
        """DOWN -> contact (None) -> RELEASE -> return."""
        machine = single.SingleTouchFSM(config=self.test_config)
        down_point = utils.new_touch(0, 100, 100)
        contact_point = utils.new_touch(0, 100, 140)

        machine.generate_gesture(down_point)
        machine.generate_gesture(contact_point)
        result = machine.generate_gesture(None)

        assert machine.idle.is_active
        assert machine._start_point is down_point
        assert machine._last_point is contact_point
        assert isinstance(result, models.SingleTouchGesture)
        assert result.type is enums.SingleTouchType.RELEASE

    def test_generate_down_to_contact_to_release_to_down(self) -> None:
        """DOWN -> contact (None) -> RELEASE -> DOWN -> return."""
        machine = single.SingleTouchFSM(config=self.test_config)
        down_point1 = utils.new_touch(0, 100, 100)
        contact_point = utils.new_touch(0, 100, 140)
        down_point2 = utils.new_touch(0, 100, 150)

        machine.generate_gesture(down_point1)
        machine.generate_gesture(contact_point)
        machine.generate_gesture(None)
        result = machine.generate_gesture(down_point2)

        assert machine.down.is_active
        assert machine._start_point is down_point2
        assert machine._last_point is down_point2
        assert isinstance(result, models.SingleTouchGesture)
        assert result.type is enums.SingleTouchType.DOWN

    def test_generate_down_to_hold(self) -> None:
        """DOWN -> HOLD -> return."""
        machine = single.SingleTouchFSM(config=self.test_config)
        down_point = utils.new_touch(0, 100, 100)
        hold_point = utils.new_touch(0, 149, 150)

        machine.generate_gesture(down_point)
        result = machine.generate_gesture(hold_point)

        assert machine.holding.is_active
        assert machine._start_point is down_point
        assert machine._last_point is hold_point
        assert isinstance(result, models.SingleTouchGesture)
        assert result.type is enums.SingleTouchType.HOLD

    def test_generate_down_to_hold_to_release(self) -> None:
        """DOWN -> HOLD -> RELEASE -> return."""
        machine = single.SingleTouchFSM(config=self.test_config)
        down_point = utils.new_touch(0, 100, 100)
        hold_point = utils.new_touch(0, 149, 150)

        machine.generate_gesture(down_point)
        machine.generate_gesture(hold_point)
        result = machine.generate_gesture(None)

        assert machine.idle.is_active
        assert machine._start_point is down_point
        assert machine._last_point is hold_point
        assert isinstance(result, models.SingleTouchGesture)
        assert result.type is enums.SingleTouchType.RELEASE

    def test_generate_down_to_hold_to_drag(self) -> None:
        """DOWN -> HOLD -> DRAG -> return."""
        machine = single.SingleTouchFSM(config=self.test_config)
        down_point = utils.new_touch(0, 100, 100)
        hold_point = utils.new_touch(0, 149, 150)
        drag_point = utils.new_touch(0, 170, 160)

        machine.generate_gesture(down_point)
        machine.generate_gesture(hold_point)
        result = machine.generate_gesture(drag_point)

        assert machine.dragging.is_active
        assert machine._start_point is down_point
        assert machine._last_point is drag_point
        assert isinstance(result, models.SingleTouchGesture)
        assert result.type is enums.SingleTouchType.DRAG

    def test_generate_down_to_hold_to_contact(self) -> None:
        """DOWN -> HOLD -> contact (None) -> return."""
        machine = single.SingleTouchFSM(config=self.test_config)
        down_point = utils.new_touch(0, 100, 100)
        hold_point = utils.new_touch(0, 149, 150)
        contact_point = utils.new_touch(0, 169, 160)

        machine.generate_gesture(down_point)
        machine.generate_gesture(hold_point)
        result = machine.generate_gesture(contact_point)

        assert machine.holding.is_active
        assert machine._start_point is down_point
        assert machine._last_point is contact_point
        assert result is None

    def test_generate_down_to_hold_to_contact_to_release(self) -> None:
        """DOWN -> HOLD -> contact (None) -> RELEASE -> return."""
        machine = single.SingleTouchFSM(config=self.test_config)
        down_point = utils.new_touch(0, 100, 100)
        hold_point = utils.new_touch(0, 149, 150)
        contact_point = utils.new_touch(0, 169, 160)

        machine.generate_gesture(down_point)
        machine.generate_gesture(hold_point)
        machine.generate_gesture(contact_point)
        result = machine.generate_gesture(None)

        assert machine.idle.is_active
        assert machine._start_point is down_point
        assert machine._last_point is contact_point
        assert isinstance(result, models.SingleTouchGesture)
        assert result.type is enums.SingleTouchType.RELEASE

    def test_generate_down_to_drag(self) -> None:
        """DOWN -> DRAG -> return."""
        machine = single.SingleTouchFSM(config=self.test_config)
        down_point = utils.new_touch(0, 100, 100)
        drag_point = utils.new_touch(0, 170, 140)

        machine.generate_gesture(down_point)
        result = machine.generate_gesture(drag_point)

        assert machine.dragging.is_active
        assert machine._start_point is down_point
        assert machine._last_point is drag_point
        assert isinstance(result, models.SingleTouchGesture)
        assert result.type is enums.SingleTouchType.DRAG

    def test_generate_down_to_drag_to_release(self) -> None:
        """DOWN -> DRAG -> RELEASE -> return."""
        machine = single.SingleTouchFSM(config=self.test_config)
        down_point = utils.new_touch(0, 100, 100)
        drag_point = utils.new_touch(0, 170, 140)

        machine.generate_gesture(down_point)
        machine.generate_gesture(drag_point)
        result = machine.generate_gesture(None)

        assert machine.idle.is_active
        assert machine._start_point is down_point
        assert machine._last_point is drag_point
        assert isinstance(result, models.SingleTouchGesture)
        assert result.type is enums.SingleTouchType.RELEASE

    def test_generate_down_to_drag_to_drag(self) -> None:
        """DOWN -> DRAG -> DRAG -> return."""
        machine = single.SingleTouchFSM(config=self.test_config)
        down_point = utils.new_touch(0, 100, 100)
        drag_point1 = utils.new_touch(0, 170, 140)
        drag_point2 = utils.new_touch(0, 171, 141)

        machine.generate_gesture(down_point)
        machine.generate_gesture(drag_point1)
        result = machine.generate_gesture(drag_point2)

        assert machine.dragging.is_active
        assert machine._start_point is down_point
        assert machine._last_point is drag_point2
        assert isinstance(result, models.SingleTouchGesture)
        assert result.type is enums.SingleTouchType.DRAG

    def test_generate_down_to_drag_to_contact(self) -> None:
        """DOWN -> DRAG -> contact (None) -> return."""
        machine = single.SingleTouchFSM(config=self.test_config)
        down_point = utils.new_touch(0, 100, 100)
        drag_point = utils.new_touch(0, 170, 140)
        contact_point = utils.new_touch(0, 170, 141)

        machine.generate_gesture(down_point)
        machine.generate_gesture(drag_point)
        result = machine.generate_gesture(contact_point)

        assert machine.dragging.is_active
        assert machine._start_point is down_point
        assert machine._last_point is contact_point
        assert result is None

    def test_generate_down_to_drag_to_contact_to_release(self) -> None:
        """DOWN -> DRAG -> contact (None) -> RELEASE -> return."""
        machine = single.SingleTouchFSM(config=self.test_config)
        down_point = utils.new_touch(0, 100, 100)
        drag_point = utils.new_touch(0, 170, 140)
        contact_point = utils.new_touch(0, 170, 141)

        machine.generate_gesture(down_point)
        machine.generate_gesture(drag_point)
        machine.generate_gesture(contact_point)
        result = machine.generate_gesture(None)

        assert machine.idle.is_active
        assert machine._start_point is down_point
        assert machine._last_point is contact_point
        assert isinstance(result, models.SingleTouchGesture)
        assert result.type is enums.SingleTouchType.RELEASE

    def test_generate_down_to_tap(self) -> None:
        """DOWN -> FAST TAP -> return."""
        machine = single.SingleTouchFSM(config=self.test_config)
        down_point = utils.new_touch(0, 100, 100)
        contact_point = utils.new_touch(0, 95, 105)

        machine.generate_gesture(down_point)
        machine.generate_gesture(contact_point)
        result = machine.generate_gesture(None)

        assert machine.idle.is_active
        assert machine._start_point is down_point
        assert machine._last_point is contact_point
        assert isinstance(result, models.SingleTouchGesture)
        assert result.type is enums.SingleTouchType.FAST_TAP

    def test_generate_down_to_swipe(self) -> None:
        """DOWN -> SWIPE -> return."""
        machine = single.SingleTouchFSM(config=self.test_config)
        down_point = utils.new_touch(0, 100, 100)
        contact_point = utils.new_touch(0, 130, 129)

        machine.generate_gesture(down_point)
        machine.generate_gesture(contact_point)
        result = machine.generate_gesture(None)

        assert machine.idle.is_active
        assert machine._start_point is down_point
        assert machine._last_point is contact_point
        assert isinstance(result, models.SingleTouchGesture)
        assert result.type is enums.SingleTouchType.SWIPE
