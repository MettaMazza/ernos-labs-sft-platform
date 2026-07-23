# Exact noise, error, detection and correction boundaries

Claim: `SFT-INFO-NOISE-ERROR-001`

## Why

Coding cannot be derived until the model states exactly what noise changes, what detection observes and why a correction is unique. Probabilities and metrics are not necessary for these structural boundaries.

## Derivation

Channels supply source/output relations; dynamics supplies transitions and predecessor loss; entropy supplies closed classes; graphs supply paths. Ten structural axes force exact action provenance, error traces and singleton-predecessor correction.

The registered grammar boundary is:

> All finite error systems generated from canonical source and received words, held transformation actions, exact changed-position traces, valid code support and complete predecessor classes.

The complete product has `1024` candidates across
`10` declared structural dimensions. Every dimension has one
all-preserving coordinate and one explicit failure coordinate. Exactly one
product member combines all preserving coordinates.

Admitted coordinates:

- `source` — admitted `complete-canonical-sources`: Every registered clean word occurs once.
- `received` — admitted `complete-registered-images`: Every generated image under registered actions is retained.
- `action` — admitted `held-action-relation`: Each cell retains source, image and action identity.
- `error` — admitted `complete-changed-position-trace`: Every differing position retains old and new labels; identity is empty One.
- `detection` — admitted `invalid-codeword-witness`: A changed received form outside valid code support is detected structurally.
- `predecessors` — admitted `complete-source-class`: Every registered source mapping to the received form is retained.
- `correction` — admitted `singleton-predecessor`: Correction occurs exactly when one registered source remains.
- `cause` — admitted `deterministic-transformation-family`: Noise names the complete registered action relation over deterministic forms.
- `generality` — admitted `action-successor`: A fresh registered action adds its exact source/image cells and updates predecessor classes.
- `addition` — admitted `no-extra-error-model`: Detection and correction use only code support and predecessor identity.

The admitted result is:

> The noise/error kernel is complete source and received support, held action provenance, exact position traces, invalid-code detection, complete predecessor classes, singleton correction and no stochastic or metric rule.

Its operational laws are:

- identity transport has structural empty-One error trace.
- nonidentity error retains every changed position and both labels.
- detection requires a received form outside the valid codebook.
- exact correction is equivalent to a singleton registered predecessor class.
- ambiguous received forms preserve all source predecessors rather than choosing a likely one.

Depth-independent closure uses this base:

> One source under its identity action yields itself, empty-One error and a singleton predecessor class.

and this successor certificate:

> Adding one registered action adds one exact image cell for each source on which it acts. Error traces compare those forms positionwise, and each affected received predecessor class extends by precisely the new source cell.

The exact exclusions are:

- no stochastic noise cause.
- no floating error rate or threshold.
- no assumed metric or nearest-neighbor rule.
- no unrecorded source inference.

## Check

Execute all 1,024 noise kernels, verify identity and changed-position traces, detection, unique correction and an ambiguous predecessor control, run all adverse controls and independently regenerate the census.

Operational witnesses:

- `identity-error`: Identity transport returns structural empty-One error.
- `position-trace`: The first-label change retains its exact position and labels.
- `detection`: A one-label image outside the repetition codebook is structurally detectable.
- `unique-correction`: The registered b/a/a image has exactly source a.
- `ambiguous-control`: The shared b/a/b image retains both predecessors and refuses unique correction.

Four required controls reject a false premise, changed source identity, altered
survivor set and excluded boundary import. The separate validator independently
regenerates the literal candidate product and sole survivor without importing the
scientific law module.

## Boundary

This theorem closes finite structural noise and error. It does not assign a stochastic error frequency, physical noise mechanism or asymptotic reliability rate.

Conventional correspondence terms, admitted only after the derivation is sealed:
noise, error pattern, error detection, syndrome, decoding ambiguity.
