from typing import TYPE_CHECKING

import pytest

from pireader.common import models
from pireader.render import widget

if TYPE_CHECKING:
    import pytest_mock

AUTO = widget.AUTO


@pytest.fixture
def mock_paint(mocker: pytest_mock.MockerFixture) -> pytest_mock.MockType:
    """Mock paint module."""
    return mocker.patch("pireader.render.widget.paint")


class TestWidgetProperties:
    """Widget properties."""

    def test_parent_property_gets_none(self) -> None:
        """Parent property returns None when there is no parent."""
        root = widget.Widget()

        assert root.parent is None

    def test_parent_property_gets_parent(self) -> None:
        """Parent property returns parent."""
        root = widget.Widget()
        child = widget.Widget()
        child._set_parent(root)

        assert child.parent is root

    def test_children_property_returns_copy(self) -> None:
        """Children property returns a copy list."""
        children = [widget.Widget(), widget.Widget(), widget.Widget()]
        root = widget.Widget()
        root._children = children

        assert root.children is not children
        assert root.children == children

    def test_init_x_property_returns_value(self) -> None:
        """Init x property returns value."""
        root = widget.Widget()
        root._init_x = 10

        assert root.init_x == 10

    def test_init_y_property_returns_value(self) -> None:
        """Init y property returns value."""
        root = widget.Widget()
        root._init_y = 10

        assert root.init_y == 10

    def test_init_width_property_returns_value(self) -> None:
        """Init width property returns value."""
        root = widget.Widget()
        root._init_w = 10

        assert root.init_width == 10

    def test_init_height_property_returns_value(self) -> None:
        """Init height property returns value."""
        root = widget.Widget()
        root._init_h = 10

        assert root.init_height == 10

    def test_desired_pos_property_returns_value(self) -> None:
        """Desired pos property returns value."""
        pos = models.Vector2D(10.0, 15.0)
        root = widget.Widget()
        root._desired_pos = pos

        assert root.desired_pos is pos

    def test_desired_size_property_returns_value(self) -> None:
        """Desired size property returns value."""
        size = models.Size(10.0, 15.0)
        root = widget.Widget()
        root._desired_size = size

        assert root.desired_size is size

    def test_layout_pos_property_returns_value(self) -> None:
        """Layout pos property returns value."""
        pos = models.Vector2D(10.0, 15.0)
        root = widget.Widget()
        root._layout_pos = pos

        assert root.layout_pos is pos

    def test_layout_size_property_returns_value(self) -> None:
        """Layout size property returns value."""
        size = models.Size(10.0, 15.0)
        root = widget.Widget()
        root._layout_size = size

        assert root.layout_size is size

    def test_offset_property_returns_value(self) -> None:
        """Offset property returns value."""
        offset = models.Vector2D(10.0, 15.0)
        root = widget.Widget()
        root._offset = offset

        assert root.offset is offset

    def test_offset_x_property_returns_value(self) -> None:
        """Offset x property returns value."""
        offset = models.Vector2D(10.0, 15.0)
        root = widget.Widget()
        root._offset = offset

        assert root.offset_x == 10.0

    def test_offset_x_property_sets_value(self) -> None:
        """Offset x property sets value."""
        root = widget.Widget()

        root.offset_x = 10.0

        assert root._offset.x == 10.0

    def test_offset_y_property_returns_value(self) -> None:
        """Offset y property returns value."""
        offset = models.Vector2D(10.0, 15.0)
        root = widget.Widget()
        root._offset = offset

        assert root.offset_y == 15.0

    def test_offset_y_property_sets_value(self) -> None:
        """Offset y property sets value."""
        root = widget.Widget()

        root.offset_y = 15.0

        assert root._offset.y == 15.0

    def test_pivot_property_returns_value(self) -> None:
        """Pivot property returns value."""
        pivot = models.Vector2D(10.0, 15.0)
        root = widget.Widget()
        root._pivot = pivot

        assert root.pivot is pivot

    def test_pivot_x_property_returns_value(self) -> None:
        """Pivot x property returns value."""
        pivot = models.Vector2D(10.0, 15.0)
        root = widget.Widget()
        root._pivot = pivot

        assert root.pivot_x == 10.0

    def test_pivot_x_property_sets_value(self) -> None:
        """Pivot x property sets value."""
        root = widget.Widget()

        root.pivot_x = 10.0

        assert root._pivot.x == 10.0

    def test_pivot_y_property_returns_value(self) -> None:
        """Pivot y property returns value."""
        pivot = models.Vector2D(10.0, 15.0)
        root = widget.Widget()
        root._pivot = pivot

        assert root.pivot_y == 15.0

    def test_pivot_y_property_sets_value(self) -> None:
        """Pivot y property sets value."""
        root = widget.Widget()

        root.pivot_y = 15.0

        assert root._pivot.y == 15.0

    def test_scale_property_returns_scale_factors(self) -> None:
        """Scale property returns both scale x and y."""
        root = widget.Widget()
        root._scale = models.Vector2D(1.5, 2.5)

        scale_x, scale_y = root.scale

        assert scale_x == 1.5
        assert scale_y == 2.5

    def test_scale_property_sets_both_scale_factors(self) -> None:
        """Scale property sets both scale x and y."""
        root = widget.Widget()
        root.scale = 1.5

        scale_x, scale_y = root._scale

        assert scale_x == 1.5
        assert scale_y == 1.5

    def test_scale_x_property_returns_value(self) -> None:
        """Scale x property returns value."""
        scale = models.Vector2D(10.0, 15.0)
        root = widget.Widget()
        root._scale = scale

        assert root.scale_x == 10.0

    def test_scale_x_property_sets_value(self) -> None:
        """Scale x property sets value."""
        root = widget.Widget()

        root.scale_x = 10.0

        assert root._scale.x == 10.0

    def test_scale_y_property_returns_value(self) -> None:
        """Scale y property returns value."""
        scale = models.Vector2D(10.0, 15.0)
        root = widget.Widget()
        root._scale = scale

        assert root.scale_y == 15.0

    def test_scale_y_property_sets_value(self) -> None:
        """Scale y property sets value."""
        root = widget.Widget()

        root.scale_y = 15.0

        assert root._scale.y == 15.0

    def test_rotation_property_returns_value(self) -> None:
        """Rotation property returns value."""
        root = widget.Widget()
        root._rotation = -45.0

        assert root.rotation == -45.0

    def test_rotation_property_sets_value(self) -> None:
        """Rotation property sets value."""
        root = widget.Widget()

        root.rotation = -45.0

        assert root._rotation == -45.0

    def test_widget_origin_property_returns_origin(self) -> None:
        """Widget origin property returns local top-left in screen coords."""
        root = widget.Widget()
        root._offset = models.Vector2D(10.0, 15.0)

        x, y = root.widget_origin

        assert x == pytest.approx(10.0)
        assert y == pytest.approx(15.0)

    def test_style_property_returns_value(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Style property returns value."""
        mock_style = mocker.Mock()
        root = widget.Widget()
        root._style = mock_style

        assert root.style is mock_style

    def test_style_property_sets_value(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Style property sets value."""
        mock_style = mocker.Mock()
        root = widget.Widget()

        root.style = mock_style

        assert root._style is mock_style

    def test_layout_property_returns_value(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Layout property returns value."""
        mock_layout = mocker.Mock()
        root = widget.Widget()
        root._layout = mock_layout

        assert root.layout is mock_layout

    def test_layout_property_sets_value(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Layout property sets value."""
        mock_layout = mocker.Mock()
        root = widget.Widget()

        root.layout = mock_layout

        assert root._layout is mock_layout


class TestWidgetHierarchy:
    """Widget Hierarchy."""

    def test_add_child_sets_parent(self) -> None:
        """Adding a child sets its parent."""
        root = widget.Widget()
        child = widget.Widget()

        root.add_child(child)

        assert root.parent is None
        assert len(root._children) == 1

        assert child in root._children
        assert child.parent is root
        assert len(child._children) == 0

    def test_add_child_reparents_widget(self) -> None:
        """Adding a child with a parent reparents the widget."""
        root1 = widget.Widget()
        root2 = widget.Widget()
        child = widget.Widget()
        root1._children = [child]
        child._set_parent(root1)

        root2.add_child(child)

        assert root1.parent is None
        assert len(root1._children) == 0

        assert root2.parent is None
        assert len(root2._children) == 1

        assert child in root2._children
        assert child.parent is root2
        assert len(child._children) == 0

    def test_add_child_raises_error_on_self(self) -> None:
        """Attempt to add self as a child."""
        root = widget.Widget()

        with pytest.raises(ValueError, match="own child"):
            root.add_child(root)

        assert root.parent is None
        assert len(root._children) == 0

    def test_remove_child_successfully(self) -> None:
        """Set parent to None and remove from children list."""
        root = widget.Widget()
        child = widget.Widget()
        root._children = [child]
        child._set_parent(root)

        root.remove_child(child)

        assert root.parent is None
        assert len(root._children) == 0

        assert child.parent is None
        assert len(child._children) == 0

    def test_remove_child_raises_error_on_not_a_child(self) -> None:
        """Attempt to remove a widget that is not a child."""
        root1 = widget.Widget()
        root2 = widget.Widget()

        with pytest.raises(ValueError, match="not a child"):
            root1.remove_child(root2)

        assert root1.parent is None
        assert len(root1._children) == 0

        assert root2.parent is None
        assert len(root2._children) == 0


class TestWidgetMeasure:
    """Widget measure."""

    @pytest.mark.parametrize(
        ("init_x", "init_y"),
        [(AUTO, AUTO), (10, AUTO), (AUTO, 5), (10, 5)],
    )
    def test_measure_sets_desired_position(
        self, init_x: int | AUTO, init_y: int | AUTO
    ) -> None:
        """Set x and y to 0.0 if init values are None."""
        root = widget.Widget(x=init_x, y=init_y)

        root.measure(100.0, 100.0)

        assert root._desired_pos.x == 0.0 if init_x is AUTO else init_x
        assert root._desired_pos.y == 0.0 if init_y is AUTO else init_y

    def test_measure_prioritizes_explicit_size(self) -> None:
        """Explicit widget size is preferred."""
        root = widget.Widget(width=100, height=50)

        root.measure(10.0, 20.0)

        assert root._desired_size.width == 100.0
        assert root._desired_size.height == 50.0

    def test_measure_prioritizes_available_size(self) -> None:
        """Available size is preferred when widget size is auto."""
        root = widget.Widget()

        root.measure(10.0, 20.0)

        assert root._desired_size.width == 10.0
        assert root._desired_size.height == 20.0

    def test_measure_prioritizes_parent_layout_size(self) -> None:
        """Parent layout size is preferred when nothing else is defined."""
        root = widget.Widget()
        child = widget.Widget()
        root._children = [child]
        child._set_parent(root)
        root._layout_size = models.Size(100.0, 50.0)

        child.measure()

        assert child._desired_size.width == 100.0
        assert child._desired_size.height == 50.0

    def test_measure_raises_error_on_missing_dimensions(self) -> None:
        """Measure raises error when dimensions are not defined."""
        root = widget.Widget()

        with pytest.raises(ValueError, match="define a width"):
            root.measure(AUTO, 20.0)

        with pytest.raises(ValueError, match="define a height"):
            root.measure(10.0, AUTO)

    def test_measure_sets_children_desired_positions(self) -> None:
        """Child widgets have desired positions set."""
        root = widget.Widget()
        child = widget.Widget(x=10, y=5)
        root._children = [child]
        child._set_parent(root)

        root.measure(100.0, 50.0)

        assert child._desired_pos.x == 10.0
        assert child._desired_pos.y == 5.0

    def test_measure_sets_children_desired_sizes(self) -> None:
        """Child widgets have desired sizes set."""
        root = widget.Widget()
        child = widget.Widget()
        root._children = [child]
        child._set_parent(root)

        root.measure(100.0, 50.0)

        assert child._desired_size.width == 100.0
        assert child._desired_size.height == 50.0


class TestWidgetArrange:
    """Widget arrange."""

    @pytest.mark.parametrize(
        ("final_x", "final_y"),
        [(AUTO, AUTO), (10.0, AUTO), (AUTO, 5.0), (10.0, 5.0)],
    )
    def test_arrange_sets_layout_position(
        self, final_x: float | AUTO, final_y: float | AUTO
    ) -> None:
        """Set layout position to final position if defined."""
        root = widget.Widget()
        root._desired_pos = models.Vector2D(100.0, 50.0)

        root.arrange(final_x, final_y)

        assert root._layout_pos.x == 100.0 if final_x is AUTO else final_x
        assert root._layout_pos.y == 50.0 if final_y is AUTO else final_y

    @pytest.mark.parametrize(
        ("final_w", "final_h"),
        [(AUTO, AUTO), (10.0, AUTO), (AUTO, 5.0), (10.0, 5.0)],
    )
    def test_arrange_sets_layout_size(
        self, final_w: float | AUTO, final_h: float | AUTO
    ) -> None:
        """Set layout size to final size if defined."""
        root = widget.Widget()
        root._desired_size = models.Size(100.0, 50.0)

        root.arrange(final_w=final_w, final_h=final_h)

        assert root._layout_size.width == 100.0 if final_w is AUTO else final_w
        assert root._layout_size.height == 50.0 if final_h is AUTO else final_h

    def test_arrange_sets_children_layout_positions(self) -> None:
        """Child widgets have layout positions set to desired pos."""
        root = widget.Widget()
        child = widget.Widget()
        root._children = [child]
        child._set_parent(root)
        child._desired_pos = models.Vector2D(100.0, 50.0)

        root.arrange()

        assert child._layout_pos.x == 100.0
        assert child._layout_pos.y == 50.0

    def test_arrange_sets_children_layout_sizes(self) -> None:
        """Child widgets have layout sizes set to desired sizes."""
        root = widget.Widget()
        child = widget.Widget()
        root._children = [child]
        child._set_parent(root)
        child._desired_size = models.Size(100.0, 50.0)

        root.arrange()

        assert child._layout_size.width == 100.0
        assert child._layout_size.height == 50.0


class TestWidgetRenderLocal:
    """Widget render_local."""

    def test_render_local_gets_image(
        self,
        mocker: pytest_mock.MockerFixture,
        mock_paint: pytest_mock.MockType,
    ) -> None:
        """Return image on size, style, and layout constraints."""
        mock_style = mocker.Mock()
        mock_layout = mocker.Mock()
        root = widget.Widget()
        root._style = mock_style
        root._layout_size = models.Size(100.0, 50.0)
        root.layout = mock_layout

        result = root.render_local()

        mock_paint.get_widget_image.assert_called_once_with(
            (100.0, 50.0), mock_style, mock_layout
        )
        assert result is mock_paint.get_widget_image.return_value

    @pytest.mark.parametrize(
        ("width", "height"), [(0.0, 0.0), (100.0, 0.0), (0.0, 50.0)]
    )
    def test_render_local_skips_on_size_constraints(
        self,
        mocker: pytest_mock.MockerFixture,
        mock_paint: pytest_mock.MockType,
        width: float,
        height: float,
    ) -> None:
        """Return None when width or height are 0 or less."""
        root = widget.Widget()
        root._style = mocker.Mock()
        root._layout_size = models.Size(width, height)
        root.layout = mocker.Mock()

        result = root.render_local()

        mock_paint.get_widget_image.assert_not_called()
        assert result is None

    def test_render_local_skips_on_style_and_layout_being_none(
        self, mock_paint: pytest_mock.MockType
    ) -> None:
        """Return None when style and layout are None."""
        root = widget.Widget()
        root._layout_size = models.Size(100.0, 50.0)

        result = root.render_local()

        mock_paint.get_widget_image.assert_not_called()
        assert result is None


class TestWidgetRenderGlobal:
    """Widget render_global."""

    def test_render_global_resets_screen(
        self,
        mocker: pytest_mock.MockerFixture,
        mock_paint: pytest_mock.MockType,
    ) -> None:
        """Render global resets screen when desired."""
        mock_screen = mocker.Mock()
        root = widget.Widget()

        root.render_global(mock_screen, reset_screen=True)

        mock_paint.reset_screen.assert_called_once_with(mock_screen)

    def test_render_global_draws_local_image(
        self,
        mocker: pytest_mock.MockerFixture,
        mock_paint: pytest_mock.MockType,
    ) -> None:
        """Render global pastes the image onto the screen."""
        root = widget.Widget()
        mocker.patch.object(root, "render_local")

        root.render_global(mocker.Mock())

        mock_paint.draw_screen.assert_called_once()

    def test_render_global_skips_drawing_on_no_local_image(
        self,
        mocker: pytest_mock.MockerFixture,
        mock_paint: pytest_mock.MockType,
    ) -> None:
        """Render global does not paste on screen when local image is None."""
        root = widget.Widget()
        mocker.patch.object(root, "render_local", return_value=None)

        root.render_global(mocker.Mock())

        mock_paint.draw_screen.assert_not_called()

    def test_render_global_draws_children(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Render global draws children local image."""
        mock_screen = mocker.Mock()
        root = widget.Widget()
        child = widget.Widget()
        root._children = [child]
        child._set_parent(root)
        spy_render_child = mocker.spy(child, "render_global")

        root.render_global(mock_screen)

        spy_render_child.assert_called_once_with(mock_screen)


class TestWidgetGetLocalTransform:
    """Widget get_local_transform."""

    def test_local_identity_transform(self) -> None:
        """No transformations occurred."""
        root = widget.Widget()

        mat = root.get_local_transform()

        assert mat.data == pytest.approx([1, 0, 0, 0, 1, 0])

    def test_local_translation_transform(self) -> None:
        """Layout position and offsets translate the widget."""
        root = widget.Widget()
        root._layout_pos = models.Vector2D(10.0, 20.0)
        root._offset = models.Vector2D(3.0, 4.0)

        mat = root.get_local_transform()

        assert mat.data == pytest.approx([1, 0, 13, 0, 1, 24])

    def test_local_scale_transform(self) -> None:
        """Scale x and y scale the widget."""
        root = widget.Widget()
        root._scale = models.Vector2D(2.0, 4.0)

        mat = root.get_local_transform()

        assert mat.data == pytest.approx([2, 0, 0, 0, 4, 0])

    def test_local_scale_transform_with_pivot(self) -> None:
        """Scale widget at nonzero pivot."""
        root = widget.Widget()
        root._scale = models.Vector2D(2.0, 4.0)
        root._pivot = models.Vector2D(100.0, 200.0)

        mat = root.get_local_transform()
        pivot_x, pivot_y = mat.transform_point(100.0, 200.0)

        assert mat.data == pytest.approx([2, 0, -100, 0, 4, -600])
        assert pivot_x == pytest.approx(100.0)
        assert pivot_y == pytest.approx(200.0)

    def test_local_scale_transform_zero_scale(self) -> None:
        """Scale factors at 0 are changed to a small factor."""
        root = widget.Widget()
        root._scale = models.Vector2D(0.0, 0.0)

        mat = root.get_local_transform()

        mat.inverse()  # Does not raise an error
        assert mat.data == pytest.approx([1e-5, 0, 0, 0, 1e-5, 0])

    def test_local_rotation_transform(self) -> None:
        """The rotation in degrees rotates a widget."""
        root = widget.Widget()
        root._rotation = -90

        mat = root.get_local_transform()

        assert mat.data == pytest.approx([0, -1, 0, 1, 0, 0])


class TestWidgetGetGlobalTransform:
    """Widget get_global_transform."""

    def test_global_returns_local_transform(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """A widget with no parent returns its local transform."""
        root = widget.Widget()
        mock_local = mocker.patch.object(root, "get_local_transform")

        mat = root.get_global_transform()

        assert mat is mock_local.return_value

    def test_global_returns_global_transform(self) -> None:
        """A widget with a parent returns the global transform."""
        root = widget.Widget()
        child = widget.Widget()
        root._children = [child]
        child._set_parent(root)
        root._layout_pos = models.Vector2D(10.0, 20.0)
        root.scale_x = 1.5
        child._layout_pos = models.Vector2D(3.0, 4.0)

        mat = child.get_global_transform()

        assert mat.data == pytest.approx([1.5, 0, 14.5, 0, 1, 24])


class TestWidgetHitTest:
    """Widget hit_test."""

    def test_hit_test_after_translation(self) -> None:
        """Hit test after translation."""
        root = widget.Widget()
        root._layout_pos = models.Vector2D(20.0, 30.0)
        root._layout_size = models.Size(100.0, 50.0)
        root._offset = models.Vector2D(10.0, 15.0)

        assert root.hit_test(40, 55) is True  # local (10, 10)
        assert root.hit_test(130, 55) is False  # local x is outside

    def test_hit_test_after_scaling(self) -> None:
        """Hit test after scaling."""
        root = widget.Widget()
        root._layout_pos = models.Vector2D(20.0, 30.0)
        root._layout_size = models.Size(100.0, 50.0)
        root._scale = models.Vector2D(2.0, 0.5)

        assert root.hit_test(180, 50) is True  # local (80, 40)
        assert root.hit_test(222, 42.5) is False  # local x is outside

    def test_hit_test_after_rotation(self) -> None:
        """Hit test after rotation."""
        root = widget.Widget()
        root._layout_pos = models.Vector2D(20.0, 30.0)
        root._layout_size = models.Size(100.0, 50.0)
        root._rotation = 90

        assert root.hit_test(40, 20) is True  # local (10, 20)
        assert root.hit_test(40, 31) is False  # local (-1, 20) is outside


def test_local_screen_conversion_round_trips() -> None:
    """Conversions between local and screen coordinates are consistent."""
    root = widget.Widget(width=100, height=50)
    root.measure()
    root.arrange(20, 30)
    root._offset = models.Vector2D(15.0, 34.0)
    root._pivot = models.Vector2D(52.0, 0.0)
    root._scale = models.Vector2D(1.0, 0.5)
    root._rotation = -45.0

    screen = root.local_to_screen(10, 12)
    local = root.screen_to_local(screen.x, screen.y)

    assert local.x == pytest.approx(10)
    assert local.y == pytest.approx(12)
