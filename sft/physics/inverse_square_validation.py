"""Post-derivation empirical checker for the forced inverse-square exponent.

The formal exponent is already sealed by ``SFT-PHYS-FIELD-INVERSE-SQUARE-001``.
This module cannot derive or alter it.  It converts one source-bound reported
positive exponent interval into exact rational endpoints, enumerates every
positive integer inside that interval, and compares the complete survivor set
with the sealed consequence.
"""

from __future__ import annotations

from fractions import Fraction
import json
from pathlib import Path

from sft.engine.exact import PositiveCount
from sft.physics.generated_empirical_law import (
    BlindExternalMeasurementValidator,
    EmpiricalPhysicsSpec,
    ExternalTargetRow,
    empirical_dimensions,
)


CLAIM_ID = "SFT-PHYS-VALIDATION-INVERSE-SQUARE-001"
EXPERIMENT_ID = "SFT-EXP-PHYS-VALIDATION-INVERSE-SQUARE-001"
SOURCE_ID = "APS-WILLIAMS-FALLER-HILL-1971-COULOMB"
SOURCE_PATH = "experiments/external_sources/physics/snapshots/aps-prl-26-721-source-record.json"
SOURCE_HASH = "sha256:03840a7b8b64574c764c40eb91ba6e0ee2c413548ff0d317ca5c8334f72308bc"
AGREEMENT_LABEL = "reported-exponent-interval-has-sole-positive-integer-two"


def positive_integer_exponents_in_interval(
    lower: Fraction,
    upper: Fraction,
) -> tuple[PositiveCount, ...]:
    """Enumerate every positive integer exponent inside exact positive bounds."""

    if not isinstance(lower, Fraction) or not isinstance(upper, Fraction):
        raise ValueError("reported exponent bounds must be exact fractions")
    if lower <= 0 or lower > upper:
        raise ValueError("reported exponent interval must be positive and ordered")
    survivors: list[PositiveCount] = []
    candidate = PositiveCount(1)
    while Fraction(candidate.value, 1) <= upper:
        if lower <= candidate.value:
            survivors.append(candidate)
        candidate = PositiveCount(candidate.value + 1)
    return tuple(survivors)


REPORTED_LOWER = Fraction(199999999999999996, 100000000000000000)
REPORTED_UPPER = Fraction(200000000000000058, 100000000000000000)
REPORTED_SURVIVORS = positive_integer_exponents_in_interval(REPORTED_LOWER, REPORTED_UPPER)


