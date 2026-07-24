"""Exact post-seal CODATA validation of terminal proton dressing."""

from __future__ import annotations

from fractions import Fraction
import json
from pathlib import Path

from sft.engine.source import hash_file
from sft.physics.generated_empirical_law import (
    BlindExternalMeasurementValidator,
    EmpiricalPhysicsSpec,
    ExternalTargetRow,
    empirical_dimensions,
)
from sft.physics.matter_flavour_laws_v1 import bisect_bracket, isolate_cubic_roots
from sft.physics.matter_flavour_terminal_proton_laws_v1 import (
    TERMINAL_PROTON_ID,
    terminal_proton_dressing,
    terminal_proton_retention,
)


SOURCE_ID = "MATTER-FLAVOUR-TERMINAL-PROTON-AUTHORITATIVE-2022-2026"
SOURCE_PATH = "experiments/external_sources/physics/snapshots/matter-flavour-terminal-proton-source-record.json"
SOURCE_HASH = "sha256:a2fd002521902242e3db10eac896389d2190f88169b827c3575640e9a31f2790"
COMPONENT_HASH = "sha256:77fb90e66c40db3e6eb16630bc9c88e4c7c8beddbe5e71be406f2f26e3f67e67"
EXPECTED_LABEL = (
    "terminal-target-free-proton-electron-prediction-contained-inside-complete-CODATA-"
    "standard-uncertainty__observational-prediction-protocol-passed"
)


def authoritative_record(root: Path) -> dict[str, object]:
    path = root / SOURCE_PATH
    if hash_file(path) != SOURCE_HASH:
        raise ValueError("terminal proton source record identity changed")
    payload = json.loads(path.read_text(encoding="utf-8"))
    custody = payload.get("custody", {})
    required = {
        "development_target_already_known": True,
        "classification": "observational_derivation",
        "protocol_classification": "observational-data-informed_target-inaccessible_sealed-prediction",
        "empirical_prediction_protocol": True,
        "target_inaccessible_during_prediction_execution": True,
        "formal_relation_contains_measurement": False,
        "measurement_selects_formal_survivor": False,
        "engine_prediction_sealed_before_target_release_within_run": True,
        "earlier_unfavorable_receipt_preserved": True,
        "complete_uncertainty_retained": True,
    }
    if any(custody.get(key) != value for key, value in required.items()):
        raise ValueError("terminal proton custody disclosure changed")
    source = payload.get("source", {})
    component = root / source.get("snapshot_path", "missing")
    if source.get("snapshot_hash") != COMPONENT_HASH or hash_file(component) != COMPONENT_HASH:
        raise ValueError("terminal proton component identity changed")
    return payload


def refined_roots() -> tuple[tuple[Fraction, Fraction], ...]:
    pair_sum = Fraction(1, 6)
    product_value = Fraction(1, 485)
    roots = isolate_cubic_roots(pair_sum, product_value)
    resolution = Fraction(1, 10 ** 18)
    while any(upper - lower > resolution for lower, upper in roots[:2]):
        roots = tuple(bisect_bracket(root, pair_sum, product_value) for root in roots)
    return roots


def terminal_proton_prediction_interval() -> tuple[Fraction, Fraction]:
    electron_root, muon_root = refined_roots()[:2]
    electron_mass = electron_root[0] ** 2, electron_root[1] ** 2
    muon_mass = muon_root[0] ** 2, muon_root[1] ** 2
    base = (
        Fraction(1, 3) * (Fraction(1, 1) / electron_mass[1] - Fraction(1, 1) / muon_mass[0]),
        Fraction(1, 3) * (Fraction(1, 1) / electron_mass[0] - Fraction(1, 1) / muon_mass[1]),
    )
    retention = terminal_proton_retention()
    result = base[0] * retention, base[1] * retention
    if result[0] >= result[1] or retention + terminal_proton_dressing() != Fraction(1, 1):
        raise ValueError("terminal proton exact enclosure failed")
    return result


