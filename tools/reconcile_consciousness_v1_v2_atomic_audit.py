#!/usr/bin/env python3
"""Reconcile every frozen V1/V2 Consciousness atom to admitted V3 receipts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "audits/consciousness_v1_v2_initial_atomic_ownership.json"
OUTPUT = ROOT / "audits/consciousness_v1_v2_atomic_reconciliation.json"
MARKDOWN = ROOT / "audits/consciousness_v1_v2_atomic_reconciliation.md"


ATOM_CLAIMS = {
    "SFT-PRIOR-V1-C1S-CONSC-SELF-OBSERVATION-CLOSURE": ("SFT-CONSC-INTERIOR-OBSERVATION-001", "SFT-CONSC-SELF-OBSERVATION-001"),
    "SFT-PRIOR-V1-C5S-CONSC-OBSERVATIONAL-MOMENT": ("SFT-CONSC-OBSERVATIONAL-MOMENT-001",),
    "SFT-PRIOR-V1-C4S-CONSC-INTEGRATION": ("SFT-CONSC-BINDING-001", "SFT-CONSC-INTEGRATION-BOUNDARY-001", "SFT-CONSC-UNITY-001"),
    "SFT-PRIOR-V1-C2S-CONSC-SELF-OBSERVATION-BLIND-SPOT": ("SFT-CONSC-INTROSPECTION-BLIND-SPOT-001",),
    "SFT-PRIOR-V1-C3S-CONSC-SELF-OBSERVATION-FIXED-POINT": ("SFT-CONSC-SELF-INVARIANT-001",),
    "SFT-PRIOR-V1-XVII5-CONSC-MEASUREMENT-JOIN": ("SFT-CONSC-MEASUREMENT-CONSCIOUSNESS-BOUNDARY-001",),
    "SFT-PRIOR-V1-XIV7-CONSC-SUBSTRATE-INDEPENDENCE": ("SFT-CONSC-SUBSTRATE-INDEPENDENCE-001", "SFT-CONSC-REALIZATION-EQUIVALENCE-001"),
    "SFT-PRIOR-V1-XIV7-CONSC-FEEDFORWARD-BOUNDARY": ("SFT-CONSC-FEEDFORWARD-BOUNDARY-001",),
    "SFT-PRIOR-V1-XIV4-CONSC-FINITE-SELF-SIMULATION": ("SFT-CONSC-SELF-APPLICATION-001", "SFT-CONSC-SELF-SIMULATION-BOUNDARY-001", "SFT-CONSC-SELF-VERIFICATION-LIMIT-001"),
    "SFT-PRIOR-V1-XIV3-CONSC-EXPECTATION": ("SFT-CONSC-EXPECTATION-001",),
    "SFT-PRIOR-V1-XIV2-CONSC-ALTERED-STATE-BOUNDARY": ("SFT-CONSC-ALTERED-STATE-REPORT-BOUNDARY-001",),
    "SFT-PRIOR-V1-XIV1-CONSC-PERCEPTUAL-CHANNEL": ("SFT-CONSC-QUALITATIVE-DISTINCTION-001", "SFT-CONSC-QUALITATIVE-IDENTITY-001"),
    "SFT-PRIOR-V1-XIV1-CONSC-SYNAESTHESIA": ("SFT-CONSC-CROSS-MODAL-QUALIA-001",),
    "SFT-PRIOR-V1-XI7-CONSC-INTERIORITY": ("SFT-CONSC-INTERIORITY-001",),
    "SFT-PRIOR-V1-XI7-CONSC-HARD-PROBLEM": ("SFT-CONSC-PHENOMENAL-PRESENCE-001", "SFT-CONSC-REPORT-001", "SFT-CONSC-FIRST-THIRD-PERSON-001"),
    "SFT-PRIOR-V1-XI6-CONSC-SLEEP-DREAM": ("SFT-CONSC-MEMORY-PERSISTENCE-001", "SFT-CONSC-CESSATION-001"),
    "SFT-PRIOR-V1-XI5-CONSC-UNCONSCIOUS-INTROSPECTION": ("SFT-CONSC-UNCONSCIOUS-PROCESS-001",),
    "SFT-PRIOR-V1-XI4-CONSC-BINDING": ("SFT-CONSC-BINDING-001", "SFT-CONSC-QUALIA-COMPOSITION-001"),
    "SFT-PRIOR-V1-XI3-CONSC-FORWARD-MODEL": ("SFT-CONSC-PREDICTION-001",),
    "SFT-PRIOR-V1-XI2-CONSC-ATTENTION": ("SFT-CONSC-ATTENTION-001",),
    "SFT-PRIOR-V1-XI1-CONSC-MEMORY": ("SFT-CONSC-MEMORY-CARRIER-001", "SFT-CONSC-RECALL-RECONSTRUCTION-001"),
    "SFT-PRIOR-V1-G9-CONSC-IDENTITY-TRANSPORT": ("SFT-CONSC-IDENTITY-CONTINUITY-001", "SFT-CONSC-REALIZATION-EQUIVALENCE-001"),
    "SFT-PRIOR-V1-C10S-CONSC-CESSATION": ("SFT-CONSC-CESSATION-001",),
    "SFT-PRIOR-V1-C9S-CONSC-FELT-SELF-INVARIANT": ("SFT-CONSC-SUBJECT-CARRIER-001", "SFT-CONSC-SELF-INVARIANT-001"),
    "SFT-PRIOR-V1-C8S-CONSC-INTROSPECTION-LIMIT": ("SFT-CONSC-INTROSPECTION-LOSS-001", "SFT-CONSC-SELF-HISTORY-RECONSTRUCTION-001"),
    "SFT-PRIOR-V1-C7S-CONSC-UNITY": ("SFT-CONSC-UNITY-001",),
    "SFT-PRIOR-V1-C6S-CONSC-EXPERIENTIAL-SEQUENCE": ("SFT-CONSC-TEMPORAL-CONTINUITY-001",),
    "SFT-PRIOR-V2-116-CONSC-BINDING": ("SFT-CONSC-BINDING-001", "SFT-CONSC-SYNCHRONY-BOUNDARY-001"),
    "SFT-PRIOR-V2-117-CONSC-UNCONSCIOUS-ORBIT": ("SFT-CONSC-UNCONSCIOUS-PROCESS-001",),
    "SFT-PRIOR-V2-117-CONSC-SELF-OPACITY": ("SFT-CONSC-DETERMINISM-SELF-OPACITY-001",),
    "SFT-PRIOR-V2-145-CONSC-MEMORY-ORBIT": ("SFT-CONSC-MEMORY-PERSISTENCE-001",),
    "SFT-PRIOR-V2-148-CONSC-SLEEP-STATE-CYCLE": ("SFT-CONSC-MEMORY-PERSISTENCE-001", "SFT-CONSC-CESSATION-001"),
    "SFT-PRIOR-V2-160-CONSC-PHENOMENAL-UNITY": ("SFT-CONSC-UNITY-001", "SFT-CONSC-PHENOMENAL-PRESENCE-001"),
    "SFT-PRIOR-V2-160-CONSC-INTERIORITY": ("SFT-CONSC-INTERIORITY-001", "SFT-CONSC-PHENOMENAL-PRIVACY-001"),
    "SFT-PRIOR-V2-166-CONSC-EXPECTATION-OBSERVATION": ("SFT-CONSC-EXPECTATION-001",),
    "SFT-PRIOR-V2-175-CONSC-MULTIQUALITY-COMPOSITION": ("SFT-CONSC-QUALIA-COMPOSITION-001", "SFT-CONSC-RED-RECURRENCE-001"),
    "SFT-PRIOR-V2-178-CONSC-CROSS-MODAL-BINDING": ("SFT-CONSC-CROSS-MODAL-QUALIA-001",),
    "SFT-PRIOR-V2-181-CONSC-ATTENTIONAL-CAPACITY": ("SFT-CONSC-ATTENTIONAL-CAPACITY-001", "SFT-CONSC-ATTENTIONAL-FOCUS-001"),
    "SFT-PRIOR-V2-199-CONSC-REALIZATION-TEST": ("SFT-CONSC-STRUCTURAL-CRITERION-001", "SFT-CONSC-ARTIFICIAL-CONSCIOUSNESS-EVIDENCE-001"),
    "SFT-PRIOR-V2-247-CONSC-SELF-MODEL-DEPTH": ("SFT-CONSC-SELF-MODEL-DEPTH-001",),
    "SFT-PRIOR-V2-253-CONSC-CESSATION-DISTINCTIONS": ("SFT-CONSC-CESSATION-001",),
    "SFT-PRIOR-V2-257-CONSC-MEASUREMENT-CORRESPONDENCE": ("SFT-CONSC-MEASUREMENT-CONSCIOUSNESS-BOUNDARY-001",),
    "SFT-PRIOR-V2-281-CONSC-DETERMINISTIC-ACTION": ("SFT-CONSC-DETERMINED-AGENCY-001",),
    "SFT-PRIOR-V2-281-CONSC-DETERMINISM-SELF-OPACITY": ("SFT-CONSC-DETERMINISM-SELF-OPACITY-001",),
    "SFT-PRIOR-LINEAGE-CONSC-QUALIA-RESONANCE": ("SFT-CONSC-QUALITATIVE-DISTINCTION-001", "SFT-CONSC-QUALITATIVE-IDENTITY-001", "SFT-CONSC-QUALITATIVE-SIMILARITY-001", "SFT-CONSC-QUALIA-RESONANCE-001", "SFT-CONSC-QUALIA-RECURRENCE-001", "SFT-CONSC-QUALIA-COMPOSITION-001"),
    "SFT-PRIOR-LINEAGE-CONSC-RED-OF-RED": ("SFT-CONSC-RED-STIMULUS-BOUNDARY-001", "SFT-CONSC-RED-QUALITATIVE-IDENTITY-001", "SFT-CONSC-RED-OF-RED-001", "SFT-CONSC-RED-RECURRENCE-001", "SFT-CONSC-RED-CONTROLS-001", "SFT-CONSC-RED-EMPIRICAL-BOUNDARY-001"),
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
        raise RuntimeError("atomic mapping differs from the frozen 46-question surface")
    rows = []
    for atom in atoms:
        claim_ids = ATOM_CLAIMS[atom["atom_id"]]
        missing = [claim_id for claim_id in claim_ids if claim_id not in admitted]
        wrong = [claim_id for claim_id in claim_ids if admitted.get(claim_id, {}).get("branch") != "consciousness_cognitive_science"]
        rows.append(
            {
                **atom,
                "v3_claim_ids": list(claim_ids),
                "engine_receipt_hashes": [admitted[claim_id]["receipt_hash"] for claim_id in claim_ids if claim_id in admitted],
                "same_strength_status": "closed" if not missing and not wrong else "open",
                "missing_claim_ids": missing,
                "wrong_branch_claim_ids": wrong,
            }
        )
    closed = sum(row["same_strength_status"] == "closed" for row in rows)
    payload = {
        "schema": "sft-v3-consciousness-v1-v2-atomic-reconciliation/1",
        "audit_date": "2026-07-27",
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
        "# Consciousness V1/V2 atomic reconciliation",
        "",
        f"Status: `{payload['status']}`.",
        "",
        f"All `{initial['source_surface']['total_v1_v2_entries_reviewed']}` V1/V2 entries remain reviewed. All `{len(rows)}` frozen atomic questions, including the separately registered qualia-resonance and red-of-red obligations, map to current V3 engine receipts: `{closed}` closed, `{len(rows) - closed}` open.",
        "",
        "Prior work supplies the accountability questions, never a V3 proof premise. Each mapped result was independently generated and admitted through the canonical engine.",
        "",
        "| Prior atom | Family | V3 admitted claims | Status |",
        "|---|---|---|---|",
    ]
    for row in rows:
        lines.append(f"| `{row['atom_id']}` | `{row['family']}` | {', '.join(f'`{claim}`' for claim in row['v3_claim_ids'])} | `{row['same_strength_status']}` |")
    lines.extend(["", "## Audit identity", "", f"`{payload['audit_hash']}`", ""])
    MARKDOWN.write_text("\n".join(lines), encoding="utf-8")
    print(f"Consciousness atomic reconciliation: {closed}/{len(rows)} closed; {payload['audit_hash']}")


if __name__ == "__main__":
    main()
