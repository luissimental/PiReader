"""System-wide data structures that facilitate operation."""

import dataclasses
import math

from pireader.common import enums


@dataclasses.dataclass(frozen=True)
class TouchEvent:
    """The data of a touch event.

    Attributes:
      id:
        The identifier of which finger is making contact.
      x:
        The x-coordinate of the touch.
      y:
        The y-coordinate of the touch.
      timestamp:
        The timestamp of the touch in seconds since epoch.

    """

    id: int
    x: int
    y: int
    timestamp: float

    def vector_to(self, farther_touch: TouchEvent) -> tuple[int, int]:
        """Get the directional x, y offset between two touches."""
        dx = farther_touch.x - self.x
        dy = farther_touch.y - self.y
        return dx, dy

    def distance_to(self, other_touch: TouchEvent) -> float:
        """Get the distance between two touches."""
        return math.dist((self.x, self.y), (other_touch.x, other_touch.y))

    def midpoint_to(self, other_touch: TouchEvent) -> TouchEvent:
        """Get the midpoint vector between two touches."""
        mx = (self.x + other_touch.x) // 2
        my = (self.y + other_touch.y) // 2
        return TouchEvent(-1, mx, my, -1)

    def degrees_to(self, other_touch: TouchEvent) -> float:
        """Get the angle in degrees between two touches."""
        dx, dy = self.vector_to(other_touch)
        rad = math.atan2(dy, dx)
        return math.degrees(rad)

    def clock_offset_from(self, later_touch: TouchEvent) -> float:
        """Get the timestamp difference between two touches."""
        return later_touch.timestamp - self.timestamp

    def __eq__(self, other: object) -> bool:
        """Compare x and y values."""
        if isinstance(other, TouchEvent):
            return self.x == other.x and self.y == other.y
        return NotImplemented  # pragma: no cover

    def __hash__(self) -> int:
        """Hash x and y values."""
        return hash((self.x, self.y))


@dataclasses.dataclass(frozen=True, kw_only=True)
class SingleTouchGesture:
    """The data of a single-touch gesture.

    Attributes:
      type:
        The type of single-touch gesture.
      start:
        The starting point of the gesture.
      end:
        The ending point of the gesture.
      direction:
        The direction of the SWIPE gesture.

    """

    type: enums.SingleTouchType
    start: TouchEvent
    end: TouchEvent

    direction: enums.Direction | None = None


@dataclasses.dataclass(frozen=True, kw_only=True)
class MultiTouchGesture:
    """The data of a multi-touch gesture.

    Attributes:
      type:
        The type of multi-touch gesture.
      first:
        The first finger's single-touch gesture.
      second:
        The second finger's single-touch gesture.
      midpoint:
        The midpoint between the first and second finger gestures.
      direction:
        The direction of the FLICK gesture.
      offset:
        The PAN gesture's midpoint offset from first contact.
      scale:
        The ZOOM gesture's scale factor.
      angle:
        The ROTATE gesture's angular difference from first contact.

    """

    type: enums.MultiTouchType
    first: SingleTouchGesture
    second: SingleTouchGesture
    midpoint: TouchEvent = dataclasses.field(init=False)

    direction: enums.Direction | None = dataclasses.field(init=False)
    offset: TouchEvent | None = None
    scale: float = 1.0
    angle: float = 0.0

    def __post_init__(self) -> None:
        """Assign attributes after init."""
        midpoint = self.first.end.midpoint_to(self.second.end)
        object.__setattr__(self, "midpoint", midpoint)

        if self.type == enums.MultiTouchType.FLICK:
            object.__setattr__(self, "direction", self.first.direction)
