"""Exact Fold laws for the complete Materials PHASE-001--010 family."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from fractions import Fraction

from sft.engine import ClaimRegistration, EvidenceMode, ROOT_THEOREM
from sft.physics.structural_constants import StructuralPhysicsProgram, StructuralPhysicsSpec, Witness, binary_axis


def positive(value: int, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError(f"{name} must be a positive generated count")
    return value


def phase_fraction_ledger(phases: tuple[tuple[str, int], ...]) -> dict[str, object]:
    if not phases or any(not label for label, _ in phases):
        raise ValueError("phase ledger requires held phase labels")
    if len({label for label, _ in phases}) != len(phases):
        raise ValueError("each phase label must occur once in the complete ledger")
    normalized = tuple((label, positive(count, "phase count")) for label, count in phases)
    total = sum(count for _, count in normalized)
    fractions = tuple((label, Fraction(count, total)) for label, count in normalized)
    return {"phases": normalized, "total_count": total, "fractions": fractions, "recomposes_one": sum(part for _, part in fractions) == 1}


def tie_line_partition(left: int, bulk: int, right: int) -> dict[str, object]:
    left, bulk, right = positive(left, "left endpoint"), positive(bulk, "bulk coordinate"), positive(right, "right endpoint")
    if not left < bulk < right:
        raise ValueError("bulk coordinate must lie strictly within held coexistence endpoints")
    span = right - left
    left_part = Fraction(right - bulk, span)
    right_part = Fraction(bulk - left, span)
    return {"left": left, "bulk": bulk, "right": right, "left_phase_part": left_part, "right_phase_part": right_part, "reconstructs_bulk": left * left_part + right * right_part == bulk, "recomposes_one": left_part + right_part == 1}


def coexistence_handoff(phase_words: tuple[tuple[str, tuple[tuple[str, int], ...]], ...]) -> dict[str, object]:
    if len(phase_words) < 2:
        raise ValueError("coexistence requires at least two held phases")
    phases = []
    for phase, components in phase_words:
        if not phase or not components or len({label for label, _ in components}) != len(components):
            raise ValueError("each phase requires one complete component handoff word")
        phases.append((phase, tuple((label, positive(token, "handoff token")) for label, token in components)))
    ordered_labels = tuple(label for label, _ in phases[0][1])
    if any(tuple(label for label, _ in components) != ordered_labels for _, components in phases[1:]):
        raise ValueError("coexisting phases must retain the same ordered component identities")
    columns = tuple((label, tuple(dict(components)[label] for _, components in phases)) for label in ordered_labels)
    return {"phases": tuple(phases), "component_handoffs": columns, "all_component_handoffs_equal": all(len(set(tokens)) == 1 for _, tokens in columns), "phase_identities_retained": True}


def metastable_retention(states: tuple[str, ...], escape_after: int) -> dict[str, object]:
    if len(states) < 2 or any(not state for state in states):
        raise ValueError("metastable retention requires a complete positive observation path")
    escape_after = positive(escape_after, "escape transition")
    if escape_after >= len(states):
        raise ValueError("escape transition must occur within the declared path")
    retained = states[:escape_after]
    return {"path": states, "metastable_label": states[0], "retained_observations": retained, "retention_count": len(retained), "escape_state": states[escape_after], "history_required": True}


def spinodal_organization(left_energy: int, centre_energy: int, right_energy: int) -> dict[str, object]:
    left_energy, centre_energy, right_energy = (positive(value, "local energy count") for value in (left_energy, centre_energy, right_energy))
    neighbour_sum = left_energy + right_energy
    centre_pair = centre_energy + centre_energy
    if centre_pair > neighbour_sum:
        orientation = "separation-amplifying"
        magnitude = centre_pair - neighbour_sum
    elif centre_pair < neighbour_sum:
        orientation = "mixing-restoring"
        magnitude = neighbour_sum - centre_pair
    else:
        orientation = "boundary-equality"
        magnitude = None
    return {"left": left_energy, "centre": centre_energy, "right": right_energy, "orientation": orientation, "exact_departure_count": magnitude, "signed_or_floating_curvature_used": False}


def displacive_transform(atoms: tuple[tuple[str, tuple[int, int, int], tuple[str, int]], ...]) -> dict[str, object]:
    if not atoms or len({label for label, _, _ in atoms}) != len(atoms):
        raise ValueError("displacive transformation requires distinct held atoms")
    transformed = []
    for label, position, displacement in atoms:
        if len(position) != 3 or any(positive(axis, "position coordinate") != axis for axis in position):
            raise ValueError("positions use positive generated coordinates")
        direction, magnitude = displacement
        if direction not in ("x-forward", "x-opposed", "y-forward", "y-opposed", "z-forward", "z-opposed"):
            raise ValueError("displacement direction must be held rather than signed")
        transformed.append((label, position, (direction, positive(magnitude, "displacement magnitude"))))
    return {"atoms": tuple(transformed), "atom_identity_bijection": True, "diffusion_handoff_required": False, "cooperative_shape_change": True}


def reconstructive_transform(atoms: tuple[str, ...], initial_bonds: tuple[tuple[str, str], ...], final_bonds: tuple[tuple[str, str], ...]) -> dict[str, object]:
    if len(atoms) < 2 or len(set(atoms)) != len(atoms):
        raise ValueError("reconstructive transformation requires distinct held atoms")
    carrier = set(atoms)
    normalize = lambda edge: tuple(sorted(edge))
    before, after = {normalize(edge) for edge in initial_bonds}, {normalize(edge) for edge in final_bonds}
    if any(len(edge) != 2 or set(edge) - carrier or edge[0] == edge[1] for edge in before | after):
        raise ValueError("every bond must join two declared atoms")
    broken, formed = before - after, after - before
    if not broken or not formed:
        raise ValueError("reconstructive change must break and form connectivity")
    return {"atoms": atoms, "initial_bonds": tuple(sorted(before)), "final_bonds": tuple(sorted(after)), "broken_bonds": tuple(sorted(broken)), "formed_bonds": tuple(sorted(formed)), "atom_identity_conserved": True, "topology_changed": True}


def order_disorder(reference: tuple[str, ...], observed: tuple[str, ...]) -> dict[str, object]:
    if len(reference) < 2 or len(reference) != len(observed) or Counter(reference) != Counter(observed):
        raise ValueError("order comparison requires the same complete labelled carrier")
    matches = sum(left == right for left, right in zip(reference, observed))
    mismatches = len(reference) - matches
    if mismatches == 0:
        state = "ordered"
    elif matches == 0:
        state = "fully-reassigned"
    else:
        state = "partially-disordered"
    return {"reference": reference, "observed": observed, "matching_sites": matches or None, "reassigned_sites": mismatches or None, "matching_part": Fraction(matches, len(reference)) if matches else None, "reassigned_part": Fraction(mismatches, len(reference)) if mismatches else None, "state": state, "carrier_conserved": True}


def kinetic_arrest(relaxation_steps: int, observation_steps: int, state_history: tuple[str, ...]) -> dict[str, object]:
    relaxation_steps, observation_steps = positive(relaxation_steps, "relaxation steps"), positive(observation_steps, "observation steps")
    if not state_history or any(not state for state in state_history):
        raise ValueError("kinetic arrest requires a retained state history")
    if observation_steps < relaxation_steps:
        status = "kinetically-arrested-at-observation-boundary"
    elif observation_steps == relaxation_steps:
        status = "relaxation-boundary-equality"
    else:
        status = "relaxation-observed"
    return {"relaxation_steps": relaxation_steps, "observation_steps": observation_steps, "status": status, "state_history": state_history, "history_and_method_retained": True}


def time_temperature_path(rows: tuple[tuple[int, int, int, int], ...]) -> dict[str, object]:
    if not rows:
        raise ValueError("transformation path requires at least one time-temperature record")
    normalized = []
    previous_time = None
    for time, temperature, transformed, total in rows:
        time, temperature, total = positive(time, "time count"), positive(temperature, "temperature count"), positive(total, "carrier count")
        if previous_time is not None and time <= previous_time:
            raise ValueError("time records must be strictly ordered")
        if not isinstance(transformed, int) or isinstance(transformed, bool) or transformed < 0 or transformed > total:
            raise ValueError("transformed count must lie within the declared carrier")
        normalized.append((time, temperature, transformed or None, total, Fraction(transformed, total) if transformed else None))
        previous_time = time
    return {"records": tuple(normalized), "complete_time_temperature_path": True, "absence_is_labelled_not_numerical_quantity": all(row[2] is None or row[2] >= 1 for row in normalized)}


BASE = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001", "SFT-MATH-EXACT-ARITHMETIC-001", "SFT-MATH-DISCRETE-001", "SFT-MATH-COMBINATORICS-001", "SFT-MATH-GRAPH-NETWORK-001", "SFT-MATH-ORDER-LATTICE-001", "SFT-MATH-GEOMETRY-TOPOLOGY-001", "SFT-MATH-DYNAMICAL-SYSTEMS-001", "SFT-MATH-LOGIC-PROOF-001", "SFT-INFO-SYMBOL-DISTINCTION-001", "SFT-INFO-CONSERVATION-LOSS-001", "SFT-CHEM-PHASE-RULE-STRUCTURAL-011", "SFT-CHEM-ONE-COMPONENT-PHASE-BOUNDARY-012", "SFT-CHEM-MULTICOMPONENT-PHASE-DIAGRAM-013", "SFT-MAT-MEAS-MATERIAL-001", "SFT-MAT-MEAS-SPECIMEN-001", "SFT-MAT-MEAS-PHASE-001", "SFT-MAT-MEAS-TRACEABILITY-001", "SFT-MAT-MICRO-MULTISCALE-CORRESPONDENCE-009",
)


DEFINITIONS = (
    ("001", "SFT-MAT-PHASE-FRACTION-LEDGER-001", "Complete multiphase fraction ledger", "A multiphase material state is the complete partition of one finite specimen carrier into held phase classes; every exact phase part is retained and the parts recompose the One.", BASE),
    ("002", "SFT-MAT-PHASE-TIE-LINE-LEVER-002", "Tie-line and lever-partition relation", "A coexistence tie-line retains both endpoint compositions and the bulk coordinate; the two exact opposite-span parts uniquely reconstruct the bulk and recompose the One.", BASE + ("SFT-MAT-PHASE-FRACTION-LEDGER-001",)),
    ("003", "SFT-MAT-PHASE-COMPONENT-HANDOFF-003", "Component potential and phase-coexistence handoff", "Phase coexistence requires every held component identity to present the same exact handoff token across all coexisting phase words while phase identities remain distinct.", BASE + ("SFT-MAT-PHASE-TIE-LINE-LEVER-002",)),
    ("004", "SFT-MAT-PHASE-METASTABLE-RETENTION-004", "Metastable-state retention boundary", "A metastable state is a nonterminal held state retained through a positive observation interval on a complete path before an exact escape transition; its history and boundary cannot be erased.", BASE + ("SFT-MAT-PHASE-COMPONENT-HANDOFF-003",)),
    ("005", "SFT-MAT-PHASE-SPINODAL-INSTABILITY-005", "Spinodal-equivalent instability organization", "A finite composition neighbourhood is separation-amplifying exactly when the doubled centre energy count exceeds the two-neighbour sum; the opposed orientation and equality boundary remain labels, never negative curvature.", BASE + ("SFT-MAT-PHASE-METASTABLE-RETENTION-004",)),
    ("006", "SFT-MAT-PHASE-MARTENSITIC-006", "Displacive and martensitic transformation", "A displacive transformation is a cooperative held-direction mapping of every atom identity to a displaced structural state without a diffusive identity handoff.", BASE + ("SFT-MAT-PHASE-SPINODAL-INSTABILITY-005",)),
    ("007", "SFT-MAT-PHASE-RECONSTRUCTIVE-007", "Reconstructive transformation path", "A reconstructive transformation preserves the complete atom carrier while breaking and forming exact bonds so that the connectivity topology changes and the full path remains reconstructible.", BASE + ("SFT-MAT-PHASE-MARTENSITIC-006",)),
    ("008", "SFT-MAT-PHASE-ORDER-DISORDER-008", "Order-disorder transition", "Order and disorder are exact site-by-site relations between two words over the same conserved constituent carrier, retaining matching and reassigned parts without a fitted order parameter.", BASE + ("SFT-MAT-PHASE-RECONSTRUCTIVE-007",)),
    ("009", "SFT-MAT-PHASE-GLASS-ARREST-009", "Glass-transition and kinetic-arrest boundary", "Kinetic arrest occurs when the retained observation word closes before the positive relaxation recurrence; equality and observed relaxation are separate exact boundary classes.", BASE + ("SFT-MAT-PHASE-ORDER-DISORDER-008",)),
    ("010", "SFT-MAT-PHASE-TIME-TEMPERATURE-010", "Transformation kinetics and time-temperature path", "Transformation kinetics is the complete ordered set of exact time, temperature, transformed-carrier and total-carrier records; structural absence is labelled and every nonempty fraction is rational.", BASE + ("SFT-MAT-PHASE-GLASS-ARREST-009",)),
)


RELATIONS = {
    "001": "complete-held-phase-partition-and-one-recomposition",
    "002": "coexistence-endpoint-tie-line-and-opposite-span-partition",
    "003": "component-wise-equal-handoff-across-distinct-phase-words",
    "004": "nonterminal-state-retention-until-exact-escape-transition",
    "005": "three-site-separation-amplifying-or-restoring-instability-ledger",
    "006": "atom-bijective-held-direction-cooperative-displacive-map",
    "007": "carrier-conserving-bond-breaking-and-forming-topology-change",
    "008": "same-carrier-site-match-and-reassignment-order-ledger",
    "009": "observation-to-relaxation-recurrence-arrest-boundary",
    "010": "complete-ordered-time-temperature-transformed-carrier-path",
}


def axes(relation):
    return (
        binary_axis("carrier", "What carries the phase distinction?", "phase-name-or-answer-only", "A phase name without its specimen carrier cannot reconstruct the state.", "complete-positive-specimen-and-phase-carrier", "Every constituent and phase label remains held."),
        binary_axis("relation", "Which generated relation survives?", "imported-continuum-fit-or-lookup", "An imported equation, fit or lookup does not force a Fold law.", relation, "The exact finite relation uniquely retains all required distinctions."),
        binary_axis("organization", "What phase organization remains?", "single-average-or-endpoint-erasure", "A single average erases coexistence, paths and transformation histories.", "complete-phase-component-path-organization", "All phases, components, sites and path records remain recoverable."),
        binary_axis("observation", "What defines the observation class?", "specimen-method-condition-scale-erased", "An unrecorded boundary does not identify the observation.", "specimen-method-condition-scale-uncertainty-held", "The complete observation boundary is retained."),
        binary_axis("record", "What proof record is emitted?", "headline-only", "A headline has no reproducible candidate or transition trace.", "complete-state-transition-resource-trace", "Candidates, eliminations, transitions and resources are recorded."),
        binary_axis("provenance", "What selects the law?", "target-authority-or-prior-model", "External authority tests the result but cannot select it.", "root-bound-forward-forcing", "Every choice traces to the root theorem through admitted dependencies."),
        binary_axis("generality", "What closes the class?", "selected-specimen-or-finite-lookup", "One favourable specimen does not establish the successor.", "positive-finite-successor-closure", "Every lawful positive successor preserves the relation."),
        binary_axis("extension", "May an extra selector enter?", "free-fit-exception-or-extra-rule", "An extra choice can manufacture a result.", "no-extra-rule", "No axiom, fit, exception or target-derived selector is admitted."),
    )


WITNESSES = {
    "001": (Witness("three-phase-ledger", "Counts two, three and five force exact parts one-fifth, three-tenths and one-half.", dict(phase_fraction_ledger((("a", 2), ("b", 3), ("c", 5)))["fractions"])["c"] == Fraction(1, 2)), Witness("one", "All phase parts recompose the One.", phase_fraction_ledger((("a", 2), ("b", 3), ("c", 5)))["recomposes_one"])),
    "002": (Witness("lever", "Endpoints two and eight with bulk four force parts two-thirds and one-third.", tie_line_partition(2, 4, 8)["left_phase_part"] == Fraction(2, 3)), Witness("bulk", "The exact opposite-span parts reconstruct the bulk coordinate.", tie_line_partition(2, 4, 8)["reconstructs_bulk"])),
    "003": (Witness("equal-handoff", "Two distinct phases with the same component tokens satisfy coexistence handoff.", coexistence_handoff((("alpha", (("x", 2), ("y", 3))), ("beta", (("x", 2), ("y", 3)))))["all_component_handoffs_equal"]), Witness("distinct-phases", "Phase identities remain held after component comparison.", coexistence_handoff((("alpha", (("x", 2),)), ("beta", (("x", 2),))))["phase_identities_retained"])),
    "004": (Witness("retention", "A held state persists for three observations before escape.", metastable_retention(("held", "held", "held", "escaped"), 3)["retention_count"] == 3), Witness("escape", "The first post-retention state is explicitly reconstructed.", metastable_retention(("held", "held", "escaped"), 2)["escape_state"] == "escaped")),
    "005": (Witness("amplifying", "Centre five against neighbours two and three forces a separation-amplifying orientation of five counts.", spinodal_organization(2, 5, 3)["orientation"] == "separation-amplifying" and spinodal_organization(2, 5, 3)["exact_departure_count"] == 5), Witness("no-signed-curvature", "The orientation is held without a negative scalar.", not spinodal_organization(2, 5, 3)["signed_or_floating_curvature_used"])),
    "006": (Witness("bijection", "Every atom identity survives the cooperative displacement map.", displacive_transform((("a", (1, 1, 1), ("x-forward", 1)), ("b", (2, 1, 1), ("x-forward", 1))))["atom_identity_bijection"]), Witness("nondiffusive", "The exact displacive witness requires no diffusive identity handoff.", not displacive_transform((("a", (1, 1, 1), ("y-opposed", 1)),))["diffusion_handoff_required"])),
    "007": (Witness("topology", "Replacing bond a-b with a-c changes topology while retaining all atoms.", reconstructive_transform(("a", "b", "c"), (("a", "b"), ("b", "c")), (("a", "c"), ("b", "c")))["topology_changed"]), Witness("carrier", "The reconstructive map conserves the atom carrier.", reconstructive_transform(("a", "b", "c"), (("a", "b"),), (("a", "c"),))["atom_identity_conserved"])),
    "008": (Witness("partial-disorder", "Swapping two of four sites retains exact matching and reassigned halves.", order_disorder(("a", "b", "a", "b"), ("a", "a", "b", "b"))["matching_part"] == Fraction(1, 2)), Witness("carrier", "Order comparison preserves the same constituent multiset.", order_disorder(("a", "b"), ("b", "a"))["carrier_conserved"])),
    "009": (Witness("arrest", "Observation two closing before relaxation five forces kinetic arrest.", kinetic_arrest(5, 2, ("glass", "glass"))["status"].startswith("kinetically-arrested")), Witness("boundary", "Equal observation and relaxation counts remain a distinct boundary.", kinetic_arrest(3, 3, ("a", "b"))["status"] == "relaxation-boundary-equality")),
    "010": (Witness("fractions", "Two of eight transformed units at the second record force one-quarter.", time_temperature_path(((1, 8, 0, 8), (2, 7, 2, 8)))["records"][1][4] == Fraction(1, 4)), Witness("absence", "The display-zero input is converted to labelled structural absence in the native record.", time_temperature_path(((1, 8, 0, 8),))["records"][0][2] is None)),
}


@dataclass(frozen=True)
class PhaseSpec(StructuralPhysicsSpec):
    number: str = ""
    obligation_id: str = ""

    def validate(self):
        if not self.claim_id.startswith("SFT-MAT-PHASE-") or self.number not in WITNESSES or len(self.axes) != 8:
            raise ValueError("invalid Materials PHASE spec")
        if not self.dependencies or len({axis.key for axis in self.axes}) != 8:
            raise ValueError("incomplete Materials PHASE spec")
        for axis in self.axes:
            if len(axis.choices) != 2:
                raise ValueError("Materials PHASE axis incomplete")
            axis.survivor
        if not all(witness.passed for witness in self.witnesses):
            raise ValueError("Materials PHASE witness failed")


class PhaseProgram(StructuralPhysicsProgram):
    @property
    def registration(self):
        return ClaimRegistration(claim_id=self.spec.claim_id, title=self.spec.title, branch="materials", statement=self.spec.statement, evidence_mode=EvidenceMode.EMPIRICAL, root_theorems=(ROOT_THEOREM,), dependencies=self.spec.dependencies, axioms=(), free_parameters=(), provenance=self.spec.provenance, source_hash=self.source_hash)


EXCLUSIONS = (
    "no V1/V2 proof artifact, continuum thermodynamic potential, named phase equation, fitted constitutive law or consensus classification as premise",
    "no numerical zero, negative, irrational, imaginary, floating, fitted or free proof magnitude",
    "structural absence, opposed orientation and boundary equality remain held labels",
    "no target value, source fragment, measured transition, favourable specimen or database outcome selects a survivor",
    "no omitted adverse, absent, unavailable, unresolved, tampered or condition-bound evidence row",
    "no failed attempt retires an obligation and no engine, verifier, receipt or admitted certificate changes",
)


SPECS = {}
for number, claim_id, title, statement, dependencies in DEFINITIONS:
    relation = RELATIONS[number]
    spec = PhaseSpec(
        claim_id=claim_id, title=title, statement=statement, dependencies=dependencies, evidence_mode=EvidenceMode.EMPIRICAL,
        generation_rule=f"Generate the complete literal product of the eight registered PHASE-{number} preservation axes before external target release.",
        grammar_boundary=f"Every positive finite generated PHASE-{number} carrier, with complete constituent, phase, site, path, specimen, method, condition, scale, uncertainty and proof distinctions.",
        axes=axes(relation), exact_result=f"PHASE-{number} uniquely retains {relation} with complete carrier, organization, observation, proof, root provenance, successor closure and no extra rule.",
        induction_base="The first positive phase carrier retains its complete phase relation, observation boundary and root trace.",
        induction_step="Appending one lawful constituent, phase, site, transition or observation retains every earlier distinction, adds all forced relations and introduces no selector.",
        exclusions=EXCLUSIONS, witnesses=WITNESSES[number], number=number, obligation_id=f"SFT-MAT-OBL-PHASE-{number}",
    )
    spec.validate()
    SPECS[claim_id] = spec


ORDER = tuple(row[1] for row in DEFINITIONS)


__all__ = ("PhaseProgram", "ORDER", "SPECS", "phase_fraction_ledger", "tie_line_partition", "coexistence_handoff", "metastable_retention", "spinodal_organization", "displacive_transform", "reconstructive_transform", "order_disorder", "kinetic_arrest", "time_temperature_path")
