import math
from typing import TYPE_CHECKING

import pytest

from pireader import config
from pireader.common import enums, models
from pireader.touch_input.fsms import multi
from tests import utils

if TYPE_CHECKING:
    import statemachine


# --- Conditions ---
class TestMultiTouchFSMShouldHold:
    """MultiTouchFSM _should_hold."""

    def test_should_hold_returns_true_on_hold_gestures(self) -> None:
        """Both are HOLD gestures."""
        machine = multi.MultiTouchFSM()
        machine.current_state_value = machine.down.value
        first = utils.new_st_gesture(enums.SingleTouchState.HOLD)
        second = utils.new_st_gesture(enums.SingleTouchState.HOLD)

        result = machine._should_hold(first, second)

        assert result is True

    @pytest.mark.parametrize(
        ("first_state", "second_state"),
        [
            (enums.SingleTouchState.DOWN, enums.SingleTouchState.HOLD),
            (enums.SingleTouchState.HOLD, enums.SingleTouchState.DOWN),
            (enums.SingleTouchState.DOWN, enums.SingleTouchState.DOWN),
        ],
    )
    def test_should_hold_returns_false_on_not_hold_gestures(
        self,
        first_state: enums.SingleTouchState,
        second_state: enums.SingleTouchState,
    ) -> None:
        """One or both are not HOLD gestures."""
        machine = multi.MultiTouchFSM()
        machine.current_state_value = machine.down.value
        first = utils.new_st_gesture(first_state)
        second = utils.new_st_gesture(second_state)

        result = machine._should_hold(first, second)

        assert result is False

    @pytest.mark.parametrize(
        "machine_state",
        [
            multi.MultiTouchFSM.idle,
            multi.MultiTouchFSM.holding,
            multi.MultiTouchFSM.transforming,
        ],
    )
    def test_should_hold_returns_false_on_not_machine_down_state(
        self, machine_state: statemachine.State
    ) -> None:
        """Machine is not on down state."""
        machine = multi.MultiTouchFSM()
        machine.current_state_value = machine_state.value
        first = utils.new_st_gesture(enums.SingleTouchState.HOLD)
        second = utils.new_st_gesture(enums.SingleTouchState.HOLD)

        result = machine._should_hold(first, second)

        assert result is False


class TestMultiTouchFSMShouldUpdate:
    """MultiTouchFSM _should_update."""

    @pytest.mark.parametrize(
        ("first_state", "second_state"),
        [
            (enums.SingleTouchState.DOWN, enums.SingleTouchState.DRAG),
            (enums.SingleTouchState.DRAG, enums.SingleTouchState.DOWN),
            (enums.SingleTouchState.DRAG, enums.SingleTouchState.DRAG),
        ],
    )
    def test_should_update_returns_true_on_drag_gesture(
        self,
        first_state: enums.SingleTouchState,
        second_state: enums.SingleTouchState,
    ) -> None:
        """One or both are DRAG gestures."""
        machine = multi.MultiTouchFSM()
        machine.current_state_value = machine.down.value
        first = utils.new_st_gesture(first_state)
        second = utils.new_st_gesture(second_state)

        result = machine._should_update(first, second)

        assert result is True

    def test_should_update_returns_false_on_no_drag_gesture(self) -> None:
        """None are DRAG gestures."""
        machine = multi.MultiTouchFSM()
        machine.current_state_value = machine.down.value
        first = utils.new_st_gesture(enums.SingleTouchState.DOWN)
        second = utils.new_st_gesture(enums.SingleTouchState.DOWN)

        result = machine._should_update(first, second)

        assert result is False

    @pytest.mark.parametrize(
        ("first_state", "second_state"),
        [
            (enums.SingleTouchState.DRAG, enums.SingleTouchState.RELEASE),
            (enums.SingleTouchState.RELEASE, enums.SingleTouchState.DRAG),
            (enums.SingleTouchState.RELEASE, enums.SingleTouchState.RELEASE),
        ],
    )
    def test_should_update_returns_false_on_lifecycle_end(
        self,
        first_state: enums.SingleTouchState,
        second_state: enums.SingleTouchState,
    ) -> None:
        """One or both are lifecycle end gestures."""
        machine = multi.MultiTouchFSM()
        machine.current_state_value = machine.down.value
        first = utils.new_st_gesture(first_state)
        second = utils.new_st_gesture(second_state)

        result = machine._should_update(first, second)

        assert result is False


