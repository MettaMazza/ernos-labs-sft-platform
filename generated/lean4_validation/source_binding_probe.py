#!/usr/bin/env python3
"""Read-only bridge from the registered Python executions to Lean's source gate.

The current model's executable claim factories are Python artifacts.  This
probe loads each factory through the frozen repository implementation,
recomputes its complete byte-level source manifest, and compares that manifest
with both the executable registration and the claim certificate.  It writes no
repository file; its single JSON object on stdout is consumed by Lean.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys

def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("usage: source_binding_probe.py <repository-root>")

    root = Path(sys.argv[1]).resolve()
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    from sft.engine.source import build_source_manifest, hash_file
    from sft.verification import _load_execution

    entries = json.loads(
        (root / "census" / "execution_manifest.json").read_text(encoding="utf-8")
    ).get("claims")
    if not isinstance(entries, list):
        raise SystemExit("execution manifest claims must be a list")
    census_rows = json.loads(
        (root / "census" / "claims.json").read_text(encoding="utf-8")
    ).get("claims")
    if not isinstance(census_rows, list):
        raise SystemExit("claim census claims must be a list")
    current_receipts = {
        row.get("claim_id"): row.get("receipt_hash")
        for row in census_rows
        if isinstance(row, dict)
    }

    passed_claim_ids: list[str] = []
    issues: list[dict[str, str]] = []
    preserved_certificate_source_lineages = 0
    for entry in entries:
        claim_id = str(entry.get("claim_id", "<missing-claim-id>"))
        try:
            execution = _load_execution(root, entry)
            if execution.program.registration.claim_id != claim_id:
                raise ValueError("execution factory and manifest claim identities differ")
            manifest = build_source_manifest(root, execution.source_files)
            registration_hash = execution.program.registration.source_hash
            certificate = json.loads(
                (root / "claims" / claim_id / "certificate.json").read_text(encoding="utf-8")
            )
            certificate_hash = certificate.get("source_manifest_hash")
            if manifest.manifest_hash != registration_hash:
                raise ValueError(
                    "recomputed source manifest differs from executable registration: "
                    f"recomputed={manifest.manifest_hash} registered={registration_hash}"
                )
            if manifest.manifest_hash != certificate_hash:
                certificate_receipt = certificate.get("engine_receipt_hash")
                if certificate_receipt == current_receipts.get(claim_id):
                    raise ValueError(
                        "recomputed source manifest differs from current-lineage certificate: "
                        f"recomputed={manifest.manifest_hash} certificate={certificate_hash}"
                    )
                preserved_certificate_source_lineages += 1
            passed_claim_ids.append(claim_id)
        except Exception as exc:  # fail closed while retaining all claim-level failures
            issues.append(
                {
                    "claim_id": claim_id,
                    "detail": f"{type(exc).__name__}: {exc}",
                }
            )

    result = {
        "schema": "sft-lean4-source-binding-probe/1",
        "claim_count": len(entries),
        "census_file_hash": hash_file(root / "census" / "claims.json"),
        "execution_manifest_file_hash": hash_file(
            root / "census" / "execution_manifest.json"
        ),
        "passed_claim_ids": passed_claim_ids,
        "passed_claim_count": len(passed_claim_ids),
        "preserved_certificate_source_lineage_count": preserved_certificate_source_lineages,
        "issue_count": len(issues),
        "issues": issues,
    }
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0 if not issues else 1


if __name__ == "__main__":
    raise SystemExit(main())
