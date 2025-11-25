from .population_objects import (
    PopulationObject,
    CompositePopulationObject,
    FunctionalPopulationObject,
    VariablePopulationObject,
)

from itertools import product

from sympy import S, parse_expr, sympify

structured_inputs = {"i": {"axes": ["a"], "connections": {}}}  # optional

structured_axes = {
    "a": {
        "k": 3,
    },
    "x": {"k": 2},
}


class StructuredPopulationObject(PopulationObject):
    PARSING_DATA = {
        "structured_axes": dict,
        "structured_inputs": dict,
        "structured_outputs": dict,
        "structured_variables": dict,
    }

    def __init__(
        self,
        structured_axes: dict = {},
        structured_inputs: dict = {},
        structured_outputs: dict = {},
        structured_variables: dict = {},
        **ported_object_kwargs,
    ):
        super().__init__(**ported_object_kwargs)
        self.parse_parameters(
            structured_axes=structured_axes,
            structured_inputs=structured_inputs,
            structured_outputs=structured_outputs,
            structured_variables=structured_variables,
        )

    def _iter_axis_combinations(self, axes):
        axes = list(axes)
        if not axes:
            yield tuple()
            return

        index_ranges = [
            range(
                1,
                self.get_parameter(
                    f"structured_axes.{axis}.k", default=1, search_ancestry=True
                )
                + 1,
            )
            for axis in axes
        ]

        for indices in product(*index_ranges):
            yield tuple(zip(axes, indices))

    @staticmethod
    def _format_structured_suffix(axis_combo):
        if not axis_combo:
            return ""
        return "_".join(f"{axis}_{index}" for axis, index in axis_combo)

    def _structured_name(self, base, axis_combo):
        suffix = self._format_structured_suffix(axis_combo)
        return base if not suffix else f"{base}_{suffix}"

    def _structured_names(self, base, axes):
        axis_combos = list(self._iter_axis_combinations(axes))
        names = [self._structured_name(base, combo) for combo in axis_combos]
        return axis_combos, names

    def _axis_index_variable(self, axis):
        try:
            return self.get_parameter(
                f"structured_axes.{axis}.index_variable",
                default="i",
                search_ancestry=True,
            )
        except Exception:
            return "i"

    def _axis_index_expression(self, axis, index):
        index_variable = self._axis_index_variable(axis)

        try:
            index_function = self.get_parameter(
                f"structured_axes.{axis}.index_function",
                default="i/k",
                search_ancestry=True,
            )
        except Exception:
            index_function = "i/k"

        if not index_function:
            return S(index)

        index_expr = parse_expr(str(index_function))

        substitution = {index_variable: S(index)}

        try:
            axis_config = self.get_parameter(
                f"structured_axes.{axis}", default={}, search_ancestry=True
            )
        except Exception:
            axis_config = {}

        if isinstance(axis_config, dict):
            for param_name, param_value in axis_config.items():
                if param_name in {"index_function", "index_variable"}:
                    continue
                if param_value is None:
                    continue
                try:
                    substitution[param_name] = sympify(param_value)
                except Exception:
                    continue

        substituted_expr = index_expr.subs(substitution)
        return sympify(substituted_expr)
    

    def build_object(self):
        structured_inputs = self.get_parameter(
            "structured_inputs", default={}, search_ancestry=False
        )
        structured_outputs = self.get_parameter(
            "structured_outputs", default={}, search_ancestry=False
        )
        structured_variables = self.get_parameter(
            "structured_variables", default={}, search_ancestry=False
        )
        for port, data in structured_inputs.items():
            axes = data.get("axes", [])
            connection = data.get("connection", {})
            axis_combos, port_names = self._structured_names(port, axes)
            if port_names:
                self.add_input_ports(*port_names)
            if connection:
                self.add_input_connections(
                    **{
                        port_name: self._structured_name(connection, combo)
                        for port_name, combo in zip(port_names, axis_combos)
                    }
                )

        for port, data in structured_outputs.items():
            axes = data.get("axes", [])
            connections = data.get("connections", {})
            axis_combos, port_names = self._structured_names(port, axes)
            if port_names:
                self.add_output_ports(*port_names)
            if connections:
                mapping = {}
                for connection in connections:
                    for port_name, combo in zip(port_names, axis_combos):
                        mapping[port_name] = self._structured_name(connection, combo)
                if mapping:
                    self.add_output_connections(**mapping)

        for port, data in structured_variables.items():
            axes = data.get("axes", [])
            connections = data.get("connections", {})
            axis_combos, port_names = self._structured_names(port, axes)
            if port_names:
                self.add_variable_ports(*port_names)
            if connections:
                mapping = {}
                for connection in connections:
                    for port_name, combo in zip(port_names, axis_combos):
                        mapping[port_name] = self._structured_name(connection, combo)
                if mapping:
                    self.add_variable_connections(**mapping)

        super().build_object()

    def _generate_structured_assignments(
        self,
        structured_assignments: dict | None,
        structured_inputs: dict | None,
    ) -> list[tuple[str, str]]:
        structured_assignments = structured_assignments or {}
        structured_inputs = structured_inputs or {}
        resolved_assignments: list[tuple[str, str]] = []

        for assignment_name, assignment_data in structured_assignments.items():
            axes = assignment_data.get("axes", [])
            function = assignment_data.get("function")
            if not function:
                raise ValueError(
                    f"Assignment '{assignment_name}' must define a 'function' expression."
                )

            reducers = assignment_data.get("reducers", {}) or {}
            assignment_axes_set = set(axes)

            invalid_reducer_axes = assignment_axes_set.intersection(reducers.keys())
            if invalid_reducer_axes:
                raise ValueError(
                    "Reducers cannot be defined for axes that already belong to the"
                    f" assignment '{assignment_name}': {sorted(invalid_reducer_axes)}"
                )

            for input_name, input_data in structured_inputs.items():
                input_axes = input_data.get("axes", [])
                missing_axes = [
                    axis
                    for axis in input_axes
                    if axis not in assignment_axes_set and axis not in reducers
                ]
                if missing_axes:
                    raise ValueError(
                        f"Assignment '{assignment_name}' requires reducers for axes"
                        f" {missing_axes} due to input '{input_name}'."
                    )

            reducer_axes = list(reducers.keys())
            extra_axis_combos = (
                list(self._iter_axis_combinations(reducer_axes))
                if reducer_axes
                else [tuple()]
            )

            parse_function = parse_expr(function)
            axis_combos, assignment_names = self._structured_names(
                assignment_name, axes
            )

            for combo, full_assignment_name in zip(axis_combos, assignment_names):
                assignment_axis_map = dict(combo)
                terms_map = {}

                for extra_combo in extra_axis_combos:
                    extra_axis_map = dict(extra_combo)
                    substitution = {}
                    axis_indices = {**assignment_axis_map, **extra_axis_map}

                    for axis, index in axis_indices.items():
                        substitution[axis] = self._axis_index_expression(axis, index)
                        index_variable = self._axis_index_variable(axis)
                        if index_variable and index_variable != axis:
                            substitution[index_variable] = S(index)

                        axis_config = self.get_parameter(
                            f"structured_axes.{axis}",
                            default={},
                            search_ancestry=True,
                        )
                        if isinstance(axis_config, dict):
                            for param_name, param_value in axis_config.items():
                                if param_name in {"index_function", "index_variable"}:
                                    continue
                                if param_value is None:
                                    continue
                                try:
                                    substitution[param_name] = sympify(param_value)
                                except Exception:
                                    continue

                    for input_name, input_data in structured_inputs.items():
                        input_axes = input_data.get("axes", [])
                        input_indices = []
                        for axis in input_axes:
                            if axis in assignment_axis_map:
                                input_indices.append((axis, assignment_axis_map[axis]))
                            elif axis in extra_axis_map:
                                input_indices.append((axis, extra_axis_map[axis]))
                            else:
                                raise ValueError(
                                    f"Input '{input_name}' is missing index data for axis"
                                    f" '{axis}' in assignment '{assignment_name}'."
                                )
                        substitution[input_name] = sympify(
                            self._structured_name(input_name, input_indices)
                        )

                    term_expr = sympify(parse_function.subs(substitution))

                    weights = {}
                    for axis, _ in extra_combo:
                        reducer_conf = reducers.get(axis, {})
                        method = reducer_conf.get("method", "sum")
                        if method not in {"sum", "product", "mean", "variance"}:
                            raise NotImplementedError(
                                f"Reducer method '{method}' for axis '{axis}' is not supported."
                            )

                        measure = reducer_conf.get("measure")
                        if measure is None:
                            weight_expr = S.One
                        elif isinstance(measure, str):
                            weight_expr = sympify(
                                parse_expr(measure).subs(substitution)
                            )
                        else:
                            weight_expr = sympify(measure)

                        weights[axis] = weight_expr

                    terms_map[tuple(extra_combo)] = (term_expr, weights)

                aggregated_expr = self._apply_reducers(
                    terms_map, reducers, reducer_axes
                )
                resolved_assignments.append(
                    (full_assignment_name, str(aggregated_expr))
                )

        return resolved_assignments

    def _apply_reducers(self, terms_map, reducers, reducer_axes):
        if not reducer_axes:
            if len(terms_map) != 1:
                raise ValueError("Unexpected number of terms without reducers.")
            return next(iter(terms_map.values()))[0]

        remaining_axes = list(reducer_axes)
        current = terms_map

        while remaining_axes:
            axis_name = remaining_axes.pop()
            axis_idx = len(remaining_axes)
            reducer_conf = reducers.get(axis_name, {})
            method = reducer_conf.get("method", "sum")

            grouped = {}
            for combo, (value_expr, weights_dict) in current.items():
                if axis_idx >= len(combo):
                    raise ValueError(
                        f"Reducer axis '{axis_name}' not present in combination '{combo}'."
                    )

                axis_entry = combo[axis_idx]
                if axis_entry[0] != axis_name:
                    raise ValueError(
                        f"Reducer axis order mismatch for axis '{axis_name}'."
                    )

                weight = weights_dict.get(axis_name, S.One)
                remaining_weights = {
                    axis: weight_expr
                    for axis, weight_expr in weights_dict.items()
                    if axis != axis_name
                }

                prefix_combo = combo[:axis_idx]
                state = grouped.get(prefix_combo)

                if method == "sum":
                    aggregated = state[0] if state else S.Zero
                    aggregated += value_expr * weight
                    grouped[prefix_combo] = (aggregated, remaining_weights)
                elif method == "product":
                    aggregated = state[0] if state else S.One
                    aggregated *= value_expr * weight
                    grouped[prefix_combo] = (aggregated, remaining_weights)
                elif method == "mean":
                    if state is None:
                        grouped[prefix_combo] = (
                            value_expr * weight,
                            weight,
                            remaining_weights,
                        )
                    else:
                        sum_expr, weight_sum, _ = state
                        grouped[prefix_combo] = (
                            sum_expr + value_expr * weight,
                            weight_sum + weight,
                            remaining_weights,
                        )
                elif method == "variance":
                    if state is None:
                        grouped[prefix_combo] = (
                            value_expr * weight,
                            (value_expr ** 2) * weight,
                            weight,
                            remaining_weights,
                        )
                    else:
                        sum_expr, sum_sq_expr, weight_sum, _ = state
                        grouped[prefix_combo] = (
                            sum_expr + value_expr * weight,
                            sum_sq_expr + (value_expr ** 2) * weight,
                            weight_sum + weight,
                            remaining_weights,
                        )
                else:
                    raise NotImplementedError(
                        f"Reducer method '{method}' for axis '{axis_name}' is not supported."
                    )

            new_current = {}
            for prefix_combo, state in grouped.items():
                if method == "sum":
                    aggregated_value, remaining_weights = state
                elif method == "product":
                    aggregated_value, remaining_weights = state
                elif method == "mean":
                    sum_expr, weight_sum, remaining_weights = state
                    if weight_sum == 0:
                        raise ValueError(
                            "Mean reducer encountered zero total weight."
                        )
                    aggregated_value = sum_expr / weight_sum
                elif method == "variance":
                    sum_expr, sum_sq_expr, weight_sum, remaining_weights = state
                    if weight_sum == 0:
                        raise ValueError(
                            "Variance reducer encountered zero total weight."
                        )
                    mean_expr = sum_expr / weight_sum
                    aggregated_value = sum_sq_expr / weight_sum - mean_expr**2
                else:
                    raise NotImplementedError(
                        f"Reducer method '{method}' for axis '{axis_name}' is not supported."
                    )

                new_current[prefix_combo] = (aggregated_value, remaining_weights)

            current = new_current

        if len(current) != 1 or () not in current:
            raise ValueError("Reducer computation failed to collapse all axes.")

        final_value, _ = current[()]
        return final_value


