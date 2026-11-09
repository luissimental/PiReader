# pragma: exclude file
"""System-wide enums that support operation."""

import enum


class SingleTouchState(enum.Enum):
    """Identifiers for the states of single-touch gestures."""

    # Form of (value, is_lifecycle_end)
    FAST_TAP = (enum.auto(), True)  # For tap actions with no tap counts
    SLOW_TAP = (enum.auto(), True)  # For double tap, triple tap, etc.
    SWIPE = (enum.auto(), True)
    HOLD = (enum.auto(), False)
    DRAG = (enum.auto(), False)
    DOWN = (enum.auto(), False)
    RELEASE = (enum.auto(), True)

    def __init__(self, value: object, is_lifecycle_end: bool) -> None:  # noqa: FBT001
        self._value_ = value
        self.is_lifecycle_end = is_lifecycle_end


class MultiTouchState(enum.Flag):
    """Bitmask flags tracking combined multi-touch states."""

    NO_OP = enum.auto()  # Internal use only

    # Structural tracking flags
    POINTER_DOWN = enum.auto()  # A secondary finger has made contact
    POINTER_UP = enum.auto()  # A secondary finger has left contact

    # Static multi-touch states
    POINTER_HOLD = enum.auto()  # Both fingers are in the HOLD state

    # Active multi-touch transformation states (can be combined via |)
    PAN = enum.auto()
    ZOOM = enum.auto()
    ROTATE = enum.auto()

    # Misc. multi-touch states
    FAST_TAP = enum.auto()  # For tap actions with no tap counts
    SLOW_TAP = enum.auto()  # For double tap, triple tap, etc.
    ANCHOR_TAP = enum.auto()  # One finger is HOLD/DRAG other is FAST TAP
    FLICK = enum.auto()  # Both fingers swiped in one direction


class Direction(enum.Flag):
    """Flags for general directions."""

    LEFT = enum.auto()
    RIGHT = enum.auto()
    UP = enum.auto()
    DOWN = enum.auto()


class Color(enum.IntEnum):
    """The system's supported colors."""

    BLACK = 0
    DARK_GRAY = 85
    LIGHT_GRAY = 170
    WHITE = 255

    def __repr__(self) -> str:
        """Generate a string representation of the object."""
        return f"{self.__class__.__name__}.{self.name}"
