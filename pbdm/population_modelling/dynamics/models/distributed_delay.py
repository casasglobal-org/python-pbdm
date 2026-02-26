from ...odes import ODESystem
from ....age_structure.objects import AgeStructuredCompositePopulationObject
from ...functions import AgeStructuredFunction

class DistributedDelayODEs(ODESystem):
    PARSING_DATA = ODESystem.PARSING_DATA | {
        "rate_name": str,
        "variable": str,
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
        axis_name, _ = self.get_age_axis_config()
        variable_name = self.get_parameter("variable", default="var", search_ancestry=False)
        if rate:
            rate_function = AgeStructuredFunction(name="rate", **rate)
            self.add_children(rate_function)

        rate_function = self.children["rate"]
        rate_output = rate_function.get_parameter("output_name", default="function", search_ancestry=False)

        dd_odes = DistributedDelayODEs(
            name="odes",
            rate_name=f"DD_rate_{axis_name}",
            variable=variable_name,
        )

        #rate_structured_outputs = rate_function.get_parameter("structured_outputs", default={}, search_ancestry=False)
        #rate_structured_outputs |= {rate_output: {"axes": ["a"], "connections": {f"{self.name}.odes.DD_rate"}}}
        #TODO: update "a" dynamically
        #rate_function.parameters.set(structured_outputs=rate_structured_outputs)
        rate_function.add_age_structured_output(rate_output, connections = f"{self.name}.odes.DD_rate")

        self.add_age_structured_variable(variable_name)

        self.add_children(dd_odes)

        super().build_object()

        # Bridge structured variables on the parent to the unstructured child ports.
        k = self.get_parameter("age_axis.k", search_ancestry=True)
        #self.compile_structured_ports()
        for i in range(1, k + 1):
            parent_port = self._structured_name(variable_name, ((axis_name, i),))
            child_port = f"odes.{variable_name}_{i}"
            self.add_variable_wire([child_port], parent_port=parent_port)