# ODE Components Overview

Population dynamics rely on ordinary differential equations to describe how state variables evolve over time. This module provides three layers of abstraction:

- `DifferentialEquation`: single ODE definition with one exposed variable.
- `ODESystem`: tightly-coupled system sharing a set of variables.
- `DifferentialEquations`: composite container that organises many named ODE components.

Each class follows the same pattern as the functional API: parse parameters in `__init__`, then build connections inside `build_object()`.

## `DifferentialEquation`

`DifferentialEquation` inherits from `VariablePopulationObject`. It wraps a symbolic expression and exposes it through a variable port. The expression is parsed later by the backend (e.g. SymPy).

```python
from pbdm.population_modelling.odes import DifferentialEquation

prey_rate = DifferentialEquation(
  name="prey_rate",
  function="a*x - b*x*y",
  variable="x"
)

mortality = DifferentialEquation(
  name="mortality",
  function="-c*y"  # variable defaults to "var"
)
```

### Key Parameters

- `function`: **required** string expression for the derivative.
- `variable`: optional string naming the exposed variable; defaults to `"var"` when omitted.
- `inputs`: symbol bindings passed through `ported_object_kwargs`.
- Any other keyword arguments are stored by `VariablePopulationObject`.

During `build_object()` the class registers the assignment `(variable, function)` and lets the base class configure ports and connections.

## `ODESystem`

`ODESystem` is a convenience wrapper for coupled equations that naturally share a set of variables. Instead of instantiating multiple `DifferentialEquation` objects, you can declare the variable-expression pairs in one block.

```python
from pbdm.population_modelling.odes import ODESystem

lotka_volterra = ODESystem(
  name="lotka_volterra",
  odes={
    "x": "a*x - b*x*y",
    "y": "d*x*y - c*y"
  }
)

lotka_volterra.build_object()
```

`ODESystem` expects an `odes` dictionary where each key is the variable name and the value is the corresponding expression. During `build_object()` it registers all assignments with `add_variable_assignments` before delegating to the base class.

## `DifferentialEquations`

`DifferentialEquations` mirrors the `Functions` composite. It accepts either a list of `DifferentialEquation` instances or a dictionary of raw definitions.

```python
from pbdm.population_modelling.odes import DifferentialEquation, DifferentialEquations

prey_rate = DifferentialEquation(
  name="prey_rate",
  function="a*x - b*x*y",
  variable="x",
  inputs={"y": "pred_prey.predator_rate.y"}
)

predator_rate = DifferentialEquation(
  name="predator_rate",
  function="d*x*y - c*y",
  variable="y",
  inputs={"x": "pred_prey.prey_rate.x"}
)

pred_prey = DifferentialEquations(
  name="pred_prey",
  odes=[prey_rate, predator_rate],
  inputs={"a": 1.2, "b": 0.6, "d": 0.5, "c": 0.8}
)

pred_prey.build_object()
pred_prey._process_temp_parameter_connections()
pred_prey.search_inputs({"rule": "all"})
pred_prey.pre_compile()
print(pred_prey.to_data())
pred_prey.draw()  # default PNG
```

```python
pred_prey.draw(filename="docs/pred_prey.svg")
```

![Predator-prey ODE composite](pred_prey.svg)

The composite iterates through the parsed definitions, instantiates each child (`DifferentialEquation` by default), and adds the child to itself. After `super().build_object()` runs, the composite exposes each child variable port at the composite level, similar to the `Functions` class. Cross-dependencies (e.g. predator dynamics depending on the prey state) must be wired manually via the `inputs` mapping, as shown above.

### Dictionary form

You can provide the same model via JSON-like data:

```json
{
  "name": "pred_prey",
  "inputs": {"a": 1.2, "b": 0.6, "d": 0.5, "c": 0.8},
  "odes": {
    "prey_rate": {
      "function": "a*x - b*x*y",
      "variable": "x",
      "inputs": {"y": "pred_prey.predator_rate.y"}
    },
    "predator_rate": {
      "function": "d*x*y - c*y",
      "variable": "y",
      "inputs": {"x": "pred_prey.prey_rate.x"}
    }
  }
}
```

Omitting `variable` in any entry will expose the default port name `"var"`.

## Usage checklist

Once you instantiate either `ODESystem` or `DifferentialEquations`, the typical preparation pipeline is:

1. `build_object()`
2. `_process_temp_parameter_connections()` (if deferred references exist)
3. `search_inputs()` to resolve required inputs
4. `pre_compile()` to generate executable forms
5. `to_data()` for inspection or serialisation
6. `draw()` to export a diagram (supports `filename="docs/pred_prey.svg"`, `filename="model.pdf"`, etc.)

This mirrors the workflow for functional components, making it easier to swap or combine functions and ODEs inside larger population models.

> **Note:** SymPy reserves certain names (e.g. `gamma`) for special functions. Use neutral identifiers such as `a`, `b`, `c`, `d` or append suffixes (`gamma_`) to avoid name clashes when strings are parsed into symbolic expressions.

> **Tip:** When one equation references another equation's state, provide an explicit connection via `inputs`. The value should be the fully-qualified address of the target variable port (e.g. `"pred_prey.prey_rate.x"`). This keeps every dependency explicit and prevents missing-input warnings during `search_inputs()`.