SPEC = EmpiricalPhysicsSpec(
    claim_id=CLAIM_ID,
    title="Post-seal experimental agreement of the inverse-square exponent",
    statement=(
        "After the Fold structure independently forces and seals positive integer exponent two, the Williams, "
        "Faller and Hill Coulomb-law experiment reports q = (2.7 +/- 3.1) x 10^-16 in the tested form "
        "1/r^(2+q).  Converting only the reported finite interval to exact positive rational exponent bounds "
        "and enumerating every positive integer inside them leaves two as the sole compatible exponent."
    ),
    dependencies=(
        "SFT-PHYS-FIELD-INVERSE-SQUARE-001",
        "SFT-PHYS-MEAS-BOUNDARY-GROWTH-001",
        "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
        "SFT-PHYS-MEAS-CAPABILITY-PREDICTION-001",
        "SFT-PHYS-MEAS-TARGET-CUSTODY-001",
        "SFT-PHYS-MEAS-HOSTILE-PACKAGE-001",
        "SFT-PHYS-MEAS-VALUE-RECORD-001",
        "SFT-PHYS-MEAS-UNCERTAINTY-001",
        "SFT-MATH-EXACT-ARITHMETIC-001",
        "SFT-MATH-ORDER-LATTICE-001",
    ),
    generation_rule=(
        "Generate the complete product of physical carrier, inverse-square relation, provenance, capability-"
        "closed prediction, separate measurement record, complete rows, positive-successor closure and no-extra-"
        "rule forms."
    ),
    grammar_boundary=(
        "All exact post-seal comparisons between the forced positive integer exponent and the complete finite "
        "positive exponent interval reported by the registered primary experiment."
    ),
    dimensions=empirical_dimensions(
        "forced-exponent-two-versus-complete-reported-interval",
        "The structural exponent is sealed first; the complete source-bound interval is then converted to exact "
        "positive rational endpoints and exhaustively checked for compatible positive integers.",
    ),
    exact_result=(
        "The complete reported experimental exponent interval contains exactly one positive integer exponent, "
        "two, agreeing with the independently sealed inverse-square law."
    ),
    induction_base="The first positive integer receives one exact below, inside or above interval decision.",
    induction_step=(
        "Advance by one positive successor until the candidate exceeds the upper endpoint; every later positive "
        "integer is then also above it, closing the family without a completed infinite object."
    ),
    exclusions=(
        "no measured result used by the formal inverse-square derivation",
        "no logarithm, regression, floating fit or best-match selection in the checker",
        "no semantic numerical zero, negative, irrational or imaginary proof value",
        "no omission of the reported central value or uncertainty",
        "no claim that interval agreement proves an exact physical value",
    ),
    operational_witnesses=(
        (
            "reported-interval-census",
            "The complete exact reported interval contains only positive integer exponent two.",
            REPORTED_SURVIVORS == (PositiveCount(2),),
        ),
        (
            "lower-bound-control",
            "The first positive integer lies strictly below the reported interval.",
            Fraction(1, 1) < REPORTED_LOWER,
        ),
        (
            "upper-bound-control",
            "The third positive integer lies strictly above the reported interval.",
            REPORTED_UPPER < Fraction(3, 1),
        ),
    ),
    experiment_id=EXPERIMENT_ID,
    expected_observation_label=AGREEMENT_LABEL,
    target_rows=(
        ExternalTargetRow(
            target_id="APS-PRL-26-721-REPORTED-EXPONENT-INTERVAL",
            source_id=SOURCE_ID,
            source_locator="publisher abstract; DOI 10.1103/PhysRevLett.26.721",
            observed_label=AGREEMENT_LABEL,
        ),
    ),
    source_snapshot_path=SOURCE_PATH,
    source_snapshot_hash=SOURCE_HASH,
    falsification_condition=(
        "The complete registered reported interval does not contain exponent two, contains another positive "
        "integer exponent, differs from its source hash, is opened into the formal derivation, or a tampered "
        "comparison is accepted."
    ),
)


class InverseSquareExternalValidator:
    """Reconstruct the numeric target from the source record before comparison."""

    def __init__(self, root: Path):
        self.root = root.resolve()

    def validate(self, sealed):
        payload = json.loads((self.root / SOURCE_PATH).read_text(encoding="utf-8"))
        observation = payload["reported_observation"]
        lower_row = observation["positive_exponent_interval"]["lower"]
        upper_row = observation["positive_exponent_interval"]["upper"]
        lower = Fraction(lower_row["numerator"], lower_row["denominator"])
        upper = Fraction(upper_row["numerator"], upper_row["denominator"])
        if payload["source_id"] != SOURCE_ID:
            raise ValueError("inverse-square target source identity changed")
        if payload["doi"].lower() != "10.1103/physrevlett.26.721":
            raise ValueError("inverse-square target DOI changed")
        if positive_integer_exponents_in_interval(lower, upper) != (PositiveCount(2),):
            raise ValueError("registered experimental interval does not uniquely retain exponent two")
        return BlindExternalMeasurementValidator(self.root, SPEC).validate(sealed)


SPEC.validate()


__all__ = (
    "AGREEMENT_LABEL",
    "CLAIM_ID",
    "EXPERIMENT_ID",
    "InverseSquareExternalValidator",
    "REPORTED_LOWER",
    "REPORTED_SURVIVORS",
    "REPORTED_UPPER",
    "SOURCE_HASH",
    "SOURCE_ID",
    "SOURCE_PATH",
    "SPEC",
    "positive_integer_exponents_in_interval",
)
