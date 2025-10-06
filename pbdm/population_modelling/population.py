from __future__ import annotations
from ..abstract.population_objects import CompositePopulationObject
from ..core.base import ModelWithFunctions
from .functions import Functions
from .processes import PopulationProcesses
from .dynamics import PopulationDynamics

class Population(ModelWithFunctions):
    PARSING_DATA = {
        "functions": Functions,
        "sub_populations": dict,
        "dynamics": PopulationDynamics,
        "processes": PopulationProcesses,
    }

    def __init__(
        self,
        functions=None,
        sub_populations=None,
        dynamics=None,
        processes=None,
        **ported_object_kwargs
    ):
        super().__init__(functions=functions, **ported_object_kwargs)
        self.parse_parameters(
            sub_populations=sub_populations,
            dynamics=dynamics,
            processes=processes,
        )

    def build_object(self):
        dynamics = self.get_parameter("dynamics", default={}, search_ancestry=False)
        if dynamics:
            dynamics_class = self.PARSING_DATA["dynamics"]
            dynamics_object = dynamics_class(name="dynamics", **dynamics)
            self.add_children(dynamics_object)

        if processes := self.get_parameter("processes", default={}, search_ancestry=False):
            print("PROCESSES", processes)
            processes_class = self.PARSING_DATA["processes"]
            processes_object = processes_class(name="processes", **processes)
            self.add_children(processes_object)

        if sub_populations := self.get_parameter("sub_populations", default={}, search_ancestry=False):
            for name, population_data in sub_populations.items():
                #population_class = self.PARSING_DATA["sub_populations"]
                sub_population = Population(name=name, **population_data)
                self.add_children(sub_population)

        super().build_object()
