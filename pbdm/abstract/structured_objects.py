from .population_objects import (
    PopulationObject,
    CompositePopulationObject,
    FunctionalPopulationObject,
    VariablePopulationObject,
)

from itertools import product
from copy import deepcopy

from sympy import S, Symbol, parse_expr, sympify

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
    }

    def __init__(
        self,
        structured_axes: dict | None = None,
        structured_inputs: dict | None = None,
        structured_outputs: dict | None = None,
        structured_variables: dict | None = None,
        **ported_object_kwargs,
    ):
        self._structured_port_specs = {
            "inputs": {},
            "outputs": {},
            "variables": {},
        }
        self._compiled_structured_port_names = {
            "inputs": set(),
            "outputs": set(),
            "variables": set(),
        }
        self._structured_ports_compiled = False

        super().__init__(**ported_object_kwargs)
        self.parse_parameters(structured_axes=structured_axes or {})

        self._ingest_structured_port_mapping("inputs", structured_inputs)
        self._ingest_structured_port_mapping("outputs", structured_outputs)
        self._ingest_structured_port_mapping("variables", structured_variables)

    def _ingest_structured_port_mapping(
        self,
        collection_name: str,
        port_mapping: dict | None,
    ) -> None:
        if not port_mapping:
            return
        for port_name, entry in port_mapping.items():
            coerced = self._coerce_structured_port_spec(collection_name, entry)
            self._update_structured_port_spec(collection_name, port_name, coerced)

    def _coerce_structured_port_spec(self, collection_name: str, entry) -> dict:
        if isinstance(entry, dict):
            spec = dict(entry)
        else:
            if entry in (None, {}):
                spec = {}
            elif collection_name == "inputs":
                spec = {"connection": entry}
            else:
                values = entry if isinstance(entry, (list, tuple, set)) else [entry]
                spec = {"connections": list(values)}

        axes = spec.get("axes")
        if axes is not None:
            spec["axes"] = self._normalise_axes(axes)

        if collection_name != "inputs":
            if "connections" in spec:
                spec["connections"] = self._normalise_connections(spec["connections"])
            else:
                connection_value = spec.pop("connection", None)
                if connection_value is not None:
                    spec["connections"] = self._normalise_connections(connection_value)

        return spec

    def _update_structured_port_spec(
        self,
        collection_name: str,
        port_name: str,
        update: dict,
    ) -> dict:
        specs = self._structured_port_specs[collection_name]
        entry = dict(specs.get(port_name, {}))
        if not update:
            specs[port_name] = entry
            return entry

        axes = update.get("axes")
        if axes is not None:
            update["axes"] = self._normalise_axes(axes)

        if collection_name != "inputs" and "connections" in update:
            update["connections"] = self._normalise_connections(update["connections"])

        entry.update({k: v for k, v in update.items() if v is not None})
        specs[port_name] = entry
        self._structured_ports_compiled = False
        self._sync_structured_port_parameters(collection_name)
        return entry

    @staticmethod
    def _normalise_axes(axes: list | tuple | set | None) -> list | None:
        if axes is None:
            return None
        return list(axes)

    @staticmethod
    def _normalise_connections(values: list | tuple | set | str | None) -> list | None:
        if values is None:
            return None
        if isinstance(values, (list, tuple, set)):
            return list(values)
        return [values]

    def add_structured_input(
        self,
        name: str,
        *,
        axes: list | tuple | set | None = None,
        connection: str | None = None,
        spec=None,
        **extra,
    ) -> dict:
        update = dict(extra)
        if spec is not None:
            update.update(self._coerce_structured_port_spec("inputs", spec))
        if axes is not None:
            update["axes"] = axes
        if connection is not None:
            update["connection"] = connection
        return self._update_structured_port_spec("inputs", name, update)

    def add_structured_output(
        self,
        name: str,
        *,
        axes: list | tuple | set | None = None,
        connections: list | tuple | set | str | None = None,
        spec=None,
        **extra,
    ) -> dict:
        update = dict(extra)
        if spec is not None:
            update.update(self._coerce_structured_port_spec("outputs", spec))
        if axes is not None:
            update["axes"] = axes
        if connections is not None:
            update["connections"] = connections
        #print("ADDING STRUCTURED OUTPUT", name, update)
        return self._update_structured_port_spec("outputs", name, update)

    def add_structured_variable(
        self,
        name: str,
        *,
        axes: list | tuple | set | None = None,
        connections: list | tuple | set | str | None = None,
        spec=None,
        **extra,
    ) -> dict:
        update = dict(extra)
        if spec is not None:
            update.update(self._coerce_structured_port_spec("variables", spec))
        if axes is not None:
            update["axes"] = axes
        if connections is not None:
            update["connections"] = connections
        return self._update_structured_port_spec("variables", name, update)

    def _set_structured_port_collection(
        self,
        kind: str,
        mapping: dict | None,
    ) -> None:
        normalised = {}
        if mapping:
            for name, entry in mapping.items():
                normalised[name] = self._coerce_structured_port_spec(kind, entry)
        self._structured_port_specs[kind] = normalised
        self._structured_ports_compiled = False
        self._sync_structured_port_parameters(kind)

    def set_structured_inputs(self, mapping: dict | None) -> None:
        self._set_structured_port_collection("inputs", mapping)

    def set_structured_outputs(self, mapping: dict | None) -> None:
        self._set_structured_port_collection("outputs", mapping)

    def set_structured_variables(self, mapping: dict | None) -> None:
        self._set_structured_port_collection("variables", mapping)

    def _sync_structured_port_parameters(self, kind: str | None = None) -> None:
        mapping = {
            "inputs": "structured_inputs",
            "outputs": "structured_outputs",
            "variables": "structured_variables",
        }
        target_kinds = mapping.keys() if kind is None else (kind,)
        for internal_kind in target_kinds:
            parameter_name = mapping[internal_kind]
            self.parameters.set(
                **{parameter_name: deepcopy(self._structured_port_specs[internal_kind])}
            )

    def _copy_structured_port_specs(self, kind: str) -> dict:
        return deepcopy(self._structured_port_specs[kind])

    def get_structured_inputs_spec(self) -> dict:
        return self._copy_structured_port_specs("inputs")

    def get_structured_outputs_spec(self) -> dict:
        return self._copy_structured_port_specs("outputs")

    def get_structured_variables_spec(self) -> dict:
        return self._copy_structured_port_specs("variables")

    def compile_structured_ports(self, *, force: bool = False) -> None:
        self._compile_structured_ports(force=force)

    def _compile_structured_ports(self, *, force: bool = False) -> None:
        for kind in ("inputs", "outputs", "variables"):
            self._compile_structured_port_collection(kind, force=force)
        self._structured_ports_compiled = True

    def _compile_structured_port_collection(self, kind: str, *, force: bool = False) -> None:
        specs = self._structured_port_specs[kind]
        compiled_names = self._compiled_structured_port_names[kind]
        for port, data in specs.items():
            axes = data.get("axes", [])
            axis_combos, port_names = self._structured_names(port, axes)
            entries = list(zip(port_names, axis_combos))

            names_to_add = [
                name for name, _ in entries if name not in compiled_names
            ]
            if names_to_add:
                if kind == "inputs":
                    self.add_input_ports(*names_to_add)
                elif kind == "outputs":
                    self.add_output_ports(*names_to_add)
                else:
                    self.add_variable_ports(*names_to_add)
                compiled_names.update(names_to_add)

            if not entries:
                continue

            if kind == "inputs":
                connection = data.get("connection")
                if connection:
                    mapping = {
                        port_name: self._structured_name(connection, combo)
                        for port_name, combo in entries
                    }
                    if mapping:
                        self.add_input_connections(**mapping)
            else:
                connections = data.get("connections") or []
                if connections:
                    mapping = {}
                    for connection in connections:
                        for port_name, combo in entries:
                            mapping[port_name] = self._structured_name(
                                connection, combo
                            )
                    if mapping:
                        if kind == "outputs":
                            self.add_output_connections(**mapping)
                        else:
                            self.add_variable_connections(**mapping)

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

            local_dict = {
                input_name: Symbol(input_name)
                for input_name in structured_inputs.keys()
            }
            local_dict.setdefault(assignment_name, Symbol(assignment_name))
            for axis in axes:
                local_dict.setdefault(axis, Symbol(axis))
                axis_index_variable = self._axis_index_variable(axis)
                if axis_index_variable:
                    local_dict.setdefault(
                        axis_index_variable, Symbol(axis_index_variable)
                    )
            for axis in reducer_axes:
                local_dict.setdefault(axis, Symbol(axis))
                axis_index_variable = self._axis_index_variable(axis)
                if axis_index_variable:
                    local_dict.setdefault(
                        axis_index_variable, Symbol(axis_index_variable)
                    )

            parse_function = parse_expr(function, local_dict=local_dict)
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

                    substitution[assignment_name] = sympify(full_assignment_name)
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

    def compile_structured_ports(self, *, force = False):
        for child in self.children.values():
            if isinstance(child, StructuredPopulationObject):
                child.compile_structured_ports(force=force)
        super().compile_structured_ports(force=force)


