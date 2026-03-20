from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from sympy import parse_expr, symbols

from ..population_modelling.functions import AgeStructuredFunction, Function
from .core.helpers import merge_parameters


BoundsValue = bool | int | float | str | None


@dataclass(slots=True)
class _ParameterSpec:
    value: Any = None
    structured: bool = False


@dataclass(slots=True)
class BiodemographicFunctionSpec:
    name: str
    function: str
    climate_variable: str | None = None
    parameters: dict | None = None
    bound_above: BoundsValue = None
    bound_below: BoundsValue = None
    function_variable: str = "x"
    output_name: str | None = None
    ported_object_kwargs: dict = field(default_factory=dict)

    def _convert_bdf(self) -> str:
        expression = parse_expr(self.function)
        variable = symbols(self.function_variable)
        if variable in expression.free_symbols:
            if not self.climate_variable:
                raise ValueError(
                    f"Independent variable '{self.function_variable}' found in function "
                    f"{self.function} but no climate_variable provided."
                )
            expression = expression.subs(variable, symbols(self.climate_variable))
        
        result = str(expression)
        if self.bound_above is not None:
            result = self._apply_bound(result, self.bound_above, upper=True)
        if self.bound_below is not None:
            result = self._apply_bound(result, self.bound_below, upper=False)
        return result
    
    @staticmethod
    def _apply_bound(expression: str, bound: BoundsValue, *, upper: bool) -> str:
        if bound is False:
            return expression
        if bound is True:
            bound = 1 if upper else 0
        bound_value = str(bound)
        wrapper = "min" if upper else "max"
        return f"{wrapper}({expression}, {bound_value})"

    def to_dict(self) -> dict:
        data = {
            "function": self._convert_bdf(),
        }
        if self.output_name is not None:
            data["output_name"] = self.output_name
        data.update(self.ported_object_kwargs)
        if self.parameters is not None:
            data = merge_parameters(data, "inputs", self.parameters)
        data["type"] = "single"
        return data

    def build(self) -> Function:
        params = self.to_dict()
        return Function(name=self.name, **params)

@dataclass(slots=True)
class AgeStructuredBiodemographicFunctionSpec(BiodemographicFunctionSpec):
    structured_inputs: dict | list | None = None

    def to_dict(self) -> dict:
        data = BiodemographicFunctionSpec.to_dict(self)
        data["type"] = "age_structured"
        if self.structured_inputs is not None:
            if isinstance(self.structured_inputs, list):
                self.structured_inputs = {key: None for key in self.structured_inputs}
            data = merge_parameters(data, "structured_inputs", self.structured_inputs)
        return data

