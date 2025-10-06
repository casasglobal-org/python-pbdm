from __future__ import annotations

from ..abstract.population_objects import CompositePopulationObject
from ..core.base import ModelWithFunctions
from ..population_modelling.population import Population
from .processes import PBDMBiodemographicProcess

class FunctionalPopulation(Population):
    PARSING_DATA = {
        "sub_populations": list,
        "processes": PBDMBiodemographicProcess
    }
    def __init__(
        self,
        name: str, 
        functions=None,
        sub_populations=None,
        dynamics=None,
        processes=None,
        metabolism=None,
        **ported_object_kwargs
    ):
        super().__init__(name=name, functions=functions, **ported_object_kwargs)
        self.parse_parameters(sub_populations=sub_populations, dynamics=dynamics, processes=processes, metabolism=metabolism)

    def build_object(self):
        sub_populations = self.get_parameter("sub_populations", default={}, search_ancestry=False)
        
        for name, population_data in sub_populations.items():
            #stage_structure = self.get_parameter(f"stage_structure.{name}", {})
            #stage_structure.update(ancestor=self.name)
            #print("PASSSTR", stage_structure)
            #population_data.update(stage_structure=stage_structure)
            functional_population = FunctionalPopulation(name=name, **population_data)
            self.add_children(functional_population)

        dynamics = self.get_parameter("dynamics", default={}, search_ancestry=False)
        if dynamics:
            pass

        processes = self.get_parameter("processes", default={}, search_ancestry=False)
        if processes:
            pass

        super().build_object()