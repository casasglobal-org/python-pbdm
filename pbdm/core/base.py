#from ..abstract.population_objects import CompositePopulationObject
from ..population_modelling.functions import Functions
from ..abstract.structured_objects import AgeStructuredCompositePopulationObject

class ModelWithFunctions(AgeStructuredCompositePopulationObject):
    def __init__(self, functions=None, **ported_object_kwargs):
        super().__init__(**ported_object_kwargs)
        self.parse_parameters(functions=functions)

    def build_object(self):
        functions = self.get_parameter("functions", default={}, search_ancestry=False)
        if functions:
            functions_object = Functions(name="functions", **functions)
            self.add_children(functions_object)

        super().build_object()