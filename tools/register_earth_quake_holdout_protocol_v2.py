#!/usr/bin/env python3
"""Register an independent homogeneous-magnitude holdout after the mixed-catalog adverse result."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "experiments/earth_environment/quake_magnitude_frequency_holdout_protocol_v2.json"


def digest(value: object) -> str:
    return "sha256:" + hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def main() -> None:
    first = json.loads((ROOT / "experiments/earth_environment/quake_magnitude_frequency_result.json").read_text(encoding="utf-8"))
    if first["passed"] is not False or first["adverse_conditions"]["magnitude_type_heterogeneity_present"] is not True:
        raise ValueError("the registered reason for a homogeneous holdout is absent")
    protocol = {
        "schema": "sft-v3-earth-quake-magnitude-frequency-holdout-protocol/2",
        "claim_id": "SFT-EARTH-QUAKE-MAGNITUDE-FREQUENCY-001",
        "experiment_id": "SFT-EXP-EARTH-QUAKE-MAGNITUDE-FREQUENCY-001-E2",
        "pre_source_derivation_seal": json.loads((ROOT / "experiments/sealed_predictions/earth_environment_foundation_complete_pre_source.json").read_text(encoding="utf-8"))["complete_branch_pre_source_seal_hash"],
        "first_adverse_result_path": "experiments/earth_environment/quake_magnitude_frequency_result.json",
        "first_adverse_result_hash": first["result_hash"],
        "first_adverse_result_remains_dispositive_for_its_mixed_catalog": True,
        "holdout_reason": "The first protocol preregistered magnitude-type heterogeneity as an adverse condition. This new unopened interval tests one uniform USGS preferred moment-magnitude label; it does not reclassify the first result.",
        "target_query": {"endpoint": "https://earthquake.usgs.gov/fdsnws/event/1/query", "format": "geojson", "starttime": "2020-01-01T00:00:00Z", "endtime": "2026-01-01T00:00:00Z", "minmagnitude": "6.0", "orderby": "time-asc", "limit": "20000"},
        "registered_analysis_class": {"magnitude_type_exact_label": "mww", "lower_threshold": "6.0", "upper_threshold": "7.0"},
        "all_nonmatching_rows_preserved": True,
        "sealed_expected_exceedance_share": {"numerator": 1, "denominator": 10},
        "acceptance": "One tenth must fall inside the two-sided Clopper-Pearson 95-percent finite-sample interval for N(mww>=7)/N(mww>=6); the query must be untruncated and every returned row retained.",
        "target_opened_before_registration": False,
        "derivation_or_first_protocol_changed": False,
    }
    protocol["protocol_hash"] = digest(protocol)
    PATH.write_text(json.dumps(protocol, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    checkpoint_path = ROOT / "census/earth_environment_continuation_checkpoint.json"
    checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
    checkpoint.update({"quake_holdout_protocol_path": str(PATH.relative_to(ROOT)), "quake_holdout_protocol_hash": protocol["protocol_hash"], "quake_holdout_target_opened": False, "next_exact_operation": "open_fixed_homogeneous_magnitude_holdout_and_preserve_all_returned_rows"})
    checkpoint_path.write_text(json.dumps(checkpoint, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"registered quake holdout protocol: {protocol['protocol_hash']}")


if __name__ == "__main__":
    main()
