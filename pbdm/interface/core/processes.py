from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from ..core.coerce import coerce_entry, coerce_tree
from ...population_modelling.processes import PopulationProcess, PopulationProcesses


@dataclass(slots=True)
class ProcessSpec:
    name: str
    rates: Any | None = None
    variables: Any | None = None
    outputs: Any | None = None
    functions: Any | None = None
    extra: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        data: dict[str, Any] = {}
        if self.rates is not None:
            data["rates"] = self._coerce_entry(self.rates)
        if self.variables is not None:
            data["variables"] = self._coerce_entry(self.variables)
        if self.outputs is not None:
            data["outputs"] = self._coerce_entry(self.outputs)
        if self.functions is not None:
            data["functions"] = self._coerce_entry(self.functions)
        data.update(self.extra)
        return data

    def build(self, **kwargs) -> PopulationProcess:
        params = self.to_dict()
        params.update(kwargs)
        return PopulationProcess(name=self.name, **params)

    @staticmethod
    def _coerce_entry(entry: Any) -> Any:
        if hasattr(entry, "to_dict"):
            return entry.to_dict()
        if isinstance(entry, dict):
            return coerce_tree(entry)
        raise TypeError(
            "ProcessSpec entries must be spec objects or dicts; "
            f"received {type(entry)}"
        )


@dataclass(slots=True)
class ProcessesSpec:
    name: str
    processes: Mapping[str, Any]
    extra: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        processes_payload: dict[str, Any] = {}
        for name, entry in self.processes.items():
            processes_payload[name] = self._coerce_entry(entry)

        data = {"processes": processes_payload}
        data.update(self.extra)
        return data

    def build(self, **kwargs) -> PopulationProcesses:
        params = self.to_dict()
        params.update(kwargs)
        return PopulationProcesses(name=self.name, **params)

    @staticmethod
    def _coerce_entry(entry: Any) -> Any:
        if hasattr(entry, "to_dict"):
            return entry.to_dict()
        if isinstance(entry, dict):
            return coerce_tree(entry)
        raise TypeError(
            "ProcessesSpec entries must be spec objects or dicts; "
            f"received {type(entry)}"
        )