class StructuredFunctionalPopulationObject(
    FunctionalPopulationObject, StructuredPopulationObject
):
    PARSING_DATA = StructuredPopulationObject.PARSING_DATA | {"structured_assignments": dict} 
    # REMOVE STRUCTURED VARIABLES
    def __init__(
        self,
        structured_assignments: dict = {},
        **ported_object_kwargs,
    ):
        super().__init__(**ported_object_kwargs)
        self.parse_parameters(
            structured_assignments=structured_assignments,
        )

    def build_object(self):
        structured_assignments = self.get_parameter(
            "structured_assignments", default={}, search_ancestry=False
        )
        structured_inputs = self.get_parameter(
            "structured_inputs", default={}, search_ancestry=False
        )

        assignments = self._generate_structured_assignments(
            structured_assignments,
            structured_inputs,
        )
        if assignments:
            self.add_parameter_assignments(*assignments)

        super().build_object()


class StructuredVariablePopulationObject(
    VariablePopulationObject, StructuredPopulationObject
):
    PARSING_DATA = StructuredPopulationObject.PARSING_DATA | {
        "structured_assignments": dict
    }

    def __init__(
        self,
        structured_assignments: dict | None = None,
        **ported_object_kwargs,
    ):
        super().__init__(**ported_object_kwargs)
        self.parse_parameters(structured_assignments=structured_assignments or {})

    def build_object(self):
        structured_assignments = self.get_parameter(
            "structured_assignments", default={}, search_ancestry=False
        )
        structured_inputs = self.get_parameter(
            "structured_inputs", default={}, search_ancestry=False
        )

        assignments = self._generate_structured_assignments(
            structured_assignments,
            structured_inputs,
        )
        if assignments:
            self.add_variable_assignments(*assignments)

        super().build_object()


