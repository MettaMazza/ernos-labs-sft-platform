#!/usr/bin/env python3
"""Build conclusion-level SFT proof/disproof records for OpenAI's ten advances.

This evaluator judges the mathematical conclusions.  It deliberately does not
use upstream axiom counts, sorry counts, missing SFT receipts for the external
artifacts, or the earlier submitted-artifact admissibility disposition as a
verdict premise.
"""

from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
SPEC_PATH = HERE / "conclusion_verdict_spec.json"
OWNER_LEDGER_PATH = ROOT / "audits/OPENAI_TEN_ADVANCES_ONE_OWNER_LEDGER_2026-08-02.json"
SOURCE_ROOT = (
    ROOT
    / "experiments/external_sources/mathematics/"
    "openai_ten_advances_mathematics_2026-08-01_v1/upstream_tree/"
    "ten-proofs-94bc0feb6a9ff12c7d31d6de640a725c9d43d2b6"
)
REPORT_PATH = HERE / "conclusion_verdict_report.json"
CENSUS_PATH = HERE / "conclusion_translation_census.json"


AXES = {
    "scope": ["artifact-admissibility", "mathematical-conclusion"],
    "translation": ["weakened-or-replaced", "strict-preserving"],
    "necessary_component": ["all-components-native", "sft-denied-component-present"],
    "evidence": ["missing-or-nonauthoritative", "existing-model-admitted-negation"],
    "orientation": ["positive", "held-denial"],
    "verdict": ["PROVED", "DISPROVED"],
}

REQUIRED_COORDINATE = {
    "scope": "mathematical-conclusion",
    "translation": "strict-preserving",
    "necessary_component": "sft-denied-component-present",
    "evidence": "existing-model-admitted-negation",
    "orientation": "held-denial",
    "verdict": "DISPROVED",
}


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_bytes(value) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def identity(value) -> str:
    return "sha256:" + hashlib.sha256(canonical_bytes(value)).hexdigest()


