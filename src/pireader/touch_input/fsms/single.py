"""State machine for generating single-touch gestures."""

import statemachine

from pireader import config
from pireader.common import enums, models


class SingleTouchFSM(statemachine.StateChart):
    """State machine for processing TouchEvents into SingleTouchGestures.

    Example:
      Generate a gesture from a TouchEvent::

        point: TouchEvent | None = ...
        machine = SingleTouchFSM()
        gesture = machine.generate_gesture(point)

    """

    # --- States ---
    idle = statemachine.State(initial=True)
    down = statemachine.State()
    holding = statemachine.State()
    dragging = statemachine.State()

    # --- Transitions ---
    touch_down = down.from_(idle)
    hold = holding.from_(down)
    drag = dragging.from_(down, holding, dragging)
    release = idle.from_(down, holding, dragging)

    def __init__(
        self, *, config: config.GestureConfig = config.GESTURE_CONFIG
    ) -> None:
        super().__init__()
        self._conf = config
        self._start_point: models.TouchEvent | None = None
        self._last_point: models.TouchEvent | None = None
        self._current_gesture: models.SingleTouchGesture | None = None

    def generate_gesture(
        self, point: models.TouchEvent | None
    ) -> models.SingleTouchGesture | None:
        """Generate a gesture from a TouchEvent.

        Args:
          point:
            The TouchEvent to be processed. May be None when when the finger
            is released from the screen.

        Returns:
          The gesture after processing. May be None when the current state does
          not detect a valid gesture.

        """
        self._current_gesture = None

        # Trigger release transition if finger lifted off screen.
        if point is None:
            if not self.idle.is_active:
                self.release()
            return self._current_gesture

        # Traverse state machine
        if self.idle.is_active:
            self._start_point = point
            self.touch_down(point)
        elif self.down.is_active:
            if self._should_drag(point):
                self.drag(point)
            elif self._should_hold(point):
                self.hold(point)
        elif (
            self.holding.is_active or self.dragging.is_active
        ) and self._should_drag(point):
            self.drag(point)

        self._last_point = point
        return self._current_gesture

    # --- Conditions ---
    def _should_hold(self, point: models.TouchEvent) -> bool:
        """Must satisfy distance and duration thresholds."""
        if self._start_point is None:
            return False

        distance = self._start_point.distance_to(point)
        duration = self._start_point.clock_offset_from(point)
        return self._conf.hold.threshold_is_met(distance, duration)

    def _should_drag(self, point: models.TouchEvent) -> bool:
        """Must satisfy distance threshold or be a unique dragging point."""
        if self._start_point is None:
            return False

        # If already dragging, only trigger a transition if finger moved.
        if self.dragging.is_active:
            return point != self._last_point

        distance = self._start_point.distance_to(point)
        return self._conf.drag.threshold_is_met(distance)

    # --- Action Hooks ---
    def on_touch_down(self, point: models.TouchEvent) -> None:
        """Generate a DOWN gesture."""
        self._current_gesture = models.SingleTouchGesture(
            type=enums.SingleTouchType.DOWN,
            start=point,
            end=point,
        )

    def on_hold(self, point: models.TouchEvent) -> None:
        """Generate a HOLD gesture."""
        if self._start_point is None:
            msg = "_start_point is None."
            raise RuntimeError(msg)

        self._current_gesture = models.SingleTouchGesture(
            type=enums.SingleTouchType.HOLD,
            start=self._start_point,
            end=point,
        )

    def on_drag(self, point: models.TouchEvent) -> None:
        """Generate a DRAG gesture."""
        if self._start_point is None:
            msg = "_start_point is None."
            raise RuntimeError(msg)

        self._current_gesture = models.SingleTouchGesture(
            type=enums.SingleTouchType.DRAG,
            start=self._start_point,
            end=point,
        )

    def on_release(self) -> None:
        """Generate one of FAST TAP, SWIPE, or RELEASE gestures."""
        if self._start_point is None:
            msg = "_start_point is None."
            raise RuntimeError(msg)

        if self._last_point is None:
            msg = "_last_point is None."
            raise RuntimeError(msg)

        distance = self._start_point.distance_to(self._last_point)
        duration = self._start_point.clock_offset_from(self._last_point)

        # Fast Tap gesture
        if self._conf.fast_tap.threshold_is_met(distance, duration):
            self._current_gesture = models.SingleTouchGesture(
                type=enums.SingleTouchType.FAST_TAP,
                start=self._start_point,
                end=self._last_point,
            )
        # Swipe gesture
        elif self._conf.swipe.threshold_is_met(distance, duration):
            dx, dy = self._start_point.vector_to(self._last_point)
            if abs(dx) > abs(dy):
                dr = enums.Direction.RIGHT if dx > 0 else enums.Direction.LEFT
            else:
                dr = enums.Direction.DOWN if dy > 0 else enums.Direction.UP
            self._current_gesture = models.SingleTouchGesture(
                type=enums.SingleTouchType.SWIPE,
                start=self._start_point,
                end=self._last_point,
                direction=dr,
            )
        # Release gesture
        else:
            self._current_gesture = models.SingleTouchGesture(
                type=enums.SingleTouchType.RELEASE,
                start=self._start_point,
                end=self._last_point,
            )
