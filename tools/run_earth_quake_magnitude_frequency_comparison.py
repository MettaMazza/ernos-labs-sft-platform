#!/usr/bin/env python3
"""Open the fixed USGS target and execute the preregistered comparison."""

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


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL_PATH = ROOT / "experiments/earth_environment/quake_magnitude_frequency_protocol.json"
TARGET_PATH = ROOT / "experiments/external_sources/earth_environment/targets/usgs_quakes_2010_2020_m5.geojson"
RESULT_PATH = ROOT / "experiments/earth_environment/quake_magnitude_frequency_result.json"


def digest(value: object) -> str:
    return "sha256:" + hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def clopper_pearson(k: int, n: int, alpha: float = 0.05) -> tuple[float, float]:
    """Exact-binomial interval evaluated in the empirical adapter."""
    try:
        from scipy.stats import beta
    except ImportError as error:  # pragma: no cover - environment evidence
        raise RuntimeError("the registered exact-binomial empirical evaluator is unavailable") from error
    lower = 0.0 if k == 0 else float(beta.ppf(alpha / 2, k, n - k + 1))
    upper = 1.0 if k == n else float(beta.ppf(1 - alpha / 2, k + 1, n - k))
    return lower, upper


def main() -> None:
    protocol = json.loads(PROTOCOL_PATH.read_text(encoding="utf-8"))
    claimed = protocol.pop("protocol_hash")
    if digest(protocol) != claimed:
        raise ValueError("Earth quake protocol changed")
    protocol["protocol_hash"] = claimed
    checkpoint = json.loads((ROOT / "census/earth_environment_continuation_checkpoint.json").read_text(encoding="utf-8"))
    if checkpoint.get("quake_target_opened") is not False:
        raise ValueError("the fixed quake target has already been opened")

    query_parameters = {key: value for key, value in protocol["target_query"].items() if key != "endpoint"}
    query = urllib.parse.urlencode(query_parameters)
    locator = protocol["target_query"]["endpoint"] + "?" + query
    request = urllib.request.Request(locator, headers={"User-Agent": "Ernos-Labs-SFT-Earth-Evidence-Capture/1.0"})
    opened_at = datetime.now(timezone.utc).isoformat()
    with urllib.request.urlopen(request, timeout=60) as response:
        raw = response.read()
        resolved = response.geturl()
        http_status = getattr(response, "status", None)
        content_type = response.headers.get_content_type()
    TARGET_PATH.parent.mkdir(parents=True, exist_ok=True)
    TARGET_PATH.write_bytes(raw)
    target_hash = "sha256:" + hashlib.sha256(raw).hexdigest()
    document = json.loads(raw)
    features = document.get("features", [])
    limit = int(protocol["target_query"]["limit"])
    truncated = len(features) >= limit
    magnitude_rows = []
    missing = []
    for feature in features:
        properties = feature.get("properties", {})
        magnitude = properties.get("mag")
        record = {
            "event_id": feature.get("id"),
            "magnitude": magnitude,
            "magnitude_type": properties.get("magType"),
            "status": properties.get("status"),
            "time": properties.get("time"),
        }
        if isinstance(magnitude, bool) or not isinstance(magnitude, (int, float)) or not math.isfinite(float(magnitude)):
            missing.append(record)
        else:
            magnitude_rows.append(record)

    n5 = sum(float(row["magnitude"]) >= 5.0 for row in magnitude_rows)
    n6 = sum(float(row["magnitude"]) >= 6.0 for row in magnitude_rows)
    if n5 < 1 or n6 < 1:
        raise ValueError("the fixed quake target lacks the registered positive counts")
    exceedance = Fraction(n6, n5)
    count_ratio = Fraction(n5, n6)
    lower, upper = clopper_pearson(n6, n5)
    expected_share = Fraction(1, 10)
    compatible = lower <= float(expected_share) <= upper
    passed = compatible and not truncated and not missing

    result = {
        "schema": "sft-v3-earth-quake-magnitude-frequency-result/1",
        "claim_id": protocol["claim_id"],
        "experiment_id": protocol["experiment_id"],
        "protocol_path": str(PROTOCOL_PATH.relative_to(ROOT)),
        "protocol_hash": claimed,
        "target_opened_at_utc": opened_at,
        "transport_history": [
            {
                "status": "failed_before_target_release",
                "http_status": 400,
                "reason": "runner serialized the registered endpoint field as an unintended query parameter",
                "target_body_opened": False,
                "scientific_protocol_changed": False,
            },
            {
                "status": "captured",
                "http_status": http_status,
                "requested_locator": locator,
                "resolved_locator": resolved,
                "target_body_opened": True,
            },
        ],
        "requested_locator": locator,
        "resolved_locator": resolved,
        "http_status": http_status,
        "content_type": content_type,
        "target_snapshot_path": str(TARGET_PATH.relative_to(ROOT)),
        "target_snapshot_hash": target_hash,
        "returned_event_count": len(features),
        "catalog_limit": limit,
        "catalog_truncated": truncated,
        "usable_magnitude_count": len(magnitude_rows),
        "missing_or_nonfinite_magnitude_count": len(missing),
        "missing_or_nonfinite_magnitude_rows": missing,
        "magnitude_type_counts": dict(sorted(Counter(str(row["magnitude_type"]) for row in magnitude_rows).items())),
        "event_status_counts": dict(sorted(Counter(str(row["status"]) for row in magnitude_rows).items())),
        "threshold_counts": {"magnitude_at_least_5": n5, "magnitude_at_least_6": n6},
        "observed_exceedance_share_exact": {"numerator": exceedance.numerator, "denominator": exceedance.denominator},
        "observed_count_ratio_exact": {"numerator": count_ratio.numerator, "denominator": count_ratio.denominator},
        "sealed_expected_exceedance_share_exact": {"numerator": expected_share.numerator, "denominator": expected_share.denominator},
        "clopper_pearson_95_interval_comparison_only": {"lower": format(lower, ".17g"), "upper": format(upper, ".17g")},
        "sealed_unit_exponent_compatible_on_registered_catalog": compatible,
        "passed": passed,
        "adverse_conditions": {
            "catalog_truncated": truncated,
            "missing_or_nonfinite_magnitudes": bool(missing),
            "magnitude_type_heterogeneity_present": len({row["magnitude_type"] for row in magnitude_rows}) > 1,
            "event_status_heterogeneity_present": len({row["status"] for row in magnitude_rows}) > 1,
            "heterogeneity_rows_preserved_not_filtered": True,
        },
        "measurement_changed_derivation": False,
    }
    result["result_hash"] = digest(result)
    RESULT_PATH.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    checkpoint["quake_target_opened"] = True
    checkpoint["quake_target_snapshot_path"] = str(TARGET_PATH.relative_to(ROOT))
    checkpoint["quake_target_snapshot_hash"] = target_hash
    checkpoint["quake_numeric_result_path"] = str(RESULT_PATH.relative_to(ROOT))
    checkpoint["quake_numeric_result_hash"] = result["result_hash"]
    checkpoint["quake_numeric_result_passed"] = passed
    checkpoint["status"] = "quake_target_compared_claim_external_targets_not_yet_consolidated"
    checkpoint["next_exact_operation"] = "build_complete_claim_specific_external_target_record_preserving_all_adverse_rows"
    (ROOT / "census/earth_environment_continuation_checkpoint.json").write_text(json.dumps(checkpoint, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Earth quake comparison: events={len(features)} n5={n5} n6={n6} ratio={count_ratio.numerator}/{count_ratio.denominator} interval=[{lower:.6g},{upper:.6g}] passed={passed}")
    print(f"result={result['result_hash']}")


if __name__ == "__main__":
    main()