# --- Action Hooks ---
class TestMultiTouchFSMOnTouchDown:
    """MultiTouchFSM on_touch_down."""

    def test_on_touch_down_creates_pointers_down_gesture(self) -> None:
        """Generates a POINTERS DOWN gesture."""
        machine = multi.MultiTouchFSM()
        machine.current_state_value = machine.idle.value
        first = utils.new_st_gesture(end=(100, 100, -1))
        second = utils.new_st_gesture(end=(150, 120, -1))

        machine.on_touch_down(first, second)

        curr_gest = machine._current_gesture
        assert isinstance(curr_gest, models.MultiTouchGesture)
        assert curr_gest.state == enums.MultiTouchState.POINTER_DOWN
        assert curr_gest.first is first
        assert curr_gest.second is second
        assert curr_gest.midpoint.x == 125
        assert curr_gest.midpoint.y == 110


class TestMultiTouchFSMOnHold:
    """MultiTouchFSM on_hold."""

    def test_on_hold_creates_pointer_hold_gesture(self) -> None:
        """Generates a POINTER HOLD gesture."""
        machine = multi.MultiTouchFSM()
        machine.current_state_value = machine.down.value
        first = utils.new_st_gesture(end=(100, 100, -1))
        second = utils.new_st_gesture(end=(150, 120, -1))

        machine.on_hold(first, second)

        curr_gest = machine._current_gesture
        assert isinstance(curr_gest, models.MultiTouchGesture)
        assert curr_gest.state == enums.MultiTouchState.POINTER_HOLD
        assert curr_gest.first is first
        assert curr_gest.second is second
        assert curr_gest.midpoint.x == 125
        assert curr_gest.midpoint.y == 110


