#!/usr/bin/env python3
"""Independently verify the complete Chemistry discipline census."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = ROOT / "census/chemistry_discipline_obligations.json"


def fail(message: str) -> None:
    raise SystemExit("CHEMISTRY DISCIPLINE CENSUS: FAIL - " + message)


def canonical_hash(payload: object) -> str:
    body = json.dumps(payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return "sha256:" + hashlib.sha256(body).hexdigest()


def main() -> None:
    result = subprocess.run(
        [sys.executable, "tools/verify_engine_seal.py"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    if "SFT ENGINE SEAL: VALID CANONICAL ENGINE" not in result.stdout:
        fail("canonical engine seal is invalid")
    payload = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    identity = payload.get("census_identity")
    body = dict(payload)
    body.pop("census_identity", None)
    if identity != canonical_hash(body):
        fail("census identity does not reproduce")
    rows = payload.get("obligations", [])
    ids = [row.get("obligation_id") for row in rows]
    if len(ids) != len(set(ids)) or any(not item for item in ids):
        fail("obligation identities are missing or duplicated")
    if any(row.get("owner") != "chemistry" for row in rows):
        fail("one-owner rule failed")
    claims = {row["claim_id"]: row for row in json.loads((ROOT / "census/claims.json").read_text(encoding="utf-8"))["claims"]}
    closed = [row for row in rows if str(row.get("status", "")).startswith("closed_")]
    opened = [row for row in rows if str(row.get("status", "")).startswith("open_")]
    if len(closed) != 87 or len(opened) != 185 or len(rows) != 272:
        fail("expected 86 existing, one newly closed and 185 open expansion obligations")
    for row in closed:
        if len(row.get("current_claim_ids", [])) != 1 or len(row.get("receipt_hashes", [])) != 1:
            fail(f"closed obligation lacks one exact receipt mapping: {row['obligation_id']}")
        claim_id = row["current_claim_ids"][0]
        claim = claims.get(claim_id)
        if not isinstance(claim, dict) or claim.get("branch") != "chemistry" or claim.get("model_admitted") is not True:
            fail(f"closed obligation maps to a non-admitted claim: {row['obligation_id']}")
        receipt_path = ROOT / claim["receipt_path"]
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        receipt_file_hash = "sha256:" + hashlib.sha256(receipt_path.read_bytes()).hexdigest()
        if not (
            receipt.get("receipt_hash") == claim.get("receipt_hash") == row["receipt_hashes"][0]
            and receipt.get("model_admitted") is True
            and row["receipt_file_sha256"] == [receipt_file_hash]
        ):
            fail(f"closed obligation receipt identity differs: {row['obligation_id']}")
    if any(row.get("current_claim_ids") or row.get("receipt_hashes") for row in opened):
        fail("an open obligation contains a synthetic admission mapping")
    summary = payload.get("summary", {})
    if not (
        summary.get("total_obligation_count") == 272
        and summary.get("closed_existing_count") == 86
        and summary.get("closed_total_count") == 87
        and summary.get("expansion_obligation_count") == 186
        and summary.get("closed_expansion_count") == 1
        and summary.get("open_expansion_count") == 185
        and summary.get("open_count") == 185
        and summary.get("required_field_count") == 13
        and summary.get("one_owner_passed") is True
        and summary.get("all_required_fields_represented") is True
        and summary.get("publication_blocked") is True
    ):
        fail("summary does not match obligation evidence")
    field_rows = payload.get("field_summary", [])
    if len(field_rows) != 13 or any(row.get("total", 0) < 1 or row.get("open", 0) + row.get("closed", 0) != row.get("total") for row in field_rows):
        fail("required field coverage is incomplete")
    print("CHEMISTRY DISCIPLINE CENSUS: PASS")
    print("existing model-admitted obligations: 86")
    print("full-discipline expansion obligations: 186")
    print("closed expansion obligations: 1")
    print("total current obligations: 272")
    print("open obligations requiring derivation: 185")
    print("required expansion fields represented: 13/13")
    print("canonical engine unchanged: PASS")


if __name__ == "__main__":
    main()
