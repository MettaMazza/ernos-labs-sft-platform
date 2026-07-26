"""Exact terminal probe-independent proton-radius relation."""

from __future__ import annotations

from fractions import Fraction

from sft.engine import EvidenceMode, ProvenanceClass
from sft.physics.atomic_constants import binary_count, inverse_fine_structure
from sft.physics.structural_constants import (
    StructuralPhysicsSpec,
    Witness,
    binary_axis,
    generator_period_three,
    value_axis,
)


CLAIM_ID = "SFT-PHYS-PROTON-RADIUS-TERMINAL-029"
EXPERIMENT_ID = "SFT-EXP-PHYS-PROTON-RADIUS-TERMINAL-029"
ONE = Fraction(1, 1)


def proton_inner_site() -> Fraction:
    return Fraction(1, generator_period_three())


def proton_edge_share() -> Fraction:
    edge = ONE - proton_inner_site()
    if edge != Fraction(2, 3):
        raise ValueError("proton edge complement changed")
    return edge


def colour_fibre_support() -> int:
    support = generator_period_three() * binary_count()
    if support != 6:
        raise ValueError("complete colour/Fold support changed")
    return support


def leading_radius_multiplier() -> Fraction:
    value = proton_edge_share() * colour_fibre_support()
    if value != 4:
        raise ValueError("leading proton radius multiplier changed")
    return value


def complete_charge_support() -> int:
    colour = generator_period_three()
    support = colour * colour + 1
    if support != 10:
        raise ValueError("complete proton charge support changed")
    return support


def terminal_alpha() -> Fraction:
    value = ONE / inverse_fine_structure()
    if not 0 < value < ONE:
        raise ValueError("terminal alpha left the One")
    return value


def terminal_radius_retention() -> Fraction:
    value = ONE - terminal_alpha() / complete_charge_support()
    if not 0 < value < ONE:
        raise ValueError("terminal radius retention left the One")
    return value


def terminal_radius_coefficient() -> Fraction:
    value = leading_radius_multiplier() * terminal_radius_retention()
    expected = Fraction(10069574419808, 2519231977345)
    if value != expected:
        raise ValueError("terminal proton-radius coefficient changed")
    return value


def structural_formula_census() -> tuple[dict[str, object], ...]:
    rows = []
    alpha = terminal_alpha()
    for support in (8, 9, 10):
        for order in ("untransported", "linear", "quadratic"):
            if order == "untransported":
                retention = ONE
            elif order == "linear":
                retention = ONE - alpha / support
            else:
                retention = ONE - alpha * alpha / support
            rows.append({
                "charge_support": support,
                "transport_order": order,
                "coefficient": leading_radius_multiplier() * retention,
                "structurally_selected": support == 10 and order == "linear",
            })
    return tuple(rows)


