"""B1 — density of states, in the permitted language. An ensemble of ones folded together;
the observable is how many occupy each region of the whole (exact counts). The even whole
folds to even occupancy (the monad); an overlay of two different rational lattices folds to
a structured profile — some regions cluster, some thin. Counts are scaffolding tallies, not
magnitudes; magnitudes stay strictly positive parts of the One."""
from fractions import Fraction
from ratio import fold

def occupancy(starts, folds, regions):
    pts=list(starts)
    for _ in range(folds): pts=[fold(p) for p in pts]
    idxs=[ int(p*regions) % regions for p in pts ]   # region index per point; mod, no subtraction
    return [ sum(1 for ix in idxs if ix==r) for r in range(regions) ]   # tally per region (no zero seed)

def even_lattice(N):  return [Fraction(i,N) for i in range(1,N+1)]

if __name__=="__main__":
    print("power-of-two lattice is all-dyadic: it collapses to the One under folding (exact edge):")
    occ0=occupancy(even_lattice(256), 20, 8)
    print(f"  N=256 (=2^8), 8 regions after 20 folds: {occ0}")
    print("\nodd-denominator lattice folded -> occupancy across regions (orbits stay periodic):")
    occ=occupancy(even_lattice(255), 12, 8)
    print(f"  N=255, 8 regions after 12 folds: {occ}  spread across {sum(1 for c in occ if c)} of 8 regions")
    print("\noverlay of two coprime odd lattices -> structured occupancy:")
    occ2=occupancy(even_lattice(105)+even_lattice(77), 12, 12)
    print(f"  N=105 with N=77, 12 regions after 12 folds: {occ2}")
    print(f"  least-occupied {min(occ2)}, most {max(occ2)}")
