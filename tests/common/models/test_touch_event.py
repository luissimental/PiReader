import math

from tests import utils


class TestTouchEventVectorField:
    """TouchEvent vector field."""

    def test_vector_is_assigned_after_init(self) -> None:
        """Vector field is assigned."""
        point = utils.new_touch(100, 50, -1)

        assert point.vector.x == 100
        assert point.vector.y == 50


class TestTouchEventVectorTo:
    """TouchEvent vector_to."""

    def test_vector_to_success(self) -> None:
        """Returns correct dx, dy."""
        point1 = utils.new_touch(100, 50, -1)
        point2 = utils.new_touch(175, 75, -1)

        dx, dy = point1.vector_to(point2)

        assert dx == 75
        assert dy == 25


class TestTouchEventDistanceTo:
    """TouchEvent distance_to."""

    def test_distance_to_success(self) -> None:
        """Returns correct distance."""
        point1 = utils.new_touch(0, 1, -1)
        point2 = utils.new_touch(1, 0, -1)

        distance = point1.distance_to(point2)

        assert math.isclose(distance, math.sqrt(2))


class TestTouchEventMidpointTo:
    """TouchEvent midpoint_to."""

    def test_midpoint_to_success(self) -> None:
        """Returns correct midpoint."""
        point1 = utils.new_touch(-100, 5, -1)
        point2 = utils.new_touch(120, 25, -1)

        midpoint = point1.midpoint_to(point2)

        assert midpoint.x == 10
        assert midpoint.y == 15


class TestTouchEventDegreesTo:
    """TouchEvent degrees_to."""

    def test_degrees_to_success(self) -> None:
        """Returns correct degrees."""
        point1 = utils.new_touch(-100, 0, -1)
        point2 = utils.new_touch(0, 100, -1)

        degrees = point1.degrees_to(point2)

        assert degrees == 45


class TestTouchEventClockOffsetFrom:
    """TouchEvent clock_offset_from."""

    def test_clock_offset_from_success(self) -> None:
        """Returns correct duration."""
        point1 = utils.new_touch(0, 0, 100)
        point2 = utils.new_touch(0, 0, 155)

        duration = point1.clock_offset_from(point2)

        assert duration == 55
