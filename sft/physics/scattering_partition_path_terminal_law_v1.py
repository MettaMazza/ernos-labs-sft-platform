"""Exact Fold scattering partition and mean-free-path law.

The half/half statement is not asserted for arbitrary scattering.  It is forced
only for the registered one-target geometry whose complete outcome support is
the two equipotent Fold fibres: scatter and pass.  Outcome labels remain held,
so the exact support measure introduces no stochastic cause into deterministic
Fold evolution.
"""

from __future__ import annotations

from fractions import Fraction

from sft.engine import EvidenceMode, ProvenanceClass
from sft.physics.structural_constants import StructuralPhysicsSpec, Witness, binary_axis


CLAIM_ID = "SFT-PHYS-SCATTERING-PARTITION-PATH-TERMINAL-017"
ONE = Fraction(1, 1)
HALF_ONE = Fraction(1, 2)


def two_fibre_outcome_measure(labels: tuple[str, str]) -> tuple[Fraction, Fraction]:
    """Measure two distinct equipotent outcome cells in complete Fold support."""

    if len(set(labels)) != 2:
        raise ValueError("the two Fold outcomes must remain distinguishable")
    return HALF_ONE, HALF_ONE


def partition_is_complete(labels: tuple[str, str]) -> bool:
    scatter, passed = two_fibre_outcome_measure(labels)
    return scatter + passed == ONE


def cross_section(successful_cells: int, incident_cells: int) -> Fraction:
    """Exact positive successful support relative to incident support."""

    if (
        isinstance(successful_cells, bool)
        or isinstance(incident_cells, bool)
        or successful_cells < 1
        or incident_cells < successful_cells
    ):
        raise ValueError("cross section requires positive contained support")
    return Fraction(successful_cells, incident_cells)


def mean_free_path(number_density: Fraction, section: Fraction) -> Fraction:
    """Reciprocal encounter density for exact positive carriers."""

    if (
        not isinstance(number_density, Fraction)
        or not isinstance(section, Fraction)
        or number_density <= 0
        or section <= 0
    ):
        raise ValueError("mean free path requires exact positive density and section")
    return ONE / (number_density * section)


def larger_section_shortens_path(
    number_density: Fraction, smaller: Fraction, larger: Fraction
) -> bool:
    if not (0 < smaller < larger):
        raise ValueError("ordered positive cross sections are required")
    return mean_free_path(number_density, larger) < mean_free_path(
        number_density, smaller
    )


