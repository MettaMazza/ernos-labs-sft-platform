"""Independent reconstruction of the OpenAI/SFT admissibility audit."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REPORT = HERE / "admissibility_report.json"
CENSUS = HERE / "candidate_census.json"
LEDGER = ROOT / "audits/OPENAI_TEN_ADVANCES_ONE_OWNER_LEDGER_2026-08-02.json"
OUTPUT = HERE / "independent_verification_report.json"


def canonical_hash(value: object) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def main() -> None:
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    census = json.loads(CENSUS.read_text(encoding="utf-8"))
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))

    checks = {
        "twelve_unique_atomic_rows": len(report["rows"]) == 12
        and len({row["atomic_id"] for row in report["rows"]}) == 12,
        "ten_unique_advertised_advances": len(report["advertised_advances"]) == 10
        and {row["advertised_advance"] for row in report["advertised_advances"]} == set(range(1, 11)),
        "owner_ledger_identity": {row["atomic_id"] for row in report["rows"]}
        == {row["atomic_id"] for row in ledger["rows"]},
        "owner_counts": sum(row["owner"] == "mathematics" for row in report["rows"]) == 9
        and sum(row["owner"] == "computation" for row in report["rows"]) == 2
        and sum(row["owner"] == "quantum_computation" for row in report["rows"]) == 1,
        "three_explicit_axioms_each": all(
            row["upstream_axioms"] == ["propext", "Classical.choice", "Quot.sound"]
            for row in report["rows"]
        ),
        "zero_upstream_sorries_asserted": all(row["upstream_sorry_count"] == 0 for row in report["rows"]),
        "binary_verdict_each": all(
            row["verdict"] == "DISPROVED_AS_SUBMITTED_SFT_THEOREM"
            and row["observed_matches_required_sft_form"] is False
            for row in report["rows"]
        ),
        "complete_candidate_count": census["total_candidate_count"] == 3072
        and census["candidate_count_per_declaration"] == 256,
        "one_observed_and_one_admissible_form_each": all(
            sum(candidate["matches_supplied_artifact"] for candidate in census["candidates"] if candidate["atomic_id"] == atomic_id) == 1
            and sum(candidate["is_sft_admissible_form"] for candidate in census["candidates"] if candidate["atomic_id"] == atomic_id) == 1
            for atomic_id in {row["atomic_id"] for row in report["rows"]}
        ),
        "census_hash_matches": canonical_hash(census) == report["candidate_census_hash"],
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise SystemExit("independent audit failed: " + ", ".join(failed))
    result = {
        "schema": "sft-v3-external-proof-admissibility-independent-verification/1.0",
        "status": "PASS",
        "checks": checks,
        "verified_artifacts": {
            "admissibility_report": canonical_hash(report),
            "candidate_census": canonical_hash(census),
            "one_owner_ledger": canonical_hash(ledger),
        },
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
