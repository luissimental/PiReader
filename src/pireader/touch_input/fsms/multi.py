"""State machine for generating multi-touch gestures."""

import math

import statemachine

from pireader import config
from pireader.common import enums, geometry, models


class MultiTouchFSM(statemachine.StateChart):
    """State machine for processing SingleTouchGestures into MultiTouchGestures.

    Example:
      Generate a gesture from two SingleTouchGestures::

        gesture1: SingleTouchGesture = ...
        gesture2: SingleTouchGesture = ...
        machine = MultiTouchFSM()
        result = machine.generate_gesture(gesture1, gesture2)

    """  # noqa: E501

    # --- States ---
    idle = statemachine.State(initial=True)
    down = statemachine.State()
    holding = statemachine.State()
    transforming = statemachine.State()  # PAN, ZOOM, ROTATE

    # --- Transitions ---
    touch_down = down.from_(idle)
    hold = holding.from_(down)
    update = transforming.from_(down, holding, transforming)
    release = idle.from_(down, holding, transforming)

    def __init__(
        self, *, config: config.GestureConfig = config.GESTURE_CONFIG
    ) -> None:
        super().__init__()
        self._conf = config
        self._start_first: models.TouchEvent | None = None
        self._start_second: models.TouchEvent | None = None
        self._start_midpoint: models.TouchEvent | None = None
        self._start_distance = 0.0
        self._start_angle = 0.0
        self._current_gesture: models.MultiTouchGesture | None = None

    def generate_gesture(
        self,
        first: models.SingleTouchGesture,
        second: models.SingleTouchGesture,
    ) -> models.MultiTouchGesture | None:
        """Generate a multi-touch gesture from two single-touch gestures.

        Args:
          first:
            The first single-touch gesture.
          second:
            The second single-touch gesture.

        Returns:
          The multi-touch gesture after processing. May be None when the
          current state does not detect a valid gesture.

        """
        self._current_gesture = None

        # Traverse state machine
        if self.idle.is_active:
            self._set_up_initial_values(first.end, second.end)
            self.touch_down(first, second)
        elif self._should_hold(first, second):
            self.hold(first, second)
        elif self._should_update(first, second):
            self.update(first, second)
        else:
            self.release(first, second)

        return self._current_gesture

    def _set_up_initial_values(
        self, first_point: models.TouchEvent, second_point: models.TouchEvent
    ) -> None:
        """Set up cached variables."""
        self._start_first = first_point
        self._start_second = second_point
        self._start_midpoint = first_point.midpoint_to(second_point)
        self._start_distance = first_point.distance_to(second_point)
        self._start_angle = first_point.degrees_to(second_point)

    # --- Conditions ---
    def _should_hold(
        self,
        first: models.SingleTouchGesture,
        second: models.SingleTouchGesture,
    ) -> bool:
        """Both gestures must be HOLD and machine must be in down state."""
        if self.down.is_active:
            return first.type is second.type is enums.SingleTouchType.HOLD
        return False

    def _should_update(
        self,
        first: models.SingleTouchGesture,
        second: models.SingleTouchGesture,
    ) -> bool:
        """One or both gestures must be DRAG and not ending the lifecycle."""
        gesture_types = {first.type, second.type}
        is_end = first.type.is_lifecycle_end or second.type.is_lifecycle_end
        return not is_end and enums.SingleTouchType.DRAG in gesture_types

    # --- Action Hooks ---
    def on_touch_down(
        self,
        first: models.SingleTouchGesture,
        second: models.SingleTouchGesture,
    ) -> None:
        """Generate a POINTER DOWN gesture."""
        self._current_gesture = models.MultiTouchGesture(
            type=enums.MultiTouchType.POINTER_DOWN, first=first, second=second
        )

    def on_hold(
        self,
        first: models.SingleTouchGesture,
        second: models.SingleTouchGesture,
    ) -> None:
        """Generate a POINTER HOLD gesture."""
        self._current_gesture = models.MultiTouchGesture(
            type=enums.MultiTouchType.POINTER_HOLD, first=first, second=second
        )

    def on_update(
        self,
        first: models.SingleTouchGesture,
        second: models.SingleTouchGesture,
    ) -> None:
        """Generate one of PAN, ZOOM, ROTATE, or a combination gesture."""
        if self._start_first is None:
            msg = "_start_first is None."
            raise RuntimeError(msg)

        if self._start_second is None:
            msg = "_start_second is None."
            raise RuntimeError(msg)

        if self._start_midpoint is None:
            msg = "_start_midpoint is None."
            raise RuntimeError(msg)

        gesture_type = enums.MultiTouchType.NO_OP
        offset_vector: models.TouchEvent | None = None
        scale_factor = 1.0

        # PAN gesture
        current_midpoint = first.end.midpoint_to(second.end)
        is_dragging = first.type is second.type is enums.SingleTouchType.DRAG
        if is_dragging and self._conf.pan.threshold_is_met(
            self._start_midpoint, current_midpoint
        ):
            dx, dy = self._start_midpoint.vector_to(current_midpoint)
            offset_vector = models.TouchEvent(-1, dx, dy, -1)
            gesture_type |= enums.MultiTouchType.PAN

        # ZOOM gesture
        curr_dist = first.end.distance_to(second.end)
        if self._conf.zoom.threshold_is_met(curr_dist - self._start_distance):
            if not math.isclose(self._start_distance, 0):  # pragma: no branch
                scale_factor = curr_dist / self._start_distance
            gesture_type |= enums.MultiTouchType.ZOOM

        # ROTATE gesture
        current_angle = first.end.degrees_to(second.end)
        angular_diff = geometry.angular_diff(self._start_angle, current_angle)
        if self._conf.rotate.threshold_is_met(abs(angular_diff)):
            gesture_type |= enums.MultiTouchType.ROTATE

        if gesture_type != enums.MultiTouchType.NO_OP:
            self._current_gesture = models.MultiTouchGesture(
                type=gesture_type ^ enums.MultiTouchType.NO_OP,  # remove NO_OP
                first=first,
                second=second,
                offset=offset_vector,
                scale=scale_factor,
                angle=angular_diff,
            )

    def on_release(
        self,
        first: models.SingleTouchGesture,
        second: models.SingleTouchGesture,
    ) -> None:
        """Generate a FAST TAP, ANCHOR TAP, FLICK, or POINTER UP gesture."""
        gesture_types = {first.type, second.type}
        is_hold_or_drag = bool(
            gesture_types
            & {enums.SingleTouchType.HOLD, enums.SingleTouchType.DRAG}
        )
        is_fast_tap = enums.SingleTouchType.FAST_TAP in gesture_types

        # FAST TAP gesture
        if first.type is second.type is enums.SingleTouchType.FAST_TAP:
            self._current_gesture = models.MultiTouchGesture(
                type=enums.MultiTouchType.FAST_TAP, first=first, second=second
            )
        # ANCHOR TAP gesture
        elif is_hold_or_drag and is_fast_tap:
            self._current_gesture = models.MultiTouchGesture(
                type=enums.MultiTouchType.ANCHOR_TAP,
                first=first,
                second=second,
            )
        # FLICK gesture
        elif (
            first.type is second.type is enums.SingleTouchType.SWIPE
            and first.direction == second.direction
        ):
            self._current_gesture = models.MultiTouchGesture(
                type=enums.MultiTouchType.FLICK, first=first, second=second
            )
        # POINTER UP gesture
        elif enums.SingleTouchType.RELEASE in gesture_types:
            self._current_gesture = models.MultiTouchGesture(
                type=enums.MultiTouchType.POINTER_UP,
                first=first,
                second=second,
            )
