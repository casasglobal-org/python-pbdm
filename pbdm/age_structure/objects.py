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
