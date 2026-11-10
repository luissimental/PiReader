import pytest

from pireader.render import widget
from pireader.ui.boxes import vbox


class TestVBoxProperties:
    """VBox properties."""

    def test_spacing_gets_value(self) -> None:
        """Spacing property gets value."""
        root = vbox.VBox()
        root._spacing = 20

        assert root.spacing == 20

    def test_spacing_sets_value(self) -> None:
        """Spacing property sets value."""
        root = vbox.VBox()

        root.spacing = 20

        assert root._spacing == 20

    @pytest.mark.parametrize(
        ("attribute", "value", "changes_transform"),
        [("spacing", 1, True), ("spacing", 0, False)],
    )
    def test_properties_invalidate_matrix_caches(
        self, attribute: str, value: int, changes_transform: bool
    ) -> None:
        """Spacing property invalidates matrix cache."""
        root = vbox.VBox()

        root_local = root.get_local_transform()
        root_global = root.get_global_transform()

        setattr(root, attribute, value)

        if changes_transform:
            assert root._local_matrix is None
            assert root._global_matrix is None
        else:
            assert root._local_matrix is root_local
            assert root._global_matrix is root_global


class TestVBoxOnMeasure:
    """VBox _on_measure."""

    def test_measure_no_auto_heights(self) -> None:
        """All children are not auto height."""
        root = vbox.VBox(width=50, height=300)
        root._spacing = 3
        top = widget.Widget(height=10)
        middle = widget.Widget(height=20)
        bottom = widget.Widget(height=30)
        root._children = [top, middle, bottom]
        top._set_parent(root)
        middle._set_parent(root)
        bottom._set_parent(root)

        root.measure()

        assert top._desired_size.height == pytest.approx(10)
        assert middle._desired_size.height == pytest.approx(20)
        assert bottom._desired_size.height == pytest.approx(30)

    def test_measure_all_auto_heights(self) -> None:
        """All children are auto height."""
        root = vbox.VBox(width=50, height=300)
        root._spacing = 3
        top = widget.Widget()
        middle = widget.Widget()
        bottom = widget.Widget()
        root._children = [top, middle, bottom]
        top._set_parent(root)
        middle._set_parent(root)
        bottom._set_parent(root)

        root.measure()
        # 300 - 3 - 3 = 294 / 3 = 98
        assert top._desired_size.height == pytest.approx(98)
        assert middle._desired_size.height == pytest.approx(98)
        assert bottom._desired_size.height == pytest.approx(98)

    def test_measure_top_is_auto_height(self) -> None:
        """Top child is auto height."""
        root = vbox.VBox(width=50, height=300)
        root._spacing = 3
        top = widget.Widget()
        middle = widget.Widget(height=10)
        bottom = widget.Widget(height=20)
        root._children = [top, middle, bottom]
        top._set_parent(root)
        middle._set_parent(root)
        bottom._set_parent(root)

        root.measure()
        # 10 + 20 + 3 = 33 ; 300 - 33 = 267 - 3 = 264
        assert top._desired_size.height == pytest.approx(264)
        assert middle._desired_size.height == pytest.approx(10)
        assert bottom._desired_size.height == pytest.approx(20)

    def test_measure_middle_is_auto_height(self) -> None:
        """Middle child is auto height."""
        root = vbox.VBox(width=50, height=300)
        root._spacing = 3
        top = widget.Widget(height=10)
        middle = widget.Widget()
        bottom = widget.Widget(height=20)
        root._children = [top, middle, bottom]
        top._set_parent(root)
        middle._set_parent(root)
        bottom._set_parent(root)

        root.measure()

        assert top._desired_size.height == pytest.approx(10)
        assert middle._desired_size.height == pytest.approx(264)
        assert bottom._desired_size.height == pytest.approx(20)

    def test_measure_bottom_is_auto_height(self) -> None:
        """Bottom child is auto height."""
        root = vbox.VBox(width=50, height=300)
        root._spacing = 3
        top = widget.Widget(height=10)
        middle = widget.Widget(height=20)
        bottom = widget.Widget()
        root._children = [top, middle, bottom]
        top._set_parent(root)
        middle._set_parent(root)
        bottom._set_parent(root)

        root.measure()

        assert top._desired_size.height == pytest.approx(10)
        assert middle._desired_size.height == pytest.approx(20)
        assert bottom._desired_size.height == pytest.approx(264)


class TestVBoxOnArrange:
    """VBox _on_arrange."""

    def test_arrange_stacks_children(self) -> None:
        """Stack children vertically."""
        """Bottom child is auto height."""
        root = vbox.VBox(width=50, height=300)
        root._spacing = 3
        top = widget.Widget(height=10)
        middle = widget.Widget(height=10)
        bottom = widget.Widget(height=10)
        root._children = [top, middle, bottom]
        top._set_parent(root)
        middle._set_parent(root)
        bottom._set_parent(root)

        root.measure()
        root.arrange()

        assert top._layout_pos.y == pytest.approx(0)
        assert middle._layout_pos.y == pytest.approx(13)
        assert bottom._layout_pos.y == pytest.approx(26)

    def test_arrange_stretches_single_child(self) -> None:
        """Child is stretched to fill bounds."""
        root = vbox.VBox(width=50, height=300)
        child = widget.Widget()
        root._children = [child]
        child._set_parent(root)

        root.measure()
        root.arrange()

        assert child._layout_size.width == pytest.approx(50)
        assert child._layout_size.height == pytest.approx(300)

    def test_arrange_respects_init_x(self) -> None:
        """Init x is respected."""
        root = vbox.VBox(width=50, height=300)
        child = widget.Widget(x=10)
        root._children = [child]
        child._set_parent(root)

        root.measure()
        root.arrange()

        assert child._layout_pos.x == pytest.approx(10)

    def test_arrange_respects_init_width(self) -> None:
        """Init width is respected."""
        root = vbox.VBox(width=50, height=300)
        child = widget.Widget(width=10)
        root._children = [child]
        child._set_parent(root)

        root.measure()
        root.arrange()

        assert child._layout_size.width == pytest.approx(10)

    def test_arrange_respects_init_height(self) -> None:
        """Init y is respected."""
        root = vbox.VBox(width=50, height=300)
        child = widget.Widget(height=10)
        root._children = [child]
        child._set_parent(root)

        root.measure()
        root.arrange()

        assert child._layout_size.height == pytest.approx(10)

    def test_arrange_ignores_init_y(self) -> None:
        """Init y is ignored."""
        root = vbox.VBox(width=50, height=300)
        child = widget.Widget(y=10)
        root._children = [child]
        child._set_parent(root)

        root.measure()
        root.arrange()

        assert child._layout_pos.y == pytest.approx(0)
