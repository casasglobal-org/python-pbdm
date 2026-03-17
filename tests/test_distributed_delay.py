from pbdm.population_modelling.dynamics.models.distributed_delay import (
    DistributedDelayModel,
)


def _build_model(age_axis, variable="x"):
    model = DistributedDelayModel(
        name="dd",
        rate={"function": "1", "output_name": "rate"},
        age_axis=age_axis,
        variable=variable,
    )
    model.build_object()
    model.compile_structured_ports()
    return model


def test_distributed_delay_respects_axis_name():
    model = _build_model({"name": "A", "k": 2}, variable="x")
    data = model.to_data()["object_data"]

    variable_ports = {port["name"] for port in data["variable_ports"]}
    assert variable_ports == {"x_A_1", "x_A_2"}

    wires = data.get("variable_wires", [])
    assert len(wires) == 2
    assert wires[0]["parent_port"].startswith("x_A_")

    odes = model.children["odes"].get_parameter("odes", search_ancestry=False)
    assert set(odes) == {"x_1", "x_2"}
    assert "DD_rate_A_1" in odes["x_1"]


def test_distributed_delay_respects_axis_k():
    model = _build_model({"name": "age", "k": 4}, variable="y")
    data = model.to_data()["object_data"]

    variable_ports = {port["name"] for port in data["variable_ports"]}
    assert variable_ports == {"y_age_1", "y_age_2", "y_age_3", "y_age_4"}

    wires = data.get("variable_wires", [])
    assert len(wires) == 4

    odes = model.children["odes"].get_parameter("odes", search_ancestry=False)
    assert set(odes) == {"y_1", "y_2", "y_3", "y_4"}
