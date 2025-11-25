from ..abstract.population_objects import VariablePopulationObject
from ..age_structure.objects import (
    AgeStructuredCompositePopulationObject,
    AgeStructuredVariablePopulationObject,
)
from ._structured_ports import _normalise_structured_ports

class ODESystem(VariablePopulationObject):
    PARSING_DATA = {
        "odes": dict
    }
    def __init__(self, odes=None, **ported_object_kwargs):
        super().__init__(**ported_object_kwargs)
        self.parse_parameters(odes=odes)
    
    def build_object(self):
        odes = self.get_parameter("odes", default={}, search_ancestry=False)
        assignments = list(odes.items())
        print(assignments)
        self.add_variable_assignments(*assignments)
        super().build_object()
        self.odes = odes

class DifferentialEquation(VariablePopulationObject):
    PARSING_DATA = {
        "function": str,
        "variable": str,
    }
    """
    Builds a `VariablePortedObject` with variable port `variable` exposing the ODE `function`.

    Example:
        ```json title=".json format"
        {
            "function": <function(str, required, not searched), required>,
            "variable": <variable(str, default = "var", searched>,
        } 
        ```

    Keyword Args: Required parameters
        function (str): string representation of the ODE function to be parsed. Required.

    Keyword Args: Searched parameters 
        variable (str, optional): name of the variable port exposing the ODE. Defaults to "var".
    """
    def __init__(self, function, variable = None, **ported_object_kwargs):
        print("HERE3", ported_object_kwargs)
        super().__init__(**ported_object_kwargs)
        self.parse_parameters(function=function, variable=variable)

    def build_object(self):
        function = self.get_parameter("function", search_ancestry=False)
        variable = self.get_parameter("variable", default="var")
        assignment = (variable, function)
        print(assignment)
        self.add_variable_assignments(assignment)
        super().build_object()


class AgeStructuredDifferentialEquation(AgeStructuredVariablePopulationObject):
    PARSING_DATA = AgeStructuredVariablePopulationObject.PARSING_DATA | {
        "function": str,
        "variable": str,
    }

    def __init__(
        self,
        function: str | None = None,
        variable: str | None = None,
        age_axis: dict | None = None,
        structured_inputs: dict | None = None,
        **ported_object_kwargs,
    ):
        self._raw_structured_inputs = dict(structured_inputs or {})

        super().__init__(
            age_axis=age_axis,
            structured_assignments={},
            **ported_object_kwargs,
        )

        self.parse_parameters(function=function, variable=variable)

    def build_object(self):
        axis_name, _ = self.get_age_axis_config()
        variable_name = self.get_parameter("variable", default="var")
        function_expr = self.get_parameter("function", search_ancestry=False)

        structured_assignments = {
            variable_name: {
                "axes": [axis_name],
                "function": function_expr,
            }
        }

        structured_inputs = _normalise_structured_ports(
            self._raw_structured_inputs,
            axis_name,
        )

        self.parameters.set(
            structured_assignments=structured_assignments,
            structured_inputs=structured_inputs,
        )

        super().build_object()

class DifferentialEquations(AgeStructuredCompositePopulationObject):
    PARSING_DATA = (
        AgeStructuredCompositePopulationObject.PARSING_DATA
        | {"odes": DifferentialEquation}
    )

    def __init__(self, odes=None, **ported_object_kwargs):
        """
        Accepts a dict of odes (from JSON) or a list of DifferentialEquation objects.

        Expected:
            DifferentialEquations(odes=[DifferentialEquation(), DifferentialEquation(), ...], name="my_odes")
            or
            DifferentialEquations(odes={"ode_1": {}, "ode_2": {}}, name="my_odes")

        """
        super().__init__(**ported_object_kwargs)
        print("HERE2", odes)
        self.parse_parameters(odes=odes)

    def build_object(self):
        odes = self.get_parameter("odes", {})
        print("ODES", odes)
        for ode_name, ode_data in odes.items():
            ode_type = ode_data.get("type", "single")
            if ode_type == "single":
                ode_class = DifferentialEquation
            elif ode_type == "age_structured":
                ode_class = AgeStructuredDifferentialEquation
            else:
                raise ValueError(
                    "DifferentialEquations only accepts 'single' or 'age_structured'"
                    f" entries. Received '{ode_type}' for '{ode_name}'."
                )

            ode_kwargs = dict(ode_data)
            ode_kwargs.pop("type", None)
            ode_object = ode_class(name=ode_name, **ode_kwargs)
            self.add_children(ode_object)

        super().build_object()