from ..population_modelling.processes import PopulationProcess
from ..population_modelling.functions import Functions, Function
from ..population_modelling.odes import DifferentialEquations
from .bdfs import BiodemographicFunction

class PBDMGeneralInteraction(PopulationProcess):
    def __init__(
        self,
        name,
        variable_1,
        variable_2,
        rate_1: Function|BiodemographicFunction|str|dict,
        rate_2: Function|BiodemographicFunction|str|dict,
        **parameters
    ):
        rate_1_object = self._process_rate(rate_1, "rate_1_function")
        rate_2_object = self._process_rate(rate_2, "rate_2_function")
        super().__init__(
            name=name,
            functions=Functions(
                name="functions",
                functions=[rate_1_object, rate_2_object]
            ),
            rates=Functions(
                name="rates",
                functions={
                    "rate_1": {
                        "function": f"{rate_1_object.name}*{variable_1}*{variable_2}",
                    },
                    "rate_2": {
                        "function": f"{rate_2_object.name}*{variable_1}*{variable_2}",
                    }
                },
                input_ports = [variable_1, variable_2],
                inputs = {variable_1: f"{name}.variables.var_1.{variable_1}", variable_2: f"{name}.variables.var_2.{variable_2}"},
            ),
            variables=DifferentialEquations(
                name="variables",
                odes={
                    "var_1": {
                        "function": "rate_1",
                        "variable": variable_1,
                    },
                    "var_2": {
                        "function": "rate_2",
                        "variable": variable_2,
                    }
                },
            ),
            variable_ports=[variable_1, variable_2],
            variable_connections={
                variable_1: {f"{name}.variables.var_1.{variable_1}"},
                variable_2: {f"{name}.variables.var_2.{variable_2}"},
            },
            **parameters
        )

    def _process_rate(self, rate, rate_name):
        """
        Coerce the user's input into a Function object. If it's already a Function, return it.
        """
        if isinstance(rate, Function):
            return rate
        elif isinstance(rate, str):
            return Function(name=rate_name, function=rate)
        elif isinstance(rate, dict):
            type = rate.get("type", "function")
            if type == "function":
                function_class = Function
            elif type == "biodemographic":
                function_class = BiodemographicFunction
            else:
                raise ValueError(f"Unknown function type: {type}")
            return function_class(name=rate_name, **rate)
        else:
            raise ValueError(f"Invalid rate format: {rate}")

class PBDMResponseInteraction(PBDMGeneralInteraction):
    pass