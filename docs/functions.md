# Functions Overview

### Key Parameters

- `function`: **required** string expression evaluated by the underlying symbolic engine.
- `output_name`: optional string naming the output port; defaults to `"function"`.
- `inputs`: mapping of symbol names to constants or references; passed through `ported_object_kwargs`.
- Any additional keyword arguments are forwarded to `FunctionalPopulationObject` and stored as parameters.

During `build_object()` the class retrieves these parameters, registers the assignment `(output_name, function)`, and delegates to the base class to assemble ports and connections.

## `Functions`

`Functions` extends `CompositePopulationObject` and stores a dictionary or list of `Function` instances. It parses child definitions during initialisation and instantiates each concrete `Function` inside `build_object()`.

```python
F = Function(
    function="3*r",
    output_name="rate",
 This mirrors the Python API and allows the same objects to be reconstructed from configuration files. Leaving out `output_name` in a JSON entry will expose the default port name `"function"`.
    name="birth_rate"
)

G = Function(
    function="-2*s*r",
    inputs={"s": 10},
    output_name="rate",
    name="death_rate"
)

X = Functions(
    functions=[F, G],
    inputs={"r": 5},
    name="dynamics_rates"
)

X.build_object()
```

### How it works

1. `Functions.__init__` parses either
   - a list of `Function` objects, or
   - a dictionary mapping names to raw parameter dictionaries.
2. `Functions.build_object()` iterates through the parsed data and instantiates child `Function` objects.
3. Each child is added to the composite and its single output port is exposed on the composite using the child name. The child is also wired to reference the composite address (e.g. `dynamics_rates.birth_rate`).
4. Finally `CompositePopulationObject.build_object()` connects everything together and prepares the object graph for compilation.

### Useful methods

After constructing the composite you can:

```python
X._process_temp_parameter_connections()
X.search_inputs({"rule": "all"})
X.pre_compile()
print(X.to_data())
X.draw()  # defaults to PNG written next to the Python file
```

- `_process_temp_parameter_connections()` resolves deferred references between functions.
- `search_inputs` inspects required inputs and fills in defaults.
- `pre_compile` prepares the object for execution (e.g. compiling SymPy expressions).
- `to_data` serialises the composite to a dictionary for inspection or export.
- `draw` renders a diagram of the composite.

```python
X.draw(filename="docs/dynamics_rates.svg")  # choose path and format (svg, png, pdf, ...)
```

![Dynamics rates composite](dynamics_rates.svg)

## JSON Structure

Both `Function` and `Functions` can be defined via JSON. A simple configuration might look like:

```json
{
  "functions": {
    "birth_rate": {
      "function": "3*r",
      "output_name": "rate"
    },
    "death_rate": {
      "function": "-2*s*r",
      "inputs": {"s": 10},
      "output_name": "rate"
    }
  }
}
```

This mirrors the Python API and allows the same objects to be reconstructed from configuration files. Leaving out `output_name` in a JSON entry will expose the default port name `"function"`.

## Next Steps

Future documentation can extend this example to show how these functions plug into the wider population dynamics framework, how to reference variables from other components, and how to serialise complete models.
Graphs generated with `draw()` are useful references to drop into the docs folder alongside narrative explanations, as illustrated above.
