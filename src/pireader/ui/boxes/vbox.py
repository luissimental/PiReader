"""Widget to arrange content vertically."""

import dataclasses
from typing import override

from pireader.common import models
from pireader.render import widget

AUTO = widget.AUTO


@dataclasses.dataclass(repr=False, slots=True, weakref_slot=True)
class VBox(widget.Widget):
    """A widget that arranges content vertically.

    This widget respects children's explicit heights and automatically
    calculates auto-heights. The initial y position of children is ignored due
    to their positioning during arrangement.

    Widths are stretched to fill the bounds unless explicitly defined. Children
    are positioned at x = 0 unless explicitly defined.

    """

    # --- Init Positional Arguments ---
    name: str = "VBox"

    _: dataclasses.KW_ONLY

    # --- Layout Pass Input Fields ---
    _spacing: int = dataclasses.field(init=False, default=0)

    # --- Layout Pass Properties ---
    @property
    def spacing(self) -> int:
        """The spacing between widgets in pixels."""
        return self._spacing

    @spacing.setter
    def spacing(self, value: int) -> None:
        if value != self._spacing:
            self._spacing = value
            self.invalidate_transform_cache()

    @override
    def _on_measure(
        self, available_width: float, available_height: float
    ) -> models.Size:
        """Measure children vertically."""
        total_height = 0
        auto_count = 0
        for child in self._children:
            if child.init_height is AUTO:
                auto_count += 1
            else:
                total_height += child.init_height

        # Calculate the max height a widget with auto height can have
        num = len(self._children)
        total_spacing = (num - 1) * self._spacing if num > 1 else 0
        max_height = (
            (available_height - total_height - total_spacing) / auto_count
            if auto_count
            else available_height
        )

        # Children with auto height will stretch to fill in the remaining space
        for child in self._children:
            child.measure(available_width, max_height)

        return models.Size(available_width, available_height)

    @override
    def _on_arrange(self, final_w: float, final_h: float) -> None:
        """Stack children sequentially down the layout."""
        current_y = 0.0
        for child in self._children:
            # Assign position and pass layout command downwards
            child.arrange(child.desired_pos.x, current_y)
            current_y += child.desired_size.height + self._spacing
