from pbdm.abstract.structured_objects import (
    StructuredCompositePopulationObject,
    StructuredFunctionalPopulationObject,
)

A = StructuredCompositePopulationObject(
    name="A",
    structured_axes={
        "a": {"k": 2},
        "x": {"k": 3},
    },
    structured_inputs={
        "i": {"axes": ["a", "x"], "connection": {}},
        "j": {"axes": ["x"], "connection": {}},
    },
)

B = StructuredFunctionalPopulationObject(
    name="B",
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
    },
    structured_inputs={
        "f": {"axes": ["a"], "connection": {}},
        "g": {"axes": ["a", "x"], "connection": {}},
    },
)

C = StructuredFunctionalPopulationObject(
    name="C",
    structured_axes={
        "x": {"k": 2, "index_variable": "i", "index_function": "i/F"},
        "y": {"k": 2, "index_variable": "j", "index_function": "j/G"},
        "z": {"k": 2, "index_variable": "k", "index_function": "k/H"},
        "a": {"k": 2, "index_variable": "i", "index_function": "i/D"},
    },
    structured_inputs={"g": {"axes": ["x", "y", "z"], "connection": {}}},
    structured_assignments={
        "mean_rate": {
            "axes": ["y", "z"],
            "function": "g",
            "reducers": {"x": {"method": "mean"}},
        },
        "var_rate": {
            "axes": ["z"],
            "function": "g",
            "reducers": {"x": {"method": "variance"}, "y": {"method": "sum"}},
        },
        "prod_rate": {
            "axes": ["x", "y", "z"],
            "function": "a*g",
        },
    },
)

C.build_object()
print(C.to_data())

"""
from sympy import simplify, sympify

from pbdm.abstract.structured_objects import StructuredFunctionalPopulationObject


def _build_structured_object():
    structured_object = StructuredFunctionalPopulationObject(
        name="B",
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
    return {item["parameter"]: item["expression"] for item in assignments}


def _assert_equivalent(actual, expected):
    actual_expr = sympify(actual)
    expected_expr = sympify(expected)
    assert simplify(actual_expr - expected_expr) == 0


def test_sum_reducer_produces_expected_expression():
    assignments = _assignment_map(_build_structured_object())
    _assert_equivalent(
        assignments["mort_rate_a_1"],
        "c*g_a_1_x_1/D + c*g_a_1_x_2/D + c*g_a_1_x_3/D",
    )
    _assert_equivalent(
        assignments["mort_rate_a_2"],
        "2*c*(g_a_2_x_1 + g_a_2_x_2 + g_a_2_x_3)/D",
    )


def test_product_reducer_multiplies_axis_terms():
    assignments = _assignment_map(_build_structured_object())
    _assert_equivalent(
        assignments["contact_product_a_1"],
        "g_a_1_x_1*g_a_1_x_2*g_a_1_x_3",
    )
    _assert_equivalent(
        assignments["contact_product_a_2"],
        "g_a_2_x_1*g_a_2_x_2*g_a_2_x_3",
    )


def test_mean_reducer_averages_axis_terms():
    assignments = _assignment_map(_build_structured_object())
    _assert_equivalent(
        assignments["contact_mean_a_1"],
        "(g_a_1_x_1 + g_a_1_x_2 + g_a_1_x_3)/3",
    )
    _assert_equivalent(
        assignments["contact_mean_a_2"],
        "(g_a_2_x_1 + g_a_2_x_2 + g_a_2_x_3)/3",
    )


def test_variance_reducer_matches_second_central_moment():
    assignments = _assignment_map(_build_structured_object())
    _assert_equivalent(
        assignments["contact_variance_a_1"],
        "(g_a_1_x_1**2 + g_a_1_x_2**2 + g_a_1_x_3**2)/3 -"
        " ((g_a_1_x_1 + g_a_1_x_2 + g_a_1_x_3)/3)**2",
    )
    _assert_equivalent(
        assignments["contact_variance_a_2"],
        "(g_a_2_x_1**2 + g_a_2_x_2**2 + g_a_2_x_3**2)/3 -"
        " ((g_a_2_x_1 + g_a_2_x_2 + g_a_2_x_3)/3)**2",
    )
"""


{
    "metadata": {"name": "C", "type": "fpo"},
    "object_data": {
        "input_ports": [
            {"name": "g_x_2_y_1_z_1", "description": "", "default_value": None},
            {"name": "g_x_1_y_1_z_1", "description": "", "default_value": None},
            {"name": "g_x_1_y_1_z_2", "description": "", "default_value": None},
            {"name": "g_x_2_y_1_z_2", "description": "", "default_value": None},
            {"name": "g_x_2_y_2_z_1", "description": "", "default_value": None},
            {"name": "g_x_1_y_2_z_1", "description": "", "default_value": None},
            {"name": "g_x_2_y_2_z_2", "description": "", "default_value": None},
            {"name": "g_x_1_y_2_z_2", "description": "", "default_value": None},
            {"name": "a", "description": "", "default_value": None},
        ],
        "assignments": [
            {
                "expression": "g_x_1_y_1_z_1/2 + g_x_2_y_1_z_1/2",
                "parameter": "mean_rate_y_1_z_1",
            },
            {
                "expression": "g_x_1_y_1_z_2/2 + g_x_2_y_1_z_2/2",
                "parameter": "mean_rate_y_1_z_2",
            },
            {
                "expression": "g_x_1_y_2_z_1/2 + g_x_2_y_2_z_1/2",
                "parameter": "mean_rate_y_2_z_1",
            },
            {
                "expression": "g_x_1_y_2_z_2/2 + g_x_2_y_2_z_2/2",
                "parameter": "mean_rate_y_2_z_2",
            },
            {
                "expression": "(g_x_1_y_1_z_1 + g_x_1_y_2_z_1)**2/2 + (g_x_2_y_1_z_1 + g_x_2_y_2_z_1)**2/2 - (g_x_1_y_1_z_1/2 + g_x_1_y_2_z_1/2 + g_x_2_y_1_z_1/2 + g_x_2_y_2_z_1/2)**2",
                "parameter": "var_rate_z_1",
            },
            {
                "expression": "(g_x_1_y_1_z_2 + g_x_1_y_2_z_2)**2/2 + (g_x_2_y_1_z_2 + g_x_2_y_2_z_2)**2/2 - (g_x_1_y_1_z_2/2 + g_x_1_y_2_z_2/2 + g_x_2_y_1_z_2/2 + g_x_2_y_2_z_2/2)**2",
                "parameter": "var_rate_z_2",
            },
            {"expression": "a*g_x_1_y_1_z_1", "parameter": "prod_rate_x_1_y_1_z_1"},
            {"expression": "a*g_x_1_y_1_z_2", "parameter": "prod_rate_x_1_y_1_z_2"},
            {"expression": "a*g_x_1_y_2_z_1", "parameter": "prod_rate_x_1_y_2_z_1"},
            {"expression": "a*g_x_1_y_2_z_2", "parameter": "prod_rate_x_1_y_2_z_2"},
            {"expression": "a*g_x_2_y_1_z_1", "parameter": "prod_rate_x_2_y_1_z_1"},
            {"expression": "a*g_x_2_y_1_z_2", "parameter": "prod_rate_x_2_y_1_z_2"},
            {"expression": "a*g_x_2_y_2_z_1", "parameter": "prod_rate_x_2_y_2_z_1"},
            {"expression": "a*g_x_2_y_2_z_2", "parameter": "prod_rate_x_2_y_2_z_2"},
        ],
        "create_input_ports": True,
    },
}
