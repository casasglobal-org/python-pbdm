from ..population_modelling.functions import Functions
from .bdfs import BiodemographicFunction, ScalarFunction
from ..population_modelling.processes import PopulationProcess
from ..population_modelling.odes import DifferentialEquations, DifferentialEquation


class PBDMBasicProcess(PopulationProcess):
    def __init__(
        self, name, rate: BiodemographicFunction, scalars: list[ScalarFunction] = None
    ):
        super().__init__(name=name, rates=Functions(functions=[]))


class PBDMBiodemographicProcess(PopulationProcess):
    def __init__(
        self,
        name,
        variable,
        rate: BiodemographicFunction,
        scalars: list[ScalarFunction] = None,
        **parameters
    ):
        self.rate = rate
        self.scalars = scalars or []
        rate_function = f"{rate.name}*{variable}"
        scalar_functions = "*".join([scalar.name for scalar in scalars])
        super().__init__(
            name=name,
            rates=Functions(
                name="rates",
                functions={
                    "base_rate": {
                        "function": rate_function,
                        "inputs": {variable: f"{name}.{variable}"},
                    }
                }
            ),
            variables=DifferentialEquations(
                name="variables",
                odes={
                    "ode_out": {
                        "function": f"base_rate * {scalar_functions}" if scalar_functions else "base_rate",
                        "variable": variable
                    }
                },
                #odes = DifferentialEquation(name="ode_out", function=f"base_rate * {scalar_functions}", variable=variable)
            ),
            functions=Functions(
                name="functions",
                functions=scalars + [rate]
            ),
            input_ports=[variable],
            **parameters
        )


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
