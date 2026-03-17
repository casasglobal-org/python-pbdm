from pbdm.interface.bdfs import BiodemographicFunction, PBDMFunction
from pbdm.population_modelling.functions import AgeStructuredFunction, Function


def test_pbdm_function_without_age_axis_returns_function():
    func = PBDMFunction(
        name="temp_coeff",
        form="3*x",
        climate_variable="temp",
        parameters={"k": {"value": 2}},
        bound_above=5,
    )

    assert isinstance(func, Function)
    func.build_object()

    assert func.parameters["function"] == "min(3*temp, 5)"


def test_pbdm_function_with_age_axis_registers_structured_inputs():
    func = PBDMFunction(
        name="mortality",
        form="x * rate",
        climate_variable="temp",
        age_axis={"name": "age", "k": 2},
        parameters={"rate": {"structured": True, "connection": "rates.death_rate"}},
    )

    assert isinstance(func, AgeStructuredFunction)

    func.build_object()
    spec = func.get_age_structured_inputs_spec()
    assert "rate" in spec
    assert spec["rate"].get("connection") == "rates.death_rate"

    data = func.to_data()["object_data"]
    assignments = {item["parameter"] for item in data["assignments"]}
    assert assignments == {"function_age_1", "function_age_2"}


def test_biodemographic_function_defaults_to_placeholder_variable():
    func = BiodemographicFunction(
        name="bdf",
        form="2*x",
        parameters={"scale": {"value": 0.25}},
    )

    assert isinstance(func, Function)
    func.build_object()
    assert func.parameters["function"] == "2*x"