class TestMultiTouchFSMOnUpdate:
    """MultiTouchFSM on_update."""

    # --- ALL COMBINATIONS ---
    # None

    # PAN (midpoint dx, dy threshold)
    # ZOOM (first and second distance threshold)
    # ROTATE (angular difference threshold)

    # PAN ZOOM
    # PAN ZOOM ROTATE
    # PAN ROTATE

    # ZOOM ROTATE

    test_config = config.GestureConfig(
        pan=config.PanConfig(min_px=20),
        zoom=config.ZoomConfig(min_px=20),
        rotate=config.RotateConfig(min_deg=90),
    )

    def test_on_update_no_threshold_met(self) -> None:
        """No gesture is generated due to no thresholds met."""
        machine = multi.MultiTouchFSM(config=self.test_config)
        machine.current_state_value = machine.transforming.value
        machine._set_up_initial_values(
            utils.new_touch(100, 100, -1),
            utils.new_touch(100, 120, -1),
        )
        first = utils.new_st_gesture(  # + 19 px
            enums.SingleTouchState.DRAG, end=(100, 119, -1)
        )
        second = utils.new_st_gesture(  # + 19 px
            enums.SingleTouchState.DRAG, end=(100, 139, -1)
        )

        machine.on_update(first, second)

        assert machine._current_gesture is None

    def test_on_update_creates_pan_gesture(self) -> None:
        """Generates a PAN gesture."""
        machine = multi.MultiTouchFSM(config=self.test_config)
        machine.current_state_value = machine.transforming.value
        machine._set_up_initial_values(
            utils.new_touch(100, 100, -1),
            utils.new_touch(100, 120, -1),
        )
        first = utils.new_st_gesture(  # + 20 px
            enums.SingleTouchState.DRAG, end=(100, 120, -1)
        )
        second = utils.new_st_gesture(  # + 20 px
            enums.SingleTouchState.DRAG, end=(100, 140, -1)
        )

        machine.on_update(first, second)

        curr_gest = machine._current_gesture
        assert isinstance(curr_gest, models.MultiTouchGesture)
        assert curr_gest.state == enums.MultiTouchState.PAN
        assert curr_gest.first is first
        assert curr_gest.second is second
        assert curr_gest.midpoint.x == 100
        assert curr_gest.midpoint.y == 130
        assert isinstance(curr_gest.offset, models.Vector2D)
        assert curr_gest.offset.x == 0
        assert curr_gest.offset.y == 20
        assert math.isclose(curr_gest.scale, 1.0)
        assert math.isclose(curr_gest.angle, 0.0)

    def test_on_update_creates_zoom_gesture(self) -> None:
        """Generates a ZOOM gesture."""
        machine = multi.MultiTouchFSM(config=self.test_config)
        machine.current_state_value = machine.transforming.value
        machine._set_up_initial_values(
            utils.new_touch(100, 100, -1),
            utils.new_touch(100, 120, -1),
        )
        first = utils.new_st_gesture(  # - 10 px
            enums.SingleTouchState.DRAG, end=(100, 90, -1)
        )
        second = utils.new_st_gesture(  # + 10 px
            enums.SingleTouchState.DRAG, end=(100, 130, -1)
        )

        machine.on_update(first, second)

        curr_gest = machine._current_gesture
        assert isinstance(curr_gest, models.MultiTouchGesture)
        assert curr_gest.state == enums.MultiTouchState.ZOOM
        assert curr_gest.first is first
        assert curr_gest.second is second
        assert curr_gest.midpoint.x == 100
        assert curr_gest.midpoint.y == 110
        assert curr_gest.offset is None
        assert math.isclose(curr_gest.scale, 2.0)
        assert math.isclose(curr_gest.angle, 0.0)

    def test_on_update_creates_zoom_gesture_skips_pan_check(self) -> None:
        """Generates a ZOOM gesture skipping the PAN check."""
        machine = multi.MultiTouchFSM(config=self.test_config)
        machine.current_state_value = machine.transforming.value
        machine._set_up_initial_values(
            utils.new_touch(100, 100, -1),
            utils.new_touch(100, 120, -1),
        )
        first = utils.new_st_gesture(
            enums.SingleTouchState.HOLD, end=(100, 100, -1)
        )
        second = utils.new_st_gesture(  # + 20 px
            enums.SingleTouchState.DRAG, end=(100, 140, -1)
        )

        machine.on_update(first, second)

        curr_gest = machine._current_gesture
        assert isinstance(curr_gest, models.MultiTouchGesture)
        assert curr_gest.state == enums.MultiTouchState.ZOOM
        assert curr_gest.first is first
        assert curr_gest.second is second
        assert curr_gest.midpoint.x == 100
        assert curr_gest.midpoint.y == 120
        assert curr_gest.offset is None
        assert math.isclose(curr_gest.scale, 2.0)
        assert math.isclose(curr_gest.angle, 0.0)

    def test_on_update_creates_rotate_gesture(self) -> None:
        """Generates a ROTATE gesture."""
        machine = multi.MultiTouchFSM(config=self.test_config)
        machine.current_state_value = machine.transforming.value
        machine._set_up_initial_values(
            utils.new_touch(-100, 0, -1),
            utils.new_touch(100, 0, -1),
        )
        first = utils.new_st_gesture(  # 90 deg
            enums.SingleTouchState.DRAG, end=(0, 100, -1)
        )
        second = utils.new_st_gesture(  # 90 deg
            enums.SingleTouchState.DRAG, end=(0, -100, -1)
        )

        machine.on_update(first, second)

        curr_gest = machine._current_gesture
        assert isinstance(curr_gest, models.MultiTouchGesture)
        assert curr_gest.state == enums.MultiTouchState.ROTATE
        assert curr_gest.first is first
        assert curr_gest.second is second
        assert curr_gest.midpoint.x == 0
        assert curr_gest.midpoint.y == 0
        assert curr_gest.offset is None
        assert math.isclose(curr_gest.scale, 1.0)
        assert math.isclose(curr_gest.angle, -90.0)

    def test_on_update_creates_pan_zoom_gesture(self) -> None:
        """Generates a PAN ZOOM gesture."""
        machine = multi.MultiTouchFSM(config=self.test_config)
        machine.current_state_value = machine.transforming.value
        machine._set_up_initial_values(
            utils.new_touch(100, 100, -1),
            utils.new_touch(100, 120, -1),
        )
        first = utils.new_st_gesture(  # + 20 px - 10 px
            enums.SingleTouchState.DRAG, end=(100, 110, -1)
        )
        second = utils.new_st_gesture(  # + 20 px + 10 px
            enums.SingleTouchState.DRAG, end=(100, 150, -1)
        )

        machine.on_update(first, second)

        curr_gest = machine._current_gesture
        assert isinstance(curr_gest, models.MultiTouchGesture)
        assert (
            curr_gest.state
            == enums.MultiTouchState.PAN | enums.MultiTouchState.ZOOM
        )
        assert curr_gest.first is first
        assert curr_gest.second is second
        assert curr_gest.midpoint.x == 100
        assert curr_gest.midpoint.y == 130
        assert isinstance(curr_gest.offset, models.Vector2D)
        assert curr_gest.offset.x == 0
        assert curr_gest.offset.y == 20
        assert math.isclose(curr_gest.scale, 2.0)
        assert math.isclose(curr_gest.angle, 0.0)

    def test_on_update_creates_pan_zoom_rotate_gesture(self) -> None:
        """Generates a PAN ZOOM ROTATE gesture."""
        machine = multi.MultiTouchFSM(config=self.test_config)
        machine.current_state_value = machine.transforming.value
        machine._set_up_initial_values(
            utils.new_touch(-100, 0, -1),
            utils.new_touch(100, 0, -1),
        )
        first = utils.new_st_gesture(  # 90 deg + 20 px + 10 px
            enums.SingleTouchState.DRAG, end=(0, 130, -1)
        )
        second = utils.new_st_gesture(  # 90 deg + 20 px - 10 px
            enums.SingleTouchState.DRAG, end=(0, -90, -1)
        )

        machine.on_update(first, second)

        curr_gest = machine._current_gesture
        assert isinstance(curr_gest, models.MultiTouchGesture)
        assert (
            curr_gest.state
            == enums.MultiTouchState.PAN
            | enums.MultiTouchState.ZOOM
            | enums.MultiTouchState.ROTATE
        )
        assert curr_gest.first is first
        assert curr_gest.second is second
        assert curr_gest.midpoint.x == 0
        assert curr_gest.midpoint.y == 20
        assert isinstance(curr_gest.offset, models.Vector2D)
        assert curr_gest.offset.x == 0
        assert curr_gest.offset.y == 20
        assert math.isclose(curr_gest.scale, 220 / 200)
        assert math.isclose(curr_gest.angle, -90.0)

    def test_on_update_creates_pan_rotate_gesture(self) -> None:
        """Generates a PAN ROTATE gesture."""
        machine = multi.MultiTouchFSM(config=self.test_config)
        machine.current_state_value = machine.transforming.value
        machine._set_up_initial_values(
            utils.new_touch(-100, 0, -1),
            utils.new_touch(100, 0, -1),
        )
        first = utils.new_st_gesture(  # 90 deg + 20 px
            enums.SingleTouchState.DRAG, end=(0, 120, -1)
        )
        second = utils.new_st_gesture(  # 90 deg + 20 px
            enums.SingleTouchState.DRAG, end=(0, -80, -1)
        )

        machine.on_update(first, second)

        curr_gest = machine._current_gesture
        assert isinstance(curr_gest, models.MultiTouchGesture)
        assert (
            curr_gest.state
            == enums.MultiTouchState.PAN | enums.MultiTouchState.ROTATE
        )
        assert curr_gest.first is first
        assert curr_gest.second is second
        assert curr_gest.midpoint.x == 0
        assert curr_gest.midpoint.y == 20
        assert isinstance(curr_gest.offset, models.Vector2D)
        assert curr_gest.offset.x == 0
        assert curr_gest.offset.y == 20
        assert math.isclose(curr_gest.scale, 1.0)
        assert math.isclose(curr_gest.angle, -90.0)

    def test_on_update_creates_zoom_rotate_gesture(self) -> None:
        """Generate a ZOOM ROTATE gesture."""
        machine = multi.MultiTouchFSM(config=self.test_config)
        machine.current_state_value = machine.transforming.value
        machine._set_up_initial_values(
            utils.new_touch(-100, 0, -1),
            utils.new_touch(100, 0, -1),
        )
        first = utils.new_st_gesture(  # 90 deg + 10 px
            enums.SingleTouchState.DRAG, end=(0, 110, -1)
        )
        second = utils.new_st_gesture(  # 90 deg - 10 px
            enums.SingleTouchState.DRAG, end=(0, -110, -1)
        )

        machine.on_update(first, second)

        curr_gest = machine._current_gesture
        assert isinstance(curr_gest, models.MultiTouchGesture)
        assert (
            curr_gest.state
            == enums.MultiTouchState.ZOOM | enums.MultiTouchState.ROTATE
        )
        assert curr_gest.first is first
        assert curr_gest.second is second
        assert curr_gest.midpoint.x == 0
        assert curr_gest.midpoint.y == 0
        assert curr_gest.offset is None
        assert math.isclose(curr_gest.scale, 220 / 200)
        assert math.isclose(curr_gest.angle, -90.0)

    def test_on_update_fails_on_no_start_first(self) -> None:
        """Start first is None."""
        machine = multi.MultiTouchFSM()
        machine.current_state_value = machine.transforming.value
        machine._start_second = utils.new_touch(-1, -1, -1)
        machine._start_midpoint = utils.new_vector2d(-1, -1)

        with pytest.raises(RuntimeError):
            machine.on_update(utils.new_st_gesture(), utils.new_st_gesture())

        assert machine._current_gesture is None

    def test_on_update_fails_on_no_start_second(self) -> None:
        """Start second is None."""
        machine = multi.MultiTouchFSM()
        machine.current_state_value = machine.transforming.value
        machine._start_first = utils.new_touch(-1, -1, -1)
        machine._start_midpoint = utils.new_vector2d(-1, -1)

        with pytest.raises(RuntimeError):
            machine.on_update(utils.new_st_gesture(), utils.new_st_gesture())

        assert machine._current_gesture is None

    def test_on_update_fails_on_no_start_midpoint(self) -> None:
        """Start midpoint is None."""
        machine = multi.MultiTouchFSM()
        machine.current_state_value = machine.transforming.value
        machine._start_first = utils.new_touch(-1, -1, -1)
        machine._start_second = utils.new_touch(-1, -1, -1)

        with pytest.raises(RuntimeError):
            machine.on_update(utils.new_st_gesture(), utils.new_st_gesture())

        assert machine._current_gesture is None


