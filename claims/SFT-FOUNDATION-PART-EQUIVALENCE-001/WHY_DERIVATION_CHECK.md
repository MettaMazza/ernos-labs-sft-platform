# Cross-partition exact part equivalence

## WHY

An exact held/whole coordinate records its construction, but differently
generated partitions can identify the same portion. The equivalence law must be
derived without importing multiplication, division, fraction reduction or
decimal comparison.

## DERIVATION

For every generated fibre of partition A, the common-refinement generator emits
one pair cell with every generated fibre of partition B. Grouping by the first
label refines A; grouping by the second refines B. Each held selection is lifted
to all pair cells descending from its held source fibres. The two coordinates
are equivalent exactly when the lifted selected traces admit a complete
one-to-one and onto pairing.

The witness grammar independently classifies refinement coverage, overlap,
fibre equality, refinement of A and B, complete lifting of both selections,
four pairing classes and extra data. Its complete product contains 1,024 forms.
Only the complete, disjoint, equal, doubly refining, doubly lifted, bijective,
addition-free witness survives.

Identity pairings give reflexivity, reversing pairings gives symmetry, and
chaining unique mates gives transitivity. Uniform further refinement preserves
the pairing. The construction uses nested finite generation rather than an
imported multiplication law.

## CHECK

All 1,024 forms receive decisions and proof identities. A generated one-of-two
versus two-of-four example has a pairing; a one-of-two versus one-of-three
control does not. Source, second-survivor and arithmetic-import controls are
also required. A standalone implementation regenerates the grammar and result.
