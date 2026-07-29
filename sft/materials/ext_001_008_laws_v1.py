"""Exact Fold laws for the complete Materials EXT-001--008 family."""

from dataclasses import dataclass

from sft.engine import ClaimRegistration, EvidenceMode, ROOT_THEOREM
from sft.physics.structural_constants import (
    StructuralPhysicsProgram,
    StructuralPhysicsSpec,
    Witness,
    binary_axis,
)


def positive(value, name):
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError(name + " must be positive")
    return value


def ordered_response(specimen, condition_steps, states, transitions, method, uncertainty):
    steps = tuple(positive(value, "condition step") for value in condition_steps)
    states = tuple(states)
    transitions = tuple(tuple(row) for row in transitions)
    if not specimen or not steps or len(states) != len(steps) or len(transitions) + 1 != len(states):
        raise ValueError("extreme response path invalid")
    if any(len(row) != 2 for row in transitions) or not method or not uncertainty:
        raise ValueError("extreme response custody invalid")
    return {
        "specimen": specimen,
        "condition_steps": steps,
        "states": states,
        "transitions": transitions,
        "method": method,
        "uncertainty": uncertainty,
        "complete_path": True,
    }


def high_pressure_state(specimen, pressure_steps, states, transitions, method, uncertainty):
    result = ordered_response(specimen, pressure_steps, states, transitions, method, uncertainty)
    return {**result, "condition": "pressure", "pressure_state_held": True}


def high_temperature_state(specimen, temperature_steps, states, transitions, method, uncertainty):
    result = ordered_response(specimen, temperature_steps, states, transitions, method, uncertainty)
    return {**result, "condition": "temperature", "temperature_state_held": True}


def cryogenic_response(specimen, descending_steps, states, transitions, method, uncertainty):
    steps = tuple(descending_steps)
    if len(steps) < 2 or any(positive(value, "cryogenic step") <= positive(next_value, "cryogenic step") for value, next_value in zip(steps, steps[1:])):
        raise ValueError("cryogenic steps must descend")
    result = ordered_response(specimen, steps, states, transitions, method, uncertainty)
    return {**result, "condition": "cryogenic", "descending_path_held": True}


def electric_field_response(specimen, field_steps, states, transitions, method, uncertainty):
    result = ordered_response(specimen, field_steps, states, transitions, method, uncertainty)
    return {**result, "condition": "electric-field", "field_response_held": True}


def magnetic_field_response(specimen, field_steps, states, transitions, method, uncertainty):
    result = ordered_response(specimen, field_steps, states, transitions, method, uncertainty)
    return {**result, "condition": "magnetic-field", "field_response_held": True}


def shock_response(specimen, rate_steps, states, transitions, impact_path, method, uncertainty):
    result = ordered_response(specimen, rate_steps, states, transitions, method, uncertainty)
    impact_path = tuple(impact_path)
    if len(impact_path) < 2:
        raise ValueError("shock impact path incomplete")
    return {**result, "condition": "strain-rate-shock", "impact_path": impact_path, "shock_path_held": True}


def radiation_response(specimen, event_steps, states, transitions, defect_records, method, uncertainty):
    result = ordered_response(specimen, event_steps, states, transitions, method, uncertainty)
    defects = tuple((identity, before, after) for identity, before, after in defect_records)
    if not defects or len({row[0] for row in defects}) != len(defects):
        raise ValueError("radiation defect custody invalid")
    return {**result, "condition": "radiation", "defect_records": defects, "defect_custody_held": True}


def combined_extreme(specimen, condition_names, condition_steps, states, transitions, method, uncertainty):
    names = tuple(condition_names)
    step_rows = tuple(tuple(positive(value, "combined condition step") for value in row) for row in condition_steps)
    if len(names) < 2 or len(set(names)) != len(names) or not step_rows or any(len(row) != len(names) for row in step_rows):
        raise ValueError("combined extreme conditions invalid")
    result = ordered_response(specimen, tuple(range(1, len(step_rows) + 1)), states, transitions, method, uncertainty)
    return {**result, "condition_names": names, "condition_steps": step_rows, "combined_path_held": True}


