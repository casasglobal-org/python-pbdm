from psymple_connections.connections.connection_ported_objects import (
    CompositePortedObjectWithConnections,
    PortedObjectWithAssignmentsAndConnections,
)
from psymple.build import FunctionalPortedObject, VariablePortedObject
from psymple_connections.connections.automatic.search import PortedObjectWithSearch
from psymple_connections.parameters.parameter_search import ParameterSearchObject


class PopulationObject(PortedObjectWithSearch, ParameterSearchObject):
    PORTED_OBJECT_DATA = {
        "name",
        "input_ports",
        "output_ports",
        "variable_ports",
        "inputs",
        "output_connections",
        "variable_connections",
        "parsing_locals",
    }

    def build_object(self):
        print("Building Population Object", self.address)

    def search_inputs(self, search_rule, skip_inputs=set()):
        def _filter_callback(missing_inputs: set[str]) -> set[str]:
            filtered_inputs = set()
            for input in missing_inputs:
                if input in self.parameters:
                    parameter_value = self.parameters[input]
                    if input in self.input_ports:
                        port = self.input_ports[input]
                        if value := port.default_value:
                            # TODO: We could check if the value is the same as the parameter value
                            # NOTE: This branch doesn't seem to be used, as the parameter is not
                            # considered missing. This is probably desired behaviour.
                            raise Exception(
                                f"Parameter '{input}' has already been defined as an "
                                f"input port of {self.address} with value {value} and "
                                f"cannot be overwitten."
                            )
                        else:
                            port.default_value = parameter_value
                    else:
                        self.add_input_ports(
                            {"name": input, "default_value": self.parameters[input]}
                        )
                else:
                    filtered_inputs.add(input)
            return filtered_inputs

        super().search_inputs(search_rule, skip_inputs, _filter_callback)


class CompositePopulationObject(
    PopulationObject,
    CompositePortedObjectWithConnections,
):
    PORTED_OBJECT_DATA = PopulationObject.PORTED_OBJECT_DATA | {
        "children",
        "variable_wires",
        "directed_wires",
    }

    def build_children(self):
        for child in self.children.values():
            child.build_object()

    def build_object(self):
        self.build_children()
        super().build_object()

    def search_inputs(self, search_rule, skip_inputs=set()):
        for child in self.children.values():
            child.search_inputs(search_rule, skip_inputs)
        super().search_inputs(search_rule, skip_inputs)


class FunctionalPopulationObject(
    PopulationObject,
    PortedObjectWithAssignmentsAndConnections,
    FunctionalPortedObject,
):
    PORTED_OBJECT_DATA = PopulationObject.PORTED_OBJECT_DATA - {
        "output_ports",
        "variable_ports",
        "variable_connections",
    } | {"assignments", "create_input_ports"}


class VariablePopulationObject(
    PopulationObject,
    PortedObjectWithAssignmentsAndConnections,
    VariablePortedObject,
):
    PORTED_OBJECT_DATA = PopulationObject.PORTED_OBJECT_DATA - {"output_ports"} | {
        "assignments",
        "create_input_ports",
        "create_output_ports",
    }

