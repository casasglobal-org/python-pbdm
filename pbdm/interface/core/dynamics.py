from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from ..core.coerce import coerce_entry
from ...population_modelling.dynamics.dynamics import PopulationDynamics


@dataclass(slots=True)
class PopulationDynamicsSpec:
    name: str
    dynamics: Mapping[str, Any]
    extra: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        dynamics_payload: dict[str, Any] = {}
        for name, entry in self.dynamics.items():
            coerced = coerce_entry(entry, "PopulationDynamicsSpec")
            if isinstance(coerced, dict):
                coerced = self._ensure_ode_types(coerced)
            dynamics_payload[name] = coerced

        data = {"dynamics": dynamics_payload}
        data.update(self.extra)
        return data

    def build(self, **kwargs) -> PopulationDynamics:
        params = self.to_dict()
        params.update(kwargs)
        return PopulationDynamics(name=self.name, **params)

    @staticmethod
    def _ensure_ode_types(payload: dict) -> dict:
        odes = payload.get("odes")
        if not isinstance(odes, dict):
            return payload

        normalised = dict(payload)
        normalised_odes = dict(odes)
        for name, ode_data in normalised_odes.items():
            if isinstance(ode_data, dict) and "type" not in ode_data:
                updated = dict(ode_data)
                updated["type"] = "single"
                normalised_odes[name] = updated
        normalised["odes"] = normalised_odes
        return normalised
