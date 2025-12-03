"""Helper utilities for age-structured population objects."""

from __future__ import annotations

from typing import Any, Set, Tuple


def _filter_ports_by_axis(port_spec: dict | None, axis: str) -> dict:
	if not port_spec:
		return {}
	filtered: dict[str, Any] = {}
	for name, entry in port_spec.items():
		axes = entry.get("axes") or []
		if axis in axes:
			filtered[name] = entry
	return filtered


def get_age_structured_inputs_spec(obj, *, axis: str) -> dict:
	spec = getattr(obj, "get_structured_inputs_spec")()
	return _filter_ports_by_axis(spec, axis)


def get_age_structured_outputs_spec(obj, *, axis: str) -> dict:
	spec = getattr(obj, "get_structured_outputs_spec")()
	return _filter_ports_by_axis(spec, axis)


def get_age_structured_variables_spec(obj, *, axis: str) -> dict:
	spec = getattr(obj, "get_structured_variables_spec")()
	return _filter_ports_by_axis(spec, axis)


_PORT_KIND_TO_ATTR = {
	"inputs": "input_ports",
	"outputs": "output_ports",
	"variables": "variable_ports",
}

_PORT_KIND_TO_AGE_SPEC_GETTER = {
	"inputs": "get_age_structured_inputs_spec",
	"outputs": "get_age_structured_outputs_spec",
	"variables": "get_age_structured_variables_spec",
}


def _collect_port_names(port_collection) -> Set[str]:
	if port_collection is None:
		return set()
	if isinstance(port_collection, dict):
		return set(port_collection.keys())
	try:
		return set(port_collection)
	except TypeError:
		return set()


def get_age_structured_port_set(obj, kind: str) -> Tuple[Set[str], Set[str]]:
	"""Return (structured_prefixes, unstructured_ports) for the requested kind."""

	if kind not in _PORT_KIND_TO_ATTR:
		raise ValueError(
			f"Unsupported port kind '{kind}'. Expected one of: {sorted(_PORT_KIND_TO_ATTR)}"
		)

	port_names = _collect_port_names(getattr(obj, _PORT_KIND_TO_ATTR[kind], None))

	getter_name = _PORT_KIND_TO_AGE_SPEC_GETTER[kind]
	if hasattr(obj, getter_name):
		structured_spec = getattr(obj, getter_name)() or {}
		structured_prefixes: Set[str] = set(structured_spec.keys())
	else:
		structured_prefixes = set()

	if not structured_prefixes:
		return set(), set(port_names)

	prefix_tuple = tuple(structured_prefixes)
	unstructured_ports = {name for name in port_names if not name.startswith(prefix_tuple)}
	return structured_prefixes, unstructured_ports
