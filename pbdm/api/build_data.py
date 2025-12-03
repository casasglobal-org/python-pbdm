"""
This module is designed to interpret build "survey" data for populations into pbdm objects.

Data structure:

population_name: {
    process_name: {
        subpop_name: {
            "metadata": {} <- how to read the rest of the data, I guess
            "variable": {} <- need to get from somewhere
            "rate": {}
            "scalars": {}
            "**parameters": {}
        }
    }
}
"""
import json

from collections import defaultdict

from ..interface.processes import PBDMBiodemographicProcess
from ..interface.bdfs import BiodemographicFunction, ScalarFunction
from ..interface.functional_population import FunctionalPopulation

class Builder:
    def __init__(self, data: dict):
        self.metadata = self._read_metadata(data)

    def _read_metadata(self, data):
        return data.pop("metadata", {})

    @classmethod
    def from_json(cls, json_fp: str):
        """
        Create a Builder instance from JSON data.
        """
        with open(json_fp, 'r') as file:
            data = json.load(file)
        return cls(data=data)

class PopulationBuilder(Builder):
    def __init__(self, data: dict):
        super().__init__(data)
        sub_populations = data.get("stages", {})
        sub_populations = {name: None for name in sub_populations}
        process_data = data.get("processes", {})
        species_data = data.get("species_info", {})

        for population in sub_populations:
            process_objects = self.get_data_by_process(population, process_data)
            population_object = FunctionalPopulation(
                name=population,
                processes=process_objects,
            )
            sub_populations[population] = population_object


        species_name = species_data.get("species_tag", "species")
        species = FunctionalPopulation(
            name=species_name,
            children=sub_populations.values()
        )

        self.species = species


    def get_data_by_process(self, population, process_data):
        processes = []
        print("BEGUG", process_data.items())
        for name, data in process_data.items():
            print("BEGUG2", name, data)
            if population not in data:
                return processes
            population_process_data = data.get(population, {})
            
            if name in ["dynamics", "reproduction"]:
                #"data = pop -> [rate, scalars, variables, outputs]"
                object_data = population_process_data
                object = ProcessBuilder(
                    name=name,
                    data=object_data
                ).object
                processes = [object]
            elif name in ["mortality", "interaction"]:
                #"data = pop -> rates -> id -> [rate, scalars, variables, outputs]"
                objects_data = population_process_data.get("rates", {})
                for id, object_data in objects_data.items():
                    object = ProcessBuilder(
                        name=f"{name}_{id}",
                        data=object_data
                    ).object
                    processes.append(object)
            else: 
                raise ValueError(f"Process {name} not recognised in population {population}.")   
        return processes


class ProcessBuilder(Builder):
    PROCESS_TYPES = {
        "bidemographic": PBDMBiodemographicProcess,
        # Add other process types as needed
    }
    def __init__(self, name: str, data: dict):
        super().__init__(data)
        print(name, data)
        process_type = self.metadata.get("type", "bidemographic")
        process_class = self.PROCESS_TYPES.get(process_type)
        if not process_class:
            raise ValueError(f"Unsupported process type: {process_type}")
        if process_type == "bidemographic":
            # Probably shouldn't have defaults here, but for now...
            variable = data.pop("variable", "M")
            rate_data = data.pop("rate", {})
            scalars_data = data.pop("scalars", []).values()
            print(scalars_data)
            object = PBDMBiodemographicProcess(
                name=name,
                rate=BiodemographicFunction(**rate_data),
                scalars=[ScalarFunction(**scalar) for scalar in scalars_data],
                variable=variable,
                **data # Data shouldn't be free, should be in parameters dict?
            )

        self.object = object

