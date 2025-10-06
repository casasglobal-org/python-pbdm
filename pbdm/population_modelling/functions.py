

from ..abstract.population_objects import FunctionalPopulationObject, CompositePopulationObject

from sympy import parse_expr, solve, symbols

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
    def __init__(self, function, output_name = None, **ported_object_kwargs):
        super().__init__(**ported_object_kwargs)
        self.parse_parameters(function=function, output_name=output_name)

    def build_object(self):
        function = self.get_parameter("function", search_ancestry=False)
        output_name = self.get_parameter("output_name", default="function")
        assignment = (output_name, function)
        print(assignment)
        self.add_parameter_assignments(assignment)
        super().build_object()

class Functions(CompositePopulationObject):
    PARSING_DATA = {
        "functions": Function
    }
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
        print("FUNCTIONS", functions)
        for function_name, function_data in functions.items():
            type = function_data.get("type", "single")
            if type == "single":
                function_class = Function
        
            function_object = function_class(name=function_name, **function_data)
            self.add_children(function_object)

        super().build_object()

        # NOTE: Manual expose for now
        for child in self.children.values():
            print("CHILD", child.name, child.output_ports)
            assert len(child.output_ports) == 1
            self.add_output_ports(child.name)
            output_name = child.get_parameter("output_name")
            child.add_output_connections(**{output_name: f"{self.name}.{child.name}"})
            print("CHILD output connection", child.address, output_name, f"{self.name}.{child.name}")


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


