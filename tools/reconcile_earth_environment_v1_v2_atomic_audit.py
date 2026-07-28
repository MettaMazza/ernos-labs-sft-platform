#!/usr/bin/env python3
"""Reconcile every frozen V1/V2 Earth atom to admitted V3 receipts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "audits/earth_environment_v1_v2_initial_atomic_ownership.json"
OUTPUT = ROOT / "audits/earth_environment_v1_v2_atomic_reconciliation.json"
MARKDOWN = ROOT / "audits/earth_environment_v1_v2_atomic_reconciliation.md"

ATOM_CLAIMS = {
    "SFT-PRIOR-V1-XIV10-EARTH-IONOSPHERE-RESONANCE": ("SFT-EARTH-EARTH-IONOSPHERE-RESONANCE-001",),
    "SFT-PRIOR-V2-280-EARTH-TIPPING": ("SFT-EARTH-EARTH-SYSTEM-TIPPING-001",),
    "SFT-PRIOR-V2-280-EARTH-QUAKE-MAGNITUDE-FREQUENCY": ("SFT-EARTH-EARTHQUAKE-CATALOG-001", "SFT-EARTH-QUAKE-MAGNITUDE-FREQUENCY-001"),
}


def identity(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def main() -> None:
    initial = json.loads(INPUT.read_text(encoding="utf-8"))
    census = json.loads((ROOT / "census/claims.json").read_text(encoding="utf-8"))["claims"]
    admitted = {row["claim_id"]: row for row in census if row.get("model_admitted") is True}
    atoms = initial["atomic_questions"]
    if set(ATOM_CLAIMS) != {row["atom_id"] for row in atoms}:
        raise RuntimeError("atomic mapping differs from the frozen Earth surface")
    rows = []
    for atom in atoms:
        claim_ids = ATOM_CLAIMS[atom["atom_id"]]
        missing = [claim_id for claim_id in claim_ids if claim_id not in admitted]
        wrong = [claim_id for claim_id in claim_ids if admitted.get(claim_id, {}).get("branch") != "earth_environment"]
        rows.append({
            **atom,
            "v3_claim_ids": list(claim_ids),
            "engine_receipt_hashes": [admitted[claim_id]["receipt_hash"] for claim_id in claim_ids if claim_id in admitted],
            "same_strength_status": "closed" if not missing and not wrong else "open",
            "missing_claim_ids": missing,
            "wrong_branch_claim_ids": wrong,
        })
    closed = sum(row["same_strength_status"] == "closed" for row in rows)
    payload = {
        "schema": "sft-v3-earth-environment-v1-v2-atomic-reconciliation/1",
        "audit_date": "2026-07-28",
        "initial_audit_path": str(INPUT.relative_to(ROOT)),
        "initial_audit_identity": initial["audit_identity"],
        "source_surface": initial["source_surface"],
        "prior_answers_used_as_v3_premises": False,
        "prior_questions_used_as_accountability_surface": True,
        "atom_count": len(rows),
        "same_strength_closed_atom_count": closed,
        "same_strength_open_atom_count": len(rows) - closed,
        "all_engine_receipts_present": closed == len(rows),
        "status": "current_evidence_closed_extension_open" if closed == len(rows) else "open",
        "atoms": rows,
    }
    payload["audit_hash"] = identity(payload)
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Earth and Environmental Sciences V1/V2 atomic reconciliation",
        "",
        f"Status: `{payload['status']}`.",
        "",
        f"All `{initial['source_surface']['total_v1_v2_entries_reviewed']}` V1/V2 entries remain reviewed. All `{len(rows)}` frozen Earth questions map to current V3 engine receipts: `{closed}` closed, `{len(rows) - closed}` open.",
        "",
        "Prior work supplies accountability questions, never a V3 proof premise. Each mapped result was independently generated and admitted through the canonical engine.",
        "",
        "| Prior atom | Family | V3 admitted claims | Status |",
        "|---|---|---|---|",
    ]
    for row in rows:
        lines.append(f"| `{row['atom_id']}` | `{row['family']}` | {', '.join(f'`{claim}`' for claim in row['v3_claim_ids'])} | `{row['same_strength_status']}` |")
    lines.extend(["", "## Audit identity", "", f"`{payload['audit_hash']}`", ""])
    MARKDOWN.write_text("\n".join(lines), encoding="utf-8")
    if closed != len(rows):
        raise RuntimeError("Earth atomic reconciliation remains open")
    print(f"Earth atomic reconciliation: {closed}/{len(rows)} closed; {payload['audit_hash']}")


if __name__ == "__main__":
    main()
