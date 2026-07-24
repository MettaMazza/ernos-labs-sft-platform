"""Post-seal NIST comparison for terminal atomic-precision successors."""

from __future__ import annotations

from fractions import Fraction
import json
from pathlib import Path

from sft.engine.source import hash_file
from sft.physics.atomic_precision_successor_laws_v1 import (
    TERMINAL_FINE_ID,
    TERMINAL_HYPERFINE_ID,
    TERMINAL_LAMB_ID,
    terminal_fine_carrier,
    terminal_hyperfine_carrier_interval,
    terminal_lamb_carrier,
)
from sft.physics.generated_empirical_law import (
    BlindExternalMeasurementValidator,
    EmpiricalPhysicsSpec,
    ExternalTargetRow,
    empirical_dimensions,
)
from sft.physics.prior_value_laws import positive_take


SOURCE_ID = "ATOMIC-PRECISION-SUCCESSOR-NIST-2022-2026"
SOURCE_PATH = "experiments/external_sources/physics/snapshots/atomic-precision-successor-source-record.json"
SOURCE_HASH = "sha256:1660817704753cfd689a7f9a4513cab4b3f40a53f5c58329d3610cc905dffd84"
COMPONENT_HASHES = {
    "rydberg": "sha256:77fb90e66c40db3e6eb16630bc9c88e4c7c8beddbe5e71be406f2f26e3f67e67",
    "lamb_and_fine": "sha256:4d7e7f34b98ab2fc4df68b38247f818f6fc8bdf7f25f91abcdfbc329e22d2f32",
    "hyperfine": "sha256:33d048a7f7a8d83e5c2b0b96e442b495cf23b888ad1386d7205b17930af9f152",
}
LAMB_LABEL = "terminal-Lamb-prediction-contained-in-complete-NIST-Bezginov-interval__observational-prediction-protocol-passed"
FINE_LABEL = "terminal-fine-prediction-contained-in-conservative-direct-NIST-experimental-interval__observational-prediction-protocol-passed"
HYPERFINE_LABEL = "terminal-hyperfine-central-prediction-inside-NIST-21cm-interval-and-complete-carrier-interval-overlaps__observational-prediction-protocol-passed"


def authoritative_record(root: Path) -> dict[str, object]:
    path = root / SOURCE_PATH
    if hash_file(path) != SOURCE_HASH:
        raise ValueError("atomic precision source record identity changed")
    payload = json.loads(path.read_text(encoding="utf-8"))
    custody = payload.get("custody", {})
    required = {
        "development_targets_already_known": True,
        "classification": "observational_derivation",
        "protocol_classification": "observational-data-informed_target-inaccessible_sealed-prediction",
        "empirical_prediction_protocol": True,
        "target_inaccessible_during_prediction_execution": True,
        "formal_relations_contain_measurement": False,
        "measurements_select_formal_survivors": False,
        "engine_prediction_sealed_before_target_release_within_run": True,
        "complete_reported_uncertainties_retained": True,
        "earlier_leading_receipts_preserved": True,
        "unfavorable_results_preserved": True,
    }
    if any(custody.get(key) != value for key, value in required.items()):
        raise ValueError("atomic precision custody disclosure changed")
    sources = payload.get("sources", {})
    if set(sources) != set(COMPONENT_HASHES):
        raise ValueError("atomic precision source set changed")
    for key, expected in COMPONENT_HASHES.items():
        row = sources[key]
        component = root / row.get("snapshot_path", "missing")
        if row.get("snapshot_hash") != expected or hash_file(component) != expected:
            raise ValueError(f"atomic precision component identity changed: {key}")
    fine = sources["lamb_and_fine"]["rows"]["direct_experimental_fine_interval"]
    if fine.get("consensus_ritz_value_used") is not False:
        raise ValueError("atomic fine comparison admitted a consensus Ritz selector")
    if payload.get("comparison_policy", {}).get("provenance") != (
        "Observation informed the explicit frozen successor relations. The executable law module contains none of these values and cannot open this record. Complete grammar enumeration, unique selection and sealing precede target release."
    ):
        raise ValueError("atomic precision comparison provenance changed")
    return payload


def symmetric_interval(value: str, uncertainty: str) -> tuple[Fraction, Fraction]:
    centre = Fraction(value)
    spread = Fraction(uncertainty)
    lower = positive_take(centre, spread)
    return lower, centre + spread


