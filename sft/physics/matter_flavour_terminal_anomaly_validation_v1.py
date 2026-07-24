"""Exact post-seal validation of terminal electron and muon anomalies.

The observational data informed the explicit laws.  During each official
prediction execution this module's source capability remains closed until the
engine has enumerated, uniquely selected and sealed the exact consequence.
Only then is the registered measurement record released for comparison.
"""

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
from sft.physics.matter_flavour_terminal_anomaly_laws_v1 import (
    TERMINAL_ELECTRON_ANOMALY_ID,
    TERMINAL_MUON_ANOMALY_ID,
    terminal_electron_anomaly,
    terminal_muon_anomaly,
)
from sft.physics.prior_value_laws import positive_take


SOURCE_ID = "MATTER-FLAVOUR-TERMINAL-ANOMALY-AUTHORITATIVE-2022-2026"
SOURCE_PATH = "experiments/external_sources/physics/snapshots/matter-flavour-terminal-anomaly-source-record.json"
SOURCE_HASH = "sha256:4b506052fc5037576cd6ba4de8ee5afce74460f7a5cb8da4bc58cbb823f6732f"
COMPONENT_HASHES = {
    "electron": "sha256:77fb90e66c40db3e6eb16630bc9c88e4c7c8beddbe5e71be406f2f26e3f67e67",
    "muon": "sha256:22fa2f99c52932ed012dc222eb821c2cb1a3d387671d650b23fbbed87a6e80a0",
}
ELECTRON_LABEL = (
    "terminal-target-inaccessible-electron-anomaly-prediction-inside-complete-CODATA-"
    "interval__observational-prediction-protocol-passed"
)
MUON_LABEL = (
    "terminal-target-inaccessible-muon-anomaly-prediction-inside-complete-Fermilab-"
    "world-average-interval__observational-prediction-protocol-passed"
)


def authoritative_record(root: Path) -> dict[str, object]:
    path = root / SOURCE_PATH
    if hash_file(path) != SOURCE_HASH:
        raise ValueError("terminal anomaly source record identity changed")
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
        "complete_uncertainties_retained": True,
    }
    if any(custody.get(key) != value for key, value in required.items()):
        raise ValueError("terminal anomaly custody disclosure changed")
    sources = payload.get("sources", {})
    if set(sources) != set(COMPONENT_HASHES):
        raise ValueError("terminal anomaly source set changed")
    for key, expected_hash in COMPONENT_HASHES.items():
        source = sources[key]
        component = root / source.get("snapshot_path", "missing")
        if source.get("snapshot_hash") != expected_hash or hash_file(component) != expected_hash:
            raise ValueError(f"terminal {key} anomaly source identity changed")
    return payload


def source_interval(root: Path, key: str) -> tuple[Fraction, Fraction]:
    source = authoritative_record(root)["sources"][key]
    row = source["row"]
    centre = Fraction(row["value"])
    uncertainty = Fraction(row["standard_uncertainty"])
    lower = positive_take(centre, uncertainty)
    if not isinstance(lower, Fraction):
        raise ValueError(f"terminal {key} anomaly uncertainty exhausted its centre")
    return lower, centre + uncertainty


def anomaly_classification(root: Path, key: str) -> str:
    prediction = {
        "electron": terminal_electron_anomaly,
        "muon": terminal_muon_anomaly,
    }[key]()
    lower, upper = source_interval(root, key)
    if not lower <= prediction <= upper:
        raise ValueError(f"terminal {key} anomaly prediction left its complete interval")
    return {"electron": ELECTRON_LABEL, "muon": MUON_LABEL}[key]


