#!/usr/bin/env python3
"""Build local same-paper roadmap successors without changing scientific receipts.

The operation copies each latest valid paper, changes only its successor version
boundary, and inserts the applicable branch roadmap before its references. It
does not modify the admission engine, protected verifiers, claims, receipts,
census or any published remote record.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


SPECS = (
    {
        "branch": "methods",
        "source": "publications/successors/methods/THERE_IS_NO_NOTHING_METHODS_PAPER_001_V0_2.md",
        "target": "publications/successors/methods/THERE_IS_NO_NOTHING_METHODS_PAPER_001_V0_3.md",
        "old": "0.2.0",
        "new": "0.3.0",
        "roadmap": "docs/branch_roadmaps/README.md",
        "marker": "## References",
        "status": (
            "Methods Paper 00 owns the shared empirical constitution and publication lifecycle, not downstream laws. "
            "Version 0.3 adds the complete two-layer roadmap governing all fifteen branches. The two inaugural proofs "
            "and every existing receipt remain unchanged."
        ),
    },
    {
        "branch": "foundation",
        "source": "publications/successors/foundation/FROM_NOTHING_TO_FOLD_FOUNDATION_PAPER_001_V1_2.md",
        "target": "publications/successors/foundation/FROM_NOTHING_TO_FOLD_FOUNDATION_PAPER_001_V1_3.md",
        "old": "1.2",
        "new": "1.3",
        "roadmap": "docs/branch_roadmaps/00-foundation.md",
        "marker": "## References",
        "status": (
            "The sixteen-law Foundation inventory remains current-evidence complete at its exact registered boundary. "
            "The continuing programme strengthens grammar reach, induction, constructor uniqueness, proof portability "
            "and adversarial authority studies; it does not replay or weaken the admitted foundation."
        ),
    },
    {
        "branch": "mathematics",
        "source": "publications/current/mathematics/FROM_FOLD_TO_MATHEMATICS.md",
        "target": "publications/successors/mathematics/FROM_FOLD_TO_MATHEMATICS_PAPER_001_V1_4.md",
        "old": "1.3",
        "new": "1.4",
        "roadmap": "docs/branch_roadmaps/01-mathematics.md",
        "marker": "## References",
        "status": (
            "The twenty-two-law mathematical kernel and active calculator lineage remain admitted at their exact "
            "boundaries. They establish the field's foundation but do not, by themselves, exhaust every named subject "
            "in mathematical science. Version 1.4 preserves all results and registers the complete-field programme."
        ),
    },
    {
        "branch": "information_science",
        "source": "publications/current/information_science/FROM_DISTINCTION_TO_INFORMATION.md",
        "target": "publications/successors/information_science/FROM_DISTINCTION_TO_INFORMATION_PAPER_001_V1_3.md",
        "old": "1.2",
        "new": "1.3",
        "roadmap": "docs/branch_roadmaps/02-information-science.md",
        "marker": "## References",
        "status": (
            "The twelve-law Information Science kernel and 77 same-strength prior obligations remain closed at the "
            "published boundary. Version 1.3 preserves those receipts while opening the registered programme across "
            "channels, codes, compression, signals, inference, privacy and cross-science information handoffs."
        ),
    },
    {
        "branch": "computation",
        "source": "publications/current/computation/AFTER_TURING_THE_FOLD_MACHINE.md",
        "target": "publications/successors/computation/AFTER_TURING_THE_FOLD_MACHINE_PAPER_001_V1_3.md",
        "old": "1.2.0",
        "new": "1.3.0",
        "roadmap": "docs/branch_roadmaps/03-classical-computation.md",
        "marker": "## References",
        "status": (
            "All 116 published computational laws and 134 prior-corpus obligations retain their receipts and exact "
            "boundaries. Version 1.3 distinguishes that admitted foundation/current inventory from the continuing "
            "complete-field programme across nine computational subbranches and bounded frontier requirements."
        ),
    },
    {
        "branch": "quantum_computation",
        "source": "publications/current/quantum_computation/THE_QUANTUM_FOLD_MACHINE.md",
        "target": "publications/successors/quantum_computation/THE_QUANTUM_FOLD_MACHINE_PAPER_001_V1_3.md",
        "old": "1.2.0",
        "new": "1.3.0",
        "roadmap": "docs/branch_roadmaps/04-quantum-computation.md",
        "marker": "## References",
        "status": (
            "All 22 published reversible and quantum-computation laws retain their receipts, including the separately "
            "forced unbounded-finite fault-tolerance result. Version 1.3 adds the complete operational, algorithmic, "
            "coding, verification, learning and limits roadmap without treating new fault models as automatic."
        ),
    },
    {
        "branch": "physics",
        "source": "publications/current/physics/FROM_FOLD_TO_PHYSICS.md",
        "target": "publications/successors/physics/FROM_FOLD_TO_PHYSICS_PAPER_001_V1_2.md",
        "old": "1.1",
        "new": "1.2",
        "roadmap": "docs/branch_roadmaps/05-physics.md",
        "marker": "## References and official data bodies",
        "status": (
            "The 349-law Physics census, both Grand Locks and all 488 Physics-owned prior atoms remain current-evidence "
            "complete at the dated corpus boundary. Version 1.2 adds the permanent field roadmap and categorical "
            "handoffs while preserving Physics as open to new measurements, corrections and lawful discoveries."
        ),
    },
    {
        "branch": "materials",
        "source": "publications/current/materials/FROM_FOLD_TO_MATERIALS.md",
        "target": "publications/successors/materials/FROM_FOLD_TO_MATERIALS_PAPER_001_V1_2.md",
        "old": "1.1.0",
        "new": "1.2.0",
        "roadmap": "docs/branch_roadmaps/07-materials.md",
        "marker": "## 27. References",
        "status": (
            "The 84-law Materials foundation and its 21,504 candidate decisions remain admitted at their exact "
            "boundaries. Version 1.2 places that foundation inside the wider field programme across microstructure, "
            "properties, processing, extreme conditions, computation and downstream handoffs."
        ),
    },
)


def sha(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def demote_roadmap(text: str) -> str:
    output = []
    for line in text.splitlines():
        if line.startswith("# "):
            continue
        if line.startswith("### "):
            output.append("#### " + line[4:])
        elif line.startswith("## "):
            output.append("### " + line[3:])
        else:
            output.append(line)
    return "\n".join(output).strip()


def successor_boundary(branch: str, old: str, new: str) -> str:
    return (
        f"**LOCAL SAME-PAPER SUCCESSOR VERSION {new}; REMOTE PUBLICATION IS NOT AUTHORIZED.** "
        f"The preceding version {old} and its DOI record remain unchanged. This roadmap update does not authorize a "
        "commit, push, release, upload, DOI-version action or publication."
    )


def build_one(spec: dict[str, str]) -> dict[str, object]:
    source = ROOT / spec["source"]
    target = ROOT / spec["target"]
    roadmap = demote_roadmap((ROOT / spec["roadmap"]).read_text(encoding="utf-8"))
    text = source.read_text(encoding="utf-8")
    if spec["marker"] not in text:
        raise SystemExit(f"{spec['branch']} insertion marker is absent")

    # Change the first visible version boundary only. Historical evidence and
    # citations retain the version at which they were actually produced.
    if spec["branch"] == "methods":
        text = text.replace("successor version 0.2.0", "successor version 0.3.0", 1)
        text = text.replace("**Version:** 0.2.0", "**Version:** 0.3.0", 1)
        text = text.replace(
            "> **Exact release status.** Version 0.2 preserves",
            "> **Exact release status.** Version 0.3 preserves version 0.2 and",
            1,
        )
        text = text.replace(
            "**Version:** 0.3.0 · **Published:** 26 July 2026",
            "**Version:** 0.3.0 · **Local successor prepared:** 27 July 2026",
            1,
        )
        old_status_tail = """> The Foundation, Mathematics, Information Science, Classical Computation,
