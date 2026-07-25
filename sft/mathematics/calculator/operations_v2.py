"""Corrected circle-enclosure operation for calculator version two.

Version one reversed the upper/lower parity of an alternating arctangent
partial sum.  Its immutable admission receipt is retained as adverse evidence.
This module corrects that certificate without altering the frozen engine or
rewriting the earlier source surface.
"""

from __future__ import annotations

from fractions import Fraction

from .operations import *  # noqa: F401,F403 - the unchanged exact operation surface
from .operations import multiply, subtract
from .values import CertifiedInterval, CalculatorHalt, forward


def _atan_unit_enclosure_v2(x: Fraction, terms: int) -> CertifiedInterval:
    if not Fraction(0) < x <= Fraction(1):
        raise CalculatorHalt("alternating arctangent certificate requires a positive part at most One")
    if terms < 1:
        raise CalculatorHalt("arctangent certificate requires a positive term count")
    positive_total = Fraction(0)
    counter_total = Fraction(0)
    for index in range(terms):
        term = x ** (2 * index + 1) / (2 * index + 1)
        if index % 2:
            counter_total += term
        else:
            positive_total += term
    partial = positive_total - counter_total
    next_term = x ** (2 * terms + 1) / (2 * terms + 1)
    # An odd number of terms ends on a positive term and is the upper
    # alternating bound.  An even number ends on a subtracted term and is the
    # lower bound.  The next term supplies the opposite rational endpoint.
    if terms % 2:
        lower, upper = partial - next_term, partial
    else:
        lower, upper = partial, partial + next_term
    return CertifiedInterval(
        forward(lower),
        forward(upper),
        (f"atan-alternating-terms:{terms}", f"next-term-bound:{next_term}", "parity-checked:v2"),
    )


def circle_constant_enclosure(terms: int = 32) -> CertifiedInterval:
    """Enclose the circle constant with exact angle-composition evidence."""

    fifth = _atan_unit_enclosure_v2(Fraction(1, 5), terms)
    two_thirty_ninth = _atan_unit_enclosure_v2(Fraction(1, 239), terms)
    result = subtract(multiply(forward(16), fifth), multiply(forward(4), two_thirty_ninth))
    if not isinstance(result, CertifiedInterval):
        raise CalculatorHalt("circle enclosure construction failed")
    return CertifiedInterval(
        result.lower,
        result.upper,
        result.certificate
        + (
            "exact-angle-composition:16*atan(1/5)-4*atan(1/239)",
            "tangent-certificate:tan(4*atan(1/5)-atan(1/239))=One",
        ),
    )
