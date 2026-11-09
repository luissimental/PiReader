"""Functions that facilitate the Paint Pass stage of a widget."""

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from PIL import Image, ImageDraw

if TYPE_CHECKING:
    from pireader.common import models
    from pireader.render import matrix

type AcceptsImage = Callable[[Image.Image], Any]


# --- Screen Functions ---
def new_screen(size: tuple[int, int]) -> Image.Image:
    """Return a new screen image."""
    return Image.new("LA", size, (255, 255))


def reset_screen(screen: Image.Image) -> None:
    """Wipe the screen image."""
    screen.paste((255, 255), (0, 0, screen.width, screen.height))


def show_screen(screen: Image.Image) -> None:
    """Show the screen image."""
    screen.convert("L").show()


def draw_screen(
    transform: matrix.AffineMatrix, layer: Image.Image, screen: Image.Image
) -> None:
    """Transform the layer and paste it on the screen."""
    transformed_layer = layer.transform(
        screen.size,
        Image.Transform.AFFINE,
        transform.data,
        resample=Image.Resampling.BILINEAR,
    )
    screen.alpha_composite(transformed_layer)


# --- Widget Functions ---
def get_widget_image(
    size: tuple[int, int],
    style: models.WidgetStyle | None,
    layout: AcceptsImage | None,
) -> Image.Image:
    """Return an image with the widget's style and layout."""
    if style is None:
        img = Image.new("LA", size)
        if layout is not None:
            layout(img)
        return img

    img = Image.new("LA", size, color=style.background_values)

    if style.border_width > 0:
        rectangle(img, (0, 0), size, outline=style.border_values)

    if layout is not None:
        layout(img)

    return img


# --- Paint Pass Layout Drawing Functions ---
def rectangle(
    img: Image.Image,
    start_pos: tuple[int, int],
    size: tuple[int, int],
    /,
    *,
    fill: tuple[int, float] | None = None,
    outline: tuple[int, float, int] | None = None,
) -> None:
    """Draw a rectangle.

    Note: Opacity values are between 0.0 and 1.0.

    Args:
      img:
        The image object to draw the rectangle on.
      start_pos:
        The starting x and y coordinates.
      size:
        The width and height of the rectangle.
      fill:
        The color and opacity of the rectangle.
      outline:
        The color, opacity, and width of the outline.

    """
    final_outline = None
    outline_width = 1
    if outline is not None:
        color, opacity, outline_width = outline
        final_outline = (color, int(255 * opacity))
    if fill is not None:
        color, opacity = fill
        fill = (color, int(255 * opacity))

    overlay = Image.new("LA", size)
    draw = ImageDraw.ImageDraw(overlay)

    width, height = size
    draw.rectangle(
        (0, 0, width - 1, height - 1), fill, final_outline, outline_width
    )

    img.alpha_composite(overlay, start_pos)
