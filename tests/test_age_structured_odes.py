import pytest
from sympy import simplify, sympify

from pbdm.population_modelling.odes import (
    AgeStructuredDifferentialEquation,
    DifferentialEquations,
)


def _assignment_map(data):
    mapped = {}
    for item in data["assignments"]:
        key = "parameter" if "parameter" in item else "variable"
        mapped[item[key]] = item["expression"]
    return mapped


def _assert_equivalent(actual, expected):
    assert simplify(sympify(actual) - sympify(expected)) == 0


def test_age_structured_differential_equation_creates_age_specific_variables():
    ode = AgeStructuredDifferentialEquation(
        name="infection",
        function="beta * age",
        variable="I",
        age_axis={"k": 3},
        structured_inputs={"beta": None},
    )

    ode.build_object()
    ode.compile_structured_ports()
    data = ode.to_data()["object_data"]
    assignments = _assignment_map(data)

    assert set(assignments) == {"I_age_1", "I_age_2", "I_age_3"}
    _assert_equivalent(assignments["I_age_1"], "beta_age_1/3")
    _assert_equivalent(assignments["I_age_3"], "beta_age_3")

    input_ports = {port["name"] for port in data["input_ports"]}
    assert input_ports == {"beta_age_1", "beta_age_2", "beta_age_3"}

    variable_ports = {port["name"] for port in data["variable_ports"]}
    assert variable_ports == {"I_age_1", "I_age_2", "I_age_3"}


def test_age_structured_differential_equation_structures_variable_symbol():
    ode = AgeStructuredDifferentialEquation(
        name="decay",
        function="-4*M",
        variable="M",
        age_axis={"name": "A", "k": 2},
    )

    ode.build_object()
    ode.compile_structured_ports()
    data = ode.to_data()["object_data"]
    assignments = _assignment_map(data)

    _assert_equivalent(assignments["M_A_1"], "-4*M_A_1")
    _assert_equivalent(assignments["M_A_2"], "-4*M_A_2")


def test_age_structured_differential_equation_normalises_structured_variables():
    ode = AgeStructuredDifferentialEquation(
        name="mass",
        function="sigma * I",
        variable="dI",
        age_axis={"name": "A", "k": 2},
        structured_inputs={"sigma": None},
        structured_variables={"I": "population.I"},
    )

    ode.build_object()
    ode.compile_structured_ports()
    data = ode.to_data()["object_data"]

    variable_ports = {port["name"] for port in data["variable_ports"]}
    assert {"I_A_1", "I_A_2"}.issubset(variable_ports)

    structured_variables = ode.get_parameter(
        "structured_variables",
        search_ancestry=False,
    )
    assert structured_variables["I"]["axes"] == ["A"]
    assert structured_variables["I"]["connections"] == ["population.I"]


def test_differential_equations_share_age_axis_with_children():
    odes = DifferentialEquations(
        name="age_rates",
        age_axis={"name": "A", "k": 2},
        odes={
            "infection": {
                "type": "age_structured",
                "function": "beta * A",
                "variable": "I",
                "structured_inputs": {"beta": None},
            }
        },
    )

    odes.build_object()

    infection = odes.children["infection"]
    data = infection.to_data()["object_data"]
    assignments = _assignment_map(data)

    assert set(assignments) == {"I_A_1", "I_A_2"}
    _assert_equivalent(assignments["I_A_1"], "beta_A_1/2")
    _assert_equivalent(assignments["I_A_2"], "beta_A_2")

    input_ports = {port["name"] for port in data["input_ports"]}
    assert input_ports == {"beta_A_1", "beta_A_2"}


def test_differential_equations_reject_unhandled_types():
    odes = DifferentialEquations(
        name="invalid",
        odes={
            "system": {
                "type": "system",
                "function": "x",
                "variable": "x",
            }
        },
    )

    with pytest.raises(
        ValueError,
        match="only accepts 'single' or 'age_structured' entries",
    ):
        odes.build_object()
