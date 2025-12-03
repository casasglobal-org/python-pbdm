from ...odes import ODESystem
from ....age_structure.objects import AgeStructuredCompositePopulationObject
from ...functions import AgeStructuredFunction

class DistributedDelayODEs(ODESystem):
    PARSING_DATA = ODESystem.PARSING_DATA | {
        "rate_name": str,
        "variable_name": str,
    }

    def __init__(self, rate_name=None, variable=None, **ported_object_kwargs):
        super().__init__(**ported_object_kwargs)
        self.parse_parameters(rate_name=rate_name, variable=variable)

    def build_object(self):
        k = self.get_parameter("age_axis.k", search_ancestry=True)
        rate_name = self.get_parameter("rate_name", default="DD_rate", search_ancestry=False)
        variable_name = self.get_parameter("variable", default="var", search_ancestry=True)
        
        odes = {
            f"{variable_name}_1": f" - {rate_name}_1 * {variable_name}_1"} | {
            f"{variable_name}_{i}": f"{rate_name}_{i} * ({variable_name}_{i-1} - {variable_name}_{i})"
            for i in range(2, k + 1)
        }

        self.parameters.set(odes=odes)
        super().build_object()

class DistributedDelayModel(AgeStructuredCompositePopulationObject):
    PARSING_DATA = AgeStructuredCompositePopulationObject.PARSING_DATA | {
        "rate": AgeStructuredFunction,
        "variable": str,
    }
    def __init__(self, rate, variable = "var", **kwargs):
        super().__init__(**kwargs)
        self.parse_parameters(rate=rate, variable=variable)

    def build_object(self):
        # TODO: general Function object which has a "type"?
        rate = self.get_parameter("rate", default={}, search_ancestry=False)
        if rate:
            rate_function = AgeStructuredFunction(name="rate", **rate)
            self.add_children(rate_function)

        rate_function = self.children["rate"]
        rate_output = rate_function.get_parameter("output_name", default="function", search_ancestry=False)

        dd_odes = DistributedDelayODEs(
            name="odes",
            rate_name="DD_rate_a",
        )

        #rate_structured_outputs = rate_function.get_parameter("structured_outputs", default={}, search_ancestry=False)
        #rate_structured_outputs |= {rate_output: {"axes": ["a"], "connections": {f"{self.name}.odes.DD_rate"}}}
        #TODO: update "a" dynamically
        #rate_function.parameters.set(structured_outputs=rate_structured_outputs)
        rate_function.add_age_structured_output(rate_output, connections = f"{self.name}.odes.DD_rate")

        self.add_children(dd_odes)

        super().build_object()