"""Fail-closed coverage audit for externally testable SFT consequences.

The audit does not decide scientific truth and cannot admit claims. It checks
that every empirical registration has executable measurement evidence and that
no Physics result terminates without reaching a post-seal empirical claim.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path


class ExternalMeasurementCoverageError(RuntimeError):
    """Raised when the current corpus leaves measurable coverage open."""


@dataclass(frozen=True)
class ExternalMeasurementCoverage:
    registered_claims: int
    empirical_claims: int
    physics_formal_claims: int
    physics_formal_claims_reaching_measurement: int
    missing_empirical_contexts: tuple[str, ...]
    physics_results_without_empirical_descendant: tuple[str, ...]

    @property
    def complete(self) -> bool:
        return not (
            self.missing_empirical_contexts
            or self.physics_results_without_empirical_descendant
        )


def audit_external_measurement_coverage(root: Path) -> ExternalMeasurementCoverage:
    """Generate coverage from the live census, executions and dependencies."""

    from sft.verification import _load_execution

    root = root.resolve()
    rows = json.loads((root / "census/claims.json").read_text(encoding="utf-8"))["claims"]
    entries = json.loads(
        (root / "census/execution_manifest.json").read_text(encoding="utf-8")
    )["claims"]
    row_by_id = {row["claim_id"]: row for row in rows}
    executions = {entry["claim_id"]: _load_execution(root, entry) for entry in entries}

    empirical_ids = {
        claim_id
        for claim_id, row in row_by_id.items()
        if row.get("external_status")
        == "empirically_tested_and_independently_replicated"
    }
    missing_contexts = []
    for claim_id in sorted(empirical_ids):
        execution = executions[claim_id]
        if execution.empirical_validator is None:
            missing_contexts.append(claim_id)
            continue
        evidence_path = root / "claims" / claim_id / "empirical_validation.json"
        try:
            evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            missing_contexts.append(claim_id)
            continue
        if (
            evidence.get("claim_id") != claim_id
            or evidence.get("passed") is not True
            or evidence.get("all_rows_preserved") is not True
            or not evidence.get("data_source_ids")
        ):
            missing_contexts.append(claim_id)

    reaches_measurement = set(empirical_ids)
    stack = list(empirical_ids)
    while stack:
        claim_id = stack.pop()
        execution = executions.get(claim_id)
        if execution is None:
            continue
        for dependency in execution.program.registration.dependencies:
            if dependency not in reaches_measurement:
                reaches_measurement.add(dependency)
                stack.append(dependency)

    physics_formal = {
        claim_id
        for claim_id, row in row_by_id.items()
        if row.get("branch") == "physics"
        and row.get("external_status") == "independently_replicated"
    }
    uncovered = tuple(sorted(physics_formal - reaches_measurement))
    return ExternalMeasurementCoverage(
        registered_claims=len(rows),
        empirical_claims=len(empirical_ids),
        physics_formal_claims=len(physics_formal),
        physics_formal_claims_reaching_measurement=len(physics_formal) - len(uncovered),
        missing_empirical_contexts=tuple(sorted(set(missing_contexts))),
        physics_results_without_empirical_descendant=uncovered,
    )


def require_external_measurement_coverage(root: Path) -> ExternalMeasurementCoverage:
    report = audit_external_measurement_coverage(root)
    if not report.complete:
        details = []
        if report.missing_empirical_contexts:
            details.append(
                "missing empirical replay contexts: "
                + ", ".join(report.missing_empirical_contexts)
            )
        if report.physics_results_without_empirical_descendant:
            details.append(
                "Physics results without a post-seal empirical descendant: "
                + ", ".join(report.physics_results_without_empirical_descendant)
            )
        raise ExternalMeasurementCoverageError("; ".join(details))
    return report


__all__ = (
    "ExternalMeasurementCoverage",
    "ExternalMeasurementCoverageError",
    "audit_external_measurement_coverage",
    "require_external_measurement_coverage",
)