> Quantum Computation, Chemistry and Materials papers now exist; the expanded
> Physics paper completes the present ordered publication update. Chemistry,
> Materials and every later branch remain outside this release sequence."""
        new_status_tail = """> The published ordered sequence runs through Physics. Local same-paper roadmap
> successors now cover Methods Paper 00 through Materials, including the secure
> Chemistry foundation and its 90 admitted extensions through ORG-011. These
> local successors are not remotely published or authorized by this build."""
        text = text.replace(old_status_tail, new_status_tail, 1)
    elif spec["branch"] == "foundation":
        text = text.replace("patch, version 1.2", "roadmap successor, version 1.3", 1)
        text = text.replace(
            "This version 1.2 patch reports",
            "This version 1.3 roadmap successor preserves the complete version 1.2 evidence and reports",
            1,
        )
    elif spec["branch"] == "mathematics":
        text = text.replace("Version 1.3 -", "Version 1.4 -", 1)
        text = text.replace(
            "version 1.3 preserves that scientific record while moving",
            "version 1.4 preserves the complete version 1.3 scientific record, adds the full-field roadmap, and keeps",
            1,
        )
    elif spec["branch"] == "information_science":
        text = text.replace("Version 1.2 -", "Version 1.3 -", 1)
        text = text.replace(
            "This paper reports the completed Information Science branch",
            "This version 1.3 paper preserves the completed foundational Information Science inventory",
            1,
        )
    elif spec["branch"] == "computation":
        text = text.replace("version 1.2.0", "version 1.3.0", 1)
        text = text.replace(
            "This paper reports the completed Classical Computation branch",
            "This version 1.3 paper preserves the complete registered Classical Computation inventory",
            1,
        )
    elif spec["branch"] == "quantum_computation":
        text = text.replace("version 1.2.0", "version 1.3.0", 1)
        text = text.replace(
            "This paper reports the completed Reversible and Quantum Computation branch",
            "This version 1.3 paper preserves the complete registered Reversible and Quantum Computation inventory",
            1,
        )
    elif spec["branch"] == "physics":
        text = text.replace(
            "# From Fold to Physics\n",
            "# From Fold to Physics\n\n**Physics Branch Paper 001, local same-paper successor version 1.2.0**\n",
            1,
        )
        published = "**PUBLISHED OPEN-ACCESS BRANCH PAPER.** DOI: [10.5281/zenodo.21591791](https://doi.org/10.5281/zenodo.21591791). This canonical Markdown paper, its rendered PDF, complete evidence/source archive and checksum ledger form the Physics Branch Paper 001 release."
        text = text.replace(published, successor_boundary("physics", spec["old"], spec["new"]), 1)
    elif spec["branch"] == "materials":
        text = text.replace("version 1.1.0", "version 1.2.0", 1)
        text = text.replace(
            "This paper reports the complete Materials Science branch",
            "This version 1.2 paper preserves the complete foundational Materials Science inventory",
            1,
        )

    block = f"""## Foundation and full-field reconstruction roadmap — version {spec['new']}

