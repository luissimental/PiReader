from pireader.common import enums, models


def new_vector2d(x: int, y: int) -> models.Vector2D:
    """Create a Vector2D object."""
    return models.Vector2D(x, y)


def new_touch(
    x: int, y: int, timestamp: float, id_: int = -1
) -> models.TouchEvent:
    """Create a TouchEvent with default values."""
    return models.TouchEvent(id_, x, y, timestamp)


def new_st_gesture(
    state: enums.SingleTouchState = enums.SingleTouchState.DOWN,
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
        state=state,
        start=new_touch(*start),
        end=new_touch(*end),
        direction=direction,
    )


def new_mt_gesture(
    state: enums.MultiTouchState = enums.MultiTouchState.POINTER_DOWN,
    *,
    first_end: tuple[int, int, int, int] | tuple[int, int, int] | None = None,
    second_end: tuple[int, int, int, int] | tuple[int, int, int] | None = None,
) -> models.MultiTouchGesture:
    """Generate a MultiTouchGesture with default values."""
    first = new_st_gesture(end=first_end)
    second = new_st_gesture(end=second_end)
    return models.MultiTouchGesture(state=state, first=first, second=second)
