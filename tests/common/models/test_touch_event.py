import math

from tests import utils


class TestTouchEventVectorTo:
    """TouchEvent vector_to."""

    def test_vector_to_success(self) -> None:
        """Returns correct dx, dy."""
        point1 = utils.new_touch(100, 50, 0)
        point2 = utils.new_touch(175, 75, 0)

        dx, dy = point1.vector_to(point2)

        assert dx == 75
        assert dy == 25


class TestTouchEventDistanceTo:
    """TouchEvent distance_to."""

    def test_distance_to_success(self) -> None:
        """Returns correct distance."""
        point1 = utils.new_touch(0, 1, 0)
        point2 = utils.new_touch(1, 0, 0)

        distance = point1.distance_to(point2)

        assert math.isclose(distance, math.sqrt(2))


class TestTouchEventClockOffsetFrom:
    """TouchEvent clock_offset_from."""

    def test_clock_offset_from_success(self) -> None:
        """Returns correct duration."""
        point1 = utils.new_touch(0, 0, 100)
        point2 = utils.new_touch(0, 0, 155)

        duration = point1.clock_offset_from(point2)

        assert duration == 55


class TestTouchEventEq:
    """TouchEvent __eq__."""

    def test_eq_returns_true(self) -> None:
        """Correctly compares x and y values and returns True."""
        point1 = utils.new_touch(177, 177, 155, id_=1)
        point2 = utils.new_touch(177, 177, 190, id_=2)

        assert (point1 == point2) is True

    def test_eq_returns_false(self) -> None:
        """Correctly compares x and y values and returns False."""
        point1 = utils.new_touch(177, 177, 155, id_=1)
        point2 = utils.new_touch(180, 177, 190, id_=2)

        assert (point1 == point2) is False


class TestTouchEventHash:
    """TouchEvent __hash__."""

    def test_hash_is_the_same_on_equal_points(self) -> None:
        """Hash returns the same value when points are equal."""
        point1 = utils.new_touch(177, 177, 155, id_=1)
        point2 = utils.new_touch(177, 177, 190, id_=2)

        assert point1.__hash__() == point2.__hash__()

    def test_hash_is_different_on_unequal_points(self) -> None:
        """Hash returns different value when points are unequal."""
        point1 = utils.new_touch(177, 177, 155, id_=1)
        point2 = utils.new_touch(180, 177, 190, id_=2)

        assert point1.__hash__() != point2.__hash__()
