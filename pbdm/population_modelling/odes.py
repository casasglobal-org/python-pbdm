from ..abstract.population_objects import VariablePopulationObject, CompositePopulationObject

class ODESystem(VariablePopulationObject):
    PARSING_DATA = {
        "odes": dict
    }
    def __init__(self, odes, **ported_object_kwargs):
        super().__init__(**ported_object_kwargs)
        self.parse_parameters(odes=odes)
    
    def build_object(self):
        odes = self.get_parameter("odes", search_ancestry=False)
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
    def __init__(self, function, variable = None, **ported_object_kwargs):
        super().__init__(**ported_object_kwargs)
        self.parse_parameters(function=function, variable=variable)

    def build_object(self):
        function = self.get_parameter("function", search_ancestry=False)
        variable = self.get_parameter("variable", default="var")
        assignment = (variable, function)
        print(assignment)
        self.add_variable_assignments(assignment)
        super().build_object()

class DifferentialEquations(CompositePopulationObject):
    PARSING_DATA = {
        "odes": DifferentialEquation
    }
    def __init__(self, odes = None, **ported_object_kwargs):
        """
        Accepts a dict of functions (from JSON) or a list of Function objects.

        Expected:
            Functions(functions=[Function(), Function(), ...], name="my_functions")
            or
            Functions(functions={"func_1": {}, "func_2": {}}, name="my_functions")

        
        """
        super().__init__(**ported_object_kwargs)
        self.parse_parameters(odes=odes)

    def build_object(self):
        odes = self.get_parameter("odes", {})
        print("ODES", odes)
        for ode_name, ode_data in odes.items():
            type = ode_data.get("type", "single")
            #output_name = function_data.get("output_name", "function")
            #expose = function_data.get("expose", True)
            if type == "single":
                ode_class = DifferentialEquation

            ode_object = ode_class(name=ode_name, **ode_data)
            self.add_children(ode_object)

        super().build_object()