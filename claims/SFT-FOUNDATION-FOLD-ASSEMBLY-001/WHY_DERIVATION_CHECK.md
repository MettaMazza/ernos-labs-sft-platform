# Complete finite Fold-word assembly

## WHY

The minimal Fold supplies two held fibres, but not yet the law for repeated
composition. Complete support must be generated without importing binary
notation, exponentiation or an infinite word space.

## DERIVATION

The base is the structural empty One word, not numerical zero. Each successor
Fold appends `held-a` and `held-b` once to every prior word. This forces all and
only the next words, one held label per Fold step. Distinct predecessors or
distinct appended labels have distinct construction traces.

The 192-form representation grammar classifies trace coverage, word-length
consistency, support completeness, duplication, transitions, returns and extra
data. Only complete coverage with consistent unique complete support, retained
transitions and returns, and no addition survives.

## CHECK

The independent implementation regenerates supports through five successive
Folds with generated counts 2, 4, 8, 16 and 32, while the proof of generality is
the base/successor construction rather than those finite examples. Controls
reject a missing one-step branch, source drift, duplicated or missing words and
claims of imported binary arithmetic or completed-infinite support.
