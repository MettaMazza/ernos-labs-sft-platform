#!/usr/bin/env python3
"""Execute the registered homogeneous-magnitude earthquake holdout."""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import urllib.parse
import urllib.request

from scipy.stats import beta

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "experiments/earth_environment/quake_magnitude_frequency_holdout_protocol_v2.json"
TARGET = ROOT / "experiments/external_sources/earth_environment/targets/usgs_quakes_2020_2026_m6_holdout.geojson"
RESULT = ROOT / "experiments/earth_environment/quake_magnitude_frequency_holdout_result_v2.json"


def digest(value: object) -> str:
    return "sha256:" + hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def main() -> None:
    protocol = json.loads(PROTOCOL.read_text(encoding="utf-8"))
    protocol_hash = protocol.pop("protocol_hash")
    if digest(protocol) != protocol_hash:
        raise ValueError("quake holdout protocol changed")
    protocol["protocol_hash"] = protocol_hash
    checkpoint_path = ROOT / "census/earth_environment_continuation_checkpoint.json"
    checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
    if checkpoint.get("quake_holdout_target_opened") is not False:
        raise ValueError("quake holdout target was already opened")
    parameters = {key: value for key, value in protocol["target_query"].items() if key != "endpoint"}
    locator = protocol["target_query"]["endpoint"] + "?" + urllib.parse.urlencode(parameters)
    request = urllib.request.Request(locator, headers={"User-Agent": "Ernos-Labs-SFT-Earth-Evidence-Capture/1.0"})
    opened = datetime.now(timezone.utc).isoformat()
    with urllib.request.urlopen(request, timeout=60) as response:
        raw = response.read(); status = getattr(response, "status", None); resolved = response.geturl()
    TARGET.write_bytes(raw)
    target_hash = "sha256:" + hashlib.sha256(raw).hexdigest()
    document = json.loads(raw)
    features = document.get("features", [])
    retained = []
    for feature in features:
        p = feature.get("properties", {})
        retained.append({"event_id": feature.get("id"), "magnitude": p.get("mag"), "magnitude_type": p.get("magType"), "status": p.get("status"), "time": p.get("time")})
    homogeneous = [row for row in retained if row["magnitude_type"] == protocol["registered_analysis_class"]["magnitude_type_exact_label"] and isinstance(row["magnitude"], (int, float)) and not isinstance(row["magnitude"], bool) and math.isfinite(float(row["magnitude"]))]
    lower_threshold = float(protocol["registered_analysis_class"]["lower_threshold"])
    upper_threshold = float(protocol["registered_analysis_class"]["upper_threshold"])
    n = sum(float(row["magnitude"]) >= lower_threshold for row in homogeneous)
    k = sum(float(row["magnitude"]) >= upper_threshold for row in homogeneous)
    if not (n > 0 and k > 0 and k < n):
        raise ValueError("holdout lacks a positive finite two-threshold sample")
    lower = float(beta.ppf(0.025, k, n-k+1)); upper = float(beta.ppf(0.975, k+1, n-k))
    expected = Fraction(1, 10)
    truncated = len(features) >= int(protocol["target_query"]["limit"])
    passed = lower <= float(expected) <= upper and not truncated
    result = {
        "schema": "sft-v3-earth-quake-magnitude-frequency-holdout-result/2",
        "claim_id": protocol["claim_id"], "experiment_id": protocol["experiment_id"],
        "protocol_path": str(PROTOCOL.relative_to(ROOT)), "protocol_hash": protocol_hash,
        "first_adverse_result_hash": protocol["first_adverse_result_hash"], "first_adverse_result_reclassified": False,
        "target_opened_at_utc": opened, "requested_locator": locator, "resolved_locator": resolved, "http_status": status,
        "target_snapshot_path": str(TARGET.relative_to(ROOT)), "target_snapshot_hash": target_hash,
        "returned_event_count": len(features), "catalog_truncated": truncated,
        "all_returned_rows_retained": True, "returned_magnitude_type_counts": dict(sorted(Counter(str(row["magnitude_type"]) for row in retained).items())),
        "registered_homogeneous_label": "mww", "homogeneous_lower_threshold_count": n, "homogeneous_upper_threshold_count": k,
        "observed_exceedance_share_exact": {"numerator": k, "denominator": n},
        "observed_count_ratio_exact": {"numerator": Fraction(n,k).numerator, "denominator": Fraction(n,k).denominator},
        "clopper_pearson_95_interval_comparison_only": {"lower": format(lower,".17g"), "upper": format(upper,".17g")},
        "sealed_expected_share_inside_interval": lower <= float(expected) <= upper,
        "passed": passed, "derivation_changed": False,
    }
    result["result_hash"] = digest(result)
    RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    checkpoint.update({"quake_holdout_target_opened": True, "quake_holdout_target_snapshot_path": str(TARGET.relative_to(ROOT)), "quake_holdout_target_snapshot_hash": target_hash, "quake_holdout_result_path": str(RESULT.relative_to(ROOT)), "quake_holdout_result_hash": result["result_hash"], "quake_holdout_result_passed": passed, "status": "quake_mixed_adverse_and_homogeneous_holdout_recorded_external_targets_not_yet_consolidated", "next_exact_operation": "build_complete_claim_specific_external_target_record_preserving_both_quake_results"})
    checkpoint_path.write_text(json.dumps(checkpoint, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"quake holdout: returned={len(features)} mww6={n} mww7={k} interval=[{lower:.6g},{upper:.6g}] passed={passed}")
    print(f"result={result['result_hash']}")


if __name__ == "__main__":
    main()