BASE = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001",
    "SFT-MATH-EXACT-ARITHMETIC-001",
    "SFT-MATH-DISCRETE-001",
    "SFT-INFO-CONSERVATION-LOSS-001",
    "SFT-COMP-FORM-STATE-TRANSITION-001",
    "SFT-MAT-MEAS-TRACEABILITY-001",
    "SFT-MAT-PROC-WINDOW-PROVENANCE-010",
    "SFT-MAT-COMP-SIMULATION-EXPERIMENT-012",
)

DEFINITIONS = (
    ("001", "SFT-MAT-EXT-HIGH-PRESSURE-STATE-001", "High-pressure material state", "A high-pressure material state is the complete specimen, positive pressure-step, state-transition, method and uncertainty path; pressure cannot erase phase history.", BASE),
    ("002", "SFT-MAT-EXT-HIGH-TEMPERATURE-STATE-002", "High-temperature material state", "A high-temperature material state is the complete specimen, positive temperature-step, state-transition, method and uncertainty path; a terminal property cannot replace its thermal history.", BASE + ("SFT-MAT-EXT-HIGH-PRESSURE-STATE-001",)),
    ("003", "SFT-MAT-EXT-CRYOGENIC-RESPONSE-003", "Cryogenic material response", "Cryogenic response retains the exact descending positive temperature order and every material-state transition, method and uncertainty distinction.", BASE + ("SFT-MAT-EXT-HIGH-TEMPERATURE-STATE-002",)),
    ("004", "SFT-MAT-EXT-ELECTRIC-FIELD-RESPONSE-004", "High-electric-field material response", "Electric-field response retains every positive field step and material-state transition with specimen, method and uncertainty custody.", BASE + ("SFT-MAT-EXT-CRYOGENIC-RESPONSE-003", "SFT-MAT-ELEC-DIELECTRIC-LOSS-004")),
    ("005", "SFT-MAT-EXT-MAGNETIC-FIELD-RESPONSE-005", "High-magnetic-field material response", "Magnetic-field response retains every positive field step and material-state transition with specimen, method and uncertainty custody.", BASE + ("SFT-MAT-EXT-ELECTRIC-FIELD-RESPONSE-004", "SFT-MAT-MAGSC-SC-CRITICAL-FIELDS-009")),
    ("006", "SFT-MAT-EXT-SHOCK-RESPONSE-006", "High-strain-rate and shock response", "Shock response is the complete positive rate sequence, impact path and material-state transition trace; endpoint damage cannot erase loading history.", BASE + ("SFT-MAT-EXT-MAGNETIC-FIELD-RESPONSE-005", "SFT-MAT-MECH-IMPACT-011")),
    ("007", "SFT-MAT-EXT-RADIATION-RESPONSE-007", "Extreme-radiation material response", "Extreme-radiation response retains event order and every identified before-and-after defect record alongside the material-state path.", BASE + ("SFT-MAT-EXT-SHOCK-RESPONSE-006", "SFT-MAT-DEGR-RADIATION-DEFECT-RECOVERY-007")),
    ("008", "SFT-MAT-EXT-COMBINED-PATH-CUSTODY-008", "Combined-extreme condition and path custody", "A combined-extreme result retains at least two named conditions jointly at every ordered state; no single-condition projection may stand for the joint path.", BASE + ("SFT-MAT-EXT-RADIATION-RESPONSE-007",)),
)

RELATIONS = dict(zip((f"{index:03d}" for index in range(1, 9)), (
    "specimen-pressure-state-transition-method-uncertainty-path",
    "specimen-temperature-state-transition-method-uncertainty-path",
    "descending-positive-temperature-state-transition-path",
    "positive-electric-field-state-transition-path",
    "positive-magnetic-field-state-transition-path",
    "positive-rate-impact-state-transition-path",
    "radiation-event-defect-state-transition-path",
    "joint-named-condition-state-transition-path",
)))


def axes(relation):
    return (
        binary_axis("carrier", "carrier?", "terminal-label-only", "erased", "complete-positive-extreme-material-carrier", "held"),
        binary_axis("relation", "relation?", "imported-response-model", "not forced", relation, "exact"),
        binary_axis("path", "path?", "endpoint-only", "history erased", "complete-extreme-condition-state-path", "retained"),
        binary_axis("observation", "conditions?", "specimen-method-erased", "not reproducible", "specimen-method-condition-scale-uncertainty-held", "held"),
        binary_axis("record", "record?", "headline-only", "not reproducible", "complete-trace", "retained"),
        binary_axis("provenance", "selector?", "target-or-prior-model", "external selector", "root-bound-forward-forcing", "forced"),
        binary_axis("generality", "closure?", "selected-instance", "no successor", "positive-finite-successor-closure", "preserved"),
        binary_axis("extension", "extra?", "fit-exception-extra-rule", "manufactured", "no-extra-rule", "none"),
    )


