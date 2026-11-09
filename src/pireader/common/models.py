"""System-wide data structures that facilitate operation."""

import dataclasses
import math
from typing import TYPE_CHECKING

from pireader.common import enums, mixins

if TYPE_CHECKING:
    from collections.abc import Iterator


def _clip(value: float) -> float:
    """Clip the value between 0.0 and 1.0."""
    return max(0.0, min(1.0, value))


@dataclasses.dataclass(frozen=True, slots=True)
class Size:
    """The width and height properties."""

    width: float = 0.0
    height: float = 0.0

    def __iter__(self) -> Iterator[float]:
        """Return an iterator containing the width and height values."""
        return iter((self.width, self.height))


@dataclasses.dataclass(frozen=True, slots=True)
class Vector2D:
    """The stored x and y coordinates."""

    x: float = 0.0
    y: float = 0.0

    def distance_to(self, other_vector: Vector2D) -> float:
        """Get the distance between two Vector2D objects."""
        return math.dist(self, other_vector)

    def __add__(self, other: Vector2D) -> Vector2D:
        """Addition between two Vector2D objects."""
        if isinstance(other, Vector2D):
            return Vector2D(self.x + other.x, self.y + other.y)
        return NotImplemented  # pragma: no cover

    def __sub__(self, other: Vector2D) -> Vector2D:
        """Subtraction between two Vector2D objects."""
        if isinstance(other, Vector2D):
            return Vector2D(self.x - other.x, self.y - other.y)
        return NotImplemented  # pragma: no cover

    def __truediv__(self, other: float) -> Vector2D:
        """Division between a Vector2D object and a float."""
        if isinstance(other, (int, float)):
            return Vector2D(self.x / other, self.y / other)
        return NotImplemented  # pragma: no cover

    def __floordiv__(self, other: float) -> Vector2D:
        """Floor division between a Vector2D object and an float."""
        if isinstance(other, (int, float)):
            return Vector2D(self.x // int(other), self.y // int(other))
        return NotImplemented  # pragma: no cover

    def __iter__(self) -> Iterator[float]:
        """Return an iterator containing the x and y values."""
        return iter((self.x, self.y))


@dataclasses.dataclass(frozen=True, slots=True)
class TouchEvent:
    """The data of a touch event.

    Attributes:
      id:
        The identifier of which finger is making contact.
      vector:
        The x and y coordinates of the touch.
      timestamp:
        The timestamp of the touch in seconds since epoch.

    """

    id: int
    x: dataclasses.InitVar[int]
    y: dataclasses.InitVar[int]
    vector: Vector2D = dataclasses.field(init=False)
    timestamp: float

    def __post_init__(self, x: int, y: int) -> None:
        """Assign attributes after init."""
        object.__setattr__(self, "vector", Vector2D(x, y))

    def vector_to(self, farther_touch: TouchEvent) -> Vector2D:
        """Get the directional x, y offset between two touches."""
        return farther_touch.vector - self.vector

    def distance_to(self, other_touch: TouchEvent) -> float:
        """Get the distance between two touches."""
        return math.dist(self.vector, other_touch.vector)

    def midpoint_to(self, other_touch: TouchEvent) -> Vector2D:
        """Get the midpoint vector between two touches."""
        return (self.vector + other_touch.vector) / 2

    def degrees_to(self, other_touch: TouchEvent) -> float:
        """Get the angle in degrees between two touches."""
        dx, dy = other_touch.vector - self.vector
        rad = math.atan2(dy, dx)
        return math.degrees(rad)

    def clock_offset_from(self, later_touch: TouchEvent) -> float:
        """Get the timestamp difference between two touches."""
        return later_touch.timestamp - self.timestamp


@dataclasses.dataclass(frozen=True, kw_only=True, slots=True)
class SingleTouchGesture:
    """The data of a single-touch gesture.

    Attributes:
      state:
        The state of the single-touch gesture.
      start:
        The starting touch of the gesture.
      end:
        The ending touch of the gesture.
      direction:
        The direction of the SWIPE gesture.
      tap_count:
        The number of taps in the SLOW TAP gesture (double tap, etc.)

    """

    state: enums.SingleTouchState
    start: TouchEvent
    end: TouchEvent

    direction: enums.Direction | None = None
    tap_count: int = 0


@dataclasses.dataclass(frozen=True, kw_only=True, slots=True)
class MultiTouchGesture:
    """The data of a multi-touch gesture.

    Attributes:
      state:
        The state of the multi-touch gesture.
      first:
        The first finger's single-touch gesture.
      second:
        The second finger's single-touch gesture.
      midpoint:
        The midpoint between the first and second finger gestures.
      direction:
        The direction of the FLICK gesture.
      tap_count:
        The number of taps in the SLOW TAP gesture (double tap, etc.)
      offset:
        The PAN gesture's midpoint offset from first contact.
      scale:
        The ZOOM gesture's scale factor.
      angle:
        The ROTATE gesture's angular difference from first contact.

    """

    state: enums.MultiTouchState
    first: SingleTouchGesture
    second: SingleTouchGesture
    midpoint: Vector2D = dataclasses.field(init=False)

    direction: enums.Direction | None = dataclasses.field(init=False)
    tap_count: int = 0
    offset: Vector2D | None = None
    scale: float = 1.0
    angle: float = 0.0

    def __post_init__(self) -> None:
        """Assign attributes after init."""
        midpoint = self.first.end.midpoint_to(self.second.end)
        object.__setattr__(self, "midpoint", midpoint)

        if self.state == enums.MultiTouchState.FLICK:
            object.__setattr__(self, "direction", self.first.direction)


@dataclasses.dataclass(frozen=True, kw_only=True, slots=True, repr=False)
class WidgetStyle(mixins.InitReprMixin):
    """The available styles a widget can have."""

    _repr_dirty_only = True

    background_color: enums.Color | None = None
    background_opacity: float = 1.0
    border_color: enums.Color = enums.Color.BLACK
    border_opacity: float = 1.0
    border_width: int = 0

    def __post_init__(self) -> None:
        """Assign attributes after init."""
        object.__setattr__(
            self, "background_opacity", _clip(self.background_opacity)
        )
        object.__setattr__(self, "border_opacity", _clip(self.border_opacity))

    @property
    def background_values(self) -> tuple[int, int]:
        """The background color and opacity [0 - 255] values."""
        if self.background_color is None:
            return (enums.Color.WHITE, 0)
        return (self.background_color, int(self.background_opacity * 255))

    @property
    def border_values(self) -> tuple[int, float, int]:
        """The border color, opacity [0.0 - 1.0], and width values."""
        return (self.border_color, self.border_opacity, self.border_width)