class TestMultiTouchFSMOnRelease:
    """MultiTouchFSM on_release."""

    # --- ALL POSSIBLE GESTURES ---
    # None
    # FAST TAP
    # ANCHOR TAP
    # FLICK
    # POINTER_UP

    def test_on_release_no_condition_met(self) -> None:
        """No gesture is generated due to no conditions met."""
        machine = multi.MultiTouchFSM()
        machine.current_state_value = machine.down.value
        first = utils.new_st_gesture(
            enums.SingleTouchState.SWIPE, direction=enums.Direction.LEFT
        )
        second = utils.new_st_gesture(
            enums.SingleTouchState.SWIPE, direction=enums.Direction.RIGHT
        )

        machine.on_release(first, second)  # SWIPE directions are not equal

        assert machine._current_gesture is None

    def test_on_release_creates_fast_tap_gesture(self) -> None:
        """Generates a FAST TAP gesture."""
        machine = multi.MultiTouchFSM()
        machine.current_state_value = machine.transforming.value
        first = utils.new_st_gesture(
            enums.SingleTouchState.FAST_TAP, end=(15, 10, -1)
        )
        second = utils.new_st_gesture(
            enums.SingleTouchState.FAST_TAP, end=(5, 10, -1)
        )

        machine.on_release(first, second)

        curr_gest = machine._current_gesture
        assert isinstance(curr_gest, models.MultiTouchGesture)
        assert curr_gest.state == enums.MultiTouchState.FAST_TAP
        assert curr_gest.first is first
        assert curr_gest.second is second
        assert curr_gest.midpoint.x == 10
        assert curr_gest.midpoint.y == 10

    @pytest.mark.parametrize(
        ("first_state", "second_state"),
        [
            (enums.SingleTouchState.HOLD, enums.SingleTouchState.FAST_TAP),
            (enums.SingleTouchState.DRAG, enums.SingleTouchState.FAST_TAP),
            (enums.SingleTouchState.FAST_TAP, enums.SingleTouchState.HOLD),
            (enums.SingleTouchState.FAST_TAP, enums.SingleTouchState.DRAG),
        ],
    )
    def test_on_release_creates_anchor_tap_gesture(
        self,
        first_state: enums.SingleTouchState,
        second_state: enums.SingleTouchState,
    ) -> None:
        """Generates an ANCHOR TAP gesture."""
        machine = multi.MultiTouchFSM()
        machine.current_state_value = machine.down.value
        first = utils.new_st_gesture(first_state, end=(15, 10, -1))
        second = utils.new_st_gesture(second_state, end=(5, 10, -1))

        machine.on_release(first, second)

        curr_gest = machine._current_gesture
        assert isinstance(curr_gest, models.MultiTouchGesture)
        assert curr_gest.state == enums.MultiTouchState.ANCHOR_TAP
        assert curr_gest.first is first
        assert curr_gest.second is second
        assert curr_gest.midpoint.x == 10
        assert curr_gest.midpoint.y == 10

    @pytest.mark.parametrize(
        "direction", [enums.Direction.LEFT, enums.Direction.RIGHT]
    )
    def test_on_release_creates_flick_gesture(
        self, direction: enums.Direction
    ) -> None:
        """Generates a FLICK gesture."""
        machine = multi.MultiTouchFSM()
        machine.current_state_value = machine.down.value
        first = utils.new_st_gesture(
            enums.SingleTouchState.SWIPE, direction=direction, end=(15, 10, -1)
        )
        second = utils.new_st_gesture(
            enums.SingleTouchState.SWIPE, direction=direction, end=(5, 10, -1)
        )

        machine.on_release(first, second)

        curr_gest = machine._current_gesture
        assert isinstance(curr_gest, models.MultiTouchGesture)
        assert curr_gest.state == enums.MultiTouchState.FLICK
        assert curr_gest.first is first
        assert curr_gest.second is second
        assert curr_gest.midpoint.x == 10
        assert curr_gest.midpoint.y == 10
        assert curr_gest.direction == direction

    @pytest.mark.parametrize(
        ("first_state", "second_state"),
        [
            (enums.SingleTouchState.RELEASE, enums.SingleTouchState.HOLD),
            (enums.SingleTouchState.HOLD, enums.SingleTouchState.RELEASE),
        ],
    )
    def test_on_release_creates_pointer_up_gesture(
        self,
        first_state: enums.SingleTouchState,
        second_state: enums.SingleTouchState,
    ) -> None:
        """Generates a POINTER UP gesture."""
        machine = multi.MultiTouchFSM()
        machine.current_state_value = machine.down.value
        first = utils.new_st_gesture(first_state, end=(15, 10, -1))
        second = utils.new_st_gesture(second_state, end=(5, 10, -1))

        machine.on_release(first, second)

        curr_gest = machine._current_gesture
        assert isinstance(curr_gest, models.MultiTouchGesture)
        assert curr_gest.state == enums.MultiTouchState.POINTER_UP
        assert curr_gest.first is first
        assert curr_gest.second is second
        assert curr_gest.midpoint.x == 10
        assert curr_gest.midpoint.y == 10


