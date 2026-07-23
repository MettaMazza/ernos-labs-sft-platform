# Complete foundational form grammar

## WHY

Fold words describe paths through repeated Folds. A complete foundational
grammar must additionally derive every finite nested form, including nonuniform
trees, without importing a conventional term or tree calculus.

## DERIVATION

The terminal production is the structural One. The recursive production is a
Fold node with exactly two previously generated child forms, one on each
distinct held-labelled edge, plus the Fold return relation. Every construction
trace is finite and ends in One leaves.

The generator enumerates 288 production-rule shapes across base inclusion,
arity, labels, child provenance, return, termination and extra constructors.
Only the base-including, exactly-two-child, distinctly labelled, generated,
returning, finitely terminating and addition-free rule survives.

Structural induction proves both directions: every generated output is a finite
One/Fold form, and every finite One/Fold assembly parses through these two
productions.

## CHECK

Controls reject a one-child Fold, source drift, same-label edges, ungenerated
constructors and completed-infinite trees. The separate validator regenerates
the entire rule grammar and production identities.
