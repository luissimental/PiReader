"""Central handler of processing touch events."""

import queue
from typing import TYPE_CHECKING

from pireader.common import models

if TYPE_CHECKING:
    from pireader.drivers import touch
    from pireader.touch_input import engine, resolver


class TouchHandler:
    """Drive touch data through gesture generation and processing."""

    def __init__(
        self,
        *,
        driver: touch.TouchDriver,
        engine: engine.GestureEngine,
        resolver: resolver.GestureResolver,
    ) -> None:
        self._driver = driver
        self._engine = engine
        self._resolver = resolver
        self._queue = queue.Queue[
            models.SingleTouchGesture | models.MultiTouchGesture
        ]()

        self._driver.on_touch = self._touch_interrupt_handler

    def poll_for_gesture(
        self,
    ) -> models.SingleTouchGesture | models.MultiTouchGesture | None:
        """Return queued gestures through polling."""
        resolved = self._resolver.poll_for_resolved_gestures()
        single_touches, multi_touch = resolved

        for each_touch in single_touches:
            self._queue.put_nowait(each_touch)

        if multi_touch is not None:
            self._queue.put_nowait(multi_touch)

        try:
            return self._queue.get_nowait()
        except queue.Empty:
            return None

    def _touch_interrupt_handler(
        self, touch_events: list[models.TouchEvent]
    ) -> None:
        """Queue gestures generated from touch event processing."""
        gestures = self._engine.process_touch_events(touch_events)
        single_touches, multi_touch = gestures

        self._resolver.resolve_gestures(single_touches, multi_touch)

        for each_touch in single_touches:
            self._queue.put_nowait(each_touch)

        if multi_touch is not None:
            self._queue.put_nowait(multi_touch)
