"""Engine for processing TouchEvents through state machines."""

from typing import TYPE_CHECKING

from pireader.touch_input.fsms import multi, single

if TYPE_CHECKING:
    from pireader.common import models


class GestureEngine:
    """Process TouchEvents into single-touch and multi-touch gestures."""

    def __init__(self) -> None:
        self._single_fsms: dict[int, single.SingleTouchFSM] = {}
        self._multi_fsm = multi.MultiTouchFSM()

    def process_touch_events(
        self, touch_events: list[models.TouchEvent]
    ) -> tuple[
        list[models.SingleTouchGesture], models.MultiTouchGesture | None
    ]:
        """Process TouchEvents into single-touch and multi-touch gestures.

        Args:
          touch_events:
            A list of TouchEvent objects to be processed. May be empty when one
            or more fingers have lifted from the screen.

        Returns:
          A list of SingleTouchGestures and a MultiTouchGesture which may be
          None.

        """
        single_touches: list[models.SingleTouchGesture] = []
        multi_touch: models.MultiTouchGesture | None = None

        single_touches.extend(self._process_lifted_fingers(touch_events))
        single_touches.extend(self._process_each_touch_event(touch_events))

        if len(single_touches) == 2:  # noqa: PLR2004
            first, second = single_touches
            multi_touch = self._multi_fsm.generate_gesture(first, second)

        return single_touches, multi_touch

    def _process_lifted_fingers(
        self, touch_events: list[models.TouchEvent]
    ) -> list[models.SingleTouchGesture]:
        """Generate SingleTouchGestures for fingers that have been lifted."""
        if len(touch_events) >= len(self._single_fsms):
            return []

        generated_gestures: list[models.SingleTouchGesture] = []

        all_event_ids = {event.id for event in touch_events}
        machine_ids = set(self._single_fsms.keys())
        lifted_ids = machine_ids.difference(all_event_ids)

        for event_id in lifted_ids:
            machine = self._single_fsms[event_id]
            gesture = machine.generate_gesture(None)
            if gesture is not None:
                generated_gestures.append(gesture)

        return generated_gestures

    def _process_each_touch_event(
        self, touch_events: list[models.TouchEvent]
    ) -> list[models.SingleTouchGesture]:
        """Generate SingleTouchGestures for each touch event individually."""
        generated_gestures: list[models.SingleTouchGesture] = []

        for event in touch_events:
            machine = self._single_fsms.get(event.id, None)
            if machine is None:
                machine = self._single_fsms[event.id] = single.SingleTouchFSM()

            gesture = machine.generate_gesture(event)
            if gesture is not None:
                generated_gestures.append(gesture)

        return generated_gestures
