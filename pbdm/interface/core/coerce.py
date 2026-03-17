from __future__ import annotations

from typing import Any, Mapping


def coerce_entry(entry: Any, label: str) -> Any:
    if hasattr(entry, "to_dict"):
        return entry.to_dict()
    if isinstance(entry, dict):
        return coerce_tree(entry)
    raise TypeError(f"{label} entries must be spec objects or dicts; received {type(entry)}")


def coerce_tree(payload: Mapping[str, Any]) -> dict:
    converted: dict[str, Any] = {}
    for key, value in payload.items():
        if hasattr(value, "to_dict"):
            converted[key] = value.to_dict()
        elif isinstance(value, dict):
            converted[key] = coerce_tree(value)
        else:
            converted[key] = value
    return converted
