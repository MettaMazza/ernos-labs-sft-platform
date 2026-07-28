#!/usr/bin/env python3
"""Audit preregistered Earth-source features without changing sealed laws."""

from __future__ import annotations

import hashlib
import html
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "experiments/earth_environment/source_registry.json"
MANIFEST_PATH = ROOT / "experiments/external_sources/earth_environment/capture_manifest.json"
ADDENDUM_PATH = ROOT / "experiments/external_sources/earth_environment/source_transport_addendum_v1.json"
AUDIT_PATH = ROOT / "experiments/earth_environment/source_feature_audit.json"


STOPWORDS = {
    "about", "access", "after", "against", "along", "among", "archive", "authoritative", "boundary",
    "complete", "coverage", "data", "dataset", "declared", "distinction", "earth", "environmental",
    "feature", "fields", "identity", "information", "measurement", "method", "observation", "official",
    "original", "product", "program", "programme", "provenance", "quality", "record", "registered",
    "resolved", "service", "source", "spatial", "temporal", "through", "where", "with",
}


def digest(value: object) -> str:
    return "sha256:" + hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def raw_hash(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def normalized_text(path: Path) -> str:
    text = path.read_bytes().decode("utf-8", "ignore")
    text = re.sub(r"<script[\s\S]*?</script>|<style[\s\S]*?</style>", " ", text, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", html.unescape(text)).lower()


def feature_tokens(feature: str) -> tuple[str, ...]:
    words = re.findall(r"[a-z0-9]+", feature.lower())
    distinctive = [word for word in words if len(word) >= 5 and word not in STOPWORDS]
    if not distinctive:
        distinctive = [word for word in words if len(word) >= 4]
    return tuple(dict.fromkeys(word[:7] for word in distinctive))


def main() -> None:
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    registry_hash = registry.pop("registry_hash")
    if digest(registry) != registry_hash:
        raise ValueError("Earth source registry changed")
    registry["registry_hash"] = registry_hash
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    manifest_hash = manifest.pop("manifest_hash")
    if digest(manifest) != manifest_hash:
        raise ValueError("Earth source capture manifest changed")
    manifest["manifest_hash"] = manifest_hash
    addendum = json.loads(ADDENDUM_PATH.read_text(encoding="utf-8"))
    addendum_hash = addendum.pop("addendum_hash")
    if digest(addendum) != addendum_hash:
        raise ValueError("Earth source transport addendum changed")
    addendum["addendum_hash"] = addendum_hash

    captures = {row["source_id"]: row for row in manifest["captures"]}
    source_rows = []
    feature_rows = []
    for source in registry["sources"]:
        capture = captures[source["source_id"]]
        transport_history = [capture]
        snapshot_path = capture["snapshot_path"]
        status = capture["transport_status"]
        if source["source_id"] == "SMITHSONIAN-GVP-VOTW-001":
            transport_history.append({"transport_id": addendum["registration"]["transport_id"], **addendum["capture"]})
            if addendum["capture"]["snapshot_path"]:
                snapshot_path = addendum["capture"]["snapshot_path"]
                status = "captured_via_addendum_prior_failure_preserved"
        text = ""
        if snapshot_path:
            path = ROOT / snapshot_path
            expected = next(row["snapshot_hash"] for row in reversed(transport_history) if row.get("snapshot_path") == snapshot_path)
            if raw_hash(path) != expected:
                raise ValueError(f"Earth source snapshot changed: {snapshot_path}")
            text = normalized_text(path)
        local_features = []
        for feature in source["registered_features"]:
            tokens = feature_tokens(feature)
            matched = tuple(token for token in tokens if token in text)
            feature_status = "present" if matched else "absent_from_captured_surface" if snapshot_path else "unresolved_transport_failed"
            row = {
                "source_id": source["source_id"],
                "feature": feature,
                "derived_search_tokens": list(tokens),
                "matched_tokens": list(matched),
                "status": feature_status,
                "snapshot_path": snapshot_path,
            }
            local_features.append(row)
            feature_rows.append(row)
        source_rows.append({
            "source_id": source["source_id"],
            "source_identity": source["source_identity"],
            "transport_status": status,
            "transport_history": transport_history,
            "snapshot_path_used_for_feature_audit": snapshot_path,
            "registered_feature_count": len(local_features),
            "present_feature_count": sum(row["status"] == "present" for row in local_features),
            "absent_feature_count": sum(row["status"] == "absent_from_captured_surface" for row in local_features),
            "unresolved_feature_count": sum(row["status"] == "unresolved_transport_failed" for row in local_features),
            "features": local_features,
        })

    audit = {
        "schema": "sft-v3-earth-environment-source-feature-audit/1",
        "registry_path": str(REGISTRY_PATH.relative_to(ROOT)),
        "registry_hash": registry_hash,
        "capture_manifest_path": str(MANIFEST_PATH.relative_to(ROOT)),
        "capture_manifest_hash": manifest_hash,
        "source_transport_addendum_path": str(ADDENDUM_PATH.relative_to(ROOT)),
        "source_transport_addendum_hash": addendum_hash,
        "feature_extraction_rule": "For each preregistered feature, derive lowercase alphanumeric tokens mechanically, remove the frozen generic stopword set, truncate retained tokens to seven characters, and report every match or absence. No source-specific token was selected after capture.",
        "source_count": len(source_rows),
        "registered_feature_count": len(feature_rows),
        "present_feature_count": sum(row["status"] == "present" for row in feature_rows),
        "absent_feature_count": sum(row["status"] == "absent_from_captured_surface" for row in feature_rows),
        "unresolved_feature_count": sum(row["status"] == "unresolved_transport_failed" for row in feature_rows),
        "original_failed_transport_count": manifest["failed_count"],
        "failed_transports_preserved": True,
        "sources": source_rows,
    }
    audit["audit_hash"] = digest(audit)
    AUDIT_PATH.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    checkpoint_path = ROOT / "census/earth_environment_continuation_checkpoint.json"
    checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
    checkpoint.update({
        "status": "source_features_audited_fixed_quake_target_not_yet_opened",
        "source_feature_audit": str(AUDIT_PATH.relative_to(ROOT)),
        "source_feature_audit_hash": audit["audit_hash"],
        "registered_source_feature_count": audit["registered_feature_count"],
        "present_source_feature_count": audit["present_feature_count"],
        "absent_source_feature_count": audit["absent_feature_count"],
        "unresolved_source_feature_count": audit["unresolved_feature_count"],
        "next_exact_operation": "open_fixed_usgs_quake_target_and_execute_preregistered_numeric_comparison",
    })
    checkpoint_path.write_text(json.dumps(checkpoint, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Earth source feature audit: present={audit['present_feature_count']} absent={audit['absent_feature_count']} unresolved={audit['unresolved_feature_count']} hash={audit['audit_hash']}")


if __name__ == "__main__":
    main()