class StructuredCompositePopulationObject(
    CompositePopulationObject, StructuredPopulationObject
):
    pass


class AgeStructuredPopulationMixin:
    AGE_AXIS_DEFAULT = "age"
    PARSING_DATA = {"age_axis": dict}

    def __init__(self, *, age_axis=None, **kwargs):
        super().__init__(**kwargs)

        self.parse_parameters(age_axis=age_axis)

    def _infer_local_age_axis_name(self):
        local_age_axis = self.parameters.get("age_axis")
        if isinstance(local_age_axis, dict) and local_age_axis.get("name"):
            return local_age_axis["name"]

        local_structured_axes = self.parameters.get("structured_axes") or {}
        if self.AGE_AXIS_DEFAULT in local_structured_axes:
            return self.AGE_AXIS_DEFAULT

        if len(local_structured_axes) == 1:
            return next(iter(local_structured_axes))

        return self.AGE_AXIS_DEFAULT

    def _compose_age_axis_configuration(self, axis_name: str) -> dict:
        inherited_cfg = self.get_parameter(
            f"structured_axes.{axis_name}", default={}, search_ancestry=True
        )

        local_structured_axes = self.parameters.get("structured_axes") or {}
        local_structured_cfg = dict(local_structured_axes.get(axis_name, {}))

        local_age_axis = self.parameters.get("age_axis") or {}
        local_age_axis_cfg = (
            {key: value for key, value in local_age_axis.items() if key != "name"}
            if isinstance(local_age_axis, dict)
            else {}
        )

        axis_cfg = {}
        if isinstance(inherited_cfg, dict):
            axis_cfg.update(inherited_cfg)
        axis_cfg.update(local_structured_cfg)
        axis_cfg.update(local_age_axis_cfg)
        return axis_cfg

    def build_object(self):
        inferred_name = self._infer_local_age_axis_name()
        axis_name = self.get_parameter(
            "age_axis.name",
            default=inferred_name,
            search_ancestry=True,
        )

        axis_cfg = self._compose_age_axis_configuration(axis_name)
        axis_cfg_with_name = {"name": axis_name, **axis_cfg}

        updated_structured_axes = dict(self.parameters.get("structured_axes") or {})
        updated_structured_axes[axis_name] = dict(axis_cfg)

        self.parameters.set(
            age_axis=axis_cfg_with_name,
            structured_axes=updated_structured_axes,
        )

        super().build_object()

    
    def get_age_axis_config(self):
        try:
            age_axis = self.get_parameter("age_axis", default=None, search_ancestry=True)
        except Exception:
            age_axis = None
        if age_axis is None:
            raise ValueError(
                "Age axis is not defined for this object. Provide 'age_axis' or"
                " ensure it exists in structured_axes."
            )
        axis_name = age_axis.get("name", self.AGE_AXIS_DEFAULT)
        axis_cfg = {key: value for key, value in age_axis.items() if key != "name"}
        return axis_name, axis_cfg
    


