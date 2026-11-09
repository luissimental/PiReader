"""Base implementation for handling a UI hierarchy."""

import math
import weakref
from dataclasses import KW_ONLY, InitVar, dataclass, field  # noqa: important[import-modules-not-symbols]
from typing import TYPE_CHECKING

from pireader.common import mixins, models
from pireader.render import matrix, paint

if TYPE_CHECKING:
    from PIL import Image

Vector2D = models.Vector2D
Size = models.Size
WidgetStyle = models.WidgetStyle

AUTO = sentinel("AUTO")


@dataclass(repr=False, slots=True, weakref_slot=True)
class Widget(mixins.InitReprMixin):
    """The base class for handling components in a UI hierarchy.

    Implementation consists of three stages that must be done in the correct
    order to render a widget: Layout Pass, Paint Pass, and Composite Pass.

    * Layout Pass calculates the geometry of a widget based on layout rules
      such as the widget's width and height.
    * Paint Pass uses the widget's style and layout properties to draw pixels.
    * Composite Pass transforms the final image by applying transformations
      such as translation, rotation, and scaling on each widget.

    Step 1: Initialization
    * Initialize a widget with init values and assign children with
      `add_child()`.
    * Note: The root widget has no parent.

    Example:
    >>> from pireader.common.enums import Color
    >>> from pireader.common.models import WidgetStyle
    >>> from pireader.render.widget import Widget
    >>> root_window = Widget("RootWindow")
    >>> main_content = Widget("MainContent", y=10, height=100)  # auto x, width
    >>> main_content.style = WidgetStyle(background_color=Color.DARK_GRAY)
    >>> root_window.add_child(main_content)

    Step 2: Layout Pass
    * Measure the root widget's and its descendants' desired positions and
      sizes depending on the initial position and size fields.
    * Arrange the root widget's and its descendants' layout depending on the
      desired positions and sizes.
    * Note: descendant x, y, width, or height values being AUTO are calculated
      during this stage.

    Example:
    >>> # Root currently has no width or height, so let's assign it here
    >>> root_window.measure(480, 800)
    >>> root_window.arrange()  # Arrange root using default values

    Step 3: Paint Pass
    * Optionally assign the widget's `layout` field to a function that uses
      draw functions from the paint module to customize the widget's appearance
      further.
    * Create a screen image with the same dimensions as the root widget.
    * Traverse the widget tree to draw the root and its descendants on the
      screen.

    Example:
    >>> from pireader.render import paint
    >>> screen_image = paint.new_screen((480, 800))
    >>> root_window.render_global(screen_image)
    >>> # paint.show_screen(screen_image)

    Step 4: Composite Pass
    * Optionally transform the widget using the Composite Pass fields.
    * This stage is best suited for animations or frequent updates to avoid
      constant re-measuring and re-arranging in the Layout Pass stage.
    * Note: Transformations can occur at any time on any widget, but require a
      call to the root's `render_global` with a new screen or a screen reset to
      see results.

    Example:
    >>> main_content.rotation = -45.0  # Rotate by 45 degrees clockwise
    >>> root_window.render_global(screen_image, reset_screen=True)
    >>> # paint.show_screen(screen_image)

    """

    _repr_param_map = frozendict(
        x="init_x", y="init_y", width="init_w", height="init_h"
    )
    _repr_dirty_only = True

    # --- Init Positional Arguments ---
    name: str = "Widget"

    _: KW_ONLY

    # --- Init Keyword Arguments ---
    x: InitVar[int | AUTO] = AUTO
    y: InitVar[int | AUTO] = AUTO
    width: InitVar[int | AUTO] = AUTO
    height: InitVar[int | AUTO] = AUTO

    # --- Widget Hierarchy Fields ---
    _parent_ref: weakref.ReferenceType[Widget] | None = field(init=False)
    _children: list[Widget] = field(init=False, default_factory=list)

    # --- Layout Pass Input Fields ---
    _init_x: float | AUTO = field(init=False)
    _init_y: float | AUTO = field(init=False)
    _init_w: float | AUTO = field(init=False)
    _init_h: float | AUTO = field(init=False)

    # --- Layout Pass Output Fields (Calculated Data) ---
    _desired_pos: Vector2D = field(init=False, default_factory=Vector2D)
    _desired_size: Size = field(init=False, default_factory=Size)
    _layout_pos: Vector2D = field(init=False, default_factory=Vector2D)
    _layout_size: Size = field(init=False, default_factory=Size)

    # --- Composite Pass Input Fields ---
    _offset: Vector2D = field(init=False, default_factory=Vector2D)
    _pivot: Vector2D = field(init=False, default_factory=Vector2D)
    _scale: Vector2D = field(init=False)
    _rotation: float = field(init=False, default=0.0)

    # --- Paint Pass Input Fields ---
    _style: WidgetStyle | None = field(init=False, default=None)
    _layout: paint.AcceptsImage | None = field(init=False, default=None)

    def __post_init__(
        self,
        x: int | AUTO,
        y: int | AUTO,
        width: int | AUTO,
        height: int | AUTO,
    ) -> None:
        """Assign attributes after init."""
        self._init_x = x
        self._init_y = y
        self._init_w = width
        self._init_h = height
        self._parent_ref = None
        self._scale = Vector2D(1.0, 1.0)

    # --- Widget Hierarchy Properties ---
    @property
    def parent(self) -> Widget | None:
        """The parent of this widget."""
        if self._parent_ref is None:
            return None
        return self._parent_ref()

    @property
    def children(self) -> list[Widget]:
        """The copied list of children widgets."""
        return self._children.copy()

    # --- Layout Pass Properties ---
    @property
    def init_x(self) -> float | AUTO:
        """The initial x position of the widget."""
        return self._init_x

    @property
    def init_y(self) -> float | AUTO:
        """The initial y position of the widget."""
        return self._init_y

    @property
    def init_width(self) -> float | AUTO:
        """The initial width of the widget."""
        return self._init_w

    @property
    def init_height(self) -> float | AUTO:
        """The initial height of the widget."""
        return self._init_h

    @property
    def desired_pos(self) -> Vector2D:
        """The measured position of the widget before arrangement."""
        return self._desired_pos

    @property
    def desired_size(self) -> Size:
        """The measured size of the widget before arrangement."""
        return self._desired_size

    @property
    def layout_pos(self) -> Vector2D:
        """The final position of the widget before transformations."""
        return self._layout_pos

    @property
    def layout_size(self) -> Size:
        """The final size of the widget before transformations."""
        return self._layout_size

    # --- Composite Pass Properties ---
    @property
    def offset(self) -> Vector2D:
        """The x and y translation coordinates."""
        return self._offset

    @property
    def offset_x(self) -> float:
        """The x translation coordinate."""
        return self._offset.x

    @offset_x.setter
    def offset_x(self, value: float) -> None:
        self._offset = Vector2D(value, self._offset.y)

    @property
    def offset_y(self) -> float:
        """The y translation coordinate."""
        return self._offset.y

    @offset_y.setter
    def offset_y(self, value: float) -> None:
        self._offset = Vector2D(self._offset.x, value)

    @property
    def pivot(self) -> Vector2D:
        """The x and y pivot coordinates for rotations and scaling."""
        return self._pivot

    @property
    def pivot_x(self) -> float:
        """The x pivot coordinate for rotations and scaling."""
        return self._pivot.x

    @pivot_x.setter
    def pivot_x(self, value: float) -> None:
        self._pivot = Vector2D(value, self._pivot.y)

    @property
    def pivot_y(self) -> float:
        """The y pivot coordinate for rotations and scaling."""
        return self._pivot.y

    @pivot_y.setter
    def pivot_y(self, value: float) -> None:
        self._pivot = Vector2D(self._pivot.x, value)

    @property
    def scale(self) -> Vector2D:
        """The x and y scale factors."""
        return self._scale

    @scale.setter
    def scale(self, value: float) -> None:
        self._scale = Vector2D(value, value)

    @property
    def scale_x(self) -> float:
        """The x scale factor."""
        return self._scale.x

    @scale_x.setter
    def scale_x(self, value: float) -> None:
        self._scale = Vector2D(value, self._scale.y)

    @property
    def scale_y(self) -> float:
        """The y scale factor."""
        return self._scale.y

    @scale_y.setter
    def scale_y(self, value: float) -> None:
        self._scale = Vector2D(self._scale.x, value)

    @property
    def rotation(self) -> float:
        """The angle of the widget in degrees.

        Positive is counterclockwise and negative is clockwise.
        """
        return self._rotation

    @rotation.setter
    def rotation(self, value: float) -> None:
        self._rotation = value

    @property
    def widget_origin(self) -> Vector2D:
        """The origin of the widget after transformations."""
        return self.local_to_screen(0.0, 0.0)

    # --- Paint Pass Properties ---
    @property
    def style(self) -> WidgetStyle | None:
        """The style of the widget."""
        return self._style

    @style.setter
    def style(self, value: WidgetStyle | None) -> None:
        self._style = value

    @property
    def layout(self) -> paint.AcceptsImage | None:
        """The layout of the widget."""
        return self._layout

    @layout.setter
    def layout(self, value: paint.AcceptsImage | None) -> None:
        self._layout = value

    # --- Widget Hierarchy Methods ---
    def _set_parent(self, value: Widget | None, /) -> None:
        """Set this widget's parent."""
        self._parent_ref = None if value is None else weakref.ref(value)

    def add_child(self, child: Widget) -> None:
        """Add a child to this widget and reparent if needed."""
        if child is self:
            msg = f"A widget cannot be its own child: {child}"
            raise ValueError(msg)

        if child.parent is not None:
            child.parent.remove_child(child)

        self._children.append(child)
        child._set_parent(self)

    def remove_child(self, child: Widget) -> None:
        """Remove a child from this widget."""
        if child in self._children:
            self._children.remove(child)
            child._set_parent(None)
        else:
            msg = f"{child} is not a child of {self}"
            raise ValueError(msg)

    # --- Layout Pass: Measure ---
    def measure(
        self,
        available_width: float | AUTO = AUTO,
        available_height: float | AUTO = AUTO,
    ) -> Size:
        """Determine the widget and descendant desired position and sizes.

        Will always respect the initial width and height, then fall back to the
        available size or parent layout size, whichever is defined.

        Args:
          available_width:
            The available width for widgets with auto width. AUTO will fall
            back to the parent's layout width.
          available_height:
            The available height for widgets with auto height. AUTO will fall
            back to the parent's layout height.

        """
        calc_x = 0.0 if self._init_x is AUTO else self._init_x
        calc_y = 0.0 if self._init_y is AUTO else self._init_y

        if self._init_w is not AUTO:
            calc_w = self._init_w
        elif available_width is not AUTO:
            calc_w = available_width
        elif self.parent is not None:
            calc_w = self.parent.layout_size.width
        else:
            msg = f"Widgets with no parent must define a width: {self}"
            raise ValueError(msg)

        if self._init_h is not AUTO:
            calc_h = self._init_h
        elif available_height is not AUTO:
            calc_h = available_height
        elif self.parent is not None:
            calc_h = self.parent.layout_size.height
        else:
            msg = f"Widgets with no parent must define a height: {self}"
            raise ValueError(msg)

        # Delegate child measurement to subclasses by overriding _on_measure
        self._desired_pos = Vector2D(calc_x, calc_y)
        self._desired_size = self._on_measure(calc_w, calc_h)
        return self._desired_size

    def _on_measure(
        self, available_width: float, available_height: float
    ) -> Size:
        """Take up as much space available."""
        for child in self._children:
            child.measure(available_width, available_height)

        return Size(available_width, available_height)

    # --- Layout Pass: Arrange ---
    def arrange(
        self,
        final_x: float | AUTO = AUTO,
        final_y: float | AUTO = AUTO,
        final_w: float | AUTO = AUTO,
        final_h: float | AUTO = AUTO,
    ) -> None:
        """Assign the widget and descendants the final position and dimensions.

        This is the final arrangement before transformations are applied in the
        Composite Pass stage.

        Args:
          final_x:
            The overridden x position. AUTO will use the desired x.
          final_y:
            The overridden y position. AUTO will use the desired y.
          final_w:
            The overridden width. AUTO will use the desired width.
          final_h:
            The overridden height. AUTO will use the desired height.

        """
        final_x = self._desired_pos.x if final_x is AUTO else final_x
        final_y = self._desired_pos.y if final_y is AUTO else final_y
        final_w = self._desired_size.width if final_w is AUTO else final_w
        final_h = self._desired_size.height if final_h is AUTO else final_h

        self._layout_pos = Vector2D(final_x, final_y)
        self._layout_size = Size(final_w, final_h)

        # Delegate child positioning to subclasses by overriding _on_arrange
        self._on_arrange(final_w, final_h)

    def _on_arrange(self, final_w: float, final_h: float) -> None:  # noqa: ARG002
        """Arrange by desired positions and sizes."""
        for child in self._children:
            child.arrange(*child.desired_pos, *child.desired_size)

    # --- Paint Pass: Local Rendering ---
    def render_local(self) -> Image.Image | None:
        """Render this widget's style and layout onto an image."""
        width = int(self._layout_size.width)
        height = int(self._layout_size.height)

        if width <= 0 or height <= 0:
            return None
        if self._style is None and self._layout is None:
            return None

        return paint.get_widget_image(
            (width, height), self._style, self._layout
        )

    # --- Paint Pass: Global Rendering ---
    def render_global(
        self, screen: Image.Image, *, reset_screen: bool = False
    ) -> None:
        """Render this widget and its descendants onto the screen."""
        if reset_screen is True:
            paint.reset_screen(screen)

        widget_image = self.render_local()
        if widget_image is not None:
            inv_mat = self.get_global_transform().inverse()
            paint.draw_screen(inv_mat, widget_image, screen)

        for child in self._children:
            child.render_global(screen)

    # --- Composite Pass: Local Transformations ---
    def get_local_transform(self) -> matrix.AffineMatrix:
        """Get the local transformation matrix."""
        x, y = self._layout_pos
        ox, oy = self._offset
        mat = matrix.AffineMatrix.translation(x + ox, y + oy)

        # Scaling factors being zero makes the matrix non-invertible
        scale_x, scale_y = self._scale
        if math.isclose(scale_x, 0.0, abs_tol=1e-9):
            scale_x = 1e-5
        if math.isclose(scale_y, 0.0, abs_tol=1e-9):
            scale_y = 1e-5

        # Apply transformations if needed
        if (
            not math.isclose(self._rotation, 0.0, abs_tol=1e-9)
            or not math.isclose(scale_x, 1.0, abs_tol=1e-9)
            or not math.isclose(scale_y, 1.0, abs_tol=1e-9)
        ):
            px, py = self._pivot

            pivot = matrix.AffineMatrix.translation(px, py)
            inv_pivot = matrix.AffineMatrix.translation(-px, -py)
            rot = matrix.AffineMatrix.rotation(-self._rotation)
            sc = matrix.AffineMatrix.scaling(scale_x, scale_y)

            local_transform = rot.multiply(sc).multiply(inv_pivot)
            mat = mat.multiply(pivot).multiply(local_transform)

        return mat

    # --- Composite Pass: Global Transformations ---
    def get_global_transform(self) -> matrix.AffineMatrix:
        """Get the global transformation matrix."""
        local = self.get_local_transform()
        if self.parent is not None:
            return self.parent.get_global_transform().multiply(local)
        return local

    # --- Miscellaneous ---
    def local_to_screen(self, local_x: float, local_y: float) -> Vector2D:
        """Convert local coordinates to screen coordinates."""
        global_mat = self.get_global_transform()
        return global_mat.transform_point(local_x, local_y)

    def screen_to_local(self, screen_x: float, screen_y: float) -> Vector2D:
        """Convert screen coordinates to local coordinates."""
        inv_global_mat = self.get_global_transform().inverse()
        return inv_global_mat.transform_point(screen_x, screen_y)

    def hit_test(self, screen_x: float, screen_y: float) -> bool:
        """Determine if the screen coordinates are within widget bounds."""
        local_x, local_y = self.screen_to_local(screen_x, screen_y)
        layout_w, layout_h = self._layout_size
        return 0.0 <= local_x < layout_w and 0.0 <= local_y < layout_h
