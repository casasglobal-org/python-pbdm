from sympy import simplify, sympify

from pbdm.abstract.structured_objects import (
    StructuredFunctionalPopulationObject,
    StructuredVariablePopulationObject,
)


def _build_structured_object(cls):
    structured_object = cls(
        name="structured",
        structured_axes={
            "a": {"k": 2, "index_variable": "i", "index_function": "i/D"},
            "x": {"k": 3, "index_variable": "i", "index_function": "i/F"},
        },
        structured_assignments={
            "repro_rate": {
                "axes": ["a", "x"],
                "function": "b * f * a * x",
            },
            "mort_rate": {
                "axes": ["a"],
                "function": "c * g * a",
                "reducers": {"x": {"method": "sum"}},
            },
            "contact_product": {
                "axes": ["a"],
                "function": "g",
                "reducers": {"x": {"method": "product"}},
            },
            "contact_mean": {
                "axes": ["a"],
                "function": "g",
                "reducers": {"x": {"method": "mean"}},
            },
            "contact_variance": {
                "axes": ["a"],
                "function": "g",
                "reducers": {"x": {"method": "variance"}},
            },
        },
        structured_inputs={
            "f": {"axes": ["a"], "connection": {}},
            "g": {"axes": ["a", "x"], "connection": {}},
        },
    )
    structured_object.build_object()
    return structured_object


def _assignment_map(obj):
    assignments = obj.to_data()["object_data"]["assignments"]
    mapping = {}
    for item in assignments:
        name_key = "parameter" if "parameter" in item else "variable"
        mapping[item[name_key]] = item["expression"]
    return mapping


def _assert_equivalent(actual, expected):
    actual_expr = sympify(actual)
    expected_expr = sympify(expected)
    assert simplify(actual_expr - expected_expr) == 0


def test_structured_variable_matches_functional_assignments():
    functional_map = _assignment_map(
        _build_structured_object(StructuredFunctionalPopulationObject)
    )
    variable_map = _assignment_map(
        _build_structured_object(StructuredVariablePopulationObject)
    )
    assert variable_map == functional_map


def test_structured_variable_substitutes_axis_symbol():
    variable_object = StructuredVariablePopulationObject(
        name="density",
        structured_axes={"x": {"k": 4}},
        structured_assignments={
            "density": {
                "axes": ["x"],
                "function": "x",
            }
        },
    )
    variable_object.build_object()
    assignments = _assignment_map(variable_object)

    _assert_equivalent(assignments["density_x_1"], "1/4")
    _assert_equivalent(assignments["density_x_4"], "1")


def test_structured_variable_assignments_create_matching_output_ports():
    variable_object = StructuredVariablePopulationObject(
        name="state",
        structured_axes={"age": {"k": 2}},
        structured_assignments={
            "S": {
                "axes": ["age"],
                "function": "1",
            }
        },
    )

    variable_object.build_object()
    variable_object.compile_structured_ports()

    assert set(variable_object.variable_ports.keys()) == {"S_age_1", "S_age_2"}
    assert set(variable_object.output_ports.keys()) == {"S_age_1", "S_age_2"}
