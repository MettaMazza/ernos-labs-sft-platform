#!/usr/bin/env python3
"""Audit every preregistered Consciousness source feature without erasing failures."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pypdf import PdfReader  # noqa: E402
from sft.consciousness_cognitive_science.sources import SOURCES  # noqa: E402


OUTPUT = ROOT / "experiments/consciousness/source_feature_audit.json"
SNAPSHOT_ROOT = ROOT / "experiments/external_sources/consciousness"
MANIFESTS = tuple(SNAPSHOT_ROOT / f"capture_manifest_v{version}.json" for version in range(2, 6))
MANIFESTS = (SNAPSHOT_ROOT / "capture_manifest.json",) + MANIFESTS

SEMANTIC_ALIASES = {
    ("CONSC-CIE-1931-CMF", "one nm wavelength steps"): ("1 nm wavelength steps",),
    ("CONSC-SYNESTHESIA-BATTERY-2007", "internal consistency task"): ("internal consistency test",),
}


def file_hash(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def identity(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def text_from(path: Path) -> str:
    if path.suffix.casefold() == ".pdf":
        return "\n".join(page.extract_text() or "" for page in PdfReader(path).pages)
    return path.read_text(encoding="utf-8", errors="ignore")


def is_interstitial(text: str) -> bool:
    lowered = text.casefold()
    return "recaptcha/challengepage" in lowered or "checking your browser before accessing" in lowered


def manifest_rows(payload: dict[str, object]) -> list[dict[str, object]]:
    if isinstance(payload.get("rows"), list):
        return list(payload["rows"])
    if "source_id" in payload:
        return [payload]
    return []


def main() -> None:
    manifests = [(path, json.loads(path.read_text(encoding="utf-8"))) for path in MANIFESTS]
    rows_by_source: dict[str, list[tuple[Path, dict[str, object]]]] = {}
    for manifest_path, manifest in manifests:
        for row in manifest_rows(manifest):
            rows_by_source.setdefault(str(row["source_id"]), []).append((manifest_path, row))

    source_rows = []
    total_features = present_features = absent_features = 0
    for source in SOURCES:
        transports = []
        usable_texts = []
        usable_paths = []
        for manifest_path, row in rows_by_source.get(source.source_id, []):
            snapshot = row.get("snapshot_path")
            transport = {
                "manifest_path": str(manifest_path.relative_to(ROOT)),
                "capture_status": row.get("capture_status"),
                "http_status": row.get("http_status"),
                "snapshot_path": snapshot,
                "snapshot_hash": row.get("snapshot_hash"),
                "usable_for_feature_audit": False,
                "exclusion_reason": None,
            }
            if snapshot:
                path = ROOT / str(snapshot)
                if not path.exists():
                    transport["exclusion_reason"] = "snapshot_absent"
                elif row.get("snapshot_hash") and file_hash(path) != row["snapshot_hash"]:
                    raise ValueError(f"snapshot hash mismatch: {snapshot}")
                else:
                    content = text_from(path)
                    if is_interstitial(content):
                        transport["exclusion_reason"] = "preserved_interstitial_not_scientific_content"
                    elif row.get("article_identity_verified") is False:
                        transport["exclusion_reason"] = "preserved_response_failed_article_identity_check"
                    else:
                        transport["usable_for_feature_audit"] = True
                        usable_texts.append(content)
                        usable_paths.append(str(path.relative_to(ROOT)))
            else:
                transport["exclusion_reason"] = "transport_failed_no_snapshot"
            transports.append(transport)

        corpus = "\n".join(usable_texts).casefold()
        features = []
        for feature in source.registered_features:
            literal = feature.casefold() in corpus
            aliases = SEMANTIC_ALIASES.get((source.source_id, feature), ())
            alias_hits = [alias for alias in aliases if alias.casefold() in corpus]
            status = "literal_present" if literal else "registered_unit_or_term_alias_present" if alias_hits else "absent_from_captured_content"
            features.append(
                {
                    "feature": feature,
                    "status": status,
                    "alias_hits": alias_hits,
                    "present": literal or bool(alias_hits),
                }
            )
            total_features += 1
            present_features += int(literal or bool(alias_hits))
            absent_features += int(not literal and not alias_hits)

        source_rows.append(
            {
                "source_id": source.source_id,
                "evidence_class": source.evidence_class,
                "adverse_or_boundary_role": source.adverse_or_boundary_role,
                "usable_snapshot_paths": usable_paths,
                "usable_snapshot_count": len(usable_paths),
                "transport_history": transports,
                "registered_features": features,
                "all_registered_features_present": all(row["present"] for row in features),
                "missing_registered_features": [row["feature"] for row in features if not row["present"]],
            }
        )

    payload = {
        "schema": "sft-v3-consciousness-source-feature-audit/1",
        "audit_date": "2026-07-27",
        "source_count": len(source_rows),
        "registered_feature_count": total_features,
        "present_feature_count": present_features,
        "absent_feature_count": absent_features,
        "all_transport_and_content_failures_preserved": True,
        "absence_is_not_relabelled_as_support": True,
        "semantic_alias_policy": "Only spelling-equivalent unit or registered-test-name variants listed explicitly in this artifact may satisfy a feature.",
        "manifest_hashes": {str(path.relative_to(ROOT)): file_hash(path) for path, _ in manifests},
        "sources": source_rows,
    }
    payload["audit_hash"] = identity(payload)
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    checkpoint_path = ROOT / "census/consciousness_continuation_checkpoint.json"
    checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
    checkpoint.update(
        {
            "status": "registered_source_features_audited",
            "source_feature_audit": str(OUTPUT.relative_to(ROOT)),
            "source_feature_audit_hash": payload["audit_hash"],
            "registered_source_feature_count": total_features,
            "present_source_feature_count": present_features,
            "absent_source_feature_count": absent_features,
            "next_exact_operation": "build_claim_specific_external_bindings_and_postseal_targets",
        }
    )
    checkpoint_path.write_text(json.dumps(checkpoint, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        f"audited {len(source_rows)} sources: {present_features}/{total_features} registered features present; "
        f"{absent_features} absent and preserved; {payload['audit_hash']}"
    )


if __name__ == "__main__":
    main()
