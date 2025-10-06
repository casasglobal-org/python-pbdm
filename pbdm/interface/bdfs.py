from ..population_modelling.functions import Function
from sympy import parse_expr, symbols

class PBDMFunction(Function):
    def __init__(self, name: str, form: str, climate_variable: str = None, parameters: dict = None, bound_above: float = None, bound_below: float = None):
        function_form = self._process_function(form, climate_variable, bound_above, bound_below)
        inputs = self._process_parameters(parameters)
        super().__init__(name=name, function=function_form, inputs=inputs)

    def _process_parameters(self, parameters: dict):
        if not parameters:
            return {}
        inputs = {}
        for param, data in parameters.items():
            if isinstance(data, dict):
                value = data.get("value", 0)
            elif isinstance(data, (int, float, str)):
                value = data
            else:
                raise ValueError(f"Invalid parameter data type for '{param}': {type(data)}")
            inputs[param] = value
        return inputs

    def _process_function(self, function_form: str, indep_variable: str = None, bound_above: float = None, bound_below: float = None):
        function_form = parse_expr(function_form)
        x = symbols("x")
        if x in function_form.free_symbols:
            if indep_variable:
                function_form = function_form.subs(x, indep_variable)
            else:
                raise ValueError("Independent variable 'x' found in function but no indep_variable provided.")
        function_form = str(function_form)
        if bound_above:
            if bound_above is True:
                bound_above = 1
            if isinstance(bound_above, (int, float)):
                function_form = f"min({function_form}, {bound_above})"
                # TODO: This should be sympy manipulation for min/max
        if bound_below:
            if bound_below is True:
                bound_below = 0
            if isinstance(bound_below, (int, float)):
                function_form = f"max({function_form}, {bound_below})"
        return function_form

class BiodemographicFunction(PBDMFunction):
    pass
    # TODO: form might need to be its own class 

class ScalarFunction(PBDMFunction):
    pass
