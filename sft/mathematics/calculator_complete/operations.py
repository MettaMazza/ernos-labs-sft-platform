"""Completion operations layered only on admitted calculator claim 005.

The new circular kernels add certified periodic reduction.  They do not call a
host trigonometric routine and do not turn the circle enclosure into a scalar.
"""

from __future__ import annotations

from fractions import Fraction

from sft.mathematics.calculator.operations import (
    as_interval,
    divide,
    multiply,
    require_scalar,
    subtract,
)
from sft.mathematics.calculator.operations_v2 import circle_constant_enclosure
from sft.mathematics.calculator.operations_v3 import (
    cos_value as _cos_value_v3,
    sin_value as _sin_value_v3,
)
from sft.mathematics.calculator.values import (
    CertifiedInterval,
    ComplexFibre,
    CalculatorHalt,
    Scalar,
    Value,
    forward,
    scalar_from_projection,
    scalar_to_fraction_for_projection,
)


def _nearest_whole(value: Fraction) -> int:
    """Nearest host count, used only to select an exact periodic identity."""

    if value >= 0:
        return (2 * value.numerator + value.denominator) // (2 * value.denominator)
    positive = -value
    return -((2 * positive.numerator + positive.denominator) // (2 * positive.denominator))


def _interval_width(value: CertifiedInterval) -> Fraction:
    return (
        scalar_to_fraction_for_projection(value.upper)
        - scalar_to_fraction_for_projection(value.lower)
    )


def _circle_for_turns(turns: int, places: int) -> CertifiedInterval:
    """Tighten the circle enclosure until counted translation stays certified."""

    terms = max(32, places + 8)
    target = Fraction(1, 10 ** (places + 6))
    while terms <= 512:
        circle = circle_constant_enclosure(terms)
        if abs(turns) * 2 * _interval_width(circle) <= target:
            return circle
        terms *= 2
    raise CalculatorHalt("periodic-reduction certificate exhausted its counted term bound")


def periodic_reduce(value: Value, places: int = 18) -> CertifiedInterval:
    """Enclose an argument after subtracting an exact whole number of turns."""

    if isinstance(value, ComplexFibre):
        raise CalculatorHalt("circular functions require one real Fold fibre")
    source = value if isinstance(value, CertifiedInterval) else as_interval(require_scalar(value))
    lower = scalar_to_fraction_for_projection(source.lower)
    upper = scalar_to_fraction_for_projection(source.upper)
    midpoint = (lower + upper) / 2
    initial_circle = circle_constant_enclosure(32)
    circle_midpoint = (
        scalar_to_fraction_for_projection(initial_circle.lower)
        + scalar_to_fraction_for_projection(initial_circle.upper)
    ) / 2
    turns = _nearest_whole(midpoint / (2 * circle_midpoint))
    circle = _circle_for_turns(turns, places)
    translation = multiply(scalar_from_projection(Fraction(2 * turns)), circle)
    reduced = subtract(source, translation)
    if not isinstance(reduced, CertifiedInterval):
        raise CalculatorHalt("periodic reduction did not retain an exact enclosure")
    return CertifiedInterval(
        reduced.lower,
        reduced.upper,
        reduced.certificate
        + (
            f"whole-turn-translation:{turns}",
            "periodic-identity:angle-minus-whole-times-two-circle",
        ),
    )


def sin_value(value: Value, places: int = 18) -> CertifiedInterval:
    return _sin_value_v3(periodic_reduce(value, places), places)


def cos_value(value: Value, places: int = 18) -> CertifiedInterval:
    return _cos_value_v3(periodic_reduce(value, places), places)


def tan_value(value: Value, places: int = 18) -> CertifiedInterval:
    result = divide(sin_value(value, places + 4), cos_value(value, places + 4))
    if not isinstance(result, CertifiedInterval):
        raise CalculatorHalt("tangent enclosure construction failed")
    return result


__all__ = ("cos_value", "periodic_reduce", "sin_value", "tan_value")
