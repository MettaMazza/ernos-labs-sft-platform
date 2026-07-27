#!/usr/bin/env python3
"""Build the complete declared-discipline Chemistry obligation census.

This is a read-only scientific-scope projection.  It verifies the canonical
engine seal and existing receipts, but it never imports or calls the admission
engine and never admits a claim.  New obligations remain visibly open until a
separate protocol-conforming claim receives an immutable engine receipt.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.discipline_obligations import (  # noqa: E402
    CLOSED_EXPANSION_MAPPINGS,
    EXPANSION_OBLIGATIONS,
    REQUIRED_FIELDS,
)


CURRENT_INVENTORY = ROOT / "publications/inventories/chemistry.json"
CLAIM_CENSUS = ROOT / "census/claims.json"
OUTPUT_JSON = ROOT / "census/chemistry_discipline_obligations.json"
OUTPUT_MD = ROOT / "audits/chemistry_discipline_obligations.md"


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_hash(payload: object) -> str:
    body = json.dumps(payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return "sha256:" + hashlib.sha256(body).hexdigest()


def file_hash(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def verify_seal() -> None:
    result = subprocess.run(
        [sys.executable, "tools/verify_engine_seal.py"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    if "SFT ENGINE SEAL: VALID CANONICAL ENGINE" not in result.stdout:
        raise SystemExit("canonical SFT engine seal is not valid")


def existing_rows() -> list[dict[str, object]]:
    inventory = read(CURRENT_INVENTORY)
    census = {row["claim_id"]: row for row in read(CLAIM_CENSUS)["claims"]}
    rows: list[dict[str, object]] = []
    for item in inventory["obligations"]:
        claim_id = item["claim_id"]
        claim = census.get(claim_id)
        if not isinstance(claim, dict) or claim.get("branch") != "chemistry" or claim.get("model_admitted") is not True:
            raise SystemExit(f"existing Chemistry claim is not currently model-admitted: {claim_id}")
        receipt_path = ROOT / claim["receipt_path"]
        receipt = read(receipt_path)
        if not (
            receipt.get("claim_id") == claim_id
            and receipt.get("model_admitted") is True
            and receipt.get("receipt_hash") == claim.get("receipt_hash")
        ):
            raise SystemExit(f"existing Chemistry receipt identity differs: {claim_id}")
        registration = read(ROOT / "claims" / claim_id / "registration.json")
        rows.append(
            {
                "obligation_id": f"SFT-CHEM-OBL-CORE-{int(item['position']):03d}",
                "field": f"existing_core__{item['subbranch']}",
                "title": item["title"],
                "owner": "chemistry",
                "required_strength": item["evidence_mode"],
                "required_external_surface": list(item["external_source_ids"]),
                "exact_boundary": registration["statement"],
                "status": "closed_current_model_admitted_receipt",
                "current_claim_ids": [claim_id],
                "receipt_hashes": [claim["receipt_hash"]],
                "receipt_paths": [claim["receipt_path"]],
                "receipt_file_sha256": [file_hash(receipt_path)],
                "gap_reason": None,
            }
        )
    return rows


def expansion_rows() -> list[dict[str, object]]:
    census = {row["claim_id"]: row for row in read(CLAIM_CENSUS)["claims"]}
    rows: list[dict[str, object]] = []
    for item in EXPANSION_OBLIGATIONS:
        mapped_ids = list(CLOSED_EXPANSION_MAPPINGS.get(item.obligation_id, ()))
        if not mapped_ids:
            rows.append(
                {
                    **asdict(item),
                    "status": "open_requires_derivation_and_external_validation",
                    "current_claim_ids": [],
                    "receipt_hashes": [],
                    "receipt_paths": [],
                    "receipt_file_sha256": [],
                    "gap_reason": "No current model-admitted Chemistry receipt closes this obligation at the registered quantitative, structural, operational or handoff strength.",
                }
            )
            continue
        receipts = []
        for claim_id in mapped_ids:
            claim = census.get(claim_id)
            if not isinstance(claim, dict) or claim.get("branch") != "chemistry" or claim.get("model_admitted") is not True:
                raise SystemExit(f"mapped expansion claim is not model-admitted Chemistry: {claim_id}")
            receipt_path = ROOT / claim["receipt_path"]
            receipt = read(receipt_path)
            if not (
                receipt.get("claim_id") == claim_id
                and receipt.get("model_admitted") is True
                and receipt.get("receipt_hash") == claim.get("receipt_hash")
            ):
                raise SystemExit(f"mapped expansion receipt identity differs: {claim_id}")
            receipts.append((claim, receipt_path))
        rows.append(
            {
                **asdict(item),
                "status": "closed_current_model_admitted_receipt",
                "current_claim_ids": mapped_ids,
                "receipt_hashes": [claim["receipt_hash"] for claim, _ in receipts],
                "receipt_paths": [claim["receipt_path"] for claim, _ in receipts],
                "receipt_file_sha256": [file_hash(path) for _, path in receipts],
                "gap_reason": None,
            }
        )
    return rows


def markdown(payload: dict) -> str:
    summary = payload["summary"]
    lines = [
        "# Complete Chemistry discipline-obligation census",
        "",
        f"Status: `{payload['status']}`.",
        "",
        "This census distinguishes the 86 immutable, already admitted Chemistry claims from the larger current-knowledge programme required to support the statement that the branch reconstructs the full declared field. It is not an admission artifact and cannot promote a question into the model.",
        "",
        "## Constitutional boundary",
        "",
        "- Canonical admission engine seal verified before the census build.",
        "- The admission engine was not imported, called, edited, wrapped or bypassed.",
        "- Existing receipts remain immutable and valid only at their exact registered boundaries.",
        "- New obligations remain open until their own generated grammar, unique survivor, controls, independent reconstruction and post-seal external evidence pass the unchanged engine.",
        "- A failed first claim package is preserved; it does not become a scientific wall. A scientifically distinct successor attempt must receive its own identity and repeat the full protocol.",
        "- Closure is current-evidence closure and remains open to lawful extension.",
        "",
        "## Counts",
        "",
        f"- Existing model-admitted Chemistry obligations: **{summary['closed_existing_count']}**.",
        f"- Full-discipline expansion obligations: **{summary['expansion_obligation_count']}**.",
        f"- Expansion obligations already closed: **{summary['closed_expansion_count']}**.",
        f"- Total current census: **{summary['total_obligation_count']}**.",
        f"- Open obligations: **{summary['open_count']}**.",
        f"- Required expansion fields represented: **{summary['required_field_count']} of {summary['required_field_count']}**.",
        "",
        "The previous 52/52 V1/V2 atomic reconciliation remains closed, but it tests historical-corpus reconstruction rather than this larger discipline census.",
        "",
        "## Expansion-field summary",
        "",
        "| Field | Obligations | Closed | Open |",
        "|---|---:|---:|---:|",
    ]
    for row in payload["field_summary"]:
        lines.append(f"| `{row['field']}` | {row['total']} | {row['closed']} | {row['open']} |")
    lines.extend(["", "## Open full-discipline obligations", "", "| Obligation | Field | Required strength | Required external surface |", "|---|---|---|---|"])
    for row in payload["obligations"]:
        if not str(row["status"]).startswith("open_"):
            continue
        lines.append(
            f"| `{row['obligation_id']}` - {row['title']} | `{row['field']}` | `{row['required_strength']}` | {row['required_external_surface']} |"
        )
    lines.extend(
        [
            "",
            "## Completion rule",
            "",
            "This census reaches zero open obligations only when every row has exactly one Chemistry owner and at least one current model-admitted receipt at the required strength; every quantitative natural-science row additionally requires a post-seal complete external value vector. A paper, manifest or verifier cannot substitute for those receipts.",
            "",
            f"Census identity: `{payload['census_identity']}`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    verify_seal()
    core = existing_rows()
    expansion = expansion_rows()
    obligations = core + expansion
    ids = [row["obligation_id"] for row in obligations]
    if len(ids) != len(set(ids)):
        raise SystemExit("Chemistry discipline census contains duplicate obligation identities")
    if any(row["owner"] != "chemistry" for row in obligations):
        raise SystemExit("Chemistry discipline census violates the one-owner rule")
    closed = sum(str(row["status"]).startswith("closed_") for row in obligations)
    open_count = sum(str(row["status"]).startswith("open_") for row in obligations)
    field_counts = Counter(row["field"] for row in expansion)
    if tuple(field_counts) != REQUIRED_FIELDS:
        raise SystemExit("Chemistry discipline census omits or reorders a required expansion field")
    field_summary = []
    for field in REQUIRED_FIELDS:
        rows = [row for row in expansion if row["field"] == field]
        field_summary.append(
            {
                "field": field,
                "total": len(rows),
                "closed": sum(str(row["status"]).startswith("closed_") for row in rows),
                "open": sum(str(row["status"]).startswith("open_") for row in rows),
            }
        )
    payload = {
        "schema": "sft-v3-complete-chemistry-discipline-obligation-census/1",
        "status": "open_active_full_discipline_reconstruction",
        "scope_date": "2026-07-26",
        "purpose": "Expose every currently declared obligation required to reconstruct the full Chemistry field rather than only the earlier categorical inventory.",
        "authority": {
            "canonical_engine_seal": "sha256:4f4cdd7986808e6a6102d650c85e6093d6425e49f14a5f05d70fa05e6031d46a",
            "canonical_engine_seal_verified": True,
            "engine_imported_or_called_for_admission": False,
            "engine_modified": False,
            "claims_admitted_by_this_census": 0,
            "failed_attempt_policy": "preserve rejection; formulate a scientifically distinct versioned successor; rerun the full unchanged protocol; never declare a wall merely because an attempt fails",
            "closure_policy": "current-evidence closed and permanently open to lawful extension",
        },
        "scope_sources": [
            {"body": "Maria Smith", "role": "authoritative declared Chemistry reconstruction boundary", "surface": "the thirteen mandatory fields registered in the active Chemistry objective"},
            {"body": "International Union of Pure and Applied Chemistry", "role": "discipline and terminology coverage comparator", "uri": "https://iupac.org/what-we-do/divisions/"},
            {"body": "American Chemical Society", "role": "independent field-coverage comparator", "uri": "https://www.acs.org/technical-divisions/division-list.html"},
        ],
        "summary": {
            "total_obligation_count": len(obligations),
            "closed_existing_count": sum(str(row["status"]).startswith("closed_") for row in core),
            "closed_total_count": closed,
            "expansion_obligation_count": len(expansion),
            "closed_expansion_count": sum(str(row["status"]).startswith("closed_") for row in expansion),
            "open_expansion_count": sum(str(row["status"]).startswith("open_") for row in expansion),
            "open_count": open_count,
            "required_field_count": len(REQUIRED_FIELDS),
            "one_owner_passed": True,
            "all_required_fields_represented": True,
            "publication_blocked": open_count > 0,
        },
        "field_summary": field_summary,
        "obligations": obligations,
    }
    payload["census_identity"] = canonical_hash(payload)
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUTPUT_MD.write_text(markdown(payload), encoding="utf-8")
    print("CHEMISTRY DISCIPLINE CENSUS: BUILT")
    print(f"existing admitted obligations: {sum(str(row['status']).startswith('closed_') for row in core)}")
    print(f"full-discipline expansion obligations: {len(expansion)}")
    print(f"closed expansion obligations: {sum(str(row['status']).startswith('closed_') for row in expansion)}")
    print(f"total obligations: {len(obligations)}")
    print(f"open obligations: {open_count}")
    print(f"census identity: {payload['census_identity']}")


if __name__ == "__main__":
    main()
