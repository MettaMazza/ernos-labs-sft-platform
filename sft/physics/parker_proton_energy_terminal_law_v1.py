"""Exact structural proton-energy fraction for the Parker comparison."""

from __future__ import annotations

from fractions import Fraction

from sft.engine import EvidenceMode, ProvenanceClass
from sft.physics.atomic_constants import inverse_fine_structure
from sft.physics.lineage_particle_laws import mediator_count
from sft.physics.structural_constants import StructuralPhysicsSpec, Witness, binary_axis, value_axis


CLAIM_ID = "SFT-PHYS-PARKER-PROTON-ENERGY-TERMINAL-028"
EXPERIMENT_ID = "SFT-EXP-PHYS-PARKER-PROTON-ENERGY-TERMINAL-028"
ONE = Fraction(1, 1)
FORCED_SECTORS = (2, 3, 5, 7)


def alpha_at_stage(stage: str) -> Fraction:
    if stage == "leading":
        inverse = inverse_fine_structure(1)
    elif stage == "terminal":
        inverse = inverse_fine_structure()
    else:
        raise ValueError("alpha stage must be a generated promotion boundary")
    value = ONE / inverse
    if not 0 < value < ONE:
        raise ValueError("alpha must remain a positive exact part of the One")
    return value


def colour_channel_count() -> int:
    channels = mediator_count(3)
    if channels != 8:
        raise ValueError("colour carrier count changed")
    return channels


def proton_energy_fraction(stage: str = "terminal") -> Fraction:
    value = colour_channel_count() * alpha_at_stage(stage) ** 2
    if not 0 < value < ONE:
        raise ValueError("proton energy fraction left the One")
    return value


def historical_leading_fraction() -> Fraction:
    return proton_energy_fraction("leading")


def structural_formula_census() -> tuple[dict[str, object], ...]:
    rows = []
    for sector in FORCED_SECTORS:
        channels = mediator_count(sector)
        for power in (1, 2, 3):
            rows.append({
                "sector": sector,
                "channels": channels,
                "power": power,
                "fraction": Fraction(channels, 1) * alpha_at_stage("terminal") ** power,
                "structurally_selected": sector == 3 and power == 2,
            })
    return tuple(rows)


