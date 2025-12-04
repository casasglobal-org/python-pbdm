

from ..abstract.population_objects import FunctionalPopulationObject
from ..age_structure.objects import (
    AgeStructuredFunctionalPopulationObject,
    AgeStructuredCompositePopulationObject,
)
from ..age_structure.helpers import get_age_structured_port_set

#from pbdm.age_structure.age_structure import AgeStructuredObject
#from psymple.build import HIERARCHY_SEPARATOR

"""
class Function(PBDMFunctionalObject):
    Gathers "function", "function_name" from parameters.

    def initialise_object(self, **parameters):
        # self.add_parameters(**parameters)
        function_name = self.get_parameter("function_name", default="function")
        function = self.get_parameter("function")
        self.function_name = function_name
        assignments = [(function_name, function)]
        print(assignments)
        self.add_parameter_assignments(*assignments)
        super().initialise_object()
"""

# X = Function(name="X", k=10, Del=2, named="word")
# print(X.parameters)
# X.initialise_object(function="x**2")

class Function(FunctionalPopulationObject):
    PARSING_DATA = {
        "function": str,
        "output_name": str
    }
    """
    Builds a `FunctionalPortedObject` with output port `output_name` exposing the function `function`.

    Example:
        ```json title=".json format"
        {
            "function": <function(str, required, not searched), required>,
            "output_name": <output_name(str, default = "function", searched>,
        } 
        ```

    Keyword Args: Required parameters
        function (str): string representation of the function to be parsed. Required.

    Keyword Args: Searched parameters 
        output_name (str, optional): name of the port exposing the function. Defaults to "function".
    """
    def __init__(self, function = None, output_name = None, **ported_object_kwargs):
        super().__init__(**ported_object_kwargs)
        self.parse_parameters(function=function, output_name=output_name)

    def build_object(self):
        function = self.get_parameter("function", search_ancestry=False)
        output_name = self.get_parameter("output_name", default="function")
        assignment = (output_name, function)
        self.add_parameter_assignments(assignment)
        super().build_object()


class AgeStructuredFunction(AgeStructuredFunctionalPopulationObject):
    PARSING_DATA = AgeStructuredFunctionalPopulationObject.PARSING_DATA | {
        "function": str,
        "output_name": str,
    }

    def __init__(
        self,
        function: str | None = None,
        output_name: str | None = None,
        age_axis: dict | None = None,
        structured_inputs: dict | None = None,
        **ported_object_kwargs,
    ):

        super().__init__(
            age_axis=age_axis,
            structured_assignments={},
            structured_inputs=structured_inputs,
            **ported_object_kwargs,
        )

        self.parse_parameters(function=function, output_name=output_name)

    def build_object(self):
        axis_name, _ = self.get_age_axis_config()
        assignment_name = self.get_parameter("output_name", default="function")
        function_expr = self.get_parameter("function", search_ancestry=False)

        structured_assignments = {
            assignment_name: {
                "axes": [axis_name],
                "function": function_expr,
            }
        }

        self.parameters.set(
            structured_assignments=structured_assignments,
        )

        super().build_object()


class AgeStructuredIntegral(AgeStructuredFunctionalPopulationObject):
    PARSING_DATA = AgeStructuredFunctionalPopulationObject.PARSING_DATA | {
        "function": str,
        "output_name": str,
        "lower_index": int,
        "upper_index": int,
        "measure": str,
    }

    def __init__(
        self,
        function: str | None = None,
        output_name: str | None = None,
        age_axis: dict | None = None,
        lower_index: int | None = None,
        upper_index: int | None = None,
        measure: str | None = None,
        structured_inputs: dict | None = None,
        **ported_object_kwargs,
    ):

        super().__init__(
            age_axis=age_axis,
            structured_assignments={},
            structured_inputs=structured_inputs,
            **ported_object_kwargs,
        )

        assignment_name = output_name or "integral"
        self.parse_parameters(
            function=function,
            output_name=assignment_name,
            lower_index=lower_index,
            upper_index=upper_index,
            measure=measure,
        )

    def build_object(self):
        axis_name, _ = self.get_age_axis_config()
        function_expr = self.get_parameter("function", search_ancestry=False)
        assignment_name = self.get_parameter("output_name", default="integral")

        try:
            lower_index = self.get_parameter("lower_index", search_ancestry=False)
        except Exception:
            lower_index = None

        try:
            upper_index = self.get_parameter("upper_index", search_ancestry=False)
        except Exception:
            upper_index = None

        try:
            measure = self.get_parameter("measure", search_ancestry=False)
        except Exception:
            measure = None

        combined_measure = measure
        axis_index_variable = self._axis_index_variable(axis_name)

        bounds_conditions = []
        if lower_index is not None:
            bounds_conditions.append(f"{axis_index_variable} >= {lower_index}")
        if upper_index is not None:
            bounds_conditions.append(f"{axis_index_variable} <= {upper_index}")
        if bounds_conditions:
            condition = (
                bounds_conditions[0]
                if len(bounds_conditions) == 1
                else f"And({', '.join(bounds_conditions)})"
            )
            bounds_expr = f"Piecewise((1, {condition}), (0, True))"
            combined_measure = (
                bounds_expr
                if combined_measure is None
                else f"({combined_measure})*({bounds_expr})"
            )

        reducers = {axis_name: {"method": "sum"}}
        if combined_measure is not None:
            reducers[axis_name]["measure"] = combined_measure

        structured_assignments = {
            assignment_name: {
                "axes": [],
                "function": function_expr,
                "reducers": reducers,
            }
        }

        self.parameters.set(
            structured_assignments=structured_assignments,
        )

        super().build_object()

