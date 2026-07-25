"""Corrected, superseding SFT scientific-calculator law."""

from __future__ import annotations

from dataclasses import replace
from fractions import Fraction

from sft.mathematics.generated_law import Witness

from .law import SPEC as V1_SPEC
from .operations_v2 import _atan_unit_enclosure_v2, circle_constant_enclosure
from .values import CertifiedInterval, compare_scalar


CLAIM_ID = "SFT-MATH-SCIENTIFIC-CALCULATOR-004"


def _tan_double(tangent: Fraction) -> Fraction:
    return 2 * tangent / (1 - tangent * tangent)


def _angle_identity_is_exact() -> bool:
    tangent_four_fifths = _tan_double(_tan_double(Fraction(1, 5)))
    tangent_difference = (tangent_four_fifths - Fraction(1, 239)) / (
        1 + tangent_four_fifths * Fraction(1, 239)
    )
    return tangent_four_fifths == Fraction(120, 119) and tangent_difference == 1


_atan_even = _atan_unit_enclosure_v2(Fraction(1, 5), 4)
_atan_odd = _atan_unit_enclosure_v2(Fraction(1, 5), 5)
_circle = circle_constant_enclosure(32)
_retained = tuple(
    witness for witness in V1_SPEC.witnesses if witness.name != "transcendental-enclosure"
)


SPEC = replace(
    V1_SPEC,
    claim_id=CLAIM_ID,
    title="Exact traced SFT-native scientific calculator with corrected enclosure parity",
    witnesses=_retained
    + (
        Witness(
            "alternating-parity-certificate",
            "Odd arctangent partial counts supply upper bounds; even counts supply lower bounds, with the next exact part closing the opposite endpoint.",
            isinstance(_atan_even, CertifiedInterval)
            and isinstance(_atan_odd, CertifiedInterval)
            and "parity-checked:v2" in _atan_even.certificate
            and "parity-checked:v2" in _atan_odd.certificate
            and compare_scalar(_atan_even.lower, _atan_even.upper) < 0
            and compare_scalar(_atan_odd.lower, _atan_odd.upper) < 0,
        ),
        Witness(
            "exact-angle-composition",
            "Two exact tangent doublings give 120/119 and subtraction of atan(1/239) gives tangent One, certifying the quarter-turn identity without decimal target selection.",
            _angle_identity_is_exact(),
        ),
        Witness(
            "corrected-circle-enclosure",
            "The circle constant has ordered exact rational endpoints carrying the corrected alternating parity and exact angle-composition trace.",
            isinstance(_circle, CertifiedInterval)
            and compare_scalar(_circle.lower, _circle.upper) < 0
            and any("parity-checked:v2" == item for item in _circle.certificate)
            and any("tangent-certificate" in item for item in _circle.certificate),
        ),
    ),
    check=(
        "Execute all 1,024 generated semantics, require the sole all-preserving survivor, run the exact arithmetic, "
        "root, combinatorial, transcendental, orthogonal, parser, trace and halt witnesses, verify alternating-series "
        "endpoint parity and the exact tangent-composition identity, run four adverse controls, and independently "
        "regenerate both the full product and operational certificates."
    ),
    limitations=(
        V1_SPEC.limitations
        + " The earlier 003 receipt is preserved as adverse evidence because its arctangent endpoint parity was "
        "reversed; this 004 law supersedes it and does not depend on it."
    ),
)
