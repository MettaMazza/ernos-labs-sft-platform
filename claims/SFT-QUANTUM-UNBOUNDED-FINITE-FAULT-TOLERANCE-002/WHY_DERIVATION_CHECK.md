# Unbounded finite Fold quantum fault-tolerance law

Claim: `SFT-QUANTUM-UNBOUNDED-FINITE-FAULT-TOLERANCE-002`

## WHY

V2 Step 407 closes the fault-order frontier for every supplied positive finite
allowance. A table at orders one, two and three is insufficient; the result
requires a constructive first-survivor proof, a counterexample for every
shorter width and an exact successor certificate.

## DERIVATION

For fault order `t`, no more than `t` encoded labels may change. Strict
majority therefore requires more than `t` retained source labels. The least
carrier has `t` possible changes plus `t+1` retained labels, hence width
`2t+1`. Every predecessor width `w <= 2t` is defeated by changing
`ceil(w/2)` labels, producing a tie or wrong majority. Replacing `t` by its
next generated order adds exactly two carrier positions. The construction
therefore defeats every proposed fixed positive finite ceiling without
creating a completed infinite-width code.

The eight-axis grammar contains 256 candidates and one all-preserving member.
The executed check enumerates every mask for both labels at fault orders one,
two and three; all predecessor-width counterexamples and successor rows through
order fourteen; and all 128 depth-seven source words at order fourteen before
the recovered word enters exact Fold circuit semantics.

## CHECK AND BOUNDARY

The implementation-distinct validator regenerates the candidate product and
the operational witnesses. This is an unbounded positive-finite code and
fault-order theorem. It is not a measured stochastic hardware-error rate,
physical threshold constant, correlated-noise model or device guarantee.
Those empirical quantities require separately sealed Physics and engineering
claims and cannot select this formal survivor.

