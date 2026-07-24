# Mechanically enumerated primitive Fold-map uniqueness

Claim: `SFT-FOUNDATION-PRIMITIVE-MAP-UNIQUENESS-001`

## WHY

V2 Steps 25 and 401 require an executable uniqueness theorem, an explicit grammar boundary and a mechanical extension beyond the primitive list.

## DERIVATION

The normalized zero-parameter primitive self-map grammar has four operational classes: identity `x`, square `x·x`, constant One and `cast(x joined x)`, the Fold. Raw junction is not a total self-map; guarded removal is not total; multiplication by One normalizes to identity; closed whole terms cast to One.

Identity is static. Square strictly contracts every proper exact part. Constant One collapses. Fold is noninjective and contains the exact one-third/two-thirds recurrent orbit. Therefore Fold alone satisfies the declared generator predicate at size one.

Base-four ranking enumerates 4 size-one, 16 size-two and 64 size-three ordered words: 84 exactly. Every larger word has a larger positive construction size, so no later word can displace the already qualifying size-one Fold. The result is explicitly conditional on this grammar and predicate; it is not advertised as unrestricted expression-language uniqueness.

## CHECK

The independent implementation regenerates the 84 words without importing the scientific module, confirms Fold at rank four as the sole survivor, and checks fibre collision and recurrence. Controls reject identity, shifted winners, source drift and scope expansion.
