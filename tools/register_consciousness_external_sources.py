#!/usr/bin/env python3
"""Preregister all Consciousness source identities after prediction sealing."""

from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.consciousness_cognitive_science.sources import FAMILY_SOURCE_IDS, SOURCES  # noqa: E402
from sft.engine.canonical import sha256_identity  # noqa: E402


def main() -> None:
    seal_path = ROOT / "experiments/sealed_predictions/consciousness_foundation_complete_pre_source.json"
    seal = json.loads(seal_path.read_text(encoding="utf-8"))
    claimed = seal["complete_branch_pre_source_seal_hash"]
    unsigned = {key: value for key, value in seal.items() if key != "complete_branch_pre_source_seal_hash"}
    if sha256_identity(unsigned) != claimed or seal["external_source_identities_selected"] is not False:
        raise ValueError("Consciousness predictions were not validly sealed before source selection")
    payload = {
        "schema": "sft-v3-consciousness-external-source-registry/1",
        "registration_date": "2026-07-27",
        "pre_source_prediction_seal": claimed,
        "source_content_captured_at_registration": False,
        "source_outcomes_may_change_derivation": False,
        "all_adverse_absent_null_and_unresolved_rows_required": True,
        "sources": [asdict(item) for item in SOURCES],
        "family_source_ids": FAMILY_SOURCE_IDS,
    }
    payload["registry_hash"] = sha256_identity(payload)
    path = ROOT / "experiments/consciousness/source_registry.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    checkpoint_path = ROOT / "census/consciousness_continuation_checkpoint.json"
    checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
    checkpoint.update({"status": "external_source_identities_preregistered_content_not_yet_captured", "source_registry_path": str(path.relative_to(ROOT)), "source_registry_hash": payload["registry_hash"], "registered_source_count": len(SOURCES), "next_exact_operation": "capture_preregistered_external_source_content_and_preserve_transport_failures"})
    checkpoint_path.write_text(json.dumps(checkpoint, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"registered {len(SOURCES)} Consciousness source identities: {payload['registry_hash']}")


if __name__ == "__main__":
    main()
