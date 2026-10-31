"""Resolver for gesture attributes and timed configurations."""

import dataclasses
import threading
import time
from typing import TypedDict

from pireader import config
from pireader.common import enums, models


class _ActiveSingleTouchState(TypedDict):
    gesture: models.SingleTouchGesture
    tap_count: int


class _ActiveMultiTouchState(TypedDict):
    gesture: models.MultiTouchGesture | None
    tap_count: int


class GestureResolver:
    """Resolve gesture attributes and timed configurations."""

    def __init__(
        self, config: config.GestureConfig = config.GESTURE_CONFIG
    ) -> None:
        self._config = config
        self._active_single_touches: dict[int, _ActiveSingleTouchState] = {}
        self._active_multi_touch: _ActiveMultiTouchState = {
            "gesture": None,
            "tap_count": 1,
        }
        self._lock = threading.Lock()

    def poll_for_resolved_gestures(
        self,
    ) -> tuple[
        list[models.SingleTouchGesture], models.MultiTouchGesture | None
    ]:
        """Emit time-expired gestures through polling.

        Returns:
          A list of SingleTouchGestures and a MultiTouchGesture which may be
          None.

        """
        single_touches: list[models.SingleTouchGesture] = []
        multi_touch: models.MultiTouchGesture | None = None
        now = time.time()

        with self._lock:
            # Resolve time-expired single-touch FAST TAP gestures
            for gesture_id, state_bundle in list(
                self._active_single_touches.items()
            ):
                gesture = state_bundle["gesture"]
                time_elapsed = now - gesture.end.timestamp

                if time_elapsed >= self._config.slow_tap.max_sec:
                    slow_tap = dataclasses.replace(
                        gesture,
                        state=enums.SingleTouchState.SLOW_TAP,
                        tap_count=state_bundle["tap_count"],
                    )
                    single_touches.append(slow_tap)
                    del self._active_single_touches[gesture_id]

            # Resolve time-expired multi-touch FAST TAP gestures
            multi_gesture = self._active_multi_touch["gesture"]
            if multi_gesture is not None:
                latest_timestamp = max(
                    multi_gesture.first.end.timestamp,
                    multi_gesture.second.end.timestamp,
                )
                if now - latest_timestamp >= self._config.slow_tap.max_sec:
                    multi_touch = dataclasses.replace(
                        multi_gesture,
                        state=enums.MultiTouchState.SLOW_TAP,
                        tap_count=self._active_multi_touch["tap_count"],
                    )
                    self._active_multi_touch["gesture"] = None
                    self._active_multi_touch["tap_count"] = 1

        return single_touches, multi_touch

    def resolve_gestures(
        self,
        single_touches: list[models.SingleTouchGesture],
        multi_touch: models.MultiTouchGesture | None,
    ) -> None:
        """Resolve gestures that require further processing."""
        for gesture in single_touches:
            if (  # pragma: no branch
                gesture.state is enums.SingleTouchState.FAST_TAP
            ):
                self._process_single_touch_fast_tap(gesture)

        if (
            multi_touch is not None
            and multi_touch.state == enums.MultiTouchState.FAST_TAP
        ):
            self._process_multi_touch_fast_tap(multi_touch)

    def _process_single_touch_fast_tap(
        self, gesture: models.SingleTouchGesture
    ) -> None:
        """Process single-touch FAST TAP gestures to emit SLOW TAP gestures."""
        default: _ActiveSingleTouchState = {"gesture": gesture, "tap_count": 1}

        with self._lock:
            active_state = self._active_single_touches.setdefault(
                gesture.end.id, default
            )
            if active_state is default:
                return

            active_gesture = active_state["gesture"]
            distance = active_gesture.end.distance_to(gesture.end)
            duration = active_gesture.end.clock_offset_from(gesture.end)

            if self._config.slow_tap.threshold_is_met(distance, duration):
                active_state["tap_count"] += 1
            else:
                active_state["tap_count"] = 1

            active_state["gesture"] = gesture

    def _process_multi_touch_fast_tap(
        self, gesture: models.MultiTouchGesture
    ) -> None:
        """Process multi-touch FAST TAP gestures to emit SLOW TAP gestures."""
        with self._lock:
            active_gesture = self._active_multi_touch["gesture"]
            if (
                active_gesture is not None
                and self._config.slow_tap.threshold_is_met_gestures(
                    active_gesture, gesture
                )
            ):
                self._active_multi_touch["tap_count"] += 1
            else:
                self._active_multi_touch["tap_count"] = 1

            self._active_multi_touch["gesture"] = gesture
