#!/usr/bin/env python3
"""Fail closed until the complete successor Physics branch is publishable."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def blockers() -> list[str]:
    audit = json.loads(
        (ROOT / "audits/physics_prior_value_audit_2026-07-24.json").read_text()
    )
    v1 = json.loads(
        (ROOT / "audits/v1_theorem_manifest_observation_census.json").read_text()
    )
    v2 = json.loads(
        (ROOT / "audits/v2_407_step_observation_census.json").read_text()
    )
    failures: list[str] = []
    if audit.get("status") != "closed":
        failures.append("Physics prior-value audit is not closed")
    if v1.get("unmapped_row_count"):
        failures.append(f"{v1['unmapped_row_count']} V1 observations lack explicit V3 disposition")
    if v2.get("unmapped_step_count"):
        failures.append(f"{v2['unmapped_step_count']} V2 steps lack explicit V3 disposition")
    if v2.get("same_strength_open_step_count"):
        failures.append(
            f"{v2['same_strength_open_step_count']} V2 steps lack closed same-strength reconstruction"
        )
    lepton_failure = ROOT / "audits/physics_charged_lepton_empirical_failure.json"
    if not lepton_failure.is_file():
        failures.append("charged-lepton empirical reconstruction has no preserved engine result")
    else:
        record = json.loads(lepton_failure.read_text())
        if record.get("status") != "empirical_validation_failed_not_admitted":
            failures.append("charged-lepton empirical reconstruction has no final disposition")
        # The preserved failed attempt is required evidence.  Resolution is
        # assessed from the admitted terminal successor recorded by the audit.
    lepton = audit.get("charged_lepton_cubic", {})
    if lepton.get("empirical_validation_status") != "resolved_by_terminal_refinement":
        failures.append("charged-lepton empirical reconstruction has not been resolved by an admitted successor")
    if audit.get("published_physics_claim_count") != audit.get("current_physics_claim_count"):
        failures.append("published Physics paper inventory differs from the live Physics corpus")
    alpha = audit.get("inverse_alpha", {})
    if not alpha.get("published_physics_v1_contains_claim"):
        failures.append("inverse alpha is absent from the published Physics v1 paper")
    return failures


def main() -> None:
    failures = blockers()
    if failures:
        raise SystemExit("PHYSICS SUCCESSOR PUBLICATION GATE: FAIL\n" + "\n".join(f"- {item}" for item in failures))
    print("PHYSICS SUCCESSOR PUBLICATION GATE: PASS")


if __name__ == "__main__":
    main()
