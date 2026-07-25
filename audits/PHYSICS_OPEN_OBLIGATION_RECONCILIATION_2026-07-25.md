# Physics open-obligation reconciliation — 2026-07-25

This audit records seven V1/V2 Physics rows that remained open in the prior-work
ledger after their same physical boundary had already been reconstructed by a
later, model-admitted V3 terminal claim. No engine receipt is changed, no prior
hash is replaced, and no claim is replayed merely to alter bookkeeping. The
ledger builder accepts a closure mapping only when every named claim ID already
has a model-admitted receipt in `census/claims.json`.

## Reconciled rows

| Prior row | Admitted terminal evidence | Same-strength or stronger boundary |
|---|---|---|
| V1 B9 | `SFT-PHYS-COUPLING-RUNNING-CONVERGENCE-TERMINAL-006` | The general exact pair gap `(q-p)/[(p+R)(q+R)]` at `p=2`, `q=3`, `R=2^d` is exactly `1/[(2+2^d)(3+2^d)]`; its strict successor shrinkage and finite-tolerance witness are depth-independent. |
| V2 Step 90 | `SFT-PHYS-DECAY-WIDTH-BRANCHING-LIFETIME-TERMINAL-006` | Every positive partial-width partition is generated, branch shares sum to the One, lifetime is action over total width and decreases strictly with width; the complete W branching and width vectors were compared post-seal. The early `1/4,3/4` pair is retained as one generated partition, not promoted to a universal decay vector. |
| V2 Step 185 | `SFT-PHYS-COUPLED-ENSEMBLE-SYNCHRONIZATION-TERMINAL-007`; `SFT-PHYS-COUPLED-MAP-CRITICALITY-TERMINAL-008` | The exact transverse multiplier is `m(One-g)`; the unique neutral boundary is `(m-1)/m`, hence half-One for the binary map, with expanding and contracting adverse sides and the topology limit retained. |
| V2 Step 189 | `SFT-PHYS-ORBITAL-DIMENSION-STABILITY-TERMINAL-009` | Positive denominator ordering forces restoring circular orbits only in dimensions two and three, structural marginality in four and non-restoration from five onward. This is the admissible strengthened successor: the old signed `4-d`, numerical-zero marginal and dimension-one “orbit” shorthand are retained as adverse syntax rather than copied into V3 proof arithmetic. |
| V2 Step 190 | `SFT-FOUNDATION-HALF-ONE-001`; `SFT-PHYS-SPACE-BOUNDARY-RANK-TWO-001`; `SFT-PHYS-GRAVITY-GRAVITON-POLARIZATION-003`; `SFT-PHYS-SYMMETRIC-SOURCE-CONSERVATION-TERMINAL-010` | Four generated coordinate labels, quarter-One depth-two support, rank two, ten symmetric component slots, four conservation ledgers and the tensor polarization boundary are all independently admitted. |
| V2 Step 241 | `SFT-PHYS-DYNAMICS-FREE-PHASE-DISPERSION-003`; `SFT-PHYS-STRONG-CARRIER-MASSLESS-CONFINED-TERMINAL-013` | Empty mass/rest-capture, exact One-cell-per-tick phase advance and retained phase jointly close the massless, One-speed and dispersion-free structural carrier; PDG theory/measurement limits and the lack of direct free-gluon time-of-flight evidence remain explicit. |
| V2 Step 251 | `SFT-FOUNDATION-FOLD-DYNAMICS-001`; `SFT-PHYS-ATOMIC-TRANSITION-SELECTION-004`; `SFT-PHYS-ATOMIC-FIELD-SPLITTING-TERMINAL-005` | The half-One fibre supplies the quarter/three-quarter pair and exact recomposition; the terminal field law forces `2J+1` magnetic classes, symmetric adjacent Zeeman spacing and the complete post-seal NIST field-splitting comparison. |

## Receipt boundary

All mapped terminal claims are already `depth_independent`, independently
recomputed, hostile-control tested and model-admitted. This reconciliation is
therefore an audit of ledger lag. It does not create scientific authority and
cannot close any row whose mapped receipt is absent.