class Functions(AgeStructuredCompositePopulationObject):
    PARSING_DATA = (
        AgeStructuredCompositePopulationObject.PARSING_DATA
        | {"functions": Function}
    )
    def __init__(self, functions = None, **ported_object_kwargs):
        """
        Accepts a dict of functions (from JSON) or a list of Function objects.

        Expected:
            Functions(functions=[Function(), Function(), ...], name="my_functions")
            or
            Functions(functions={"func_1": {}, "func_2": {}}, name="my_functions")

        
        """
        super().__init__(**ported_object_kwargs)
        self.parse_parameters(functions=functions)

    def build_object(self):
        functions = self.get_parameter("functions", {})
        for function_name, function_data in functions.items():
            type = function_data.get("type", "single")
            if type == "single":
                function_class = Function
            elif type == "age_structured":
                function_class = AgeStructuredFunction
            elif type == "age_integral":
                function_class = AgeStructuredIntegral
            else:
                raise ValueError(f"Unknown function type '{type}' for '{function_name}'.")

            function_object = function_class(name=function_name, **function_data)
            self.add_children(function_object)

        super().build_object()

        for function_name, function_object in self.children.items():
            child_structured_outputs, child_unstructured_outputs = get_age_structured_port_set(function_object, "outputs")
            #print("FUNCTION OUTPUTS", function_name, child_structured_outputs, child_unstructured_outputs)
            for output in child_structured_outputs:
                self.add_age_structured_output(function_name)
                function_object.add_age_structured_output(output, connections={f"{self.name}.{function_name}"})
            for output in child_unstructured_outputs:
                self.add_output_ports(function_name)
                function_object.add_output_connections(
                    **{output: f"{self.name}.{function_name}"}
                )
            #output_name = function_object.get_parameter("output_name", default="function")
            #function_name = function_object.name
            #if isinstance(function_object, AgeStructuredFunctionalPopulationObject):
            #    print("ADDING AGE STRUCTURED OUTPUT", function_name, output_name, self.name)
            #    self.add_age_structured_output(function_name)
            #    function_object.add_age_structured_output(output_name, connections={f"{self.name}.{function_name}"})
            #else: 
            #    self.add_output_ports(function_name)
            #    function_object.add_output_connections(
            #        **{output_name: f"{self.name}.{function_name}"})
                
        
        
        

        """
        for child in self.children.values():
            print("CHILD", child.name, child.output_ports)
            if len(child.output_ports) == 1:
                output_name = next(iter(child.output_ports))
                exposed_name = child.name
                self.add_output_ports(exposed_name)
                child.add_output_connections(
                    **{output_name: f"{self.name}.{exposed_name}"}
                )
                print(
                    "CHILD output connection",
                    child.address,
                    output_name,
                    f"{self.name}.{exposed_name}",
                )
            else:
                for output_name in child.output_ports:
                    exposed_name = f"{child.name}"
                    self.add_output_ports(exposed_name)
                    child.add_output_connections(
                        **{output_name: f"{self.name}.{exposed_name}"}
                    )
                    print(
                        "CHILD output connection",
                        child.address,
                        output_name,
                        f"{self.name}.{exposed_name}",
                    )
        """


""" class FunctionsOLD(CompositePopulationObject):
    def __init__(self, *functions: Function, **ported_object_kwargs):
        super().__init__(**ported_object_kwargs)
        self.parameters.set(functions=functions)

    def build_object(self):
        functions = self.get_parameter("functions", {})
        for function_name, function_data in functions.items():
            type = function_data.get("type", "single")
            #output_name = function_data.get("output_name", "function")
            #expose = function_data.get("expose", True)
            if type == "single":
                function_class = Function
        
            function_object = function_class(name=function_name, **function_data)
            self.add_children(function_object)
        
        super().build_object()

            # TODO: Expose """

"""
F = Function(
    name="birth_rate",
    function="3*r",
    output_name="rate",
    inputs={"r": "10", "s": "2"},
)

F.initialise_object()
X = F.generate_ported_object()

print("FUNCTION TEST", X.to_data())
"""


