#!/usr/bin/env python3
"""Register a replacement official coarsening identity after the frozen endpoint failed."""

from hashlib import sha256
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "census/materials_micro_coarsening_source_addendum_v1.json"


def canonical(value):
    return "sha256:" + sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def main():
    payload = {
        "schema": "sft-v3-materials-micro-source-addendum/1",
        "date": "2026-07-29",
        "authority": "Maria Smith",
        "original_registry_identity": "sha256:287bf62f3145a0701a67cf0a65a4718963ad2b6dea50403c02a48530a1e68da1",
        "affected_obligation": "SFT-MAT-OBL-MICRO-007",
        "failed_source_identity": "NIST-STRUCTURES-PRECIPITATION-HANDBOOK",
        "failed_source_status": "http_404_preserved",
        "replacement_source_identity": "NIST-BENCHMARK-COARSENING-2017",
        "replacement_source_uri": "https://www.nist.gov/publications/benchmark-problems-phase-field-modeling",
        "selection_reason": "Official NIST primary publication explicitly scoped to solute diffusion, second-phase growth, coarsening and an Ostwald-ripening benchmark.",
        "custody_disclosure": "The NIST search-result title and abstract-level topic summary were observed before this addendum; detailed document rows, figures, values and comparison outcomes were not opened.",
        "abstract_level_topic_content_observed": True,
        "detailed_target_content_present": False,
        "measured_value_present": False,
        "survivor_identity_present": False,
        "outcome_present": False,
        "failed_route_retained": "audits/MATERIALS_MICRO_001_009_SOURCE_CAPTURE_HALT_2026-07-29.json"
    }
    payload["addendum_identity"] = canonical(payload)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"addendum_identity": payload["addendum_identity"]}, indent=2))


if __name__ == "__main__":
    main()
