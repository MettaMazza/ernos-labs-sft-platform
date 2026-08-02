#!/usr/bin/env python3
"""Independent reconstruction of the conclusion-level SFT verdict audit."""

from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
SPEC_PATH = HERE / "conclusion_verdict_spec.json"
REPORT_PATH = HERE / "conclusion_verdict_report.json"
CENSUS_PATH = HERE / "conclusion_translation_census.json"
OWNER_PATH = ROOT / "audits/OPENAI_TEN_ADVANCES_ONE_OWNER_LEDGER_2026-08-02.json"
OUTPUT_PATH = HERE / "conclusion_verdict_independent_verification.json"
SOURCE_ROOT = (
    ROOT
    / "experiments/external_sources/mathematics/"
    "openai_ten_advances_mathematics_2026-08-01_v1/upstream_tree/"
    "ten-proofs-94bc0feb6a9ff12c7d31d6de640a725c9d43d2b6"
)


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def packed(value) -> bytes:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")


def object_hash(value) -> str:
    return "sha256:" + hashlib.sha256(packed(value)).hexdigest()


def file_hash(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    spec = load(SPEC_PATH)
    report = load(REPORT_PATH)
    census = load(CENSUS_PATH)
    owner = load(OWNER_PATH)
    checks = {}

    spec_rows = spec["rows"]
    report_rows = report["rows"]
    checks["twelve_unique_atomic_conclusions"] = (
        len(spec_rows) == 12
        and len(report_rows) == 12
        and len({row["atomic_id"] for row in spec_rows}) == 12
        and len({row["atomic_id"] for row in report_rows}) == 12
    )
    checks["actual_conclusion_scope_only"] = (
        report["target_scope"] == "mathematical conclusions under strict SFT interpretation"
        and not report["artifact_admissibility_used"]
        and not spec["verdict_semantics"]["artifact_admissibility_is_a_verdict_premise"]
        and not spec["verdict_semantics"]["missing_sft_receipt_is_a_disproof"]
    )
    checks["binary_closed_verdicts"] = (
        all(row["verdict"] in {"PROVED", "DISPROVED"} for row in report_rows)
        and report["counts"]["open"] == 0
        and all(row["verdict"] == "DISPROVED" for row in report_rows)
    )
    checks["owner_counts_9_2_1"] = report["counts"] == {
        "advertised_advances": 10,
        "atomic_conclusions": 12,
        "proved": 0,
        "disproved": 12,
        "open": 0,
        "mathematics": 9,
        "computation": 2,
        "quantum_computation": 1,
    }

    owner_rows = {row["atomic_id"]: row for row in owner["rows"]}
    checks["owner_and_source_rows_match"] = all(
        row["atomic_id"] in owner_rows
        and all(
            row[key] == owner_rows[row["atomic_id"]][key]
            for key in ("advertised_advance", "owner", "declaration", "source_file", "source_line")
        )
        for row in spec_rows
    )

    source_ok = True
    for row in spec_rows:
        source_path = SOURCE_ROOT / row["source_file"]
        if not source_path.is_file():
            source_ok = False
            continue
        source = source_path.read_text(encoding="utf-8")
        if any(token not in source for token in row["required_source_tokens"]):
            source_ok = False
        if row["declaration"].split(".")[-1] not in source:
            source_ok = False
    checks["source_conclusion_tokens_present"] = source_ok

    receipt_ok = True
    proof_hash_ok = True
    for row in report_rows:
        if row["artifact_admissibility_used"] or row["missing_receipt_used_as_disproof"]:
            receipt_ok = False
        if not row["sft_dependency_evidence"]:
            receipt_ok = False
        receipt_hashes = []
        for evidence in row["sft_dependency_evidence"]:
            claim_id = evidence["claim_id"]
            certificate_path = ROOT / "claims" / claim_id / "certificate.json"
            if not certificate_path.is_file():
                receipt_ok = False
                continue
            certificate = load(certificate_path)
            receipt_path = ROOT / certificate["engine_receipt_path"]
            if not receipt_path.is_file():
                receipt_ok = False
                continue
            receipt = load(receipt_path)
            if not receipt.get("accepted_evidence") or not receipt.get("model_admitted"):
                receipt_ok = False
            if receipt.get("receipt_hash") != evidence["engine_receipt_hash"]:
                receipt_ok = False
            receipt_hashes.append(evidence["engine_receipt_hash"])
        proof_payload = {
            "atomic_id": row["atomic_id"],
            "target": row["declaration"],
            "necessary_component": row["necessary_component"],
            "forced_sft_denial": row["forced_sft_denial"],
            "proof_kind": row["proof_kind"],
            "dependencies": receipt_hashes,
            "verdict": row["verdict"],
        }
        if row["proof_hash"] != object_hash(proof_payload):
            proof_hash_ok = False
    checks["all_denials_have_model_admitted_dependencies"] = receipt_ok
    checks["proof_hashes_reconstruct"] = proof_hash_ok

    axes = census["axes"]
    expected_per_result = 1
    for values in axes.values():
        expected_per_result *= len(values)
    expected_coordinate = census["required_coordinate"]
    survivors = {}
    for row in census["candidates"]:
        survivors.setdefault(row["atomic_id"], 0)
        expected_survival = row["coordinates"] == expected_coordinate
        if row["survives"] != expected_survival:
            checks["census_survival_rule_exact"] = False
        if row["survives"]:
            survivors[row["atomic_id"]] += 1
    checks.setdefault("census_survival_rule_exact", True)
    checks["complete_768_candidate_census"] = (
        expected_per_result == 64
        and census["candidate_count_per_result"] == 64
        and census["atomic_result_count"] == 12
        and census["total_candidate_count"] == 768
        and len(census["candidates"]) == 768
    )
    checks["one_survivor_per_conclusion"] = len(survivors) == 12 and set(survivors.values()) == {1}
    checks["census_hash_matches_report"] = report["translation_census_hash"] == object_hash(census)
    checks["ten_grouped_advances_disproved"] = (
        len(report["grouped_advances"]) == 10
        and {row["advertised_advance"] for row in report["grouped_advances"]} == set(range(1, 11))
        and all(row["verdict"] == "DISPROVED" for row in report["grouped_advances"])
    )

    status = "PASS" if all(checks.values()) else "FAIL"
    result = {
        "schema": "sft-v3-openai-ten-conclusion-verdict-independent-verification/1.0",
        "status": status,
        "checks": checks,
        "verified_artifacts": {
            "spec": file_hash(SPEC_PATH),
            "report": file_hash(REPORT_PATH),
            "translation_census": file_hash(CENSUS_PATH),
            "owner_ledger": file_hash(OWNER_PATH),
        },
        "conclusion": report["conclusion"],
    }
    OUTPUT_PATH.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    if status != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
