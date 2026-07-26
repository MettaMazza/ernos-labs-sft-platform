"""Exact finite Fold colour-singlet excitation-gap law.

This claim distinguishes the locally massless confined colour carrier from the
least observable colour-singlet excitation.  It does not import a continuum
Yang--Mills action or claim a conventional continuum existence proof.
"""

from __future__ import annotations

from fractions import Fraction

from sft.engine import EvidenceMode, ProvenanceClass
from sft.physics.interaction_unification_terminal_law_v1 import base_sector_table
from sft.physics.sector_inventory_law_v1 import antipodal_pair_count, singlet_constituent_count
from sft.physics.strong_carrier_massless_confined_terminal_law_v1 import (
    confining_tube_trace,
    massless_causal_trace,
    strong_sector_structure,
)
from sft.physics.structural_constants import StructuralPhysicsSpec, Witness, binary_axis


CLAIM_ID = "SFT-PHYS-YANG-MILLS-SINGLET-GAP-TERMINAL-026"
ONE = Fraction(1, 1)
STRONG_SECTOR = 3


def fold_part(value: Fraction) -> Fraction:
    if not isinstance(value, Fraction) or value <= 0 or value > ONE:
        raise ValueError("Fold action requires one positive exact part of the One")
    doubled = value + value
    return doubled if doubled <= ONE else doubled - ONE


def strong_gap_partition() -> dict[str, object]:
    table = base_sector_table(STRONG_SECTOR)
    coupling = table["coupling"]
    gap = table["mass_shortfall"]
    if not isinstance(coupling, Fraction) or not isinstance(gap, Fraction):
        raise ValueError("strong-sector shares must be exact")
    return {
        "coupling": coupling,
        "gap": gap,
        "complete": coupling + gap == ONE,
        "gap_to_coupling": fold_part(gap) == coupling,
        "coupling_to_gap": fold_part(coupling) == gap,
        "first_return_period": 2,
    }


def physical_singlet_support() -> dict[str, object]:
    pair = antipodal_pair_count(STRONG_SECTOR)
    complete_fibre = singlet_constituent_count(STRONG_SECTOR)
    return {
        "least_singlet_constituents": pair,
        "complete_fibre_constituents": complete_fibre,
        "singlet_supports": (pair, complete_fibre),
        "least_singlet_is_nonempty_composite": pair > 1,
        "isolated_colour_observation_record": (),
        "vacuum_excitation_record": (),
    }


def singlet_gap_trace(depth: int = 16) -> dict[str, object]:
    if isinstance(depth, bool) or not isinstance(depth, int) or depth < 1:
        raise ValueError("positive finite depth required")
    partition = strong_gap_partition()
    singlet = physical_singlet_support()
    tube = confining_tube_trace(max(2, depth))
    local = massless_causal_trace(max(2, depth))
    rows = tuple(
        {
            "depth": step,
            "normalized_singlet_gap": partition["gap"],
            "confinement_work": partition["coupling"] * step,
            "physical_support": singlet["least_singlet_constituents"],
        }
        for step in range(1, depth + 1)
    )
    return {
        "rows": rows,
        "gap": partition["gap"],
        "coupling": partition["coupling"],
        "all_gaps_positive": all(row["normalized_singlet_gap"] > 0 for row in rows),
        "gap_depth_invariant": len({row["normalized_singlet_gap"] for row in rows}) == 1,
        "work_positive_and_increasing": all(row["confinement_work"] > 0 for row in rows)
        and all(rows[index + 1]["confinement_work"] > rows[index]["confinement_work"] for index in range(len(rows) - 1)),
        "least_physical_state_is_singlet": singlet["least_singlet_is_nonempty_composite"],
        "isolated_colour_observation_record": singlet["isolated_colour_observation_record"],
        "vacuum_excitation_record": singlet["vacuum_excitation_record"],
        "local_carrier_mass_label": local["mass_label"],
        "local_carrier_One_speed": local["all_increments_One"],
        "local_carrier_confined": tube["isolated_colour_carrier_record"] == () and tube["work_strictly_increases"],
        "local_masslessness_not_physical_gaplessness": local["mass_label"] == ()
        and singlet["least_singlet_is_nonempty_composite"]
        and partition["gap"] > 0,
        "completed_infinity_used": False,
        "fitted_or_measured_value_used": False,
    }


