from pireader.common import enums, models


class TestWidgetStyleBackgroundValuesProperty:
    """WidgetStyle background_values property."""

    def test_bg_values_getter(self) -> None:
        """Returns background values."""
        style = models.WidgetStyle(
            background_color=enums.Color.BLACK, background_opacity=0.5
        )

        color, opacity = style.background_values

        assert color is enums.Color.BLACK
        assert opacity == 127  # 255 // 2

    def test_bg_values_color_is_none(self) -> None:
        """Returns default values if background color is None."""
        style = models.WidgetStyle(background_color=None)

        color, opacity = style.background_values

        assert color is enums.Color.WHITE
        assert opacity == 0


class TestWidgetStyleBorderValuesProperty:
    """WidgetStyle border_values property."""

    def test_bd_values_getter(self) -> None:
        """Returns border values."""
        style = models.WidgetStyle(
            border_color=enums.Color.DARK_GRAY,
            border_opacity=0.5,
            border_width=4,
        )

        color, opacity, width = style.border_values

        assert color is enums.Color.DARK_GRAY
        assert opacity == 0.5
        assert width == 4
