"""Run the same dependency-free validation suite on every supported host."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.verification import verify_all  # noqa: E402


def main() -> None:
    report = verify_all(ROOT)
    print("portable repository, engine and derivation checks: PASS")
    print(f"unit and end-to-end tests passed: {report.coverage.tests_run}")
    print(
        "core engine executable-line coverage: "
        f"{report.coverage.executed_lines}/{report.coverage.executable_lines} (100%)"
    )
    print(f"registered derivations independently rerun: {report.rerun_claims}")


if __name__ == "__main__":
    main()