WITNESSES = {
    "001": (Witness("pressure", "path", high_pressure_state("s", (1, 2), ("a", "b"), (("a", "b"),), "m", "u")["pressure_state_held"]),),
    "002": (Witness("temperature", "path", high_temperature_state("s", (1, 2), ("a", "b"), (("a", "b"),), "m", "u")["temperature_state_held"]),),
    "003": (Witness("cryogenic", "descent", cryogenic_response("s", (2, 1), ("a", "b"), (("a", "b"),), "m", "u")["descending_path_held"]),),
    "004": (Witness("electric", "field", electric_field_response("s", (1, 2), ("a", "b"), (("a", "b"),), "m", "u")["field_response_held"]),),
    "005": (Witness("magnetic", "field", magnetic_field_response("s", (1, 2), ("a", "b"), (("a", "b"),), "m", "u")["field_response_held"]),),
    "006": (Witness("shock", "path", shock_response("s", (1, 2), ("a", "b"), (("a", "b"),), ("load", "impact"), "m", "u")["shock_path_held"]),),
    "007": (Witness("radiation", "defects", radiation_response("s", (1, 2), ("a", "b"), (("a", "b"),), (("d1", "a", "b"),), "m", "u")["defect_custody_held"]),),
    "008": (Witness("combined", "joint", combined_extreme("s", ("heat", "force"), ((1, 1), (2, 2)), ("a", "b"), (("a", "b"),), "m", "u")["combined_path_held"]),),
}


@dataclass(frozen=True)
class ExtSpec(StructuralPhysicsSpec):
    number: str = ""
    obligation_id: str = ""

    def validate(self):
        if self.number not in WITNESSES or len(self.axes) != 8 or not all(witness.passed for witness in self.witnesses):
            raise ValueError("invalid EXT spec")
        for axis in self.axes:
            axis.survivor


class ExtProgram(StructuralPhysicsProgram):
    @property
    def registration(self):
        return ClaimRegistration(
            claim_id=self.spec.claim_id,
            title=self.spec.title,
            branch="materials",
            statement=self.spec.statement,
            evidence_mode=EvidenceMode.EMPIRICAL,
            root_theorems=(ROOT_THEOREM,),
            dependencies=self.spec.dependencies,
            axioms=(),
            free_parameters=(),
            provenance=self.spec.provenance,
            source_hash=self.source_hash,
        )


EXCLUSIONS = (
    "no imported continuum response equation, fitted constitutive law, opaque oracle or prior proof as premise",
    "no numerical zero, negative, irrational, imaginary, floating, fitted or free proof magnitude",
    "structural absence and every specimen, condition, state, path, method, scale, uncertainty and outcome distinction remain held labels",
    "no external outcome selects a survivor",
    "all favourable adverse absent unavailable and unresolved result classes remain retained",
    "no failed attempt retires an obligation or changes protected authority",
)

SPECS = {}
for number, claim_id, title, statement, dependencies in DEFINITIONS:
    spec = ExtSpec(
        claim_id=claim_id,
        title=title,
        statement=statement,
        dependencies=dependencies,
        evidence_mode=EvidenceMode.EMPIRICAL,
        generation_rule=f"Complete literal product of eight EXT-{number} axes before target release.",
        grammar_boundary=f"Every positive finite EXT-{number} carrier with complete specimen, condition, state, path, method, uncertainty and observation distinctions.",
        axes=axes(RELATIONS[number]),
        exact_result=f"EXT-{number} uniquely retains {RELATIONS[number]} with complete carrier, condition path, observation, proof, root provenance, successor closure and no extra rule.",
        induction_base="The first positive extreme-condition material carrier retains every distinction.",
        induction_step="One lawful successor retains the complete prior condition and state path and adds no selector.",
        exclusions=EXCLUSIONS,
        witnesses=WITNESSES[number],
        number=number,
        obligation_id=f"SFT-MAT-OBL-EXT-{number}",
    )
    spec.validate()
    SPECS[claim_id] = spec

ORDER = tuple(row[1] for row in DEFINITIONS)
