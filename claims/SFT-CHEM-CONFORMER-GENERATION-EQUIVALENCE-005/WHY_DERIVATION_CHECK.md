# Exact finite conformer generation and equivalence law

Claim: `SFT-CHEM-CONFORMER-GENERATION-EQUIVALENCE-005`  
Chemistry obligation: `SFT-CHEM-OBL-ORG-005`

## WHY

A conformer census cannot be admitted by selecting familiar conformer names, clustering coordinates with a tolerance, or taking an energy program's returned minima as the generator. ORG-005 derives the finite generation and equivalence algorithm first.

## DERIVATION

The eight-axis grammar exhausts 256 forms and leaves exactly one survivor:

`complete-finite-molecular-graph__complete-ordered-rotor-census__complete-cartesian-state-generation__exhaustive-graph-automorphism-action__exact-automorphism-orbit-equivalence__complete-disjoint-orbit-quotient__value-free-operational-census-seal__finite-product-successor-no-extra-rule`

For any positive finite connected atom-labelled graph, every ordered four-site rotor and every held torsion state are retained. The exact Cartesian product generates each multi-rotor assignment once. Every atom-type and bond-preserving position bijection is then exhaustively generated. These bijections induce exact rotor-state actions, and their disjoint orbits—not coordinate distances or energy tolerances—are the conformer equivalence classes.

The four-site witness generates three raw states: anti, gauche-forward and gauche-reverse. The complete path automorphism census contains identity and reversal. Anti is a one-member orbit; the opposed gauche states form one two-member orbit. Thus three assignments force exactly two conformer classes, with every assignment occurring once. Appending a rotor takes the exact finite product and repeats the same automorphism quotient, proving the algorithm at every positive finite graph/state boundary.

## CHECK

All four frozen external records were already development-observed and are disclosed as such; ORG-005 makes no unknown-target blind-prediction claim. The complete IUPAC records preserve single-bond rotational interconversion, distinct potential-energy minima and comparative conformational analysis.

The complete NIST page returns butane with `Anti` and `Gauche` as the two configuration labels, exactly matching the two derived equivalence classes. Its Anti configuration is marked `True`; the Gauche row is marked `False` and remains preserved as adverse evidence, while the same complete page retains a cited experimental gauche-butane conformer record. Its `16.6 kJ mol⁻¹` internal-rotation barrier is downstream evidence only and never selects generation or equivalence.

All 19 scientific tables and 105 rows are retained, including signed enthalpies, conventional zeros, absent cells, the adverse row and every reference. An implementation-distinct standard-library checker regenerates all 256 law candidates and independently reconstructs the three assignments, two graph actions and two orbit classes without importing SFT modules or reading external results.

## FALSIFICATION

The claim fails if an atom, bond, rotor, held state, Cartesian assignment or preserving graph bijection is omitted; if equivalence uses a coordinate tolerance or measured energy; if any assignment occurs in no class or more than one class; if the four-site witness does not generate three assignments, two graph actions and two classes of sizes one and two; if any of four authority records or any of the 19 tables and 105 CCCBDB rows is omitted; if Anti/Gauche is selected rather than compared after derivation; or if the adverse Gauche false-minimum row, signed values, conventional zeros or absent cells are erased.

## BOUNDARY

The algorithm is depth-independent for positive finite molecular graphs, rotors and held state alphabets. The external census is finite-complete for all four frozen sources. ORG-006 separately owns torsional energy profiles and barrier ordering.