def rydberg_interval(root: Path) -> tuple[Fraction, Fraction]:
    row = authoritative_record(root)["sources"]["rydberg"]["row"]
    return symmetric_interval(row["value_hz"], row["standard_uncertainty_hz"])


def target_interval(root: Path, kind: str) -> tuple[Fraction, Fraction]:
    sources = authoritative_record(root)["sources"]
    if kind == "lamb":
        row = sources["lamb_and_fine"]["rows"]["lamb_2p1_2_minus_2s1_2"]
        return symmetric_interval(row["value_hz"], row["standard_uncertainty_hz"])
    if kind == "fine":
        row = sources["lamb_and_fine"]["rows"]["direct_experimental_fine_interval"]
        return symmetric_interval(row["value_hz"], row["conservative_uncertainty_hz"])
    if kind == "hyperfine":
        row = sources["hyperfine"]["row"]
        return symmetric_interval(row["value_hz"], row["standard_uncertainty_hz"])
    raise ValueError("unknown atomic precision target")


def translated_prediction_interval(root: Path, kind: str) -> tuple[Fraction, Fraction]:
    rydberg = rydberg_interval(root)
    if kind == "lamb":
        carrier = terminal_lamb_carrier()
        return carrier * rydberg[0], carrier * rydberg[1]
    if kind == "fine":
        carrier = terminal_fine_carrier()
        return carrier * rydberg[0], carrier * rydberg[1]
    if kind == "hyperfine":
        carrier = terminal_hyperfine_carrier_interval()
        return carrier[0] * rydberg[0], carrier[1] * rydberg[1]
    raise ValueError("unknown atomic precision prediction")


def hyperfine_central_carrier_interval(root: Path) -> tuple[Fraction, Fraction]:
    row = authoritative_record(root)["sources"]["rydberg"]["row"]
    centre = Fraction(row["value_hz"])
    carrier = terminal_hyperfine_carrier_interval()
    return carrier[0] * centre, carrier[1] * centre


def intervals_overlap(left: tuple[Fraction, Fraction], right: tuple[Fraction, Fraction]) -> bool:
    return left[0] <= right[1] and right[0] <= left[1]


def atomic_precision_classification(root: Path, kind: str) -> str:
    prediction = translated_prediction_interval(root, kind)
    target = target_interval(root, kind)
    if kind in {"lamb", "fine"}:
        if not target[0] <= prediction[0] <= prediction[1] <= target[1]:
            raise ValueError(f"terminal {kind} prediction left the complete registered interval")
        return {"lamb": LAMB_LABEL, "fine": FINE_LABEL}[kind]
    central = hyperfine_central_carrier_interval(root)
    if not intervals_overlap(prediction, target):
        raise ValueError("complete hyperfine carrier and measurement intervals do not overlap")
    if not target[0] <= central[0] <= central[1] <= target[1]:
        raise ValueError("central-Rydberg hyperfine prediction left the complete NIST interval")
    return HYPERFINE_LABEL


