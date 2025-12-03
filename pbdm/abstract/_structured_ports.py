"""Helpers for structured population modelling constructs."""

from __future__ import annotations


def _normalise_structured_ports(port_mapping: dict | None, axis_name: str) -> dict:
    """Ensure structured port entries include the provided axis."""
    if not port_mapping:
        return {}

    normalised: dict[str, dict] = {}
    for port_name, value in port_mapping.items():
        if isinstance(value, dict):
            entry = dict(value)
            axes = entry.get("axes")
            if not axes:
                entry["axes"] = [axis_name]
            normalised[port_name] = entry
        else:
            entry = {"axes": [axis_name]}
            if value not in (None, {}):
                entry["connection"] = value
            normalised[port_name] = entry

    return normalised


