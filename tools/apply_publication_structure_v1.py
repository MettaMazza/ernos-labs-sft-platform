#!/usr/bin/env python3
"""Add explicit publication-guidance navigation surfaces to seven papers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Target:
    path: str
    inventory_anchor: str
    branch: str
    census: str
    evidence_map: str
    manifest: str
    source_surface: str


TARGETS = (
    Target(
        "publications/successors/mathematics/FROM_FOLD_TO_MATHEMATICS_PAPER_001_V1_5.md",
        "## 40. Complete-field Mathematics execution - version 1.5",
        "Mathematics",
        "census/mathematics_discipline_obligations.json",
        "publications/successors/mathematics/evidence_map_v1_5.json",
        "publications/successors/mathematics/manifest_v1_5.json",
        "experiments/external_sources/mathematics/",
    ),
    Target(
        "publications/successors/information_science/FROM_DISTINCTION_TO_INFORMATION_PAPER_001_V1_4.md",
        "## Complete-field family: SYMREP",
        "Information Science",
        "census/information_science_discipline_obligations.json",
        "publications/successors/information_science/evidence_map_v1_4.json",
        "publications/successors/information_science/manifest_v1_4.json",
        "experiments/external_sources/information_science/",
    ),
    Target(
        "publications/successors/computation/AFTER_TURING_THE_FOLD_MACHINE_PAPER_001_V1_4.md",
        "## 9. Derivation 1: Exact state and transition law",
        "Classical Computation",
        "census/computation_discipline_obligations.json",
        "publications/successors/computation/evidence_map_v1_4.json",
        "publications/successors/computation/manifest_v1_4.json",
        "experiments/external_sources/computation/",
    ),
    Target(
        "publications/successors/quantum_computation/THE_QUANTUM_FOLD_MACHINE_PAPER_001_V1_4.md",
        "## 9. Derivation 1: Complete Fold reversible-computation model",
        "Reversible and Quantum Computation",
        "census/quantum_computation_discipline_obligations.json",
        "publications/successors/quantum_computation/evidence_map_v1_4.json",
        "publications/successors/quantum_computation/manifest_v1_4.json",
        "experiments/external_sources/quantum_computation/",
    ),
    Target(
        "publications/successors/physics/FROM_FOLD_TO_PHYSICS_PAPER_001_V1_3.md",
        "## 12. Measurement Metrology",
        "Physics",
        "output/release/physics-1.3.0/05_Physics-Current-Categorical-Inventory.json",
        "output/release/physics-1.3.0/02_Physics-Paper-001-v1.3-Evidence-Map.json",
        "output/release/physics-1.3.0/03_Physics-Paper-001-v1.3-Manifest.json",
        "experiments/external_sources/physics/",
    ),
    Target(
        "publications/successors/chemistry/FROM_FOLD_TO_CHEMISTRY_PAPER_001_V1_3.md",
        "## 8. Measurement, identity, nomenclature and traceability - 8 admitted claims",
        "Chemistry",
        "census/chemistry_discipline_obligations.json",
        "publications/successors/chemistry/evidence_map_v1.3.json",
        "publications/successors/chemistry/manifest_v1.3.json",
        "experiments/external_sources/chemistry/",
    ),
    Target(
        "publications/successors/materials/FROM_FOLD_TO_MATERIALS_PAPER_001_V1_3.md",
        "## 11. Measurement Identity",
        "Materials Science",
        "census/materials_discipline_obligations.json",
        "publications/successors/materials/evidence_map_v1_3.json",
        "publications/successors/materials/manifest_v1_3.json",
        "experiments/external_sources/materials/",
    ),
)


def inventory_block(target: Target) -> str:
    return f"""## Family results, complete claim inventory and claim-level audit records

The dependency-ordered ledger below is the complete human-readable
{target.branch} claim inventory for this version. Each claim section exposes
its claim identity, family, formal and empirical status, exact statement,
dependency route, carrier and boundary, candidate grammar and count, unique
survivor, elimination logic, falsification condition, controls, source and
custody records, chronology, scientific meaning and receipt identities. Where
a generic clause is referenced, its full unchanged wording is retained in the
shared claim-record appendix. The machine packages remain authoritative for
complete candidates, decisions and executable traces.

"""


def availability_block(target: Target) -> str:
    return f"""## Data and code availability

The open repository is
[`MettaMazza/ernos-labs-sft-platform`](https://github.com/MettaMazza/ernos-labs-sft-platform).
The live model-admitted index is `census/claims.json`; the {target.branch}
field boundary is `{target.census}`. Every represented claim has its own
package under `claims/<claim-id>/` and its immutable model-admitted receipt
under `receipts/engine/model_admitted/`.

The publication evidence map is `{target.evidence_map}` and the candidate
manifest is `{target.manifest}`. Registered external records and source
captures are retained under `{target.source_surface}` together with their
source identities, transport outcomes and hashes. Files too large for ordinary
Git remain checksum-bound and are distributed through the applicable existing
Zenodo record rather than omitted or replaced.

Build, render, replay and verification programs are retained under `tools/`,
with branch implementations under `sft/`, independent reconstructions under
`generated/` and tests under `tests/`. The final approved Markdown, rendered
PDF, evidence map, manifest, metadata and checksums must agree before deposit.
No successful test is treated as empirical confirmation unless the
claim-specific evidence protocol separately authorises that status.

"""


def main() -> None:
    changed = 0
    for target in TARGETS:
        path = ROOT / target.path
        text = path.read_text(encoding="utf-8")
        if "## Family results, complete claim inventory and claim-level audit records" not in text:
            if text.count(target.inventory_anchor) != 1:
                raise SystemExit(f"inventory anchor mismatch: {target.path}")
            text = text.replace(
                target.inventory_anchor,
                inventory_block(target) + target.inventory_anchor,
                1,
            )
        if "## Data and code availability" not in text:
            marker = "## Shared claim-record clauses"
            if text.count(marker) != 1:
                raise SystemExit(f"shared-clause marker mismatch: {target.path}")
            text = text.replace(marker, availability_block(target) + marker, 1)
        path.write_text(text, encoding="utf-8")
        changed += 1
    print(f"publication structure v1: updated {changed} paper(s)")


if __name__ == "__main__":
    main()
