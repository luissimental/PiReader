import math

from tests import utils


class TestVector2DDistanceTo:
    """Vector2D distance_to."""

    def test_distance_to_vector_success(self) -> None:
        """Returns correct distance."""
        vector1 = utils.new_vector2d(0, 1)
        vector2 = utils.new_vector2d(1, 0)

        distance = vector1.distance_to(vector2)

        assert math.isclose(distance, math.sqrt(2))


class TestVector2DAdd:
    """Vector2D __add__."""

    def test_add_two_vectors_successfully(self) -> None:
        """Returns correct vector."""
        vector1 = utils.new_vector2d(100, 50)
        vector2 = utils.new_vector2d(120, 25)

        result = vector1 + vector2

        assert result.x == 220
        assert result.y == 75


class TestVector2DSub:
    """Vector2D __sub__."""

    def test_sub_two_vectors_successfully(self) -> None:
        """Returns correct vector."""
        vector1 = utils.new_vector2d(100, 50)
        vector2 = utils.new_vector2d(120, 25)

        result = vector2 - vector1

        assert result.x == 20
        assert result.y == -25


class TestVector2DTrueDiv:
    """Vector2D __truediv__."""

    def test_truediv_vector_success(self) -> None:
        """Returns correct vector."""
        vector = utils.new_vector2d(100, 50)

        result = vector / 2

        assert result.x == 50
        assert result.y == 25


class TestVector2DFloorDiv:
    """Vector2D __floordiv__."""

    def test_floordiv_vector_success(self) -> None:
        """Returns correct vector."""
        vector = utils.new_vector2d(100, 50)

        result = vector // 2

        assert result.x == 50
        assert result.y == 25


class TestVector2DIter:
    """Vector2D __iter__."""

    def test_iter_tuple_unpacking_success(self) -> None:
        """Tuple unpacking is successful."""
        vector = utils.new_vector2d(100, 50)

        x, y = vector

        assert x == 100
        assert y == 50
