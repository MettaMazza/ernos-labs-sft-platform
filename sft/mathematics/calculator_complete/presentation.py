"""Human-readable projections that never replace exact calculator evidence."""

from __future__ import annotations

from sft.mathematics.calculator.values import (
    CertifiedInterval,
    ComplexFibre,
    EmptyOne,
    Value,
    decimal_projection,
    scalar_from_projection,
    scalar_to_fraction_for_projection,
    value_text,
)


def friendly(value: Value, places: int = 16) -> str:
    if isinstance(value, CertifiedInterval):
        lower = scalar_to_fraction_for_projection(value.lower)
        upper = scalar_to_fraction_for_projection(value.upper)
        midpoint = scalar_from_projection((lower + upper) / 2)
        return "≈ " + decimal_projection(midpoint, places)
    if isinstance(value, ComplexFibre):
        return value_text(value, places)
    if isinstance(value, EmptyOne):
        return "0"
    if value.magnitude.denominator == 1:
        return ("" if value.is_forward else "−") + str(value.magnitude.numerator)
    return decimal_projection(value, places)


__all__ = ("friendly",)
