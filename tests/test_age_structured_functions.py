from sympy import simplify, sympify

from pbdm.population_modelling.functions import (
    AgeStructuredFunction,
    AgeStructuredIntegral,
    Functions,
)


def test_age_structured_function_creates_age_specific_outputs():
    age_function = AgeStructuredFunction(
        name="mortality",
        function="rate * age",
        output_name="mortality_rate",
        age_axis={"k": 3},
        structured_inputs={"rate": None},
    )
    age_function.build_object()
    data = age_function.to_data()["object_data"]
    assignments = {item["parameter"]: item["expression"] for item in data["assignments"]}

    assert set(assignments) == {
        "mortality_rate_age_1",
        "mortality_rate_age_2",
        "mortality_rate_age_3",
    }
    assert simplify(
        sympify(assignments["mortality_rate_age_1"]) - sympify("rate_age_1/3")
    ) == 0
    assert simplify(
        sympify(assignments["mortality_rate_age_3"]) - sympify("rate_age_3")
    ) == 0
    assert {port["name"] for port in data["input_ports"]} == {
        "rate_age_1",
        "rate_age_2",
        "rate_age_3",
    }


def test_age_structured_function_accepts_custom_axis_name():
    age_function = AgeStructuredFunction(
        name="survival",
        function="rate * A",
        output_name="survival_rate",
        age_axis={"name": "A", "k": 2},
        structured_inputs={"rate": None},
    )
    age_function.build_object()
    data = age_function.to_data()["object_data"]
    assignments = {item["parameter"]: item["expression"] for item in data["assignments"]}

    assert set(assignments) == {"survival_rate_A_1", "survival_rate_A_2"}
    assert {port["name"] for port in data["input_ports"]} == {"rate_A_1", "rate_A_2"}


def test_axis_symbols_use_default_index_function_ratio():
    axis_function = AgeStructuredFunction(
        name="scaled",
        function="4*A",
        output_name="scaled_value",
        age_axis={"name": "A", "k": 10},
    )
    axis_function.build_object()
    data = axis_function.to_data()["object_data"]
    assignments = {item["parameter"]: item["expression"] for item in data["assignments"]}

    assert set(assignments) == {f"scaled_value_A_{i}" for i in range(1, 11)}
    assert simplify(
        sympify(assignments["scaled_value_A_1"]) - sympify("4/10")
    ) == 0
    assert simplify(
        sympify(assignments["scaled_value_A_4"]) - sympify("16/10")
    ) == 0
    assert simplify(
        sympify(assignments["scaled_value_A_10"]) - sympify("40/10")
    ) == 0


def test_age_structured_integral_applies_bounds():
    integral = AgeStructuredIntegral(
        name="total_contact",
        function="g",
        output_name="total_contact",
        age_axis={"k": 4},
        structured_inputs={"g": None},
        lower_index=1,
        upper_index=2,
    )
    integral.build_object()
    data = integral.to_data()["object_data"]
    assignments = {item["parameter"]: item["expression"] for item in data["assignments"]}

    assert simplify(
        sympify(assignments["total_contact"]) - sympify("g_age_1 + g_age_2")
    ) == 0


def test_functions_composite_shares_age_axis_with_children():
    functions = Functions(
        name="rates",
        age_axis={"name": "A", "k": 2},
        functions={
            "mortality": {
                "type": "age_structured",
                "function": "rate * A",
                "output_name": "mortality",
                "structured_inputs": {"rate": None},
            }
        },
    )

    functions.build_object()

    mortality = functions.children["mortality"]
    mortality_data = mortality.to_data()["object_data"]
    assignments = {item["parameter"]: item["expression"] for item in mortality_data["assignments"]}

    assert set(assignments) == {"mortality_A_1", "mortality_A_2"}
    assert {port["name"] for port in mortality_data["input_ports"]} == {"rate_A_1", "rate_A_2"}


def test_age_structured_spec_helpers_filter_by_axis():
    age_function = AgeStructuredFunction(
        name="diagnostics",
        function="rate * age",
        output_name="diagnostic",
        age_axis={"name": "age", "k": 2},
        structured_inputs={"rate": None},
    )

    age_function.build_object()

    age_function.set_structured_inputs(
        {
            "rate": {"axes": ["age"]},
            "global_rate": {"axes": ["region"]},
        }
    )
    age_function.set_structured_outputs(
        {
            "diagnostic": {"axes": ["age"]},
            "regional_total": {"axes": ["region"]},
        }
    )
    age_function.set_structured_variables(
        {
            "state": {"axes": ["age"]},
            "global_state": {"axes": ["region"]},
        }
    )

    assert set(age_function.get_age_structured_inputs_spec()) == {"rate"}
    assert set(age_function.get_age_structured_outputs_spec()) == {"diagnostic"}
    assert set(age_function.get_age_structured_variables_spec()) == {"state"}