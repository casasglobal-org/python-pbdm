from __future__ import annotations

from ..abstract.structured_objects import StructuredPopulationObject
from ..abstract._structured_ports import _normalise_structured_ports


class AgeStructuredPopulationMixin:
    AGE_AXIS_DEFAULT = "age"
    PARSING_DATA = {"age_axis": dict}

    def __init__(
        self,
        *,
        age_axis=None,
        structured_inputs: dict | None = None,
        structured_outputs: dict | None = None,
        structured_variables: dict | None = None,
        **kwargs,
    ):
        super().__init__(
            structured_inputs=dict(structured_inputs or {}),
            structured_outputs=dict(structured_outputs or {}),
            structured_variables=dict(structured_variables or {}),
            **kwargs,
        )
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

    @staticmethod
    def _normalise_structured_port_map(
        port_mapping: dict | None,
        axis_name: str,
        *,
        multi_connections: bool = False,
    ) -> dict:
        normalised = _normalise_structured_ports(port_mapping, axis_name)
        if not multi_connections:
            return normalised

        for entry in normalised.values():
            if "connections" in entry:
                continue
            connection_value = entry.pop("connection", None)
            if connection_value is None:
                continue
            if isinstance(connection_value, (list, tuple, set)):
                entry["connections"] = list(connection_value)
            else:
                entry["connections"] = [connection_value]

        return normalised

    def _get_age_axis_name(self) -> str:
        try:
            axis_name, _ = self.get_age_axis_config()
        except ValueError:
            axis_name = self._infer_local_age_axis_name()
        return axis_name

    def _filter_age_structured_ports(self, spec: dict | None) -> dict:
        if not spec:
            return {}
        axis_name = self._get_age_axis_name()
        filtered = {}
        for name, entry in spec.items():
            axes = entry.get("axes") or []
            if axis_name in axes:
                filtered[name] = entry
        return filtered

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

        structured_inputs = self._normalise_structured_port_map(
            self.get_structured_inputs_spec(),
            axis_name,
        )

        structured_outputs = self._normalise_structured_port_map(
            self.get_structured_outputs_spec(),
            axis_name,
            multi_connections=True,
        )

        structured_variables = self._normalise_structured_port_map(
            self.get_structured_variables_spec(),
            axis_name,
            multi_connections=True,
        )

        self.parameters.set(
            age_axis=axis_cfg_with_name,
            structured_axes=updated_structured_axes,
        )

        self.set_structured_inputs(structured_inputs)
        self.set_structured_outputs(structured_outputs)
        self.set_structured_variables(structured_variables)

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

    def _ensure_age_axis_in_axes(self, axes: list | tuple | set | None) -> list:
        axis_name, _ = self.get_age_axis_config()
        axes_list = list(axes) if axes is not None else []
        if axis_name not in axes_list:
            axes_list.insert(0, axis_name)
        return axes_list

    def add_age_structured_input(
        self,
        name: str,
        *,
        axes: list | tuple | set | None = None,
        connection: str | None = None,
        **extra,
    ) -> dict:
        axes_with_age = self._ensure_age_axis_in_axes(axes)
        return self.add_structured_input(
            name,
            axes=axes_with_age,
            connection=connection,
            **extra,
        )

    def add_age_structured_output(
        self,
        name: str,
        *,
        axes: list | tuple | set | None = None,
        connections: list | tuple | set | str | None = None,
        **extra,
    ) -> dict:
        axes_with_age = self._ensure_age_axis_in_axes(axes)
        return self.add_structured_output(
            name,
            axes=axes_with_age,
            connections=connections,
            **extra,
        )

    def add_age_structured_variable(
        self,
        name: str,
        *,
        axes: list | tuple | set | None = None,
        connections: list | tuple | set | str | None = None,
        **extra,
    ) -> dict:
        axes_with_age = self._ensure_age_axis_in_axes(axes)
        return self.add_structured_variable(
            name,
            axes=axes_with_age,
            connections=connections,
            **extra,
        )

    def get_age_structured_inputs_spec(self) -> dict:
        return self._filter_age_structured_ports(self.get_structured_inputs_spec())

    def get_age_structured_outputs_spec(self) -> dict:
        return self._filter_age_structured_ports(self.get_structured_outputs_spec())

    def get_age_structured_variables_spec(self) -> dict:
        return self._filter_age_structured_ports(
            self.get_structured_variables_spec()
        )


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
