# Physics branch reconstruction status

Status: `superseded_historical_plan`.

This file preserves the reconstruction plan that preceded the complete-field
Physics successors. Physics now has 368/368 current registered claims, a local
version 1.4.0 successor and inclusion in the 2 August 2026 Lean 4 whole-model
PASS. It is not a current blocker. See
[`../audits/CURRENT_PROGRAMME_STATUS_2026-08-02.md`](../audits/CURRENT_PROGRAMME_STATUS_2026-08-02.md).

The sections below are retained as historical completion criteria and must not
be read as the current state.

## Historical reason Physics was open

At the time of this plan, the archived paper contained 132 required Physics
claims and eight supplemental validation claims, while the then-live corpus
contained 160. Twenty claims were therefore absent from that paper and the
larger V1/V2 physical-value reconciliation was incomplete.

The earlier publication gate verified the frozen inventory against its receipts
and manuscript. It did not prove that the frozen inventory included every
known prior Physics result. The successor gate now requires both.

## Binding completion standard

Physics Paper 002 cannot be built as a complete paper until:

1. all 356 V1 rows and 407 V2 steps have been reviewed against Physics and
   every Physics-owned atomic component has exactly one categorical owner;
2. every Physics-owned row has an explicit same-strength V3 disposition;
3. every claimed physical value is independently forced and sealed before
   authoritative measurement comparison;
4. values, units, uncertainty, source identity, complete rows and falsifiers
   are preserved;
5. failed results remain visible and keep the relevant obligation open unless
   a separately generated lawful successor closes it;
6. the successor evidence map equals the complete live Physics census; and
7. `python3 tools/verify_publication_compliance.py --branch physics
   --require-ready` passes.

## Categorical paper rule

Fine structure, lepton and particle values, force couplings, nuclear constants,
spatial dimension, inverse-square dilution and universal physical cosmology
relations belong in Physics. Chemistry and Materials may cite their immutable
receipts and derive downstream consequences, but cannot be their first or
principal exhaustive derivation papers.

Astronomy/Cosmology separately owns cosmic objects, populations, chronology,
historical state and observational interpretation.

## Current admitted progress

The twenty post-publication Physics claims remain admitted at their exact
boundaries. They include generator three, stable three-space, boundary rank
two, inverse-square dilution and validation, terminal inverse fine structure
and CODATA validation, orbit capacity, colour coupling, nuclear closures and
validation, atomic endpoint, the charged-lepton formal invariant and terminal
empirical refinement, Koide validation, dark/baryon ratios, Hubble calibration,
spatial flatness and the refined cosmic budget.

These receipts are progress toward the successor. They do not by themselves
close the complete Physics obligation inventory.

See:

- `audits/PUBLISHED_BRANCH_COMPLETENESS_AUDIT_2026-07-24.md`;
- `audits/PHYSICS_PRIOR_VALUE_AUDIT_2026-07-24.md`;
- `census/prior_obligation_ownership.json`; and
- `census/lineage_reconciliation.json`.
