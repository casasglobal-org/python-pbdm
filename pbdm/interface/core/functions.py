from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from ..core.coerce import coerce_entry
from ...population_modelling.functions import AgeStructuredFunction, Function, Functions

BoundsValue = bool | int | float | str | None


@dataclass(slots=True)
class BiodemographicFunctionSpec:
    name: str
    form: str
    climate_variable: str | None = None
    output_name: str | None = None
    parameters: Mapping[str, Any] | None = None
    inputs: Mapping[str, Any] | None = None
    bound_above: BoundsValue = None
    bound_below: BoundsValue = None
    age_axis: dict | None = None
    ported_object_kwargs: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        data = {}
        data.update(self.ported_object_kwargs)
        data["function"] = self.form
        if self.output_name is not None:
            data["output_name"] = self.output_name
        if self.parameters is not None:
            inputs = data.setdefault("inputs", {})
            inputs.update(self.parameters)
            data["inputs"] = inputs
        return data

    def build(self) -> Function:
        params = self.to_dict()
        return Function(name=self.name, **params)


@dataclass(slots=True)
class FunctionSpec:
    name: str
    function: str
    output_name: str | None = None
    inputs: Mapping[str, Any] | None = None
    extra: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        data = {
            "type": "single",
            "function": self.function,
        }
        if self.output_name is not None:
            data["output_name"] = self.output_name
        if self.inputs is not None:
            data["inputs"] = dict(self.inputs)
        data.update(self.extra)
        return data

    def build(self, **kwargs) -> Function:
        params = self.to_dict()
        params.update(kwargs)
        return Function(name=self.name, **params)


@dataclass(slots=True)
class AgeStructuredFunctionSpec:
    name: str
    function: str
    output_name: str | None = None
    age_axis: dict | None = None
    structured_inputs: Mapping[str, Any] | None = None
    structured_outputs: Mapping[str, Any] | None = None
    structured_variables: Mapping[str, Any] | None = None
    inputs: Mapping[str, Any] | None = None
    extra: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        data = {
            "type": "age_structured",
            "function": self.function,
        }
        if self.output_name is not None:
            data["output_name"] = self.output_name
        if self.age_axis is not None:
            data["age_axis"] = dict(self.age_axis)
        if self.structured_inputs is not None:
            data["structured_inputs"] = dict(self.structured_inputs)
        if self.structured_outputs is not None:
            data["structured_outputs"] = dict(self.structured_outputs)
        if self.structured_variables is not None:
            data["structured_variables"] = dict(self.structured_variables)
        if self.inputs is not None:
            data["inputs"] = dict(self.inputs)
        data.update(self.extra)
        return data

    def build(self, **kwargs) -> AgeStructuredFunction:
        params = self.to_dict()
        params.update(kwargs)
        return AgeStructuredFunction(name=self.name, **params)


@dataclass(slots=True)
class FunctionsSpec:
    name: str
    functions: Mapping[str, Any]
    inputs: Mapping[str, Any] | None = None
    extra: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        functions_payload: dict[str, Any] = {}
        for name, entry in self.functions.items():
            functions_payload[name] = coerce_entry(entry, "FunctionsSpec")

        data = {"functions": functions_payload}
        if self.inputs is not None:
            data["inputs"] = dict(self.inputs)
        data.update(self.extra)
        return data

    def build(self, **kwargs) -> Functions:
        params = self.to_dict()
        params.update(kwargs)
        return Functions(name=self.name, **params)
