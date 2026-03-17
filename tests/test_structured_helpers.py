from pbdm.abstract.structured_objects import StructuredVariablePopulationObject
from pbdm.age_structure.objects import AgeStructuredVariablePopulationObject
from pbdm.age_structure.helpers import get_age_structured_port_set


def test_add_structured_input_updates_parameters():
    helper = StructuredVariablePopulationObject(name="helper")

    helper.add_structured_input(
        "beta",
        axes=["a"],
        connection="source.beta",
        metadata="foo",
    )

    structured_inputs = helper.get_parameter(
        "structured_inputs",
        search_ancestry=False,
    )

    assert structured_inputs["beta"]["axes"] == ["a"]
    assert structured_inputs["beta"]["connection"] == "source.beta"
    assert structured_inputs["beta"]["metadata"] == "foo"


def test_add_structured_output_handles_connections():
    helper = StructuredVariablePopulationObject(name="helper")

    helper.add_structured_output(
        "flux",
        axes=["a", "b"],
        connections=["sink.rate", "sink.capacity"],
    )

    structured_outputs = helper.get_parameter(
        "structured_outputs",
        search_ancestry=False,
    )

    assert structured_outputs["flux"]["axes"] == ["a", "b"]
    assert structured_outputs["flux"]["connections"] == [
        "sink.rate",
        "sink.capacity",
    ]


def test_add_structured_variable_accepts_scalar_connection():
    helper = StructuredVariablePopulationObject(name="helper")

    helper.add_structured_variable(
        "state",
        axes=["a"],
        connections="population.state",
    )

    structured_variables = helper.get_parameter(
        "structured_variables",
        search_ancestry=False,
    )

    assert structured_variables["state"]["connections"] == ["population.state"]


def test_age_structured_helpers_infer_axis():
    helper = AgeStructuredVariablePopulationObject(
        name="age",
        age_axis={"name": "A", "k": 3},
    )

    helper.add_age_structured_input("beta", connection="source.beta")
    helper.add_age_structured_output(
        "gamma",
        connections=["sink.gamma"],
    )
    helper.add_age_structured_variable(
        "state",
        connections="population.state",
    )

    structured_inputs = helper.get_parameter(
        "structured_inputs",
        search_ancestry=False,
    )
    structured_outputs = helper.get_parameter(
        "structured_outputs",
        search_ancestry=False,
    )
    structured_variables = helper.get_parameter(
        "structured_variables",
        search_ancestry=False,
    )

    assert structured_inputs["beta"]["axes"] == ["A"]
    assert structured_outputs["gamma"]["axes"] == ["A"]
    assert structured_variables["state"]["axes"] == ["A"]


def test_get_age_structured_port_set_for_structured_object():
    class StructuredStub:
        def __init__(self):
            self.output_ports = {
                "flux_age_1",
                "flux_age_2",
                "scalar",
            }

        def get_age_structured_outputs_spec(self):
            return {"flux": {"axes": ["age"]}}

    structured, unstructured = get_age_structured_port_set(
        StructuredStub(), "outputs"
    )

    assert structured == {"flux"}
    assert unstructured == {"scalar"}


def test_get_age_structured_port_set_handles_unstructured_objects():
    class Plain:
        def __init__(self):
            self.input_ports = {"alpha": object(), "beta": object()}

    obj = Plain()
    structured, unstructured = get_age_structured_port_set(obj, "inputs")

    assert structured == set()
    assert unstructured == {"alpha", "beta"}