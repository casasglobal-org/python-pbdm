from ..odes import DifferentialEquations
from ...abstract.population_objects import CompositePopulationObject
from ..functions import AgeStructuredFunction
from ...age_structure.objects import AgeStructuredCompositePopulationObject

class PopulationDynamics(AgeStructuredCompositePopulationObject):
    PARSING_DATA = {
        "dynamics": DifferentialEquations,
    }
    def __init__(self, dynamics=None, **ported_object_kwargs):
        """
        Accepts a dict of dynamics (from JSON) or a list of DifferentialEquations objects.
        """
        super().__init__(**ported_object_kwargs)
        self.parse_parameters(dynamics=dynamics)

    def build_object(self):
        if dynamics := self.get_parameter("dynamics", default={}, search_ancestry=False):
            for dynamics_name, dynamics_data in dynamics.items():
                dynamics_class = self.PARSING_DATA["dynamics"]
                print("HERE", dynamics_name, dynamics_data)
                dynamics_object = dynamics_class(name=dynamics_name, odes=dynamics_data)
                self.add_children(dynamics_object)

        super().build_object()