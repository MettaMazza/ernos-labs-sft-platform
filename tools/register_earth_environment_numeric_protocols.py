#!/usr/bin/env python3
"""Freeze Earth numeric comparison protocols before target-data retrieval."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "experiments/earth_environment/quake_magnitude_frequency_protocol.json"


def digest(value: object) -> str:
    return "sha256:" + hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def main() -> None:
    pre_source = json.loads((ROOT / "experiments/sealed_predictions/earth_environment_foundation_complete_pre_source.json").read_text(encoding="utf-8"))
    registry = json.loads((ROOT / "experiments/earth_environment/source_registry.json").read_text(encoding="utf-8"))
    protocol = {
        "schema": "sft-v3-earth-quake-magnitude-frequency-blind-protocol/1",
        "claim_id": "SFT-EARTH-QUAKE-MAGNITUDE-FREQUENCY-001",
        "experiment_id": "SFT-EXP-EARTH-QUAKE-MAGNITUDE-FREQUENCY-001-E1",
        "complete_branch_pre_source_seal": pre_source["complete_branch_pre_source_seal_hash"],
        "source_registry_hash": registry["registry_hash"],
        "source_id": "USGS-EARTHQUAKE-FDSN-001",
        "target_query": {
            "endpoint": "https://earthquake.usgs.gov/fdsnws/event/1/query",
            "format": "geojson",
            "starttime": "2010-01-01T00:00:00Z",
            "endtime": "2020-01-01T00:00:00Z",
            "minmagnitude": "5.0",
            "orderby": "time-asc",
            "limit": "20000",
        },
        "catalog_boundary": "Global USGS-comcat events returned by the fixed FDSN query, preserving every returned magnitude, magnitude type, status and missing field.",
        "sealed_derivational_exponent": {"numerator": 1, "denominator": 1},
        "comparison_only_conventional_magnitude_relation": "For thresholds 5.0 and 6.0, compute the observed cumulative count ratio N(M>=5)/N(M>=6). The unit Gutenberg-Richter exponent corresponds to a factor of ten per one conventional magnitude unit.",
        "primary_exact_comparison": "Compare the positive finite count ratio with ten; no event may be deleted by magnitude type or residual after the target opens.",
        "sampling_interval": "Compute an exact finite binomial 95-percent confidence enclosure for the proportion N(M>=6)/N(M>=5); the sealed unit exponent is observationally compatible only if one tenth lies inside that enclosure.",
        "adverse_rows": ["missing magnitude", "nonfinite external magnitude", "catalog truncation at limit", "event status or magnitude-type heterogeneity", "ratio outside registered interval"],
        "falsification_condition": "The presealed unit exponent is adverse on this declared catalog if the exact one-tenth exceedance share is outside the preregistered 95-percent finite-sample interval, or if the query is truncated or cannot be reproduced.",
        "target_data_opened_before_protocol": False,
        "measurement_may_change_derivation": False,
    }
    protocol["protocol_hash"] = digest(protocol)
    PATH.parent.mkdir(parents=True, exist_ok=True)
    PATH.write_text(json.dumps(protocol, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    checkpoint_path = ROOT / "census/earth_environment_continuation_checkpoint.json"
    checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
    checkpoint.update({
        "quake_numeric_protocol_path": str(PATH.relative_to(ROOT)),
        "quake_numeric_protocol_hash": protocol["protocol_hash"],
        "quake_target_opened": False,
        "next_exact_operation": "audit_registered_source_features_then_open_fixed_quake_target",
    })
    checkpoint_path.write_text(json.dumps(checkpoint, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"registered Earth numeric protocol: {protocol['protocol_hash']}")


if __name__ == "__main__":
    main()
