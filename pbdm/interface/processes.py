from ..population_modelling.functions import Functions, Function
from .bdfs import BiodemographicFunction, ScalarFunction
from ..population_modelling.processes import PopulationProcess
from ..population_modelling.odes import DifferentialEquations, DifferentialEquation


class PBDMBasicProcess(PopulationProcess):
    def __init__(
        self, name, rate: BiodemographicFunction, scalars: list[ScalarFunction] = None
    ):
        super().__init__(name=name, rates=Functions(functions=[]))


class PBDMBiodemographicProcess(PopulationProcess):
    """
    TODO: A biodemographic process should be limited to accepting a biodemographic function as its rate.
    I'm assuming then that we will have a general process that can accept any function as its rate.
    It just means that I can automatically attempt to coerce a string input into a bdf, rather than
    a general function, which means e.g. climate variables can be automatically inferred.
    """
    def __init__(
        self,
        name,
        variable,
        rate: BiodemographicFunction,
        scalars: list[ScalarFunction] = None,
        **parameters
    ):
        rate_object = self._process_rate(rate, "base_rate", BiodemographicFunction)
        scalar_objects = [self._process_rate(scalar, f"scalar_{i}", ScalarFunction) for i, scalar in enumerate(scalars)]
        #rate_function = f"{rate.name}*{variable}"
        scalar_functions = "*".join([scalar.name for scalar in scalar_objects])
        super().__init__(
            name=name,
            functions=Functions(
                name="functions",
                functions=scalar_objects + [rate_object],
            ),
            rates=Functions(
                name="rates",
                functions={
                    "rate": {
                        "function": f"base_rate * {scalar_functions} * {variable}" if scalar_functions else f"base_rate * {variable}",
                    }
                },
                input_ports=[variable],
                inputs={variable: f"{name}.variables.ode_out.{variable}"},
            ),
            variables=DifferentialEquations(
                name="variables",
                odes={
                    "ode_out": {
                        "function": "rate",
                        "variable": variable
                    }
                },
                #odes = DifferentialEquation(name="ode_out", function=f"base_rate * {scalar_functions}", variable=variable)
            ),
            variable_ports=[variable],
            variable_connections={variable: {f"{name}.variables.ode_out.{variable}"}},
            **parameters
        )
    
    def _process_rate(self, rate, rate_name, rate_class):
        """
        Coerce the user's input into a Function object. If it's already a Function, return it.
        """
        if isinstance(rate, Function):
            return rate
        elif isinstance(rate, str):
            return rate_class(name=rate_name, form=rate)
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


class Mortality(PBDMBasicProcess):
    pass


"""
What's the plan?

API?

Mortality <- rate, scalars
- biodemographic functions should be stored in a registry, if class is input
    => need knowledge of registry, or population object?
- or I can input the function's address
- or I can input the data object?

"""
