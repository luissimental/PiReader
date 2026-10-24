# pragma: exclude file
"""System-wide data structures that facilitate operation."""

import dataclasses


@dataclasses.dataclass
class TouchEvent:
    """Touch coordinates of a single touch event."""

    id: int
    x: int
    y: int
    timestamp: float
