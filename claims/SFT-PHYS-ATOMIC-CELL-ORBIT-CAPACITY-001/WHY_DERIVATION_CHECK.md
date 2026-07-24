# Atomic orbit-cell capacity from three-space boundary orientation

Claim: `SFT-PHYS-ATOMIC-CELL-ORBIT-CAPACITY-001`

## WHY

At positive orbit rank r, three-space supplies one central orientation and the rank-two boundary supplies one held pair for every predecessor step. Two exclusion-distinct Fold labels occupy each orientation, forcing capacity 2(1+2(r-1)) and the sequence 2, 6, 10, 14, 18 without observation.

## DERIVATION

Grammar boundary: All orbit-cell capacity laws generated from one central orientation, positive orbit succession, the complete rank-two boundary, two held Fold labels and exclusion.

The generator exhausts the Cartesian product of every registered axis: exactly
1024 named forms. Exactly one form preserves all upstream laws and
typed structural roles:

`held-orientation-cell__one-central-orientation__one-boundary-orientation-pair__forced-rank-two-pair__both-Fold-labels__one-of-each-label-per-cell__labels-times-complete-orientations__constant-boundary-pair-successor__widths-inaccessible-until-seal__no-extra-rule`

- `carrier`: sole preserving form `held-orientation-cell`; `unlabelled-cell-count` — An unlabelled count loses orientation identity.; `held-orientation-cell` — Each cell retains its generated orientation.
- `central`: sole preserving form `one-central-orientation`; `empty-numerical-origin` — Numerical zero is not an SFT carrier.; `one-central-orientation` — Rank One retains exactly the central orientation.
- `successor`: sole preserving form `one-boundary-orientation-pair`; `free-rank-increment` — A free increment is a parameter.; `one-boundary-orientation-pair` — Each successor adds the complete two-sided boundary incidence.
- `boundary`: sole preserving form `forced-rank-two-pair`; `single-or-three-direction-addition` — One omits a boundary side and three re-adds the held normal.; `forced-rank-two-pair` — Boundary rank two supplies exactly one orientation pair.
- `label`: sole preserving form `both-Fold-labels`; `label-erased-or-selected` — Erasure or selection violates complete Fold support.; `both-Fold-labels` — Both forced Fold labels are retained.
- `exclusion`: sole preserving form `one-of-each-label-per-cell`; `duplicate-cell-label` — Duplication destroys distinguishability.; `one-of-each-label-per-cell` — Exclusion retains one state per held label and orientation.
- `capacity`: sole preserving form `labels-times-complete-orientations`; `linear-or-doubling-without-boundary` — Those former survivors ignore the newly admitted boundary discriminator.; `labels-times-complete-orientations` — The Cartesian support of labels and orientations is complete.
- `generality`: sole preserving form `constant-boundary-pair-successor`; `finite-width-list` — A list has no next-rank proof.; `constant-boundary-pair-successor` — Every successor adds one pair and therefore four label-orientation states.
- `target`: sole preserving form `widths-inaccessible-until-seal`; `width-list-visible` — That reverses derivation and test.; `widths-inaccessible-until-seal` — The positive-rank law seals before comparison.
- `extension`: sole preserving form `no-extra-rule`; `extra-degeneracy-rule` — An added degeneracy is a parameter.; `no-extra-rule` — Three-space, boundary rank, Fold labels and exclusion exhaust the cell grammar.

No axis is a free or learned parameter. The construction does not read an old
SFT answer or an external physical target.

Base: Positive orbit rank One contains one central orientation carrying both exclusion-distinct Fold labels, hence capacity two.

Successor/termination certificate: Each rank successor adds the complete boundary pair; two labels on each new orientation add exactly four states and preserve the formula.

Exact result: For every positive orbit rank r, capacity is exactly 2(1+2(r-1)); ranks one through five have capacities 2, 6, 10, 14 and 18.

## CHECK

- `first-five-capacities`: The first five positive ranks generate 2, 6, 10, 14 and 18.
- `successor-increment`: Every tested successor adds exactly four, as proved for arbitrary positive rank by the boundary-pair construction.
- `complete-cell-support`: Capacity equals the complete product of orientations and the two held labels.

An implementation-distinct standard-library validator regenerates the complete
candidate product, sole-survivor decisions and exact arithmetic witness. Four
adverse controls must pass before admission. Empirical comparison, where
available, is a separate post-seal claim and cannot rewrite this derivation.

## EXCLUSIONS

- no V1/V2 proof artifact, measured constant, observed shell list or intended Chemistry answer as a premise
- no semantic numerical zero, negative, irrational, imaginary or floating proof value
- no fitted coupling, selected candidate neighborhood or target-selected form
- no unrecorded external rule or measurement-to-derivation flow
