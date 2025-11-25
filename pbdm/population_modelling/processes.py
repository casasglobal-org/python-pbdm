from .odes import DifferentialEquations
from .functions import Functions
#from ..abstract.population_objects import CompositePopulationObject
from ..abstract.structured_objects import AgeStructuredCompositePopulationObject

class PopulationProcess(AgeStructuredCompositePopulationObject):
    PARSING_DATA = {
        "rates": Functions,
        "variables": DifferentialEquations,
        "outputs": Functions,
        "functions": Functions
    }
    """
    Keyword Args: Required Parameters
        rates (dict): A parametrisation of a `Functions` object. These are the core rates for the process
            which are passed to variable and/or output calculations.

    Keyword Args: Optional Parameters
        variables (dict): A parametrisation of a `DifferentialEquations` object. These are the process ODEs
            which are written in terms of rates, functions (optional) and other inputs (optional).
        outputs (dict): A parametrisation of a `Functions` object. These are the output funtions of the
            process which are written in terms of rates, functions (optional) and other inputs (optional).
        functions (dict): A parametrisation of a `Functions` object. 

    info: Automated internal wiring:
        There is automated wiring between:

        - rates and their appearance in variables/outputs. For example, if a rate `rate` is
            defined in `rates`, it is connected to any appearance of `rate` in any ODE in `variables`
            and any function in `outputs`.
        - functions and their appearance in rates/variables/outputs, in the same way as above.
        - ODE variables and variable ports on the surface of this object.
        - Output functions and output ports on the surface of this object.

    Example:
        ```json title=".json format"
        {
            "age_structure": {"k": 3, "variable": "A"}, # (1)!
            "rates": {
                "rate_1": {
                    "function": "func_1*a**2",
                    "inputs": {"a": "address.a"}
                },
                "rate_2": {
                    "type": "age_structured",
                    "function": "func_1*func_2*b",
                    "inputs": {"b": "b_value"},
                    "age_structured_inputs": ["func_2"] # (2)!
                }
            },
            "variables": {
                "var_1": {
                    "function": "rate_1*scalar_1*func_3",
                    "inputs": {"scalar_1": "address.scalar_1"}
                },
                "var_2": {
                    "type": "age_structured",
                    "variable": "y", # (3)!
                    "function": "(rate_1 + rate_2)*scalar_2",
                    "age_structured_inputs": ["rate_2"], 
                    "inputs": {"scalar_2": "scalar_2_value"}
                }
            },
            "outputs": {
                "out_1": {
                    "function": "rate_1*func_3"
                },
                "out_2": {
                    "type": "age_structured_integral",
                    "integrand": "rate_2*func_2",
                    "age_structured_inputs": ["rate_2", "func_2"]
                }
            },
            "functions": {
                "func_1": {
                    "function": "2*var_1",
                    "inputs": {"var_1": "name.variables.var_1.var"} # (4)!
                },
                "func_2": {
                    "type": "age_structured",
                    "function": "2*A"
                },
                "func_3": {
                    "function": "c + d",
                    "inputs": {"c": "address.c", "d_value": "1"}
                }
            }
        }
        ```

        1. This example contains age-structured functions. The age-structure parameters can be
            specified here, where needed in the function definitions, or higher up in the hierarchy.
        2. Currently, this age-structured input must be manually specified.
        3. This will expose ODEs with variables `y_1` to `y_k` rather than `var_2_1` to `var_2_k`.
        4. There is no automatic connection from rates/variables/outputs to function inputs.

        In this example, wiring is automatically created between:

        - `functions.func_1` and inputs of `rates.rate_1` and `rates.rate_2`,
        - `functions.func_2_i` (age-structured) and inputs of `rates.rate_2` and `outputs.out_2`,
        - `functions.func_3` and inputs of `outputs.out_1` and `variables.var_1`,
        - `rates.rate_1` and inputs of `outputs.out_1`, `variables.var_1` and `variables.var_2`,
        - `rates.rate_2_i` (age-structured) and inputs of `variables.var_2` and `outputs.out_2`.
    """
    def __init__(self, rates=None, variables=None, outputs=None, functions=None, **ported_object_kwargs):
        """
        Accepts a dict of rates, variables, outputs and functions (from JSON) or a list of Function objects.
        """
        super().__init__(**ported_object_kwargs)
        self.parse_parameters(rates=rates, variables=variables, outputs=outputs, functions=functions)

    def build_object(self):
        action_objects = []
        rates = self.get_parameter("rates", default = {}, search_ancestry=False)
        print("RATES", rates)
        if rates:
            functions_class = self.PARSING_DATA["rates"]
            rates_object = functions_class(name="rates", **rates)
            self.add_children(rates_object)

        variables = self.get_parameter("variables", default={}, search_ancestry=False)
        if variables:
            variables_class = self.PARSING_DATA["variables"]
            variables_object = variables_class(name="variables", **variables)
            self.add_children(variables_object)

        outputs = self.get_parameter("outputs", default={}, search_ancestry=False)
        if outputs:
            functions_class = self.PARSING_DATA["outputs"]
            outputs_object = functions_class(name="outputs", **outputs)
            self.add_children(outputs_object)

        functions = self.get_parameter("functions", default={}, search_ancestry=False)
        if functions:
            functions_class = self.PARSING_DATA["functions"]
            functions_object = functions_class(name="functions", **functions)
            self.add_children(functions_object)

        # TODO: super method
        super().build_object()

        rates_object = self.children["rates"]
        if "variables" in self.children:
            action_objects.append(self.children["variables"])
        if "outputs" in self.children:
            action_objects.append(self.children["outputs"])

        print("ACTION OBJECTS", action_objects)
        for action_object in action_objects:
            print(action_object.children)
            for object in action_object.children.values():
                print("HERE", rates_object.output_ports, object.name, object.input_ports)
                for output in set(rates_object.output_ports).intersection(
                    set(object.input_ports)
                ):
                    #print("HERE", output)
                    object.add_input_connections(
                        **{output: f"{self.name}.rates.{output}"}, overwrite=False
                    )
                    print("Adding input connection", object.address, output, f"{self.name}.rates.{output}")
            #action_object.expose_outputs(self)
            #action_object.expose_variables(self)

        #TODO: Expose

        action_objects.append(rates_object)

        print(self.children)

        if "functions" in self.children:
            functions_object = self.children["functions"]
            print("FUNCTIONS OBJECT", functions_object)
            for child_object in action_objects:
                for object in child_object.children.values():
                    # TODO: This goes into the children manually. Better way?
                    for function in set(functions_object.output_ports).intersection(
                        set(object.input_ports)
                    ):
                        object.add_input_connections(
                            **{function: f"{self.name}.functions.{function}"},
                            overwrite=False,
                        )
                        print("Adding input connection", object.name, function, f"{self.name}.functions.{function}")


class PopulationProcesses(AgeStructuredCompositePopulationObject):
    PARSING_DATA = {
        "processes": PopulationProcess
    }
    def __init__(self, processes=None, **ported_object_kwargs):
        """
        Accepts a dict of processes (from JSON) or a list of PopulationProcess objects.
        """
        super().__init__(**ported_object_kwargs)
        self.parse_parameters(processes=processes)

    def build_object(self):
        processes = self.get_parameter("processes", default={}, search_ancestry=False)
        if processes:
            for process_name, process_data in processes.items():
                # TODO: This should read "type" from the data
                process_class = self.PARSING_DATA["processes"]
                process_object = process_class(name=process_name, **process_data)
                self.add_children(process_object)
        super().build_object()

        # NOTE: Manual expose for now
        # No expose