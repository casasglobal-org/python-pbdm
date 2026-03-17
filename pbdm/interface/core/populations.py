from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from ..core.coerce import coerce_entry, coerce_tree
from ...population_modelling.population import Population


@dataclass(slots=True)
class PopulationSpec:
    name: str
    age_axis: dict | None = None
    functions: Any | None = None
    processes: Any | None = None
    dynamics: Any | None = None
    sub_populations: Mapping[str, Any] | None = None
    extra: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        data: dict[str, Any] = {}
        if self.age_axis is not None:
            data["age_axis"] = dict(self.age_axis)
        if self.functions is not None:
            data["functions"] = self._coerce_entry(self.functions)
        if self.processes is not None:
            data["processes"] = self._coerce_entry(self.processes)
        if self.dynamics is not None:
            data["dynamics"] = self._coerce_entry(self.dynamics)
        if self.sub_populations is not None:
            sub_payload: dict[str, Any] = {}
            for name, entry in self.sub_populations.items():
                sub_payload[name] = self._coerce_entry(entry)
            data["sub_populations"] = sub_payload
        data.update(self.extra)
        return data

    def build(self, **kwargs) -> Population:
        params = self.to_dict()
        params.update(kwargs)
        return Population(name=self.name, **params)

    @staticmethod
    def _coerce_entry(entry: Any) -> Any:
        if hasattr(entry, "to_dict"):
            return entry.to_dict()
        if isinstance(entry, dict):
            return coerce_tree(entry)
        raise TypeError(
            "PopulationSpec entries must be spec objects or dicts; "
            f"received {type(entry)}"
        )
