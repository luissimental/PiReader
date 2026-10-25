# pragma: exclude file
"""System-wide enums that support operation."""

import enum


class SingleTouchType(enum.Enum):
    """Identifier for types of gestures."""

    FAST_TAP = enum.auto()
    SWIPE = enum.auto()
    HOLD = enum.auto()
    DRAG = enum.auto()
    DOWN = enum.auto()
    RELEASE = enum.auto()


class Direction(enum.Flag):
    """Flags for general directions."""

    LEFT = enum.auto()
    RIGHT = enum.auto()
    UP = enum.auto()
    DOWN = enum.auto()
