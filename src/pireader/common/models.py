"""System-wide data structures that facilitate operation."""

import dataclasses
import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
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
        The type of gesture.
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
