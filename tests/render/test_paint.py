from typing import TYPE_CHECKING

import pytest

from pireader.common import enums, models
from pireader.render import paint

if TYPE_CHECKING:
    import pytest_mock


@pytest.fixture
def mock_image(mocker: pytest_mock.MockerFixture) -> pytest_mock.MockType:
    """Mock the PIL.Image module."""
    return mocker.patch("pireader.render.paint.Image")


@pytest.fixture
def mock_image_draw(mocker: pytest_mock.MockerFixture) -> pytest_mock.MockType:
    """Mock the PIL.ImageDraw.ImageDraw module."""
    return mocker.patch("pireader.render.paint.ImageDraw.ImageDraw")


@pytest.fixture
def mock_draw_methods(mocker: pytest_mock.MockerFixture) -> None:
    """Patch the paint draw methods."""
    mocker.patch("pireader.render.paint.rectangle")


class TestPaintNewScreen:
    """paint new_screen."""

    def test_new_screen_with_dimensions(
        self, mock_image: pytest_mock.MockType
    ) -> None:
        """Creates a new image with dimensions."""
        result = paint.new_screen((100, 50))

        mock_image.new.assert_called_once_with("LA", (100, 50), (255, 255))
        assert result is mock_image.new.return_value


class TestPaintResetScreen:
    """paint reset_screen."""

    def test_reset_screen_wipes_image(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Wipes the screen image."""
        mock_screen = mocker.Mock(width=100, height=50)

        paint.reset_screen(mock_screen)

        mock_screen.paste.assert_called_once_with((255, 255), (0, 0, 100, 50))


class TestPaintShowScreen:
    """paint show_screen."""

    def test_show_screen_successfully(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Shows the screen image."""
        mock_screen = mocker.Mock()

        paint.show_screen(mock_screen)

        mock_screen.convert.assert_called_once_with("L")
        mock_screen.convert.return_value.show.assert_called_once()


class TestPaintDrawScreen:
    """paint draw_screen."""

    def test_draw_screen_transforms_and_pastes_layer(
        self,
        mocker: pytest_mock.MockerFixture,
        mock_image: pytest_mock.MockType,
    ) -> None:
        """Transforms the layer and pastes to screen."""
        mock_transform = mocker.Mock()
        mock_layer = mocker.Mock()
        mock_screen = mocker.Mock(size=(100, 50))

        paint.draw_screen(mock_transform, mock_layer, mock_screen)

        mock_layer.transform.assert_called_once_with(
            (100, 50),
            mock_image.Transform.AFFINE,
            mock_transform.data,
            resample=mock_image.Resampling.BILINEAR,
        )
        mock_screen.alpha_composite.assert_called_once_with(
            mock_layer.transform.return_value
        )


@pytest.mark.usefixtures("mock_draw_methods")
class TestPaintGetWidgetImage:
    """paint get_widget_image."""

    def test_get_widget_image_no_style_no_layout(self) -> None:
        """Returns a new blank image."""
        result = paint.get_widget_image((100, 50), None, None)

        assert result.width == 100
        assert result.height == 50
        assert result.getbbox() is None

    def test_get_widget_image_both_layout_and_style(
        self,
        mocker: pytest_mock.MockerFixture,
        mock_image: pytest_mock.MockType,
    ) -> None:
        """Returns a new image with both a style and a layout."""
        style = models.WidgetStyle(
            background_color=enums.Color.WHITE, background_opacity=0.5
        )
        mock_layout = mocker.Mock()

        paint.get_widget_image((100, 50), style, mock_layout)

        mock_image.new.assert_called_once_with(
            "LA", (100, 50), color=(enums.Color.WHITE, 127)
        )
        mock_layout.assert_called_once_with(mock_image.new.return_value)

    def test_get_widget_image_only_layout(
        self,
        mocker: pytest_mock.MockerFixture,
        mock_image: pytest_mock.MockType,
    ) -> None:
        """Returns a new image with only a layout."""
        mock_layout = mocker.Mock()

        paint.get_widget_image((100, 50), None, mock_layout)

        mock_layout.assert_called_once_with(mock_image.new.return_value)

    def test_get_widget_image_only_style(
        self, mock_image: pytest_mock.MockType
    ) -> None:
        """Returns a new image with only a style."""
        style = models.WidgetStyle(
            background_color=enums.Color.WHITE, background_opacity=0.5
        )

        paint.get_widget_image((100, 50), style, None)

        mock_image.new.assert_called_once_with(
            "LA", (100, 50), color=(enums.Color.WHITE, 127)
        )

    def test_get_widget_image_draws_border(
        self,
        mocker: pytest_mock.MockerFixture,
        mock_image: pytest_mock.MockType,
    ) -> None:
        """Draw the widget's border."""
        spy_rectangle = mocker.spy(paint, "rectangle")
        style = models.WidgetStyle(
            border_color=enums.Color.WHITE, border_opacity=0.5, border_width=4
        )

        paint.get_widget_image((100, 50), style, None)

        spy_rectangle.assert_called_once_with(
            mock_image.new.return_value,
            (0, 0),
            (100, 50),
            outline=(enums.Color.WHITE, 0.5, 4),
        )


@pytest.mark.usefixtures("mock_image")
class TestPaintRectangle:
    """paint rectangle."""

    def test_rectangle_draws_no_fill_no_outline(
        self,
        mocker: pytest_mock.MockerFixture,
        mock_image: pytest_mock.MockType,
        mock_image_draw: pytest_mock.MockType,
    ) -> None:
        """Draw rectangle with no fill and no outline."""
        mock_img = mocker.Mock()

        paint.rectangle(mock_img, (10, 5), (100, 50))

        mock_image.new.assert_called_once_with("LA", (100, 50))
        mock_image_draw.assert_called_once_with(mock_image.new.return_value)
        mock_image_draw.return_value.rectangle.assert_called_once_with(
            (0, 0, 99, 49), None, None, 1
        )
        mock_img.alpha_composite.assert_called_once_with(
            mock_image.new.return_value, (10, 5)
        )

    def test_rectangle_draws_only_fill(
        self,
        mocker: pytest_mock.MockerFixture,
        mock_image_draw: pytest_mock.MockType,
    ) -> None:
        """Draw rectangle with fill and no outline."""
        paint.rectangle(mocker.Mock(), (10, 5), (100, 50), fill=(255, 0.5))

        mock_image_draw.return_value.rectangle.assert_called_once_with(
            (0, 0, 99, 49), (255, 127), None, 1
        )

    def test_rectangle_draws_fill_and_outline(
        self,
        mocker: pytest_mock.MockerFixture,
        mock_image_draw: pytest_mock.MockType,
    ) -> None:
        """Draw rectangle with fill and outline."""
        paint.rectangle(
            mocker.Mock(),
            (10, 5),
            (100, 50),
            fill=(255, 0.5),
            outline=(128, 0.5, 4),
        )

        mock_image_draw.return_value.rectangle.assert_called_once_with(
            (0, 0, 99, 49), (255, 127), (128, 127), 4
        )

    def test_rectangle_draws_only_outline(
        self,
        mocker: pytest_mock.MockerFixture,
        mock_image_draw: pytest_mock.MockType,
    ) -> None:
        """Draw rectangle with no fill and outline."""
        paint.rectangle(
            mocker.Mock(), (10, 5), (100, 50), outline=(128, 0.5, 4)
        )

        mock_image_draw.return_value.rectangle.assert_called_once_with(
            (0, 0, 99, 49), None, (128, 127), 4
        )