{successor_boundary(spec['branch'], spec['old'], spec['new'])}

{spec['status']}

This amendment adds no scientific admission by prose. Every result already in
the paper retains its exact receipt and evidence boundary. Every future result
must pass the untouched engine independently. A branch described as complete
to a dated inventory remains permanently open to lawful extension, correction,
falsification and discoveries that satisfy the same public standard.

{roadmap}

"""
    text = text.replace(spec["marker"], block + spec["marker"], 1)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text.rstrip() + "\n", encoding="utf-8")
    return {
        "branch": spec["branch"],
        "source": spec["source"],
        "source_sha256": sha(source),
        "successor": spec["target"],
        "successor_sha256": sha(target),
        "preceding_version": spec["old"],
        "successor_version": spec["new"],
        "roadmap": spec["roadmap"],
        "publication_authorized": False,
    }


def main() -> None:
    records = [build_one(spec) for spec in SPECS]
    # Chemistry v1.2 was built directly from all 176 live admitted claims and
    # already contains its roadmap; record it in the ordered successor set.
    chemistry = ROOT / "publications/current/chemistry/FROM_FOLD_TO_CHEMISTRY.md"
    records.insert(7, {
        "branch": "chemistry",
        "source": "publications/current/chemistry/FROM_FOLD_TO_CHEMISTRY.md",
        "source_sha256": sha(chemistry),
        "successor": "publications/current/chemistry/FROM_FOLD_TO_CHEMISTRY.md",
        "successor_sha256": sha(chemistry),
        "preceding_version": "1.1.0",
        "successor_version": "1.2.0",
        "roadmap": "docs/branch_roadmaps/06-chemistry.md",
        "publication_authorized": False,
    })
    output = ROOT / "publication/branch_roadmap_successor_versions.json"
    output.write_text(json.dumps({
        "schema": "sft-v3-branch-roadmap-successor-set/1",
        "publication_authorized": False,
        "remote_action_permitted": False,
        "papers": records,
    }, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"built {len(records)} local roadmap successors and {output.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