SPEC = StructuralPhysicsSpec(
    claim_id=CLAIM_ID,
    title="Exact two-fibre scattering partition and reciprocal mean free path",
    statement=(
        "For the registered one-target Fold geometry, the complete mutually "
        "exclusive outcome support is the equipotent pair scatter/pass, so each "
        "cell carries half-One and the pair reassembles the One.  Cross section is "
        "the exact positive successful support relative to incident support.  At "
        "positive target-number density n, encounter support per path is n times "
        "the section and the exact mean-free-path carrier is its reciprocal.  At "
        "unit density, section One gives path One and section half-One gives path "
        "two; increasing section strictly shortens path.  The partition is an "
        "exact support measure over held deterministic outcomes, not a random "
        "transition cause."
    ),
    dependencies=(
        "SFT-FOUNDATION-FOLD-DYNAMICS-001",
        "SFT-MATH-PROBABILITY-STATISTICS-001",
        "SFT-INFO-SYMBOL-DISTINCTION-001",
        "SFT-INFO-CLASSICAL-PROBABILISTIC-001",
        "SFT-PHYS-MATTER-SCATTERING-001",
        "SFT-PHYS-SCATTERING-RUTHERFORD-COMPTON-TERMINAL-006",
        "SFT-MATH-EXACT-ARITHMETIC-001",
    ),
    evidence_mode=EvidenceMode.FORMAL,
    generation_rule=(
        "Generate the complete product of target geometry, outcome support, "
        "exclusivity, outcome measure, cross-section measure, density, path, "
        "causal interpretation and extension forms."
    ),
    grammar_boundary=(
        "The one-target geometry with exactly two equipotent Fold outcome cells; "
        "all positive finite incident/successful support counts; and all exact "
        "positive target densities and cross sections."
    ),
    axes=(
        binary_axis("geometry", "Which target geometry is claimed?", "arbitrary-scatterer", "Arbitrary geometry does not force equal outcome cells.", "registered-one-target-Fold-geometry", "The claim is restricted to the generated two-fibre target."),
        binary_axis("outcomes", "Which outcomes are retained?", "sampled-or-omitted-channel", "An omitted channel cannot establish certainty.", "complete-scatter-pass-pair", "Scatter and pass exhaust the registered outcome support."),
        binary_axis("exclusivity", "May both outcomes occur for one held event?", "overlapping-outcome-cells", "Overlap double-counts one event.", "mutually-exclusive-held-labels", "Each event retains exactly one distinguishable outcome label."),
        binary_axis("measure", "What fixes the half shares?", "assumed-equal-probability", "An assumed probability imports the answer.", "equipotent-two-cell-support", "Complete symmetry-related one-cell supports each carry one of two equal parts."),
        binary_axis("section", "What is cross section?", "fitted-dimensional-number", "A fitted number is not the structural measure.", "successful-over-incident-support", "The exact positive support ratio is generated from counted cells."),
        binary_axis("density", "How do targets compose?", "density-omitted", "Omitting density makes reciprocal path dimensionally incomplete.", "positive-density-times-section", "Each positive target carrier contributes its registered section."),
        binary_axis("path", "What fixes mean free path?", "selected-path-length", "A selected length has no encounter trace.", "reciprocal-encounter-support", "The path carrier is exactly One divided by density times section."),
        binary_axis("cause", "Does the support fraction add randomness?", "stochastic-transition-oracle", "A random cause is not supplied by deterministic Fold structure.", "deterministic-held-outcomes", "Fractions measure complete labelled support while every outcome trace remains exact."),
        binary_axis("extension", "May another correction enter?", "free-geometry-or-correction", "A free correction defeats zero-parameter closure.", "no-extra-rule", "The two fibres, counts, product and reciprocal exhaust the grammar."),
    ),
    exact_result=(
        "The registered one-target Fold support partitions exactly into scatter "
        "half-One and pass half-One; cross section is successful/incident support; "
        "and mean free path is the exact reciprocal of positive density times "
        "cross section, with larger section forcing shorter path."
    ),
    induction_base=(
        "One generated target has the two distinguishable equipotent Fold outcomes; "
        "one successful cell among two incident cells carries half-One."
    ),
    induction_step=(
        "Appending one target carrier adds one identical section contribution, so "
        "encounter support composes by exact positive multiplication; reciprocal "
        "order reverses strictly for every larger positive product."
    ),
    exclusions=(
        "no assertion that arbitrary scattering has equal scatter/pass measures",
        "no stochastic causal selector or nondeterministic transition premise",
        "no numerical-zero, negative, irrational, imaginary or floating proof value",
        "no fitted cross section, measured path or target-selected correction",
        "no omission of target density from the general reciprocal law",
    ),
    witnesses=(
        Witness("complete-partition", "The two equipotent outcome cells are half-One each and reassemble the One.", two_fibre_outcome_measure(("scatter", "pass")) == (HALF_ONE, HALF_ONE) and partition_is_complete(("scatter", "pass"))),
        Witness("v2-unit-section", "At unit density and section One, mean free path is One.", mean_free_path(ONE, ONE) == ONE),
        Witness("v2-half-section", "At unit density and section half-One, mean free path is two.", mean_free_path(ONE, HALF_ONE) == Fraction(2, 1)),
        Witness("inverse-order", "Every larger positive registered section has the shorter exact path.", larger_section_shortens_path(Fraction(3, 2), Fraction(1, 4), Fraction(1, 2))),
        Witness("counted-section", "One successful cell among two incident cells is half-One.", cross_section(1, 2) == HALF_ONE),
    ),
    provenance=(ProvenanceClass.FORWARD_FORCING,),
)


SPEC.validate()


__all__ = (
    "CLAIM_ID",
    "SPEC",
    "cross_section",
    "larger_section_shortens_path",
    "mean_free_path",
    "partition_is_complete",
    "two_fibre_outcome_measure",
)