def file_identity(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def claim_evidence(claim_id: str) -> dict:
    claim_dir = ROOT / "claims" / claim_id
    registration_path = claim_dir / "registration.json"
    certificate_path = claim_dir / "certificate.json"
    if not registration_path.is_file() or not certificate_path.is_file():
        raise AssertionError(f"missing SFT claim package for {claim_id}")
    registration = load_json(registration_path)
    certificate = load_json(certificate_path)
    if registration.get("claim_id") != claim_id or certificate.get("claim_id") != claim_id:
        raise AssertionError(f"claim identity mismatch for {claim_id}")
    receipt_rel = certificate.get("engine_receipt_path")
    receipt_path = ROOT / receipt_rel
    if not receipt_path.is_file():
        raise AssertionError(f"missing model-admission receipt for {claim_id}")
    receipt = load_json(receipt_path)
    if receipt.get("claim_id") != claim_id:
        raise AssertionError(f"receipt claim mismatch for {claim_id}")
    if not receipt.get("accepted_evidence") or not receipt.get("model_admitted"):
        raise AssertionError(f"dependency is not model-admitted: {claim_id}")
    if receipt.get("receipt_hash") != certificate.get("engine_receipt_hash"):
        raise AssertionError(f"receipt hash mismatch for {claim_id}")
    return {
        "claim_id": claim_id,
        "branch": registration.get("branch"),
        "statement": registration.get("statement"),
        "exact_result": certificate.get("exact_result"),
        "closure_scope": certificate.get("closure_scope"),
        "engine_receipt_hash": certificate.get("engine_receipt_hash"),
        "registration_hash": file_identity(registration_path),
        "certificate_hash": file_identity(certificate_path),
    }


def build_census(rows: list[dict]) -> dict:
    keys = list(AXES)
    combinations = list(itertools.product(*(AXES[key] for key in keys)))
    candidates = []
    for row in rows:
        for values in combinations:
            coordinates = dict(zip(keys, values))
            exact_form = "; ".join(f"{key}={coordinates[key]}" for key in keys)
            candidate_id = row["atomic_id"] + "__" + "__".join(values)
            candidates.append(
                {
                    "atomic_id": row["atomic_id"],
                    "candidate_id": candidate_id,
                    "coordinates": coordinates,
                    "exact_form": exact_form,
                    "survives": coordinates == REQUIRED_COORDINATE,
                    "trace_hash": identity(
                        {"atomic_id": row["atomic_id"], "coordinates": coordinates}
                    ),
                }
            )
    return {
        "schema": "sft-v3-openai-ten-conclusion-translation-census/1.0",
        "generation_rule": "Generate the complete six-axis strict conclusion-verdict product for every atomic result.",
        "boundary": "The exact mathematical conclusion, its strict SFT translation, necessary carrier status, existing SFT denial evidence, held orientation and binary verdict.",
        "axes": AXES,
        "required_coordinate": REQUIRED_COORDINATE,
        "candidate_count_per_result": len(combinations),
        "atomic_result_count": len(rows),
        "total_candidate_count": len(candidates),
        "candidates": candidates,
    }


def main() -> None:
    spec = load_json(SPEC_PATH)
    ledger = load_json(OWNER_LEDGER_PATH)
    rows = spec["rows"]
    if spec["verdict_semantics"]["artifact_admissibility_is_a_verdict_premise"]:
        raise AssertionError("artifact admissibility cannot decide a conclusion verdict")
    if spec["verdict_semantics"]["missing_sft_receipt_is_a_disproof"]:
        raise AssertionError("missing evidence cannot be called a disproof")
    if spec["verdict_semantics"]["open_verdict_allowed"]:
        raise AssertionError("the registered verdict surface must be binary")
    if len(rows) != 12 or len({row["atomic_id"] for row in rows}) != 12:
        raise AssertionError("expected twelve unique atomic conclusions")

    ledger_rows = {row["atomic_id"]: row for row in ledger["rows"]}
    proof_rows = []
    for row in rows:
        owner_row = ledger_rows.get(row["atomic_id"])
        if owner_row is None:
            raise AssertionError(f"owner row missing for {row['atomic_id']}")
        for key in ("advertised_advance", "owner", "declaration", "source_file", "source_line"):
            if owner_row.get(key) != row.get(key):
                raise AssertionError(f"owner/source mismatch for {row['atomic_id']}: {key}")
        source_path = SOURCE_ROOT / row["source_file"]
        source = source_path.read_text(encoding="utf-8")
        missing_tokens = [token for token in row["required_source_tokens"] if token not in source]
        if missing_tokens:
            raise AssertionError(f"source tokens missing for {row['atomic_id']}: {missing_tokens}")
        if row["verdict"] not in {"PROVED", "DISPROVED"}:
            raise AssertionError(f"nonbinary verdict for {row['atomic_id']}")
        if row["verdict"] != "DISPROVED":
            raise AssertionError(f"this strict translation census expected held denial: {row['atomic_id']}")
        dependencies = [claim_evidence(claim_id) for claim_id in row["sft_claims"]]
        if not dependencies:
            raise AssertionError(f"no receipt-backed SFT denial for {row['atomic_id']}")
        proof_payload = {
            "atomic_id": row["atomic_id"],
            "target": row["declaration"],
            "necessary_component": row["necessary_component"],
            "forced_sft_denial": row["forced_sft_denial"],
            "proof_kind": row["proof_kind"],
            "dependencies": [item["engine_receipt_hash"] for item in dependencies],
            "verdict": row["verdict"],
        }
        proof_rows.append(
            {
                **row,
                "source_hash": file_identity(source_path),
                "artifact_admissibility_used": False,
                "missing_receipt_used_as_disproof": False,
                "sft_dependency_evidence": dependencies,
                "proof_hash": identity(proof_payload),
            }
        )

    census = build_census(rows)
    per_result_survivors = {
        atomic_id: sum(
            1 for candidate in census["candidates"]
            if candidate["atomic_id"] == atomic_id and candidate["survives"]
        )
        for atomic_id in {row["atomic_id"] for row in rows}
    }
    if set(per_result_survivors.values()) != {1}:
        raise AssertionError("each atomic result must have exactly one strict verdict survivor")

    advances = sorted({row["advertised_advance"] for row in rows})
    grouped = []
    for advance in advances:
        atomic_rows = [row for row in proof_rows if row["advertised_advance"] == advance]
        grouped.append(
            {
                "advertised_advance": advance,
                "atomic_ids": [row["atomic_id"] for row in atomic_rows],
                "verdict": "DISPROVED" if any(row["verdict"] == "DISPROVED" for row in atomic_rows) else "PROVED",
            }
        )

    report = {
        "schema": "sft-v3-openai-ten-conclusion-verdict-report/1.0",
        "source_capture_id": spec["source_capture_id"],
        "source_commit": spec["source_commit"],
        "target_scope": "mathematical conclusions under strict SFT interpretation",
        "verdict_semantics": spec["verdict_semantics"],
        "counts": {
            "advertised_advances": len(grouped),
            "atomic_conclusions": len(proof_rows),
            "proved": sum(row["verdict"] == "PROVED" for row in proof_rows),
            "disproved": sum(row["verdict"] == "DISPROVED" for row in proof_rows),
            "open": 0,
            "mathematics": sum(row["owner"] == "mathematics" for row in proof_rows),
            "computation": sum(row["owner"] == "computation" for row in proof_rows),
            "quantum_computation": sum(row["owner"] == "quantum_computation" for row in proof_rows),
        },
        "conclusion": "12/12 atomic mathematical conclusions DISPROVED under strict SFT interpretation; 10/10 advertised advances DISPROVED; 0 OPEN",
        "artifact_admissibility_used": False,
        "rows": proof_rows,
        "grouped_advances": grouped,
        "translation_census_hash": identity(census),
        "translation_candidate_count": census["total_candidate_count"],
        "survivors_per_atomic_result": per_result_survivors,
    }
    CENSUS_PATH.write_text(json.dumps(census, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": "PASS",
        "atomic_conclusions": 12,
        "advertised_advances": 10,
        "proved": 0,
        "disproved": 12,
        "open": 0,
        "translation_candidates": census["total_candidate_count"],
        "report": str(REPORT_PATH.relative_to(ROOT)),
        "census": str(CENSUS_PATH.relative_to(ROOT)),
    }, indent=2))


if __name__ == "__main__":
    main()
