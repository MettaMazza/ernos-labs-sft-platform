# Publication archive and successor policy

`publications/current/` is retained as a compatibility path because published
manifests, release tooling, local references and external links already bind
those locations. Its name does not presently assert that the papers are the
complete current V3 scientific account.

The eight contained branch directories are immutable v1 source trees for:
Foundation, Mathematics, Information Science, Classical Computation, Quantum
Computation, Physics, Chemistry and Materials.

New work follows these locations:

- scientific claims: `sft/<owning_branch>/` and `claims/<claim-id>/`;
- open obligations: `frontier/<owning_branch>.md`;
- audit and reconciliation evidence: `audits/` and `census/`;
- successor editorial requirements: `publications/SUCCESSOR_PAPER_RECONSTRUCTION_PLAN.md`;
- successor manuscript generation: only after the branch's full 763-entry
  ownership review, atomic same-strength closure and current gate pass; and
- immutable released artifacts: existing DOI/release records remain unchanged.

No new successor manuscript may silently overwrite a v1 paper. At successor
freeze, a versioned source directory and new manifest must be created before
any compatibility pointer changes.