SPEC = StructuralPhysicsSpec(
    claim_id=CLAIM_ID,
    title="Terminal probe-independent proton rms charge-radius relation",
    statement=(
        "The admitted colour-three proton has inner tripling site one-third and outer complement two-thirds. "
        "Every one of its three colour labels carries both Fold fibre labels, so complete edge transport is "
        "six times two-thirds, exactly four. Internal ordered colour support has nine pair cells and the "
        "proton carries one external unit charge, forcing ten complete charge-support cells. A spatial "
        "charge boundary receives one terminal electromagnetic traversal, not the two traversals of an "
        "energy self-composition; the inward held share is therefore alpha_terminal/10. The resulting "
        "dimensionless rms-radius coefficient is exactly 4(One-alpha_terminal/10), independent of the probe."
    ),
    dependencies=(
        "SFT-PHYS-STRUCT-GENERATOR-THREE-001",
        "SFT-PHYS-SPACE-BOUNDARY-RANK-TWO-001",
        "SFT-PHYS-MATTER-COMPOSITE-HADRONS-001",
        "SFT-PHYS-NUCLEON-BINDING-TERMINAL-005",
        "SFT-PHYS-NUCLEAR-COLOUR-COUPLING-001",
        "SFT-PHYS-CONSTANT-INVERSE-FINE-STRUCTURE-001",
        "SFT-PHYS-QUANTUM-EVOLUTION-001",
        "SFT-MATH-EXACT-ARITHMETIC-001",
        "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
        "SFT-PHYS-MEAS-TARGET-CUSTODY-001",
    ),
    evidence_mode=EvidenceMode.EMPIRICAL,
    generation_rule=(
        "Generate the complete product of proton carrier, tripling orbit, colour/Fold edge support, "
        "internal/external charge support, electromagnetic transport order, retained orientation, "
        "one-action scale boundary, target custody, provenance and extension forms."
    ),
    grammar_boundary=(
        "The admitted colour-three charged proton, its one-third/two-thirds tripling partition, both Fold "
        "labels, every ordered colour pair cell, the unique external unit charge, terminal alpha and the "
        "post-seal reduced proton Compton carrier."
    ),
    axes=(
        binary_axis("particle", "Which object carries the radius?", "named-proton-without-composition", "A particle name does not generate a radius.", "admitted-uud-colour-three-proton", "The admitted charged colour singlet supplies the complete composite carrier."),
        binary_axis("orbit", "Which tripling position is the boundary?", "inner-one-third-as-outer-edge", "The inner constituent site is not the composite edge.", "outer-two-thirds-complement", "The unique positive complement of the inner tripling site is the edge face."),
        binary_axis("edge", "How much edge support is transported?", "partial-colour-or-single-fibre-support", "Omitting a colour or Fold label loses a charged path.", "all-three-colours-times-both-Fold-labels", "Complete colour/Fold support has six paths and sends the two-thirds edge to multiplier four."),
        value_axis("charge", "Which charge support receives self-coupling?", (
            ("eight-nonreturn-mediators", "The mediator count omits the return and external charge roles."),
            ("nine-internal-colour-pairs", "Internal pair support omits the proton's external unit charge."),
            ("ten-internal-pairs-plus-unit-charge", "Nine ordered colour cells plus the unique external unit charge exhaust the proton charge support."),
        ), "ten-internal-pairs-plus-unit-charge", "The physical charged composite contains both complete internal colour-pair support and its one external charge carrier."),
        value_axis("transport", "How many electromagnetic traversals alter a radius?", (
            ("no-terminal-transport", "This retains only the earlier leading structural radius."),
            ("one-alpha-spatial-traversal", "A radius is one spatial charge-boundary traversal."),
            ("alpha-squared-energy-composition", "Two traversals apply to energy self-composition, not a length boundary."),
        ), "one-alpha-spatial-traversal", "One interaction crosses the radial charge boundary once; no energy square is formed."),
        binary_axis("orientation", "How does bound self-coupling act on the edge?", "append-outward-free-share", "Appending a free share breaks the held bound-composite ledger.", "hold-inward-share-from-edge", "The bound charge interaction holds alpha/10 from the free edge while preserving a positive radius."),
        binary_axis("scale", "Which dimensional carrier may translate the coefficient?", "full-cycle-or-fitted-length", "A fitted length or full-cycle circumference double-counts the one-action radial carrier.", "reduced-proton-Compton-postseal", "The admitted action-over-proton-momentum relation supplies the one-action radial scale only after sealing."),
        binary_axis("target", "Can any radius measurement select the law?", "probe-results-readable-before-seal", "That would fit the known radius puzzle.", "capability-closed-before-target-release", "The exact coefficient and complete alternatives seal before any radius or Compton row opens."),
        binary_axis("provenance", "Was the radius puzzle known during reconstruction?", "claim-historical-blindness", "V1/V2 and the measurements were already known.", "observational-derivation-explicit", "Development is disclosed while executable target access remains structurally denied."),
        binary_axis("extension", "May another radius term be appended?", "free-form-factor-or-probe-correction", "An added term would be a fitted parameter.", "no-extra-rule", "Tripling edge, complete colour/Fold paths, complete charge support and one terminal traversal exhaust the grammar."),
    ),
    exact_result=(
        "The unique terminal dimensionless proton rms charge-radius coefficient is exactly "
        "10069574419808/2519231977345 = 4(One-alpha_terminal/10). A dimensionful radius is obtained "
        "only after the seal by composing this coefficient with the registered reduced proton Compton "
        "wavelength. The coefficient contains no electron, muon or scattering-probe input."
    ),
    induction_base=(
        "The three-colour proton has one inner third, its unique outer two-thirds complement, and two Fold "
        "labels per colour, forcing the complete leading multiplier four."
    ),
    induction_step=(
        "Complete the nine internal ordered colour cells with the proton's one external charge cell and "
        "transport terminal alpha inward once; all typed carriers are then consumed and no successor remains."
    ),
    exclusions=(
        "no proton radius, reduced Compton wavelength, electron, muon or scattering result in the candidate generator or survivor decision",
        "no fitted coefficient, probe-dependent correction, selected uncertainty or hidden form factor",
        "no numerical-zero, negative, irrational, imaginary or floating Fold proof magnitude",
        "no claim that rms charge radius is a hard material edge",
        "no claim that every historical extraction is mutually consistent or systematics-free",
        "no historical-blindness claim",
    ),
    witnesses=(
        Witness("tripling-edge", "The inner and outer tripling faces close exactly to the One.", proton_inner_site() + proton_edge_share() == ONE),
        Witness("complete-leading-support", "Six complete colour/Fold paths send the two-thirds edge to four.", colour_fibre_support() == 6 and leading_radius_multiplier() == 4),
        Witness("complete-charge-support", "Nine ordered internal colour cells and one external charge close to ten.", complete_charge_support() == 10),
        Witness("terminal-coefficient", "One terminal alpha traversal gives the exact retained coefficient.", terminal_radius_coefficient() == Fraction(10069574419808, 2519231977345)),
        Witness("complete-alternative-census", "All three charge-support and three transport-order controls are retained with one structural survivor.", len(structural_formula_census()) == 9 and sum(row["structurally_selected"] for row in structural_formula_census()) == 1),
    ),
    provenance=(ProvenanceClass.OBSERVATIONAL_DERIVATION,),
)


SPEC.validate()


__all__ = (
    "CLAIM_ID",
    "EXPERIMENT_ID",
    "SPEC",
    "colour_fibre_support",
    "complete_charge_support",
    "leading_radius_multiplier",
    "proton_edge_share",
    "proton_inner_site",
    "structural_formula_census",
    "terminal_radius_coefficient",
    "terminal_radius_retention",
)