def _empirical_spec(
    claim_id: str,
    kind: str,
    label: str,
    source_locator: str,
) -> EmpiricalPhysicsSpec:
    carrier_witness = {
        "lamb": terminal_lamb_carrier() > Fraction(1, 10 ** 7),
        "fine": terminal_fine_carrier() > Fraction(1, 10 ** 6),
        "hyperfine": terminal_hyperfine_carrier_interval()[0] > Fraction(1, 10 ** 7),
    }[kind]
    comparison = {
        "lamb": "contained in the complete NIST Bezginov standard-uncertainty interval",
        "fine": "contained in the conservative direct experimental interval formed from NIST input rows A28 and A29",
        "hyperfine": "inside the NIST 21-cm interval at the central Rydberg carrier, while the complete propagated carrier interval overlaps it",
    }[kind]
    return EmpiricalPhysicsSpec(
        claim_id=claim_id,
        title=f"Terminal hydrogen {kind} post-seal NIST comparison",
        statement=(
            f"Observation informed the explicit terminal {kind} relation.  The NIST target and Rydberg "
            "carrier remain capability-closed while the engine exhausts the formal grammar and seals the "
            f"exact dimensionless prediction; post-seal translation is {comparison}."
        ),
        dependencies=(
            claim_id,
            "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
            "SFT-PHYS-MEAS-TARGET-CUSTODY-001",
            "SFT-PHYS-MEAS-UNCERTAINTY-001",
            "SFT-MATH-EXACT-ARITHMETIC-001",
        ),
        generation_rule=f"Generate the complete eight-axis post-seal terminal hydrogen {kind} comparison product.",
        grammar_boundary=f"The complete registered NIST {kind} target, exact Rydberg carrier and uncertainties, immutable predecessor receipts, custody disclosure and sealed target-inaccessible Fold prediction.",
        dimensions=empirical_dimensions(
            f"sealed-terminal-{kind}-ratio-times-postseal-Rydberg-versus-complete-NIST-interval",
            "The exact relation, all reported uncertainties, observational provenance and predecessor receipts remain visible while the post-seal interval decision is exact.",
        ),
        exact_result=f"The sealed terminal {kind} dimensionless carrier passes the complete registered NIST comparison: {comparison}.",
        induction_base="The source record retains the exact measured row, complete uncertainty, component identity, sealed prediction and observational provenance.",
        induction_step="Every later metrology revision forms a new comparison receipt and cannot rewrite this seal, its source rows or any predecessor result.",
        exclusions=(
            "no target or Rydberg value in the executable law",
            "no measured value selecting the formal survivor",
            "no fitted coefficient, hidden target knowledge or uncertainty enlargement",
            "no floating-point interval decision",
            "no erased leading or adverse receipt",
        ),
        operational_witnesses=((
            "target-free-exact-carrier",
            f"The {kind} carrier is exact and positive before source release.",
            carrier_witness,
        ),),
        experiment_id=f"SFT-EXP-PHYS-ATOMIC-{kind.upper()}-TERMINAL-005",
        expected_observation_label=label,
        target_rows=(ExternalTargetRow(
            f"NIST-ATOMIC-{kind.upper()}-COMPLETE",
            SOURCE_ID,
            source_locator,
            label,
        ),),
        source_snapshot_path=SOURCE_PATH,
        source_snapshot_hash=SOURCE_HASH,
        falsification_condition=(
            f"The sealed {kind} prediction fails its complete registered interval decision, a source or "
            "uncertainty changes, a target becomes readable before sealing, a measured value selects the "
            "formal survivor, observational provenance is hidden, or a predecessor receipt is erased."
        ),
    )


LAMB_EMPIRICAL_SPEC = _empirical_spec(
    TERMINAL_LAMB_ID,
    "lamb",
    LAMB_LABEL,
    "NIST CODATA 2022 Table XIV A29, complete Bezginov value and standard uncertainty",
)
FINE_EMPIRICAL_SPEC = _empirical_spec(
    TERMINAL_FINE_ID,
    "fine",
    FINE_LABEL,
    "positive sum of NIST CODATA 2022 Table XIV experimental inputs A28 and A29 with conservative component-uncertainty sum",
)
HYPERFINE_EMPIRICAL_SPEC = _empirical_spec(
    TERMINAL_HYPERFINE_ID,
    "hyperfine",
    HYPERFINE_LABEL,
    "NIST Atomic Spectroscopy H I 1s hyperfine and 21-cm row with complete uncertainty",
)


EMPIRICAL_SPEC_BY_ID = {
    TERMINAL_LAMB_ID: LAMB_EMPIRICAL_SPEC,
    TERMINAL_FINE_ID: FINE_EMPIRICAL_SPEC,
    TERMINAL_HYPERFINE_ID: HYPERFINE_EMPIRICAL_SPEC,
}


class AtomicPrecisionValidator:
    def __init__(self, root: Path, kind: str, spec: EmpiricalPhysicsSpec):
        self.root = root.resolve()
        self.kind = kind
        self.spec = spec

    def validate(self, sealed):
        validation = BlindExternalMeasurementValidator(self.root, self.spec).validate(sealed)
        expected = {
            "lamb": LAMB_LABEL,
            "fine": FINE_LABEL,
            "hyperfine": HYPERFINE_LABEL,
        }[self.kind]
        if atomic_precision_classification(self.root, self.kind) != expected or not validation.passed:
            raise ValueError(f"terminal {self.kind} authoritative classification changed")
        return validation


for _spec in EMPIRICAL_SPEC_BY_ID.values():
    _spec.validate()


__all__ = (
    "AtomicPrecisionValidator",
    "EMPIRICAL_SPEC_BY_ID",
    "FINE_EMPIRICAL_SPEC",
    "FINE_LABEL",
    "HYPERFINE_EMPIRICAL_SPEC",
    "HYPERFINE_LABEL",
    "LAMB_EMPIRICAL_SPEC",
    "LAMB_LABEL",
    "atomic_precision_classification",
    "authoritative_record",
    "target_interval",
    "translated_prediction_interval",
)