def source_interval(root: Path) -> tuple[Fraction, Fraction]:
    row = authoritative_record(root)["source"]["row"]
    centre = Fraction(row["value"])
    uncertainty = Fraction(row["standard_uncertainty"])
    return centre - uncertainty, centre + uncertainty


def terminal_proton_classification(root: Path) -> str:
    prediction = terminal_proton_prediction_interval()
    target = source_interval(root)
    if not target[0] <= prediction[0] <= prediction[1] <= target[1]:
        raise ValueError("terminal proton prediction left the complete CODATA interval")
    return EXPECTED_LABEL


EMPIRICAL_SPEC = EmpiricalPhysicsSpec(
    claim_id=TERMINAL_PROTON_ID,
    title="Terminal proton/electron complete precision comparison",
    statement="The sealed target-free terminal composite dressing is compared with the complete NIST CODATA proton/electron value and standard uncertainty, while the earlier non-overlap and observational provenance remain preserved.",
    dependencies=(
        TERMINAL_PROTON_ID,
        "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
        "SFT-PHYS-MEAS-TARGET-CUSTODY-001",
        "SFT-PHYS-MEAS-UNCERTAINTY-001",
        "SFT-MATH-EXACT-ARITHMETIC-001",
    ),
    generation_rule="Generate the complete eight-axis post-seal terminal proton/electron comparison product.",
    grammar_boundary="The complete registered CODATA proton/electron row, its central value, standard uncertainty, prior adverse receipt, custody disclosure and exact algebraic prediction enclosure.",
    dimensions=empirical_dimensions("sealed-terminal-proton-graph-versus-complete-CODATA-interval", "The complete uncertainty and earlier unfavorable result remain visible while only the versioned successor is tested."),
    exact_result="The target-free terminal proton/electron algebraic enclosure is wholly contained inside the complete registered CODATA one-standard-uncertainty interval.",
    induction_base="The source row retains its exact central value, standard uncertainty and sealed prediction enclosure.",
    induction_step="Every refinement narrows the same algebraic root enclosure; it cannot change the law, source row, uncertainty or earlier adverse receipt.",
    exclusions=("no target value in the executable relation", "no fitted coefficient", "no enlarged uncertainty", "no erased earlier non-overlap", "no target-readable prediction execution"),
    operational_witnesses=(("target-free-positive-dressing", "The exact dressing is generated without opening the source record.", Fraction(1, 10 ** 6) < terminal_proton_dressing() < Fraction(1, 1000)),),
    experiment_id="SFT-EXP-PHYS-MATTER-PROTON-ELECTRON-TERMINAL-004",
    expected_observation_label=EXPECTED_LABEL,
    target_rows=(ExternalTargetRow("NIST-CODATA-PROTON-ELECTRON-COMPLETE", SOURCE_ID, "complete central value and standard uncertainty", EXPECTED_LABEL),),
    source_snapshot_path=SOURCE_PATH,
    source_snapshot_hash=SOURCE_HASH,
    falsification_condition="The sealed prediction enclosure leaves the complete registered CODATA interval, any uncertainty or adverse receipt is omitted, the target enters the relation, or observational provenance is hidden.",
)


class TerminalProtonValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()

    def validate(self, sealed):
        validation = BlindExternalMeasurementValidator(self.root, EMPIRICAL_SPEC).validate(sealed)
        if terminal_proton_classification(self.root) != EXPECTED_LABEL or not validation.passed:
            raise ValueError("terminal proton authoritative classification changed")
        return validation


EMPIRICAL_SPEC.validate()


__all__ = (
    "EMPIRICAL_SPEC",
    "EXPECTED_LABEL",
    "TerminalProtonValidator",
    "authoritative_record",
    "source_interval",
    "terminal_proton_classification",
    "terminal_proton_prediction_interval",
)
