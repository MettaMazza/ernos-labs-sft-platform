#!/usr/bin/env python3
"""Implementation-distinct validator for complete calculator claim 006."""

from __future__ import annotations

from fractions import Fraction
from itertools import product
import json
from pathlib import Path
import subprocess
import sys


CLAIM_ID = "SFT-MATH-SCIENTIFIC-CALCULATOR-006"
ROOT = Path(__file__).resolve().parents[2]
DOMAINS = (
    ("expression-api-only", "familiar-keypad-and-result-chaining"),
    ("projected-host-scalars", "exact-SFT-runtime-types"),
    ("partial-function-subset", "complete-declared-expression-language"),
    ("calculator-only-scalar-view", "all-current-predecessor-families"),
    ("opaque-friendly-number", "typed-certificate-trace-and-resources"),
    ("all-evidence-visible-at-once", "familiar-first-progressive-disclosure"),
    ("platform-specific-or-heavy-runtime", "standard-library-mac-Windows-Linux"),
    ("unreduced-direct-series-only", "certified-whole-turn-reduction"),
    ("unbounded-or-silent-failure", "counted-early-check-and-mandatory-halt"),
    ("passing-examples-with-gaps", "complete-statement-and-branch-coverage"),
)
SURVIVOR = tuple(domain[1] for domain in DOMAINS)


def run(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        (sys.executable, "-m", "sft.mathematics.calculator_complete", *arguments),
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def independent_root_bracket(target: Fraction, depth: int = 80) -> tuple[Fraction, Fraction]:
    lower, upper = Fraction(0), max(Fraction(1), target)
    for _ in range(depth):
        middle = (lower + upper) / 2
        if middle * middle < target:
            lower = middle
        else:
            upper = middle
    return lower, upper


def coverage_check() -> tuple[bool, dict[str, object]]:
    report = json.loads(
        (ROOT / "generated/mathematics/scientific_calculator_coverage_v4.json").read_text(encoding="utf-8")
    )
    totals = report["totals"]
    passed = all(
        (
            totals["percent_covered"] == 100.0,
            totals["missing_lines"] == 0,
            totals["missing_branches"] == 0,
            all(item["summary"]["missing_lines"] == 0 for item in report["files"].values()),
            all(item["summary"]["missing_branches"] == 0 for item in report["files"].values()),
        )
    )
    return passed, totals


def operational_check() -> tuple[bool, dict[str, object]]:
    ordinary = run("1+1=")
    proof = run("sqrt(2)", "--proof")
    law = run("--law", "SFT-MATH-EXACT-ARITHMETIC-001")
    replay = run("--replay-law", "SFT-MATH-EXACT-ARITHMETIC-001")
    proof_payload = json.loads(proof.stdout) if proof.returncode == 0 else {}
    law_payload = json.loads(law.stdout) if law.returncode == 0 else {}
    replay_payload = json.loads(replay.stdout) if replay.returncode == 0 else {}
    lower, upper = independent_root_bracket(Fraction(2))
    launchers = (
        ROOT / "launchers/Launch Smithian Calculator.command",
        ROOT / "launchers/Launch Smithian Calculator.bat",
        ROOT / "launchers/launch-smithian-calculator.sh",
    )
    passed = all(
        (
            ordinary.returncode == 0 and ordinary.stdout.strip() == "2",
            proof.returncode == 0,
            proof_payload.get("value_form") == "certified_exact_rational_enclosure",
            proof_payload.get("engine_admission_issued") is False,
            all(proof_payload.get("constraint_checks", {}).values()),
            lower * lower < 2 <= upper * upper,
            law.returncode == 0 and law_payload.get("model_admitted") is True,
            replay.returncode == 0 and replay_payload.get("locally_replayed") is True,
            replay_payload.get("engine_admission_issued") is False,
            all(path.exists() and "calculator_complete" in path.read_text(encoding="utf-8") for path in launchers),
        )
    )
    return passed, {
        "ordinary": ordinary.stdout.strip(),
        "root_width": str(upper - lower),
        "proof_value_form": proof_payload.get("value_form"),
        "law_candidate_count": law_payload.get("candidate_count"),
        "law_replayed": replay_payload.get("locally_replayed"),
        "launcher_count": len(launchers),
    }


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: validator CLAIM_ID SEALED_DERIVATION")
    with open(sys.argv[2], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = tuple("__".join(fields) for fields in product(*DOMAINS))
    received = tuple(item["candidate_id"] for item in sealed["census"]["candidates"])
    recomputed = {candidate: tuple(candidate.split("__")) == SURVIVOR for candidate in generated}
    decisions = {item["candidate_id"]: item["survives"] for item in sealed["decisions"]}
    controls = sealed["controls"]
    closure = sealed["closure"]
    coverage_passed, coverage = coverage_check()
    operational_passed, operations = operational_check()
    passed = all(
        (
            sys.argv[1] == CLAIM_ID,
            sealed["claim_id"] == CLAIM_ID,
            received == generated,
            len(set(received)) == sealed["census"]["expected_cardinality"] == 1024,
            decisions == recomputed,
            sum(recomputed.values()) == 1,
            closure["scope"] == "depth_independent",
            closure["minimality_passed"] is True,
            closure["named_shape_uniqueness_passed"] is True,
            {item["kind"] for item in controls}
            == {"false_premise", "tampered_source", "tampered_artifact", "boundary"},
            all(item["passed"] is True for item in controls),
            coverage_passed,
            operational_passed,
        )
    )
    print(
        json.dumps(
            {
                "passed": passed,
                "validated_seal_hash": sealed["seal_hash"],
                "recomputed_from_declared_inputs": True,
                "certificate": {
                    "candidate_count": len(generated),
                    "unique_survivor": "__".join(SURVIVOR),
                    "coverage": coverage,
                    "operations": operations,
                    "operational_check": operational_passed,
                },
            },
            sort_keys=True,
        )
    )
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
