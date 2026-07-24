# Complete replayable derivation trace

Claim: `SFT-FOUNDATION-DERIVATION-TRACE-001`

## WHY

A statement cannot enter SFT authority merely because a program returned it. The complete ordered path, dependency custody and exact intermediates must be independently replayable to the root theorem.

## DERIVATION

The 256-record product classifies source custody, dependency coverage, order, exactness, operation registration, replay, terminal identity and extra data. Only the complete source-bound ordered exact record survives.

The base is an admitted exact input with its dependency receipt. The successor appends one registered operation with ordered input hashes and exact output identity. Determinism preserves replay equality at every finite successor. The terminal output identity is the result; prose cannot replace it.

V2 Step 256 is reconstructed exactly: `Fold(one-of-three)` gives two-of-three; `Take(One,two-of-three)` gives one-of-three; the next Fold gives two-of-three. The independent direct route also gives two-of-three.

## CHECK

The independent implementation regenerates all 256 records and recomputes both routes. Controls reject an unregistered operation, source drift, a changed terminal and a missing or reordered trace. The base/successor certificate is depth-independent for every generated finite derivation.
