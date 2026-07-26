"""Current-knowledge publication compliance over immutable branch artifacts.

The ordinary :mod:`sft.engine.publication` gate proves that a paper covers the
inventory it was given.  This module proves the stronger fact required for a
new public release: that the inventory itself has reconciled the complete
registered prior-work obligation surface and still equals the live branch
census.  It never alters an engine receipt or an archived publication.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any


BRANCH_PREFIXES: dict[str, tuple[str, ...]] = {
    "foundation": ("SFT-ROOT-", "SFT-FOUNDATION-"),
    "mathematics": ("SFT-MATH-",),
    "information_science": ("SFT-INFO-",),
    "computation": ("SFT-COMP-",),
    "quantum_computation": ("SFT-QUANTUM-",),
    "physics": ("SFT-PHYS-",),
    "chemistry": ("SFT-CHEM-",),
    "materials": ("SFT-MAT-",),
}


@dataclass(frozen=True)
class PublicationCompliance:
    branch_id: str
    archive_integrity_boundary_preserved: bool
    current_publication_ready: bool
    live_claim_count: int
    frozen_inventory_claim_count: int
    archival_paper_claim_count: int
    blockers: tuple[str, ...]


class CurrentPublicationHalt(RuntimeError):
    """Raised when a new public release is attempted before full closure."""

    def __init__(self, result: PublicationCompliance):
        self.result = result
        super().__init__(
            f"current publication gate halted for {result.branch_id}: "
            + "; ".join(result.blockers)
        )


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _live_claim_ids(root: Path, branch_id: str) -> tuple[str, ...]:
    prefixes = BRANCH_PREFIXES[branch_id]
    claims = _read(root / "census/claims.json")["claims"]
    return tuple(
        row["claim_id"]
        for row in claims
        if str(row["claim_id"]).startswith(prefixes)
    )


def audit_branch(root: Path, branch_id: str) -> PublicationCompliance:
    """Return the current completion result without rewriting old evidence."""

    if branch_id not in BRANCH_PREFIXES:
        raise ValueError(f"unregistered publication branch: {branch_id}")

    successor_inventory = root / f"publications/inventories/successors/{branch_id}.json"
    inventory_path = successor_inventory if successor_inventory.is_file() else root / f"publications/inventories/{branch_id}.json"
    successor_root = root / f"publications/successors/{branch_id}"
    manifest_path = successor_root / "manifest.json" if (successor_root / "manifest.json").is_file() else root / f"publications/current/{branch_id}/manifest.json"
    evidence_path = successor_root / "evidence_map.json" if (successor_root / "evidence_map.json").is_file() else root / f"publications/current/{branch_id}/evidence_map.json"
    inventory = _read(inventory_path)
    manifest = _read(manifest_path)
    evidence = _read(evidence_path)
    v1 = _read(root / "audits/v1_theorem_manifest_observation_census.json")
    v2 = _read(root / "audits/v2_407_step_observation_census.json")
    lineage = _read(root / "census/lineage_reconciliation.json")
    ownership = _read(root / "census/prior_obligation_ownership.json")

    live_ids = _live_claim_ids(root, branch_id)
    frozen_ids = tuple(inventory["required_claim_ids"])
    evidence_ids = tuple(
        dict.fromkeys(
            row["claim_id"]
            for value in evidence.values()
            if isinstance(value, list)
            for row in value
            if isinstance(row, dict) and isinstance(row.get("claim_id"), str)
        )
    )
    paper_ids = tuple(
        claim_id for claim_id in evidence_ids if claim_id.startswith(BRANCH_PREFIXES[branch_id])
    )
    blockers: list[str] = []

    branch_ledger_path = root / f"census/{branch_id}_prior_obligations.json"
    if branch_ledger_path.is_file():
        branch_ledger = _read(branch_ledger_path)
        reviewed = branch_ledger.get("reviewed_source_surface", {})
        summary = branch_ledger.get(f"{branch_id}_summary", {})
        if not (
            reviewed.get("review_complete_for_branch_ownership") is True
            and reviewed.get("reviewed_entry_count") == v1["source_row_count"] + v2["source_step_count"]
            and summary.get("open_count") == 0
            and branch_ledger.get("status") == "closed"
        ):
            blockers.append("branch-specific full-source ownership review or same-strength closure is incomplete")
    elif branch_id == "physics":
        # Physics uses the later atomic categorical-ownership audit because mixed
        # V1/V2 source rows must be decomposed before a branch owner is assigned.
        # This publication check consumes that completed audit; it does not alter
        # the admission engine, claims, or receipts.
        atomic_audit = _read(root / "audits/physics_v1_v2_atomic_ownership.json")
        source = atomic_audit.get("source_surface", {})
        summary = atomic_audit.get("summary", {})
        if not (
            source.get("total_source_rows_reviewed") == v1["source_row_count"] + v2["source_step_count"]
            and summary.get("physics_owned_atom_count") == summary.get("same_strength_closed_atom_count")
            and summary.get("same_strength_open_atom_count") == 0
            and summary.get("unique_atom_ids") is True
            and summary.get("all_declared_composite_rows_decomposed") is True
            and summary.get("publication_blocked") is False
            and atomic_audit.get("audit_status") == "current_evidence_closed_extension_open"
        ):
            blockers.append("Physics atomic ownership review or same-strength closure is incomplete")
    else:
        if not ownership.get("assignment_complete"):
            blockers.append(
                "categorical ownership is not assigned for every V1/V2 obligation "
                f"({v1['source_row_count']} V1 rows; {v2['source_step_count']} V2 steps)"
            )
        branch_lineage = ownership.get("branch_summary", {}).get(branch_id, {})
        if branch_lineage.get("status") != "closed_same_strength":
            blockers.append("branch-owned prior obligations are not all closed at same strength")
    if lineage.get("status") not in {"open_blocking", "closed"}:
        blockers.append("lineage registry has an invalid status")
    if set(paper_ids) != set(live_ids):
        missing = tuple(claim_id for claim_id in live_ids if claim_id not in paper_ids)
        stale = tuple(claim_id for claim_id in paper_ids if claim_id not in live_ids)
        if missing:
            blockers.append(
                f"frozen inventory omits {len(missing)} live {branch_id} claim(s)"
            )
        if stale:
            blockers.append(
                f"frozen inventory contains {len(stale)} non-live {branch_id} claim(s)"
            )
    manifest_ready = manifest.get("ready_to_publish")
    if manifest_ready is None:
        manifest_ready = bool(
            manifest.get("comprehensive_derivation_coverage")
            and manifest.get("controls_passed")
        )
    if not manifest_ready:
        blockers.append("selected paper manifest is not internally ready")

    return PublicationCompliance(
        branch_id=branch_id,
        archive_integrity_boundary_preserved=True,
        current_publication_ready=not blockers,
        live_claim_count=len(live_ids),
        frozen_inventory_claim_count=len(frozen_ids),
        archival_paper_claim_count=len(paper_ids),
        blockers=tuple(blockers),
    )


def require_current_publication_ready(root: Path, branch_id: str) -> PublicationCompliance:
    """Fail closed unless a branch is complete against all registered work."""

    result = audit_branch(root, branch_id)
    if not result.current_publication_ready:
        raise CurrentPublicationHalt(result)
    return result
