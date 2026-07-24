# Arbitrary admitted Fold-circuit lower-bound law

Claim: `SFT-COMP-CPLX-ARBITRARY-CIRCUIT-LOWER-BOUND-002`

## WHY

V2 Step 406 extends circuit resource counting to a necessary lower bound over every admitted circuit; a count of one implementation is not the same theorem.

## DERIVATION

The unique native edge from each word to its suffix cannot replace another source edge or close two dependent positions. Complete support therefore forces every input vertex and every layered edge; the constructed circuit meets the resulting bounds.

Boundary:

> Every circuit whose vertices are generated native Fold words and whose gates are lawful unique depth-r to depth-(r-1) Fold edges.

The complete grammar contains 256 candidates across eight binary axes. Exactly one retains every requirement.

- `gate` -> `unique-lawful-one-depth-edge`: Each source has its forced suffix edge.
- `path` -> `one-distinction-per-dependent-edge`: No lawful edge closes two dependent word positions.
- `width` -> `all-b-to-k-source-words`: Every exact depth-k input requires its held source vertex.
- `size` -> `every-source-edge-required`: Each source word has one distinct forced outgoing edge.
- `exhaustion` -> `complete-forced-edge-subset-census`: Every subset at the declared census depth is classified.
- `attainment` -> `registered-circuit-attains-all-bounds`: The complete forced-edge circuit meets path, width and size exactly.
- `successor` -> `add-next-complete-source-layer`: Depth successor adds b^(k+1) required source edges and one path edge.
- `boundary` -> `admitted-fold-circuits-only`: The theorem stays within lawful Fold edges.

Forced result:

> The unique kernel forces tight path k, width b^k and size sum(r=One..k)b^r lower bounds over every admitted Fold-edge circuit at every supplied positive finite depth.

Operational laws:

- one lawful edge closes one dependent position
- every complete source word requires its own source vertex and outgoing edge
- all forced edges are necessary for complete layered coverage
- the complete registered circuit attains the three lower bounds

Base:

> At first positive depth there are b source words, one required edge from each, path depth One and width b.

Successor:

> Adding the next word position creates b^(k+1) new source words and forced edges, increases every closing path by one and preserves every prior layer.

## CHECK

Exhaust every forced-edge subset through colour depth, execute exact resources through depth fourteen, prove the layer successor, exhaust 256 structural candidates and independently regenerate the decision vector.

- `exact-resources`: Path, width and size match k, b^k and the complete edge sum through depth fourteen.
- `subset-census`: Every subset of the fourteen forced edges through colour depth is exhausted and exactly the full set survives.
- `attainment`: The complete forced-edge set contains every source edge once at every depth through fourteen.

The false-premise, changed-source, changed-survivor and excluded-boundary controls must all reject. The independent validator regenerates the literal product without importing this scientific module.

## Exact limitation

The theorem covers every circuit in the admitted native Fold-edge grammar and does not assert lower bounds for external Boolean, arithmetic or quantum gate bases.

- no Boolean or external quantum gate basis
- no rewired Fold edge
- no sampled input support
- no completed infinite circuit
- no claim beyond admitted Fold circuits
