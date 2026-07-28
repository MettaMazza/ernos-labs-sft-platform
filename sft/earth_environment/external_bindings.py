"""Verified post-seal source bindings for Earth and Environmental Sciences."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

from sft.engine.canonical import sha256_identity
from sft.earth_environment.generated_law import EARTH_BLUEPRINTS


ROOT = Path(__file__).resolve().parents[2]
BINDINGS_PATH = "experiments/earth_environment/claim_source_bindings.json"
EXTERNAL_TARGETS_PATH = "experiments/earth_environment/claim_specific_external_targets.json"
SOURCE_FEATURE_AUDIT_PATH = "experiments/earth_environment/source_feature_audit.json"


def _verified_payload(relative: str, identity_key: str) -> dict[str, object]:
    payload = json.loads((ROOT / relative).read_text(encoding="utf-8"))
    claimed = payload.pop(identity_key)
    if sha256_identity(payload) != claimed:
        raise ValueError(f"Earth evidence identity mismatch: {relative}")
    payload[identity_key] = claimed
    return payload


@dataclass(frozen=True)
class EarthExternalBinding:
    claim_id: str
    family: str
    target_id: str
    source_ids: tuple[str, ...]
    expected_label: str
    required_evidence_features: tuple[str, ...]
    exact_numeric_test: object | None


_BINDINGS = _verified_payload(BINDINGS_PATH, "bindings_hash")
EARTH_EXTERNAL_BINDINGS = tuple(
    EarthExternalBinding(
        claim_id=row["claim_id"],
        family=row["family"],
        target_id=row["comparison_target_identity"],
        source_ids=tuple(row["source_ids"]),
        expected_label=row["sealed_predicted_observation_label"],
        required_evidence_features=tuple(row["required_evidence_features"]),
        exact_numeric_test=row["exact_numeric_test"],
    )
    for row in _BINDINGS["claims"]
)
BINDING_BY_CLAIM = {row.claim_id: row for row in EARTH_EXTERNAL_BINDINGS}


def validate_bindings() -> None:
    claim_ids = {row.claim_id for row in EARTH_BLUEPRINTS}
    if set(BINDING_BY_CLAIM) != claim_ids or len(EARTH_EXTERNAL_BINDINGS) != len(EARTH_BLUEPRINTS):
        raise ValueError("Earth external bindings do not cover the frozen inventory exactly")
    for blueprint in EARTH_BLUEPRINTS:
        binding = BINDING_BY_CLAIM[blueprint.claim_id]
        if binding.family != blueprint.family:
            raise ValueError("Earth binding family changed")
        if binding.expected_label != blueprint.predicted_observation_label:
            raise ValueError("Earth binding changed a pre-source prediction")
        if not binding.source_ids or not binding.required_evidence_features:
            raise ValueError("Earth claim lacks a registered evidence boundary")
        if binding.target_id != blueprint.claim_id.lower() + "-external-earth-evidence":
            raise ValueError("Earth target identity is invalid")


validate_bindings()


__all__ = (
    "BINDING_BY_CLAIM",
    "BINDINGS_PATH",
    "EARTH_EXTERNAL_BINDINGS",
    "EXTERNAL_TARGETS_PATH",
    "SOURCE_FEATURE_AUDIT_PATH",
    "EarthExternalBinding",
    "validate_bindings",
)
