from __future__ import annotations

from ..abstract.structured_objects import StructuredPopulationObject


class AgeStructuredPopulationMixin:
    AGE_AXIS_DEFAULT = "age"
    PARSING_DATA = {"age_axis": dict}

    def __init__(self, *, age_axis=None, **kwargs):
        super().__init__(**kwargs)
        self.parse_parameters(age_axis=age_axis)

    def _infer_local_age_axis_name(self):
        local_age_axis = self.parameters.get("age_axis")
        if isinstance(local_age_axis, dict) and local_age_axis.get("name"):
            return local_age_axis["name"]

        local_structured_axes = self.parameters.get("structured_axes") or {}
        if self.AGE_AXIS_DEFAULT in local_structured_axes:
            return self.AGE_AXIS_DEFAULT

        if len(local_structured_axes) == 1:
            return next(iter(local_structured_axes))

        return self.AGE_AXIS_DEFAULT

    def _compose_age_axis_configuration(self, axis_name: str) -> dict:
        inherited_cfg = self.get_parameter(
            f"structured_axes.{axis_name}", default={}, search_ancestry=True
        )

        local_structured_axes = self.parameters.get("structured_axes") or {}
        local_structured_cfg = dict(local_structured_axes.get(axis_name, {}))

        local_age_axis = self.parameters.get("age_axis") or {}
        local_age_axis_cfg = (
            {key: value for key, value in local_age_axis.items() if key != "name"}
            if isinstance(local_age_axis, dict)
            else {}
        )

        axis_cfg = {}
        if isinstance(inherited_cfg, dict):
            axis_cfg.update(inherited_cfg)
        axis_cfg.update(local_structured_cfg)
        axis_cfg.update(local_age_axis_cfg)
        return axis_cfg

    def build_object(self):
        inferred_name = self._infer_local_age_axis_name()
        axis_name = self.get_parameter(
            "age_axis.name",
            default=inferred_name,
            search_ancestry=True,
        )

        axis_cfg = self._compose_age_axis_configuration(axis_name)
        axis_cfg_with_name = {"name": axis_name, **axis_cfg}

        updated_structured_axes = dict(self.parameters.get("structured_axes") or {})
        updated_structured_axes[axis_name] = dict(axis_cfg)

        self.parameters.set(
            age_axis=axis_cfg_with_name,
            structured_axes=updated_structured_axes,
        )

        super().build_object()

    def get_age_axis_config(self):
        try:
            age_axis = self.get_parameter("age_axis", default=None, search_ancestry=True)
        except Exception:
            age_axis = None
        if age_axis is None:
            raise ValueError(
                "Age axis is not defined for this object. Provide 'age_axis' or"
                " ensure it exists in structured_axes."
            )
        axis_name = age_axis.get("name", self.AGE_AXIS_DEFAULT)
        axis_cfg = {key: value for key, value in age_axis.items() if key != "name"}
        return axis_name, axis_cfg


class AgeStructuredPopulationObject(
    AgeStructuredPopulationMixin, StructuredPopulationObject
):
    PARSING_DATA = StructuredPopulationObject.PARSING_DATA | {"age_axis": dict}

    def __init__(
        self,
        age_axis: dict | None = None,
        structured_axes: dict | None = None,
        **ported_object_kwargs,
    ):
        super().__init__(
            age_axis=age_axis,
            structured_axes=structured_axes,
            **ported_object_kwargs,
        )


__all__ = [
    "AgeStructuredPopulationMixin",
    "AgeStructuredPopulationObject",
]
