from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from ..core.coerce import coerce_entry
from ...population_modelling.odes import (
    AgeStructuredDifferentialEquation,
    DifferentialEquation,
    DifferentialEquations,
)


@dataclass(slots=True)
class DifferentialEquationSpec:
    name: str
    function: str
    variable: str | None = None
    inputs: Mapping[str, Any] | None = None
    structured_inputs: Mapping[str, Any] | None = None
    structured_variables: Mapping[str, Any] | None = None
    extra: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        data = {
            "type": "single",
            "function": self.function,
        }
        if self.variable is not None:
            data["variable"] = self.variable
        if self.inputs is not None:
            data["inputs"] = dict(self.inputs)
        if self.structured_inputs is not None:
            data["structured_inputs"] = dict(self.structured_inputs)
        if self.structured_variables is not None:
            data["structured_variables"] = dict(self.structured_variables)
        data.update(self.extra)
        return data

    def build(self, **kwargs) -> DifferentialEquation:
        params = self.to_dict()
        params.update(kwargs)
        return DifferentialEquation(name=self.name, **params)


@dataclass(slots=True)
class AgeStructuredDifferentialEquationSpec:
    name: str
    function: str
    variable: str | None = None
    age_axis: dict | None = None
    structured_inputs: Mapping[str, Any] | None = None
    structured_variables: Mapping[str, Any] | None = None
    inputs: Mapping[str, Any] | None = None
    extra: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        data = {
            "type": "age_structured",
            "function": self.function,
        }
        if self.variable is not None:
            data["variable"] = self.variable
        if self.age_axis is not None:
            data["age_axis"] = dict(self.age_axis)
        if self.inputs is not None:
            data["inputs"] = dict(self.inputs)
        if self.structured_inputs is not None:
            data["structured_inputs"] = dict(self.structured_inputs)
        if self.structured_variables is not None:
            data["structured_variables"] = dict(self.structured_variables)
        data.update(self.extra)
        return data

    def build(self, **kwargs) -> AgeStructuredDifferentialEquation:
        params = self.to_dict()
        params.update(kwargs)
        return AgeStructuredDifferentialEquation(name=self.name, **params)


@dataclass(slots=True)
class DifferentialEquationsSpec:
    name: str
    odes: Mapping[str, Any]
    inputs: Mapping[str, Any] | None = None
    extra: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        odes_payload: dict[str, Any] = {}
        for name, entry in self.odes.items():
            odes_payload[name] = coerce_entry(entry, "DifferentialEquationsSpec")

        data = {"odes": odes_payload}
        if self.inputs is not None:
            data["inputs"] = dict(self.inputs)
        data.update(self.extra)
        return data

    def build(self, **kwargs) -> DifferentialEquations:
        params = self.to_dict()
        params.update(kwargs)
        return DifferentialEquations(name=self.name, **params)
