#!/usr/bin/env python3
"""One-command complete calculator validator; never an admission substitute."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
ENGINE_TREE = "ad30f4866c18b2adbade95a0b2de40d5caa61308"
ACTIVE_INCLUDE = ",".join(
    (
        "sft/mathematics/calculator/values.py",
        "sft/mathematics/calculator/operations.py",
        "sft/mathematics/calculator/operations_v2.py",
        "sft/mathematics/calculator/operations_v3.py",
        "sft/mathematics/calculator/machine.py",
        "sft/mathematics/calculator/machine_v2.py",
        "sft/mathematics/calculator/machine_v3.py",
        "sft/mathematics/calculator_complete/__init__.py",
        "sft/mathematics/calculator_complete/__main__.py",
        "sft/mathematics/calculator_complete/controller.py",
        "sft/mathematics/calculator_complete/evidence.py",
        "sft/mathematics/calculator_complete/explorer.py",
        "sft/mathematics/calculator_complete/expression_census.py",
        "sft/mathematics/calculator_complete/gui.py",
        "sft/mathematics/calculator_complete/machine.py",
        "sft/mathematics/calculator_complete/operations.py",
        "sft/mathematics/calculator_complete/presentation.py",
        "sft/mathematics/calculator_complete/session.py",
    )
)


def run(*command: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        capture_output=True,
        env=env,
        check=False,
    )
    if completed.returncode != 0:
        raise SystemExit(completed.stdout + completed.stderr)
    return completed


def main() -> int:
    engine = run("git", "rev-parse", "HEAD:sft/engine").stdout.strip()
    dirty = subprocess.run(("git", "diff", "--quiet", "--", "sft/engine"), cwd=ROOT).returncode
    if engine != ENGINE_TREE or dirty != 0:
        raise SystemExit("frozen engine identity changed; calculator validation halted")

    try:
        import coverage  # noqa: F401
    except ImportError as error:
        raise SystemExit("coverage is required for the test gate; install the repository's [test] extra") from error

    with tempfile.TemporaryDirectory(prefix="sft-calculator-validation-") as directory:
        data_file = str(Path(directory) / ".coverage")
        report_file = str(Path(directory) / "coverage.json")
        environment = dict(__import__("os").environ)
        environment["COVERAGE_FILE"] = data_file
        tests = run(
            sys.executable,
            "-m",
            "coverage",
            "run",
            "--branch",
            "--source=sft.mathematics.calculator,sft.mathematics.calculator_complete",
            "-m",
            "unittest",
            "discover",
            "-s",
            "tests",
            "-p",
            "test_mathematics*calculator*.py",
            env=environment,
        )
        run(
            sys.executable,
            "-m",
            "coverage",
            "json",
            "--include=" + ACTIVE_INCLUDE,
            "--fail-under=100",
            "-o",
            report_file,
            env=environment,
        )
        report = json.loads(Path(report_file).read_text(encoding="utf-8"))

    totals = report["totals"]
    if totals["percent_covered"] != 100.0:
        raise SystemExit("active calculator coverage is not exactly 100%")
    from sft.mathematics.calculator_complete.expression_census import expression_families
    from sft.mathematics.calculator_complete.explorer import RegisteredMathematicsExplorer

    families = expression_families()
    explorer = RegisteredMathematicsExplorer(ROOT)
    replays = tuple(explorer.replay(item.claim_id) for item in families)
    if len(families) != 24 or not all(item.locally_replayed for item in replays):
        raise SystemExit("the 24-family Mathematics expression census did not replay completely")

    payload = {
        "status": "calculator_validation_complete",
        "engine_tree": engine,
        "tests": tests.stderr.strip().splitlines()[-1],
        "active_files": len(report["files"]),
        "statements": totals["num_statements"],
        "branches": totals["num_branches"],
        "statement_and_branch_coverage_percent": totals["percent_covered"],
        "mathematics_expression_families": len(families),
        "all_family_replays_passed": True,
        "admission_issued": False,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
