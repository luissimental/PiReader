"""Mixin classes that enhance functionality."""

import inspect
import types
from typing import ClassVar, Literal


class InitReprMixin:
    """A mixin that generates a __repr__ based on __init__ arguments.

    The formatted string matches the schema "ClassName(param1=val1, ...)".

    Attributes:
      _repr_fields:
        The __init__ parameters to include in the string.
      _repr_exclude:
        Specific parameters to strip out of the string.
      _repr_param_map:
        If a parameter name is stored in an attribute with a different name,
        map the parameter name to the stored attribute name here.
      _repr_dirty_only:
        If True, only include keyword arguments whose values differ from their
        specified __init__ defaults.

    """

    _repr_fields: ClassVar[Literal["__all__"] | tuple[str, ...]] = "__all__"
    _repr_exclude: ClassVar[tuple[str, ...]] = ()
    _repr_param_map: ClassVar[frozendict[str, str]] = frozendict()
    _repr_dirty_only: ClassVar[bool] = False

    def __resolve_attr_name(self, param_name: str) -> str | None:
        """Determine where the current value is actually stored."""
        if param_name in self._repr_param_map:
            attr_name = self._repr_param_map[param_name]
            if hasattr(self, attr_name):
                return attr_name
            return None

        base_name = param_name.rstrip("_")
        if hasattr(self, base_name):
            return base_name
        if hasattr(self, f"_{base_name}"):
            return f"_{base_name}"

        return None

    def __repr__(self) -> str:
        """Generate a string representation of the object."""
        try:
            parameters = inspect.signature(self.__init__).parameters
        except ValueError, TypeError:
            parameters = types.MappingProxyType[str, inspect.Parameter]({})

        repr_parts: list[str] = []
        for name, param in parameters.items():
            if name == "self":
                continue  # pragma: no cover
            # Case 1: Handle **kwargs parameter
            if param.kind == inspect.Parameter.VAR_KEYWORD:
                if self._repr_fields != "__all__":
                    repr_parts.extend(
                        f"{attr}={getattr(self, attr)!r}"
                        for attr in self.__dict__
                        if attr in self._repr_fields
                    )
            # Case 2: Handle standard parameters
            elif (
                self._repr_fields == "__all__" or name in self._repr_fields
            ) and name not in self._repr_exclude:
                attr_name = self.__resolve_attr_name(name)
                if attr_name is None:
                    continue

                # Skip if a default exists and matches
                if (
                    self._repr_dirty_only
                    and param.default != inspect.Parameter.empty
                    and getattr(self, attr_name) == param.default
                ):
                    continue

                repr_parts.append(f"{name}={getattr(self, attr_name)!r}")

        resolved_parts = dict.fromkeys(repr_parts)
        return f"{self.__class__.__name__}({', '.join(resolved_parts)})"