class TestMultiTouchFSMGenerateGesture:
    """MultiTouchFSM generate_gesture."""

    # --- ALL COMBINATIONS ---
    # POINTER DOWN -> return
    # POINTER DOWN -> POINTER UP -> return
    # POINTER DOWN -> POINTER UP -> POINTER DOWN -> return (to check cycle)

    # POINTER DOWN -> POINTER HOLD -> return
    # POINTER DOWN -> POINTER HOLD -> POINTER UP -> return
    # POINTER DOWN -> POINTER HOLD -> transform (PAN) -> return

    # POINTER DOWN -> transform (PAN) -> return
    # POINTER DOWN -> transform (PAN) -> POINTER UP -> return
    # POINTER DOWN -> transform (None) -> return
    # POINTER DOWN -> transform (None) -> POINTER UP -> return

    test_config = config.GestureConfig(
        pan=config.PanConfig(min_px=20),
        zoom=config.ZoomConfig(min_px=1000),
        rotate=config.RotateConfig(min_deg=180),
    )

    def test_generate_down(self) -> None:
        """POINTER DOWN -> return."""
        machine = multi.MultiTouchFSM()
        down_first = utils.new_st_gesture()
        down_second = utils.new_st_gesture()

        result = machine.generate_gesture(down_first, down_second)

        assert machine.down.is_active
        assert machine._start_first is down_first.end
        assert machine._start_second is down_second.end
        assert isinstance(result, models.MultiTouchGesture)
        assert result.state == enums.MultiTouchState.POINTER_DOWN

    def test_generate_down_to_up(self) -> None:
        """POINTER DOWN -> POINTER UP -> return."""
        machine = multi.MultiTouchFSM()
        down_first = utils.new_st_gesture()
        down_second = utils.new_st_gesture()
        up_first = utils.new_st_gesture(enums.SingleTouchState.RELEASE)
        up_second = utils.new_st_gesture()

        machine.generate_gesture(down_first, down_second)
        result = machine.generate_gesture(up_first, up_second)

        assert machine.idle.is_active
        assert machine._start_first is down_first.end
        assert machine._start_second is down_second.end
        assert isinstance(result, models.MultiTouchGesture)
        assert result.state == enums.MultiTouchState.POINTER_UP

    def test_generate_down_to_up_to_down(self) -> None:
        """POINTER DOWN -> POINTER UP -> POINTER DOWN -> return."""
        machine = multi.MultiTouchFSM()
        down_first = utils.new_st_gesture()
        down_second = utils.new_st_gesture()
        up_first = utils.new_st_gesture(enums.SingleTouchState.RELEASE)
        up_second = utils.new_st_gesture()
        down_first2 = utils.new_st_gesture()
        down_second2 = utils.new_st_gesture()

        machine.generate_gesture(down_first, down_second)
        machine.generate_gesture(up_first, up_second)
        result = machine.generate_gesture(down_first2, down_second2)

        assert machine.down.is_active
        assert machine._start_first is down_first2.end
        assert machine._start_second is down_second2.end
        assert isinstance(result, models.MultiTouchGesture)
        assert result.state == enums.MultiTouchState.POINTER_DOWN

    def test_generate_down_to_hold(self) -> None:
        """POINTER DOWN -> POINTER HOLD -> return."""
        machine = multi.MultiTouchFSM()
        down_first = utils.new_st_gesture()
        down_second = utils.new_st_gesture()
        hold_first = utils.new_st_gesture(enums.SingleTouchState.HOLD)
        hold_second = utils.new_st_gesture(enums.SingleTouchState.HOLD)

        machine.generate_gesture(down_first, down_second)
        result = machine.generate_gesture(hold_first, hold_second)

        assert machine.holding.is_active
        assert machine._start_first is down_first.end
        assert machine._start_second is down_second.end
        assert isinstance(result, models.MultiTouchGesture)
        assert result.state == enums.MultiTouchState.POINTER_HOLD

    def test_generate_down_to_hold_to_up(self) -> None:
        """POINTER DOWN -> POINTER HOLD -> POINTER UP -> return."""
        machine = multi.MultiTouchFSM()
        down_first = utils.new_st_gesture()
        down_second = utils.new_st_gesture()
        hold_first = utils.new_st_gesture(enums.SingleTouchState.HOLD)
        hold_second = utils.new_st_gesture(enums.SingleTouchState.HOLD)
        up_first = utils.new_st_gesture(enums.SingleTouchState.RELEASE)
        up_second = utils.new_st_gesture(enums.SingleTouchState.HOLD)

        machine.generate_gesture(down_first, down_second)
        machine.generate_gesture(hold_first, hold_second)
        result = machine.generate_gesture(up_first, up_second)

        assert machine.idle.is_active
        assert machine._start_first is down_first.end
        assert machine._start_second is down_second.end
        assert isinstance(result, models.MultiTouchGesture)
        assert result.state == enums.MultiTouchState.POINTER_UP

    def test_generate_down_to_hold_to_pan(self) -> None:
        """POINTER DOWN -> POINTER HOLD -> transform (PAN) -> return."""
        machine = multi.MultiTouchFSM(config=self.test_config)
        down_first = utils.new_st_gesture(end=(0, 100, -1))
        down_second = utils.new_st_gesture(end=(0, 100, -1))
        hold_first = utils.new_st_gesture(enums.SingleTouchState.HOLD)
        hold_second = utils.new_st_gesture(enums.SingleTouchState.HOLD)
        pan_first = utils.new_st_gesture(
            enums.SingleTouchState.DRAG, end=(0, 120, -1)
        )
        pan_second = utils.new_st_gesture(
            enums.SingleTouchState.DRAG, end=(0, 120, -1)
        )

        machine.generate_gesture(down_first, down_second)
        machine.generate_gesture(hold_first, hold_second)
        result = machine.generate_gesture(pan_first, pan_second)

        assert machine.transforming.is_active
        assert machine._start_first is down_first.end
        assert machine._start_second is down_second.end
        assert isinstance(result, models.MultiTouchGesture)
        assert result.state == enums.MultiTouchState.PAN

    def test_generate_down_to_pan(self) -> None:
        """POINTER DOWN -> transform (PAN) -> return."""
        machine = multi.MultiTouchFSM(config=self.test_config)
        down_first = utils.new_st_gesture(end=(0, 100, -1))
        down_second = utils.new_st_gesture(end=(0, 100, -1))
        pan_first = utils.new_st_gesture(
            enums.SingleTouchState.DRAG, end=(0, 120, -1)
        )
        pan_second = utils.new_st_gesture(
            enums.SingleTouchState.DRAG, end=(0, 120, -1)
        )

        machine.generate_gesture(down_first, down_second)
        result = machine.generate_gesture(pan_first, pan_second)

        assert machine.transforming.is_active
        assert machine._start_first is down_first.end
        assert machine._start_second is down_second.end
        assert isinstance(result, models.MultiTouchGesture)
        assert result.state == enums.MultiTouchState.PAN

    def test_generate_down_to_pan_to_up(self) -> None:
        """POINTER DOWN -> transform (PAN) -> POINTER UP -> return."""
        machine = multi.MultiTouchFSM(config=self.test_config)
        down_first = utils.new_st_gesture(end=(0, 100, -1))
        down_second = utils.new_st_gesture(end=(0, 100, -1))
        pan_first = utils.new_st_gesture(
            enums.SingleTouchState.DRAG, end=(0, 120, -1)
        )
        pan_second = utils.new_st_gesture(
            enums.SingleTouchState.DRAG, end=(0, 120, -1)
        )
        up_first = utils.new_st_gesture(enums.SingleTouchState.RELEASE)
        up_second = utils.new_st_gesture(enums.SingleTouchState.DRAG)

        machine.generate_gesture(down_first, down_second)
        machine.generate_gesture(pan_first, pan_second)
        result = machine.generate_gesture(up_first, up_second)

        assert machine.idle.is_active
        assert machine._start_first is down_first.end
        assert machine._start_second is down_second.end
        assert isinstance(result, models.MultiTouchGesture)
        assert result.state == enums.MultiTouchState.POINTER_UP

    def test_generate_down_to_transform_none(self) -> None:
        """POINTER DOWN -> transform (None) -> return."""
        machine = multi.MultiTouchFSM(config=self.test_config)
        down_first = utils.new_st_gesture(end=(0, 100, -1))
        down_second = utils.new_st_gesture(end=(0, 100, -1))
        transform_first = utils.new_st_gesture(
            enums.SingleTouchState.DRAG, end=(0, 119, -1)
        )
        transform_second = utils.new_st_gesture(
            enums.SingleTouchState.DRAG, end=(0, 119, -1)
        )

        machine.generate_gesture(down_first, down_second)
        result = machine.generate_gesture(transform_first, transform_second)

        assert machine.transforming.is_active
        assert machine._start_first is down_first.end
        assert machine._start_second is down_second.end
        assert result is None

    def test_generate_down_to_transform_none_to_up(self) -> None:
        """POINTER DOWN -> transform (None) -> POINTER UP -> return."""
        machine = multi.MultiTouchFSM(config=self.test_config)
        down_first = utils.new_st_gesture(end=(0, 100, -1))
        down_second = utils.new_st_gesture(end=(0, 100, -1))
        transform_first = utils.new_st_gesture(
            enums.SingleTouchState.DRAG, end=(0, 119, -1)
        )
        transform_second = utils.new_st_gesture(
            enums.SingleTouchState.DRAG, end=(0, 119, -1)
        )
        up_first = utils.new_st_gesture(enums.SingleTouchState.RELEASE)
        up_second = utils.new_st_gesture(enums.SingleTouchState.DRAG)

        machine.generate_gesture(down_first, down_second)
        machine.generate_gesture(transform_first, transform_second)
        result = machine.generate_gesture(up_first, up_second)

        assert machine.idle.is_active
        assert machine._start_first is down_first.end
        assert machine._start_second is down_second.end
        assert isinstance(result, models.MultiTouchGesture)
        assert result.state == enums.MultiTouchState.POINTER_UP