class AgeStructuredPopulationObject(
    AgeStructuredPopulationMixin, StructuredPopulationObject
):
    PARSING_DATA = StructuredPopulationObject.PARSING_DATA | {"age_axis": dict}

    def __init__(
        self,
        age_axis: dict | None = None,
        structured_axes: dict | None = None,
        **ported_object_kwargs,
    ):
        super().__init__(
            age_axis=age_axis,
            structured_axes=structured_axes,
            **ported_object_kwargs,
        )


class AgeStructuredFunctionalPopulationObject(
    AgeStructuredPopulationMixin, StructuredFunctionalPopulationObject
):
    PARSING_DATA = StructuredFunctionalPopulationObject.PARSING_DATA | {"age_axis": dict}

    def __init__(
        self,
        age_axis: dict | None = None,
        structured_axes: dict | None = None,
        **ported_object_kwargs,
    ):
        super().__init__(
            age_axis=age_axis,
            structured_axes=structured_axes,
            **ported_object_kwargs,
        )


class AgeStructuredVariablePopulationObject(
    AgeStructuredPopulationMixin, StructuredVariablePopulationObject
):
    PARSING_DATA = StructuredVariablePopulationObject.PARSING_DATA | {"age_axis": dict}

    def __init__(
        self,
        age_axis: dict | None = None,
        structured_axes: dict | None = None,
        **ported_object_kwargs,
    ):
        super().__init__(
            age_axis=age_axis,
            structured_axes=structured_axes,
            **ported_object_kwargs,
        )


class AgeStructuredCompositePopulationObject(
    AgeStructuredPopulationMixin, StructuredCompositePopulationObject
):
    PARSING_DATA = StructuredCompositePopulationObject.PARSING_DATA | {"age_axis": dict}

    def __init__(
        self,
        age_axis: dict | None = None,
        structured_axes: dict | None = None,
        **ported_object_kwargs,
    ):
        super().__init__(
            age_axis=age_axis,
            structured_axes=structured_axes,
            **ported_object_kwargs,
        )
