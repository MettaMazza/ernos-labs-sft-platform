# Exact finite channels, confusability and capacity

Claim: `SFT-INFO-CHANNEL-CAPACITY-001`

## Why

Capacity must follow from which source distinctions a channel can preserve, not from a borrowed probabilistic rate formula. Complete finite transport and confusability make that boundary exact.

## Derivation

Graphs supply relations and paths; encoding supplies messages and codewords; combinatorics exhausts selections; optimization retains all greatest codes; information quantity supplies exact distinction meaning. Ten axes force the finite zero-error channel and capacity family.

The registered grammar boundary is:

> All finite channels generated from canonical carriers, held transport relations, complete output supports, pairwise confusability checks, exhaustive input selections and exact relation composition.

The complete product has `1024` candidates across
`10` declared structural dimensions. Every dimension has one
all-preserving coordinate and one explicit failure coordinate. Exactly one
product member combines all preserving coordinates.

Admitted coordinates:

- `inputs` — admitted `complete-canonical-inputs`: Every registered input occurs once.
- `outputs` — admitted `complete-canonical-outputs`: Every registered output occurs once.
- `relation` — admitted `held-transport-relation`: Every possible source/output pair is retained.
- `totality` — admitted `nonempty-output-support-per-input`: Every input has at least one retained image.
- `confusability` — admitted `overlapping-output-support`: Confusability is exact shared output membership.
- `codes` — admitted `pairwise-disjoint-output-selection`: Every selected input pair has disjoint output support.
- `capacity` — admitted `complete-greatest-code-family`: Every input selection is generated and all maximum distinguishable ties survive.
- `composition` — admitted `exact-relational-paths`: Every source-to-middle and middle-to-target path generates one composite cell.
- `generality` — admitted `carrier-successor`: A fresh input adds its complete output support and all new confusability pairs.
- `addition` — admitted `no-extra-channel-model`: Capacity follows only from exact relation and distinguishability.

The admitted result is:

> The channel kernel is complete input/output carriers and held total transport, exact overlap confusability, exhaustive zero-error codes, the complete greatest code family, relational composition and no stochastic rule.

Its operational laws are:

- channel output support retains every possible output of one exact input.
- confusability is symmetric overlap of output supports.
- a zero-error input code has pairwise disjoint output supports.
- capacity retains every greatest distinguishable selection rather than applying an undeclared tie rule.
- composed output paths cannot restore an input distinction already merged at an intermediate interface.

Depth-independent closure uses this base:

> One input with one nonempty output support forms a one-member distinguishable code family.

and this successor certificate:

> Adding one fresh input adds its exact output support and one confusability decision with every prior input. Every prior code either extends by the fresh input when all supports are disjoint or remains unchanged.

The exact exclusions are:

- no transition probability or stochastic channel cause.
- no floating error threshold.
- no logarithmic or asymptotic capacity proof value.
- no ungenerated infinite code family.

## Check

Execute all 1,024 channel kernels, compare clean and merged channels, retain tied capacities, test a false code and exact composition, run adverse controls and independently regenerate the census.

Operational witnesses:

- `clean-capacity`: Disjoint clean outputs retain all three inputs as one greatest code.
- `merged-confusability`: Inputs a and b are confusable exactly through shared output x.
- `tied-capacity`: The merged channel retains both greatest two-input alternatives rather than tie-breaking.
- `code-control`: The a/b selection fails zero-error distinction while a/c passes.
- `composition`: Composing two clean identity-interface channels preserves exact source/output paths.

Four required controls reject a false premise, changed source identity, altered
survivor set and excluded boundary import. The separate validator independently
regenerates the literal candidate product and sole survivor without importing the
scientific law module.

## Boundary

This theorem closes finite zero-error structural capacity. Probabilistic error rates and asymptotic coding theorems require separately generated finite evidence and cannot be imported here.

Conventional correspondence terms, admitted only after the derivation is sealed:
communication channel, confusability graph, zero-error code, channel capacity, channel composition.