SPEC = StructuralPhysicsSpec(
    claim_id=CLAIM_ID,
    title="Terminal colour-channel alpha-squared proton-energy fraction",
    statement=(
        "The admitted proton colour sector has exactly three charge labels and "
        "three-squared Take One non-return channels, hence eight carrier channels. "
        "The admitted field-energy composition pairs the electromagnetic amplitude "
        "with itself, so the dimensionless proton energy share is eight times alpha "
        "squared.  At the historical leading alpha rung this is exactly "
        "500000/1173679081; at the complete terminal alpha rung it is exactly "
        "108147617771025486368/253861190227103943729961.  No proton rest-energy "
        "value or Parker observation enters this derivation."
    ),
    dependencies=(
        "SFT-PHYS-CONSTANT-INVERSE-FINE-STRUCTURE-001",
        "SFT-PHYS-FORCE-COMPLETE-SECTOR-INVENTORY-003",
        "SFT-PHYS-NUCLEON-BINDING-TERMINAL-005",
        "SFT-PHYS-MECH-WORK-ENERGY-001",
        "SFT-PHYS-SCATTERING-RUTHERFORD-COMPTON-TERMINAL-006",
        "SFT-MATH-EXACT-ARITHMETIC-001",
        "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
        "SFT-PHYS-MEAS-TARGET-CUSTODY-001",
    ),
    evidence_mode=EvidenceMode.EMPIRICAL,
    generation_rule=(
        "Generate the complete product of proton identity, alpha stage, all four "
        "forced mediator-sector counts, amplitude/energy/cubic powers, typed "
        "composition, rest-scale carrier, prediction custody, provenance, external "
        "comparison and extension forms."
    ),
    grammar_boundary=(
        "The admitted proton, all forced sectors two/three/five/seven and their "
        "mediator counts, the leading and terminal exact alpha rungs, powers one "
        "through three, and a post-seal proton-rest-energy/Parker comparison."
    ),
    axes=(
        binary_axis("particle", "Which object carries the predicted share?", "named-proton-without-composition", "A name does not generate its interaction support.", "admitted-three-colour-proton", "The admitted proton word closes three colour labels while retaining internal colour interaction channels."),
        binary_axis("alpha", "Which exact electromagnetic carrier is current?", "selected-leading-alpha-rung", "The leading rung is retained as a historical control but is not the completed promotion object.", "complete-terminal-alpha-rung", "The admitted finite promotion ladder fixes the terminal exact alpha before measurement."),
        value_axis("channels", "How many internal channels contribute?", (
            ("weak-three-channels", "The binary-sector mediator count does not match proton colour."),
            ("colour-eight-channels", "The proton colour-three pair cells Take the unique return, leaving eight."),
            ("penta-twenty-four-channels", "The penta-sector count belongs to a different forced sector."),
            ("hepta-forty-eight-channels", "The hepta-sector count belongs to a different forced sector."),
        ), "colour-eight-channels", "The proton's admitted colour-three sector uniquely supplies eight mediator channels."),
        value_axis("power", "How does coupling become energy?", (
            ("linear-alpha-amplitude", "A single amplitude is not an energy self-composition."),
            ("alpha-squared-energy", "The energy carrier pairs the interaction amplitude with itself."),
            ("alpha-cubed-extra-interaction", "A third coupling is an unforced extra interaction."),
        ), "alpha-squared-energy", "The admitted amplitude-to-energy relation uses exactly two copies of alpha."),
        binary_axis("composition", "How do channels and energy share compose?", "add-or-average-channel-shares", "Addition or averaging changes the complete channel multiplicity.", "complete-channel-count-times-energy-share", "Every one of the eight channels carries the same alpha-squared energy part exactly once."),
        binary_axis("scale", "What dimensionful scale may later translate the ratio?", "local-plasma-fit-or-free-energy", "A local field or density would be a fitted environmental parameter.", "proton-own-rest-energy-postseal", "The predicted dimensionless proton share can act on the proton's own registered rest-energy carrier only after sealing."),
        binary_axis("target", "Can Parker data select the formula?", "Parker-range-readable-before-seal", "That would permit formula selection by the observation.", "capability-closed-before-Parker-release", "The exact fraction and complete formula census seal without filesystem or target access."),
        binary_axis("provenance", "Was the historical target already known?", "claim-new-blind-discovery", "V2 and the Parker report were already known during V3 reconstruction.", "observational-derivation-explicit", "The reconstruction is target-inaccessible within execution but is not relabelled as historically blind."),
        binary_axis("comparison", "What constitutes the external test?", "treat-approximately-400-as-exact-cutoff", "The paper reports an approximate energy reach and no uncertainty on 400 keV.", "complete-reported-range-and-limitations", "The entire 67-527 keV spectrum range, approximate wording, provenance and adverse formulas are retained."),
        binary_axis("extension", "May another coefficient or local input enter?", "free-local-factor-or-correction", "A free local factor would fit the event.", "no-extra-rule", "Colour channels, terminal alpha square and proton scale exhaust the registered relation."),
    ),
    exact_result=(
        "The terminal structural proton-energy fraction is exactly "
        "108147617771025486368/253861190227103943729961 = 8 alpha_terminal^2. "
        "The superseded leading-rung prediction 500000/1173679081 is retained as "
        "an exact historical control.  External proton mass and Parker observations "
        "remain inaccessible until the derivation seal."
    ),
    induction_base=(
        "The colour-three proton supplies eight complete non-return channels and "
        "one electromagnetic energy self-composition supplies alpha squared."
    ),
    induction_step=(
        "Promotion of one remaining cover direction updates alpha through the "
        "already admitted exact ladder without changing the proton colour count, "
        "energy power or target boundary; the terminal rung has no successor."
    ),
    exclusions=(
        "no local plasma density, magnetic field, Alfven energy or guide-field parameter",
        "no proton mass-energy or Parker spectrum in the candidate generator or survivor decision",
        "no numerical-zero, negative, irrational, imaginary or floating Fold proof magnitude",
        "no claim that approximately 400 keV is an exact measured cutoff or has 0.1-percent precision",
        "no omission of alternative forced-sector/power formulas at the post-seal comparison boundary",
        "no claim of historical blindness; V2 and the external result were known before reconstruction",
    ),
    witnesses=(
        Witness("leading-fraction", "The historical exact fraction reconstructs independently.", historical_leading_fraction() == Fraction(500000, 1173679081)),
        Witness("terminal-fraction", "The completed alpha promotion yields the exact terminal successor.", proton_energy_fraction() == Fraction(108147617771025486368, 253861190227103943729961)),
        Witness("colour-channels", "The proton colour sector has eight mediator channels.", colour_channel_count() == 8),
        Witness("complete-formula-census", "All four forced sectors and three generated powers occur once, with one structurally selected row.", len(structural_formula_census()) == 12 and sum(row["structurally_selected"] for row in structural_formula_census()) == 1),
    ),
    provenance=(ProvenanceClass.OBSERVATIONAL_DERIVATION,),
)


SPEC.validate()


__all__ = (
    "CLAIM_ID",
    "EXPERIMENT_ID",
    "SPEC",
    "alpha_at_stage",
    "colour_channel_count",
    "historical_leading_fraction",
    "proton_energy_fraction",
    "structural_formula_census",
)