def _empirical_spec(
    *,
    claim_id: str,
    particle: str,
    source_name: str,
    label: str,
    experiment_id: str,
) -> EmpiricalPhysicsSpec:
    prediction = {
        "electron": terminal_electron_anomaly,
        "muon": terminal_muon_anomaly,
    }[particle]
    return EmpiricalPhysicsSpec(
        claim_id=claim_id,
        title=f"Terminal {particle} magnetic-anomaly empirical prediction",
        statement=(
            f"Observation informed the explicit terminal {particle} law.  The measurement target is then "
            "placed behind the capability boundary while the engine completely enumerates, uniquely selects "
            "and seals the exact prediction; the complete authoritative interval is released only afterward."
        ),
        dependencies=(
            claim_id,
            "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
            "SFT-PHYS-MEAS-TARGET-CUSTODY-001",
            "SFT-PHYS-MEAS-UNCERTAINTY-001",
            "SFT-MATH-EXACT-ARITHMETIC-001",
        ),
        generation_rule=f"Generate the complete eight-axis post-seal terminal {particle} anomaly comparison product.",
        grammar_boundary=(
            f"The complete registered {source_name} {particle} anomaly row, exact central value and complete "
            "standard uncertainty, together with the sealed target-inaccessible Fold prediction and preserved provenance."
        ),
        dimensions=empirical_dimensions(
            f"sealed-terminal-{particle}-anomaly-versus-complete-authoritative-interval",
            "The complete uncertainty and observational-prediction custody remain visible while the sealed prediction is tested.",
        ),
        exact_result=(
            f"The exact terminal {particle} anomaly sealed without target access lies inside the complete "
            f"registered {source_name} standard-uncertainty interval."
        ),
        induction_base="The source row retains its exact central value, complete standard uncertainty and immutable sealed prediction.",
        induction_step="Every future source revision forms a new registered comparison and cannot rewrite this seal or its provenance.",
        exclusions=(
            "no measurement target in the executable relation",
            "no measured value selecting a formal survivor",
            "no fitted coefficient or uncertainty enlargement",
            "no floating-point interval decision",
            "no hidden observational provenance",
        ),
        operational_witnesses=((
            "target-free-exact-prediction",
            f"The {particle} prediction is an exact positive fraction before source release.",
            isinstance(prediction(), Fraction) and prediction() > Fraction(1, 10000),
        ),),
        experiment_id=experiment_id,
        expected_observation_label=label,
        target_rows=(ExternalTargetRow(
            f"{particle.upper()}-MAGNETIC-ANOMALY-COMPLETE",
            SOURCE_ID,
            f"complete {source_name} central value and standard uncertainty",
            label,
        ),),
        source_snapshot_path=SOURCE_PATH,
        source_snapshot_hash=SOURCE_HASH,
        falsification_condition=(
            f"The exact sealed {particle} prediction leaves the complete registered interval, the target "
            "becomes readable before sealing, a measured value selects the survivor, an uncertainty changes, "
            "or observational provenance is hidden."
        ),
    )


ELECTRON_EMPIRICAL_SPEC = _empirical_spec(
    claim_id=TERMINAL_ELECTRON_ANOMALY_ID,
    particle="electron",
    source_name="NIST CODATA",
    label=ELECTRON_LABEL,
    experiment_id="SFT-EXP-PHYS-QED-ELECTRON-MAGNETIC-ANOMALY-004",
)
MUON_EMPIRICAL_SPEC = _empirical_spec(
    claim_id=TERMINAL_MUON_ANOMALY_ID,
    particle="muon",
    source_name="Fermilab world-average",
    label=MUON_LABEL,
    experiment_id="SFT-EXP-PHYS-QED-MUON-MAGNETIC-ANOMALY-004",
)


class TerminalAnomalyValidator:
    def __init__(self, root: Path, particle: str, spec: EmpiricalPhysicsSpec):
        self.root = root.resolve()
        self.particle = particle
        self.spec = spec

    def validate(self, sealed):
        validation = BlindExternalMeasurementValidator(self.root, self.spec).validate(sealed)
        expected = {"electron": ELECTRON_LABEL, "muon": MUON_LABEL}[self.particle]
        if anomaly_classification(self.root, self.particle) != expected or not validation.passed:
            raise ValueError(f"terminal {self.particle} anomaly authoritative classification changed")
        return validation


EMPIRICAL_SPEC_BY_ID = {
    TERMINAL_ELECTRON_ANOMALY_ID: ELECTRON_EMPIRICAL_SPEC,
    TERMINAL_MUON_ANOMALY_ID: MUON_EMPIRICAL_SPEC,
}

for _spec in EMPIRICAL_SPEC_BY_ID.values():
    _spec.validate()


__all__ = (
    "ELECTRON_EMPIRICAL_SPEC",
    "ELECTRON_LABEL",
    "EMPIRICAL_SPEC_BY_ID",
    "MUON_EMPIRICAL_SPEC",
    "MUON_LABEL",
    "TerminalAnomalyValidator",
    "anomaly_classification",
    "authoritative_record",
    "source_interval",
)
