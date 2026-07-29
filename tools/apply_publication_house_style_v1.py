#!/usr/bin/env python3
"""Insert the shared publication-status and terminology layer into seven papers.

The operation is editorial and additive. It does not alter existing scientific
statements, claim records, identifiers, evidence classes or machine identities.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MARKER = "## Current status, evidence language and reader map"


@dataclass(frozen=True)
class Target:
    path: str
    anchor: str
    branch: str
    completion: str
    candidate_version: str
    current_doi: str
    concept_doi: str


TARGETS = (
    Target(
        "publications/successors/mathematics/"
        "FROM_FOLD_TO_MATHEMATICS_PAPER_001_V1_5.md",
        "## Public scientific mission and admission boundary",
        "Mathematics",
        "323/323 frozen obligations; 323 live claims",
        "1.5.0",
        "10.5281/zenodo.21627708",
        "10.5281/zenodo.21516145",
    ),
    Target(
        "publications/successors/information_science/"
        "FROM_DISTINCTION_TO_INFORMATION_PAPER_001_V1_4.md",
        "## Public scientific mission and admission boundary",
        "Information Science",
        "262/262 frozen obligations; 262 live claims",
        "1.4.0",
        "10.5281/zenodo.21627717",
        "10.5281/zenodo.21516915",
    ),
    Target(
        "publications/successors/computation/"
        "AFTER_TURING_THE_FOLD_MACHINE_PAPER_001_V1_4.md",
        "## Public scientific mission and admission boundary",
        "Classical Computation",
        "369/369 frozen obligations; 369 live claims",
        "1.4.0",
        "10.5281/zenodo.21627721",
        "10.5281/zenodo.21518310",
    ),
    Target(
        "publications/successors/quantum_computation/"
        "THE_QUANTUM_FOLD_MACHINE_PAPER_001_V1_4.md",
        "## Public scientific mission and admission boundary",
        "Reversible and Quantum Computation",
        "288/288 frozen obligations; 288 live claims",
        "1.4.0",
        "10.5281/zenodo.21627748",
        "10.5281/zenodo.21518312",
    ),
    Target(
        "publications/successors/physics/"
        "FROM_FOLD_TO_PHYSICS_PAPER_001_V1_3.md",
        "## 1. Publication and authorship boundary",
        "Physics",
        "368/368 claims in the current registered categorical scope",
        "1.3.0",
        "10.5281/zenodo.21627765",
        "10.5281/zenodo.21520880",
    ),
    Target(
        "publications/successors/chemistry/"
        "FROM_FOLD_TO_CHEMISTRY_PAPER_001_V1_3.md",
        "## Public scientific mission and admission boundary",
        "Chemistry",
        "272/272 registered discipline obligations; 281 live claims including nine separately returned claims",
        "1.3.0",
        "10.5281/zenodo.21627782",
        "10.5281/zenodo.21531454",
    ),
    Target(
        "publications/successors/materials/"
        "FROM_FOLD_TO_MATERIALS_PAPER_001_V1_3.md",
        "## Public scientific mission and admission boundary",
        "Materials Science",
        "289/289 frozen obligations; 289 live claims",
        "1.3.0",
        "10.5281/zenodo.21629306",
        "10.5281/zenodo.21532481",
    ),
)


def block(target: Target) -> str:
    return f"""{MARKER}

| Status field | Current position |
|---|---|
| Branch and completion boundary | {target.branch}: {target.completion}. This is dated, versioned completion and remains open to lawful extension. |
| Formal status | Every live claim represented here has a current model-admitted receipt. Formal admission does not by itself imply empirical confirmation. |
| Empirical status | Claim-specific. Blind, non-blind, development-observed, holdout, adverse, unresolved, unavailable and formal-only distinctions remain exactly as recorded in the claim ledger and evidence packages. |
| Chronology | Claim-specific registration, seal, custody and observation order governs. Later evidence does not retroactively become an earlier prediction. |
| Publication status | Version {target.candidate_version} is a final publication candidate awaiting Maria Smith's approval. It is not yet deposited. |
| Existing record lineage | Current record DOI `{target.current_doi}`; concept DOI `{target.concept_doi}`. Publication is permitted only through the existing record's new-version route. |
| What is not claimed | Permanent closure of science, universal empirical confirmation, transfer of another branch's ownership or permission to replace an adverse or unresolved record. |

