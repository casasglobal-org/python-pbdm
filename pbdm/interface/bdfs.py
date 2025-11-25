from ..population_modelling.functions import Function
from sympy import parse_expr, symbols


class PBDMFunctionNew(Function):
    PARSING_DATA = {
        "form": str,
        "climate_variable": str,
        "parameters": dict,
        "bound_above": (bool, int, float),
        "bound_below": (bool, int, float),
    }

    def __init__(
        self,
        form: str,
        climate_variable: str = "x",
        parameters: dict = {},
        bound_above: float = False,
        bound_below: float = False,
        **ported_object_kwargs,
    ):
        super().__init__(**ported_object_kwargs)
        self.parse_parameters(
            form=form,
            climate_variable=climate_variable,
            parameters=parameters,
            bound_above=bound_above,
            bound_below=bound_below,
        )

    def build_object(self):
        form = self.get_parameter("form", search_ancestry=False)
        climate_variable = self.get_parameter(
            "climate_variable", default=None, search_ancestry=False
        )
        parameters = self.get_parameter("parameters", default={}, search_ancestry=False)
        bound_above = self.get_parameter(
            "bound_above", default=False, search_ancestry=False
        )
        bound_below = self.get_parameter(
            "bound_below", default=False, search_ancestry=False
        )
        function_form = self._process_function(
            form, climate_variable, bound_above, bound_below
        )
        inputs = self._process_parameters(parameters)
        self.add_input_connections(**inputs)
        self.parameters.set(
            function=function_form,
        )
        super().build_object()

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
                raise ValueError(
                    f"Invalid parameter data type for '{param}': {type(data)}"
                )
            inputs[param] = value
        return inputs

    def _process_function(
        self,
        function_form: str,
        indep_variable: str = None,
        bound_above: float = None,
        bound_below: float = None,
    ):
        function_form = parse_expr(function_form)
        print(
            "PROCESSING FUNCTION",
            function_form,
            indep_variable,
            bound_above,
            bound_below,
        )
        x = symbols("x")
        if x in function_form.free_symbols:
            if indep_variable:
                function_form = function_form.subs(x, indep_variable)
            else:
                raise ValueError(
                    "Independent variable 'x' found in function but no indep_variable provided."
                )
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


class PBDMFunction(Function):
    def __init__(
        self,
        name: str,
        form: str,
        climate_variable: str = None,
        parameters: dict = None,
        bound_above: float = None,
        bound_below: float = None,
    ):
        function_form = self._process_function(
            form, climate_variable, bound_above, bound_below
        )
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
                raise ValueError(
                    f"Invalid parameter data type for '{param}': {type(data)}"
                )
            inputs[param] = value
        return inputs

    def _process_function(
        self,
        function_form: str,
        indep_variable: str = None,
        bound_above: float = None,
        bound_below: float = None,
    ):
        function_form = parse_expr(function_form)
        x = symbols("x")
        if x in function_form.free_symbols:
            if indep_variable:
                function_form = function_form.subs(x, indep_variable)
            else:
                raise ValueError(
                    "Independent variable 'x' found in function but no indep_variable provided."
                )
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
