from pireader.common import geometry


class TestAngularDiff:
    """angular_diff."""

    def test_angular_diff_lower_bound(self) -> None:
        """Returns -180 degrees."""
        result = geometry.angular_diff(-270, -450)

        assert result == -180

    def test_angular_diff_upper_bound(self) -> None:
        """Returns 179 degrees."""
        result = geometry.angular_diff(360, 539)

        assert result == 179