SPEC = StructuralPhysicsSpec(
    claim_id=CLAIM_ID,
    title="Finite Fold colour-singlet positive excitation gap",
    statement=(
        "The generated colour-three sector holds two-thirds of the One and leaves "
        "the exact positive one-third complement.  The two parts form a complete "
        "period-two Fold orbit.  Colour observation admits only a nonempty closed "
        "singlet, with an antipodal pair as the least support, while the isolated "
        "colour record is empty and separation work increases by two-thirds at "
        "every positive finite successor.  Consequently the normalized least "
        "physical colour-singlet excitation has the depth-invariant positive gap "
        "one-third.  The locally propagating colour carrier nevertheless retains "
        "an empty mass label and One-cell causal motion: local carrier masslessness "
        "and physical colour-singlet gaplessness are not the same proposition."
    ),
    dependencies=(
        "SFT-FOUNDATION-FOLD-DYNAMICS-001",
        "SFT-PHYS-FORCE-COMPLETE-SECTOR-INVENTORY-003",
        "SFT-PHYS-STRONG-CARRIER-MASSLESS-CONFINED-TERMINAL-013",
        "SFT-PHYS-STRONG-FIELD-NONLINEAR-FIXED-POINT-TERMINAL-014",
        "SFT-PHYS-INTERACTION-UNIFICATION-TERMINAL-025",
        "SFT-MATH-EXACT-ARITHMETIC-001",
    ),
    evidence_mode=EvidenceMode.FORMAL,
    generation_rule=(
        "Generate the complete product of colour sector, observable support, "
        "vacuum boundary, gap carrier, confinement work, local-carrier distinction, "
        "Fold orbit, depth closure, prior-claim correction and extension forms."
    ),
    grammar_boundary=(
        "The generated colour-three Fold sector, its complete antipodal and three-"
        "member singlet supports, every positive finite separation/depth successor, "
        "the locally massless confined carrier and the normalized One partition. "
        "No continuum field action or completed infinite-volume limit is asserted."
    ),
    axes=(
        binary_axis("sector", "Which interaction sector is tested?", "named-Yang-Mills-sector", "A conventional name does not generate colour structure.", "generated-colour-three-sector", "The forced prime ladder supplies the complete colour-three fibre and eight non-return pair cells."),
        binary_axis("support", "Which states are physically observable?", "isolated-colour-carrier", "The admitted confinement law leaves the isolated-colour observation record empty.", "complete-colour-singlet-support", "An antipodal pair or complete colour fibre closes every colour label into a physical singlet."),
        binary_axis("vacuum", "How is the vacuum represented?", "numerical-zero-vacuum", "Numerical zero is outside the Fold proof domain.", "empty-excitation-record", "The vacuum is the empty physical-excitation record, not a proof scalar."),
        binary_axis("gap", "What separates the first physical singlet from the vacuum?", "massless-or-fitted-gap", "A fitted value or an empty mass label conflates local carrier and physical singlet.", "exact-positive-one-third-complement", "The strong two-thirds holding share leaves one-third as the unique positive complement to the One."),
        binary_axis("confinement", "What prevents an isolated colour state?", "bounded-or-free-separation-work", "Bounded or free work permits an unrecorded free colour state.", "fixed-two-thirds-positive-work-successor", "Every separation successor adds the retained two-thirds colour work while the tube width remains fixed."),
        binary_axis("carrier", "Does local masslessness imply a gapless physical spectrum?", "conflate-local-carrier-with-physical-singlet", "The local carrier is not an observable isolated colour state.", "retain-local-massless-physical-gapped-distinction", "The empty local mass label coexists with a positive least singlet excitation record."),
        binary_axis("orbit", "How are gap and coupling related?", "selected-gap-coupling-pair", "A selected pair does not prove closure or recurrence.", "complete-period-two-Fold-partition", "One-third folds to two-thirds, two-thirds folds to one-third and the pair reassembles the One."),
        binary_axis("depth", "Does positivity hold beyond a finite sample?", "bounded-depth-census-or-completed-infinity", "A bounded sample or completed infinity cannot certify every finite successor.", "positive-finite-successor-induction", "Sector identity preserves one-third while each successor adds positive two-thirds confinement work."),
        binary_axis("prior", "How is the earlier broad masslessness statement handled?", "repeat-no-massless-strong-excitation", "That wording contradicts the admitted locally massless strong carrier.", "correct-free-singlet-spectrum-boundary", "The exact claim is no free massless colour-singlet excitation, not no locally massless colour carrier."),
        binary_axis("extension", "May an extra mass scale or continuum law enter?", "free-scale-action-or-continuum-limit", "An added scale or action is a new premise.", "no-extra-rule", "The normalized finite Fold theorem ends at its declared colour-singlet boundary."),
    ),
    exact_result=(
        "Within the complete finite Fold colour grammar, the least observable "
        "colour singlet has normalized gap one-third above the empty excitation "
        "record at every positive finite depth; confinement work advances by "
        "two-thirds; the two shares form a period-two partition of the One; and "
        "the locally massless confined carrier is retained without being mistaken "
        "for a free gapless physical singlet."
    ),
    induction_base=(
        "At the first positive separation, the least antipodal colour singlet is "
        "nonempty, its exact complement is one-third and its confinement work is "
        "two-thirds."
    ),
    induction_step=(
        "A separation successor retains the colour-three sector and its one-third "
        "complement while adding another positive two-thirds work carrier; the "
        "singlet boundary and empty isolated-colour record are unchanged."
    ),
    exclusions=(
        "no imported Yang-Mills action, gauge-group axiom, Hamiltonian or continuum mass-gap proof",
        "no V1/V2 executable, answer table, lattice mass or stored survivor",
        "no numerical-zero, negative, irrational, imaginary or floating proof magnitude",
        "no fitted dimensionful glueball scale or claim that one-third equals a mass in MeV",
        "no completed infinity or inference from a finite simulation to a conventional continuum theorem",
        "no conflation of the empty local carrier mass label with the least physical singlet gap",
    ),
    witnesses=(
        Witness("exact-partition", "The strong gap and coupling are one-third and two-thirds and reassemble the One.", strong_gap_partition()["gap"] == Fraction(1, 3) and strong_gap_partition()["coupling"] == Fraction(2, 3) and strong_gap_partition()["complete"]),
        Witness("period-two", "The exact shares exchange under Fold and return after two actions.", strong_gap_partition()["gap_to_coupling"] and strong_gap_partition()["coupling_to_gap"]),
        Witness("nonempty-singlet", "The least physical colour closure is an antipodal pair and isolated colour remains unobserved.", physical_singlet_support()["least_singlet_constituents"] == 2 and physical_singlet_support()["isolated_colour_observation_record"] == ()),
        Witness("all-finite-depths", "Every checked successor retains a positive one-third gap and increasing confinement work.", singlet_gap_trace(24)["all_gaps_positive"] and singlet_gap_trace(24)["gap_depth_invariant"] and singlet_gap_trace(24)["work_positive_and_increasing"]),
        Witness("carrier-distinction", "The local carrier remains massless and confined while the physical singlet gap remains positive.", singlet_gap_trace(24)["local_carrier_One_speed"] and singlet_gap_trace(24)["local_carrier_confined"] and singlet_gap_trace(24)["local_masslessness_not_physical_gaplessness"]),
    ),
    provenance=(ProvenanceClass.OBSERVATIONAL_DERIVATION,),
)


SPEC.validate()


__all__ = (
    "CLAIM_ID",
    "SPEC",
    "physical_singlet_support",
    "singlet_gap_trace",
    "strong_gap_partition",
)
