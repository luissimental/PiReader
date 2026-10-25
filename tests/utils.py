from pireader.common import models


def new_touch(
    x: int, y: int, timestamp: float, *, id_: int = -1
) -> models.TouchEvent:
    """Create a TouchEvent with default values."""
    return models.TouchEvent(id_, x, y, timestamp)
