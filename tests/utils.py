from pireader.common import enums, models


def new_touch(
    x: int, y: int, timestamp: float, *, id_: int = -1
) -> models.TouchEvent:
    """Create a TouchEvent with default values."""
    return models.TouchEvent(id_, x, y, timestamp)


def new_st_gesture(
    type_: enums.SingleTouchType = enums.SingleTouchType.DOWN,
    *,
    start: tuple[int, int, int, int] | tuple[int, int, int] | None = None,
    end: tuple[int, int, int, int] | tuple[int, int, int] | None = None,
    direction: enums.Direction | None = None,
) -> models.SingleTouchGesture:
    """Generate a SingleTouchGesture with default values."""
    if start is None:
        start = (-1, -1, -1)
    if end is None:
        end = (-1, -1, -1)
    return models.SingleTouchGesture(
        type=type_,
        start=new_touch(*start),
        end=new_touch(*end),
        direction=direction,
    )
