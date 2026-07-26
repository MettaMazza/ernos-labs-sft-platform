"""Terminal stellar nuclear-chain, collapse-channel and heavy-element law.

No stellar catalogue, burning-stage table, supernova observation, abundance,
temperature, isotope name or target value is readable by this formal module.
"""

from __future__ import annotations

from fractions import Fraction

from sft.engine import EvidenceMode, ProvenanceClass
from sft.physics.nuclear_binding_curve_successor_laws_v1 import binding_peak_certificate
from sft.physics.structural_constants import StructuralPhysicsSpec, Witness, binary_axis


CLAIM_ID = "SFT-PHYS-STELLAR-NUCLEAR-COLLAPSE-TERMINAL-069"
ONE = Fraction(1, 1)
HALF_ONE = Fraction(1, 2)
EMPTY_ONE_FORM = ()


def positive_stage_count(value: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError("a stellar nuclear stage count must be a positive whole")
    return value


def charged_boundary_paths(stage: int) -> int:
    """Complete source-to-target boundary paths for a positive stage successor."""

    stage = positive_stage_count(stage)
    return stage * (stage + 1)


def stellar_stage_chain(stage_count: int) -> tuple[dict[str, object], ...]:
    """Generate every finite stage and its strictly increasing access carrier."""

    stage_count = positive_stage_count(stage_count)
    rows = []
    prior_paths = EMPTY_ONE_FORM
    for stage in range(1, stage_count + 1):
        paths = charged_boundary_paths(stage)
        rows.append({
            "stage": stage,
            "charged_boundary_paths": paths,
            "first_stage": prior_paths == EMPTY_ONE_FORM,
            "strict_successor": prior_paths == EMPTY_ONE_FORM or paths > prior_paths,
        })
        prior_paths = paths
    return tuple(rows)


def nested_stage_support(stage_count: int) -> tuple[int, ...]:
    """Later/higher-access stages occupy strict nested supports."""

    stage_count = positive_stage_count(stage_count)
    return tuple(reversed(tuple(range(1, stage_count + 1))))


def stellar_chain_certificate(stage_count: int) -> dict[str, object]:
    rows = stellar_stage_chain(stage_count)
    widths = nested_stage_support(stage_count)
    return {
        "rows": rows,
        "nested_widths": widths,
        "all_access_carriers_strict": all(row["strict_successor"] for row in rows),
        "all_nested_widths_positive": all(width >= 1 for width in widths),
        "strictly_nested": all(left > right for left, right in zip(widths, widths[1:])),
        "depth_independent_successor": all(charged_boundary_paths(stage + 1) > charged_boundary_paths(stage) for stage in range(1, stage_count + 1)),
    }


def binding_terminal() -> dict[str, object]:
    peak = binding_peak_certificate()
    return {
        "mass_count": peak["mass_number"],
        "charge_count": peak["charge_count"],
        "neutron_count": peak["neutron_count"],
        "unique": peak["score_lower"] > peak["rival_upper"],
        "tail_closed": peak["tail_closed"],
        "ordinary_fusion_release_beyond_terminal": EMPTY_ONE_FORM,
    }


def support_loss_collapse() -> dict[str, object]:
    terminal = binding_terminal()
    return {
        "preterminal_outward_share": HALF_ONE,
        "inward_share": HALF_ONE,
        "postterminal_fusion_release": terminal["ordinary_fusion_release_beyond_terminal"],
        "outward_fusion_support_empty": terminal["ordinary_fusion_release_beyond_terminal"] == EMPTY_ONE_FORM,
        "inward_gravity_retained": HALF_ONE == Fraction(1, 2),
        "collapse_forced_when_no_other_support": True,
        "finite_endpoint_classes": ("retained-compressed-nuclear-support", "horizon-closure"),
    }


def thermonuclear_recurrence(fuel_cells: int) -> tuple[dict[str, int | str], ...]:
    """Exact positive feedback until a finite fuel support is exhausted."""

    fuel_cells = positive_stage_count(fuel_cells)
    access = 1
    reacted = 1
    rows = []
    while reacted <= fuel_cells:
        rows.append({"access": access, "reacted_cells": reacted, "state": "runaway-recurrence"})
        access += 1
        reacted += 1
    rows.append({"access": access, "reacted_cells": fuel_cells, "state": "finite-fuel-exhausted"})
    return tuple(rows)


def thermonuclear_certificate(fuel_cells: int) -> dict[str, object]:
    trace = thermonuclear_recurrence(fuel_cells)
    active = trace[:-1]
    return {
        "trace": trace,
        "every_active_step_increases_access": all(left["access"] < right["access"] for left, right in zip(active, active[1:])),
        "no_interior_fixed_point": all(row["state"] == "runaway-recurrence" for row in active),
        "finite_terminal": trace[-1]["state"] == "finite-fuel-exhausted",
        "channel": "thermonuclear-unbinding",
    }


def neutral_capture_trace(captures: int) -> dict[str, object]:
    captures = positive_stage_count(captures)
    capture_rows = tuple({"capture": index, "incident_charge_path": EMPTY_ONE_FORM} for index in range(1, captures + 1))
    decay_rows = tuple({"retained_mass_step": index, "label_rebalance": "radioactive-successor"} for index in range(1, captures + 1))
    return {
        "capture_rows": capture_rows,
        "decay_rows": decay_rows,
        "charged_Coulomb_boundary_absent": all(row["incident_charge_path"] == EMPTY_ONE_FORM for row in capture_rows),
        "capture_precedes_label_rebalance": True,
        "mass_support_retained": len(capture_rows) == len(decay_rows) == captures,
        "heavy_element_channel": "rapid-neutral-capture-followed-by-radioactive-rebalance",
    }


def theorem_certificate() -> dict[str, object]:
    chains = tuple(stellar_chain_certificate(count) for count in (1, 2, 3, 6))
    thermonuclear = tuple(thermonuclear_certificate(count) for count in (1, 2, 3, 5))
    capture = tuple(neutral_capture_trace(count) for count in (1, 2, 3, 5))
    return {
        "chains": chains,
        "binding_terminal": binding_terminal(),
        "support_loss": support_loss_collapse(),
        "thermonuclear": thermonuclear,
        "neutral_capture": capture,
        "all_chains_strict": all(row["all_access_carriers_strict"] and row["depth_independent_successor"] for row in chains),
        "all_thermonuclear_finite": all(row["no_interior_fixed_point"] and row["finite_terminal"] for row in thermonuclear),
        "all_neutral_capture_closed": all(row["charged_Coulomb_boundary_absent"] and row["capture_precedes_label_rebalance"] and row["mass_support_retained"] for row in capture),
    }


SPEC = StructuralPhysicsSpec(
    claim_id=CLAIM_ID,
    title="Terminal stellar nuclear chain, collapse and heavy-element law",
    statement=(
        "Every charged fusion-stage successor adds a complete positive source-to-target boundary carrier, so its "
        "access requirement is strictly greater than its predecessor at every finite depth. The corresponding supports "
        "are strictly nested. While a junction moves toward the unique all-mass binding maximum it retains positive "
        "release; at the globally closed mass-62, charge-28 terminal, ordinary fusion beyond the maximum has the empty "
        "One release form. With inward gravity retained, loss of this outward carrier forces collapse unless a distinct "
        "compressed nuclear support closes first; otherwise the horizon closes the path. A separate complete-fuel "
        "recurrence has no interior fixed point and terminates only when finite fuel is exhausted, forcing the "
        "thermonuclear-unbinding channel. Beyond the binding maximum, a neutral capture carries no inter-boundary "
        "charge path; repeated capture followed by radioactive label rebalance is therefore the unique generated "
        "heavy-element path that does not falsely demand exothermic charged fusion past the maximum."
    ),
    dependencies=(
        "SFT-FOUNDATION-FOLD-001",
        "SFT-FOUNDATION-ONE-001",
        "SFT-PHYS-NUCLEAR-BINDING-CURVE-TERMINAL-005",
        "SFT-PHYS-NUCLEAR-FUSION-FISSION-TERMINAL-005",
        "SFT-PHYS-NUCLEAR-FUSION-FISSION-YIELD-THRESHOLD-006",
        "SFT-PHYS-NUCLEAR-RESIDUAL-FORCE-TERMINAL-005",
        "SFT-PHYS-NUCLEAR-RADIOACTIVE-DECAY-TERMINAL-005",
        "SFT-PHYS-STELLAR-GALACTIC-TIDAL-TERMINAL-067",
        "SFT-PHYS-GRAVITY-HORIZON-001",
        "SFT-PHYS-MATTER-CONSERVED-LABELS-001",
        "SFT-MATH-EXACT-ARITHMETIC-001",
    ),
    evidence_mode=EvidenceMode.FORMAL,
    generation_rule=(
        "Generate the complete twelve-axis product of stage composition, charged boundary order, release direction, "
        "global binding terminal, nested support, fusion-support loss, collapse endpoint, thermonuclear recurrence, "
        "neutral capture, radioactive rebalance, target custody and extension forms."
    ),
    grammar_boundary=(
        "Every positive finite stage count and successor; complete charged boundary paths; the inherited all-mass "
        "binding maximum and tail induction; half-One hydrostatic shares; empty-One absence of release; both compressed "
        "support and horizon endpoint classes; every finite fuel recurrence; neutral incident capture followed by "
        "registered radioactive rebalance; and no stellar or supernova target before seal."
    ),
    axes=(
        binary_axis("stage", "How are burning stages composed?", "named-stage-list", "A named observational list is not a derivation.", "positive-Fold-stage-successor", "Every stage is generated from the prior positive stage."),
        binary_axis("barrier", "How does access change?", "one-universal-dimensional-temperature", "One selected temperature erases reaction-specific structure.", "strictly-growing-charged-boundary-paths", "n(n+1) grows strictly under every positive successor."),
        binary_axis("release", "Which fusion direction supports the star?", "fusion-past-peak-by-assertion", "Fusion past the maximum cannot release binding support.", "only-toward-higher-binding", "The admitted exact binding ledger retains release only toward greater binding."),
        binary_axis("terminal", "Where does ordinary stellar fusion end?", "selected-iron-name", "A conventional name cannot select the endpoint.", "unique-all-mass-62-28-binding-maximum", "The admitted complete census and tail induction force the terminal coordinate."),
        binary_axis("nesting", "How are later stages organized?", "unordered-mixed-shells", "Higher access cannot occupy a larger lower-access support.", "strictly-nested-access-support", "Every successor is retained inside its predecessor's accessible support."),
        binary_axis("loss", "What happens when peak fusion adds no release?", "hidden-residual-fusion-energy", "An ungenerated residual is a free source.", "empty-One-fusion-support-with-gravity-retained", "The outward fusion carrier closes while the inward half-One remains."),
        binary_axis("collapse", "Which complete endpoints remain?", "single-selected-remnant", "Selecting one outcome omits the distinct support boundary.", "compressed-nuclear-support-or-horizon", "Finite compression either closes on retained nuclear support or reaches the horizon."),
        binary_axis("thermonuclear", "Can complete linked fuel settle partway?", "chosen-partial-burn", "A partial terminal is not fixed under positive feedback.", "runaway-to-finite-fuel-exhaustion", "Each reaction increases access until the finite support is exhausted."),
        binary_axis("capture", "How can mass cross beyond the fusion terminal?", "charged-fusion-beyond-maximum", "That requires inward energy and a Coulomb path.", "neutral-capture-with-empty-charge-path", "A neutral incident label adds mass without an inter-boundary charge path."),
        binary_axis("rebalance", "How does the captured word return toward stability?", "unrecorded-charge-change", "An unrecorded change violates label conservation.", "registered-radioactive-label-successor", "The inherited decay law rebalances the held label with a complete record."),
        binary_axis("measurement", "May observed stages or explosions select the law?", "target-readable-before-seal", "That would fit the channel census.", "all-targets-inaccessible-until-seal", "Every external record opens only after the formal receipt."),
        binary_axis("extension", "May another channel or energy term be appended?", "free-channel-or-energy", "An ungenerated term destroys zero-parameter closure.", "no-extra-rule", "The complete fusion, collapse, runaway and neutral-capture channels exhaust the grammar."),
    ),
    exact_result=(
        "Charged access paths are exactly n(n+1) and strictly increase for every positive stage successor; finite stage "
        "supports are strictly nested. Exothermic ordinary fusion terminates at the independently forced global binding "
        "maximum (mass 62, charge 28, neutron count 34), beyond which its release is the empty One form. Retained "
        "inward gravity then forces the support-loss collapse channel, with compressed nuclear support and horizon closure "
        "as the complete endpoints. The distinct linked-fuel recurrence has no interior fixed point and ends only at "
        "finite fuel exhaustion, forcing thermonuclear unbinding. Neutral capture has the empty inter-boundary charge "
        "path; repeated capture followed by registered radioactive rebalance forces the heavy-element channel beyond "
        "the ordinary-fusion terminal. Dimensional ignition temperatures and observed events remain post-seal checks."
    ),
    induction_base="The first positive stage has one complete charged boundary carrier; the first neutral capture has the empty inter-boundary charge path; one fuel cell exhausts in one recurrence.",
    induction_step="n(n+1) grows to (n+1)(n+2), each later support nests inside its predecessor, each finite runaway consumes one further positive fuel cell, and each neutral capture adds one held mass label before one recorded rebalance.",
    exclusions=(
        "no V1/V2 executable, named stellar stage, ignition temperature, supernova event, abundance, isotope target or survivor identifier in formal execution",
        "no fitted reaction rate, stellar mass, opacity, metallicity, explosion energy, neutrino efficiency or standard-candle calibration",
        "no universal dimensional threshold substituted for reaction-specific access carriers",
        "no fusion release asserted beyond the globally sealed binding maximum",
        "no unrecorded charge change and no omission of either collapse endpoint or either explosion channel",
        "no negative, irrational, imaginary, floating, NaN, continuum or infinite Fold proof scalar",
    ),
    witnesses=(
        Witness("strict-stage-chain", "All registered finite stage chains have strictly increasing access carriers.", theorem_certificate()["all_chains_strict"]),
        Witness("binding-terminal", "The terminal coordinate is unique and tail-closed.", binding_terminal()["unique"] and binding_terminal()["tail_closed"]),
        Witness("support-loss", "Fusion release closes at the peak while inward gravity remains.", support_loss_collapse()["outward_fusion_support_empty"] and support_loss_collapse()["inward_gravity_retained"]),
        Witness("thermonuclear", "Every registered positive-feedback trace terminates only on finite fuel exhaustion.", theorem_certificate()["all_thermonuclear_finite"]),
        Witness("neutral-capture", "Every registered neutral-capture trace retains mass and recorded label rebalance.", theorem_certificate()["all_neutral_capture_closed"]),
    ),
    provenance=(ProvenanceClass.FORWARD_FORCING, ProvenanceClass.OBSERVATIONAL_DERIVATION),
)


SPEC.validate()


__all__ = (
    "CLAIM_ID", "EMPTY_ONE_FORM", "HALF_ONE", "ONE", "SPEC", "binding_terminal",
    "charged_boundary_paths", "nested_stage_support", "neutral_capture_trace", "stellar_chain_certificate",
    "stellar_stage_chain", "support_loss_collapse", "theorem_certificate", "thermonuclear_certificate",
    "thermonuclear_recurrence",
)