### Corpus-wide terminology and evidence key

| Term | Reserved meaning in this paper |
|---|---|
| Theorem | A formally closed proposition at its declared grammar and dependency boundary. |
| Law | An admitted branch relation with its declared carrier, boundary, dependencies and extension rule. |
| Claim | The registered unit judged by the engine and bound to one immutable receipt. |
| Constitution | The rules governing admissible objects, derivations, evidence and publication; not an empirical result. |
| Derivation | Generation and elimination of the declared candidate space to its surviving structure. |
| Prediction | A consequence sealed before the matching target is released under the registered custody protocol. |
| Observation | A source-bound external record; it does not enter candidate generation. |
| Measurement | An instrument-, method-, condition- and uncertainty-bound observed value. |
| Reconstruction | A separately implemented regeneration or an explicitly identified inference of a retained state or history. |
| Exact numerical correspondence | Equality or registered interval relation between exact numerical objects at the declared boundary. |
| Structural correspondence | A post-derivation relation between forms without a claim of exact numerical prediction. |
| Boundary correspondence | Agreement restricted to the named interface, limit or ownership boundary. |
| Compatibility | Non-adverse but non-discriminating evidence. |
| Support | Relevant evidence that is not unique confirmation. |
| Confirmation | Used only when the current registered evidence protocol warrants that classification. |
| Validation | Successful execution of the specified formal, computational or empirical test; its kind must be named. |
| Adverse result | A registered test result that conflicts with the tested claim at its declared boundary. |
| Unresolved result | Required evidence remains unavailable, incomplete, disputed or insufficiently classified. |
| Implementation identity | The hash-bound identity of executable material; implementation success is not empirical confirmation. |
| Formal, empirical and publication status | Three independent classifications. None silently substitutes for another. |
| Foundational closure | Completion of the registered foundation only. It does not imply field-wide closure. |
| Field-wide closure | Completion of the frozen or registered dated field census named in this paper. |
| Current-evidence closure | Closure only to the evidence surface presently registered and preserved. |
| Extension openness | New questions may be added by a later version without rewriting existing receipts or history. |

Proof language is reserved for formal closure; derivation for generated
structure; implementation for executable demonstration; prediction for a
correctly sealed prospective consequence; observation and measurement for
source-bound external records; reconstruction for separately regenerated or
inferred states; correspondence for post-derivation relationships;
compatibility and support for non-unique evidence; confirmation only where the
registered protocol authorises it; adverse for conflict; and unresolved where
required evidence remains incomplete.

### Three reading levels

1. **Conceptual paper.** The abstract, headline findings, branch narrative,
   major derivations, evidence synthesis, limitations and conclusion provide
   the readable scientific argument.
2. **Scientific audit layer.** Family and claim sections preserve exact status,
   dependencies, candidate and survivor counts, controls, chronology, sources,
   corrections, adverse evidence and reconciliation.
3. **Machine archive.** The cited repository packages preserve complete
   candidates, decisions, hashes, receipts, executable traces, source snapshots
   and certificates. Those files remain authoritative where prose abbreviates
   their display.

### Editorial change control

This version may improve expression, order, typography and navigation. It may
not change scientific meaning, scope, chronology, evidence class, ownership,
claim status or machine identity. Any apparent conflict between authoritative
records must be traced and either resolved by explicit supersession or recorded
for Maria Smith; prose alone cannot manufacture agreement.

"""


def main() -> None:
    changed = 0
    for target in TARGETS:
        path = ROOT / target.path
        text = path.read_text(encoding="utf-8")
        if MARKER in text:
            continue
        if text.count(target.anchor) != 1:
            raise SystemExit(f"expected one anchor in {target.path}: {target.anchor}")
        text = text.replace(target.anchor, block(target) + target.anchor, 1)
        path.write_text(text, encoding="utf-8")
        changed += 1
    print(f"publication house style v1: updated {changed} paper(s)")


if __name__ == "__main__":
    main()
