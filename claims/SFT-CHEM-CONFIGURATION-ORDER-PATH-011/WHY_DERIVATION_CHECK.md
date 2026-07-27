# Exact molecular configuration order, basin, barrier and path law

Claim: `SFT-CHEM-CONFIGURATION-ORDER-PATH-011`  
Chemistry obligation: `SFT-CHEM-OBL-ELEC-011`

## WHY

The molecular state and transition laws do not yet order nuclear configurations into stable basins, transition configurations and complete paths. ELEC-011 derives that order without assuming a real continuum, a potential-energy function, a differential equation or a fitted coefficient. There is no numerical zero: a measured least-energy inscription is represented natively as structural `EmptyOne`.

## DERIVATION

One molecular carrier generates exact configuration nodes and adjacency edges. Every node retains its coordinate, exact positive height above the least coordinate or `EmptyOne`, and record. Complete neighbour order alone forces local minima and barriers. Appending one adjacent node gives every positive finite path; completion of a periodic generator identifies the terminal configuration with its initial class.

The eight-axis grammar contains 256 forms and exactly one survivor:

`retained-molecular-carrier__generated-configuration-nodes__exact-positive-order-or-EmptyOne__local-minimum-by-complete-neighbours__local-barrier-by-complete-neighbours__connected-complete-configuration-path__exact-periodic-endpoint-identity__complete-favourable-and-adverse-vector`

Base: One retained configuration node has one carrier, coordinate, exact positive height or structural EmptyOne and source record; three connected nodes decide one internal basin or barrier by complete neighbour comparison.

Successor: Appending one adjacent configuration extends the finite path and exposes exactly one new complete-neighbour comparison without changing any prior node, order or record; a complete period identifies the terminal class with the initial class.

## CHECK

After the law is sealed, an independent parser reconstructs every row of both NIST CCCBDB experimental ethanol internal-rotation paths: 50 measured coordinates, 46 positive energy inscriptions and four least-energy inscriptions represented as `EmptyOne`. Circular complete-neighbour comparison yields six basins, six barriers and 36 ordinary nodes; two terminal rows reproduce their initial periodic configuration and height. Both energy-unit columns are retained, and no extrema-only subset is accepted.

## FALSIFICATION

The claim fails if a configuration loses its carrier, coordinate, exact order or record; if a claimed basin or barrier fails complete-neighbour comparison; if a path skips a registered adjacent configuration; if a periodic endpoint fails identity and height recurrence; if source absence is numerical; or if any of 50 NIST rows, 46 positive energy inscriptions, four structural least-energy coordinates, six basins, six barriers, 36 ordinary path nodes or two recurrence duplicates is omitted or changed.
