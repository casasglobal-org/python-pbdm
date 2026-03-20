"""Age-structured object specializations built from structured object bases."""

from __future__ import annotations

from ..abstract.structured_objects import (
    StructuredCompositePopulationObject,
    StructuredFunctionalPopulationObject,
    StructuredVariablePopulationObject,
)
from .base import AgeStructuredPopulationMixin


class AgeStructuredFunctionalPopulationObject(
    AgeStructuredPopulationMixin, StructuredFunctionalPopulationObject
):
    """Functional population object preconfigured with age-axis behaviour."""

    PARSING_DATA = StructuredFunctionalPopulationObject.PARSING_DATA | {"age_axis": dict}

    def __init__(
        self,
        age_axis: dict | None = None,
        structured_axes: dict | None = None,
        **ported_object_kwargs,
    ):
        super().__init__(
            age_axis=age_axis,
            structured_axes=structured_axes,
            **ported_object_kwargs,
        )


class AgeStructuredVariablePopulationObject(
    AgeStructuredPopulationMixin, StructuredVariablePopulationObject
):
    """Variable population object preconfigured with age-axis behaviour."""

    PARSING_DATA = StructuredVariablePopulationObject.PARSING_DATA | {"age_axis": dict}

    def __init__(
        self,
        age_axis: dict | None = None,
        structured_axes: dict | None = None,
        **ported_object_kwargs,
    ):
        super().__init__(
            age_axis=age_axis,
            structured_axes=structured_axes,
            **ported_object_kwargs,
        )


class AgeStructuredCompositePopulationObject(
    AgeStructuredPopulationMixin, StructuredCompositePopulationObject
):
    """Composite population object that propagates age-axis behaviour to children."""

    PARSING_DATA = StructuredCompositePopulationObject.PARSING_DATA | {"age_axis": dict}

    def __init__(
        self,
        age_axis: dict | None = None,
        structured_axes: dict | None = None,
        **ported_object_kwargs,
    ):
        super().__init__(
            age_axis=age_axis,
            structured_axes=structured_axes,
            **ported_object_kwargs,
        )


__all__ = [
    "AgeStructuredFunctionalPopulationObject",
    "AgeStructuredVariablePopulationObject",
    "AgeStructuredCompositePopulationObject",
]
