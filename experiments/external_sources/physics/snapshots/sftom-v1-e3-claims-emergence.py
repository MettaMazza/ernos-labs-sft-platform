"""Emergence registry (Part B). Each result tagged THM (proved, exact) or OBS (measured,
parameter-specific). No OBS is dressed as a theorem. All built in the permitted language;
the no-apparatus gate scans these files too. Results are what the system produces — not
claims about physical phenomena."""
from fractions import Fraction
from ratio import ONE
import beats as B, density as D, aggregate as A, modulation as Md
import amplitude as Amp

def e_lcm():
    # THM: two purely-periodic parts run together return at the lcm of their periods
    cases=[(Fraction(1,3),Fraction(1,5)),(Fraction(1,7),Fraction(1,5)),(Fraction(1,7),Fraction(1,9)),(Fraction(1,11),Fraction(1,5))]
    for a,b in cases:
        pa,pb=B.period(a),B.period(b)
        if B.combined_period([a,b])!=B.lcm(pa,pb): return False
    return True
def e_dyadic_collapse():
    # THM: a power-of-two lattice is all-dyadic and folds into a single region (the One)
    occ=D.occupancy(D.even_lattice(256),20,8)
    return occ[0]==256 and not any(occ[1:])      # all other regions empty (tally falsy)
def e_oddspread():
    # OBS: an odd-denominator lattice spreads across all regions (measured)
    occ=D.occupancy(D.even_lattice(255),12,8)
    return all(occ)                              # every region occupied (tally truthy)
def e_threshold_clustering():
    # OBS: under the pairwise coupled fold the ensemble collapses to one region at g=1/2
    base=[Fraction(i,21) for i in range(1,21)]
    pts=list(base)
    for _ in range(15): pts=A.step(pts,Fraction(1,2))
    return A.occupied_regions(pts,12)==1


def e_modulation_periodic():
    # THM: the separation sequence of two interlocking streams repeats with the beat period
    from fractions import Fraction as F
    return all(Md.is_periodic_with_beat(a,b) for a,b in
               ((F(1,7),F(1,5)),(F(1,9),F(1,5)),(F(1,11),F(1,7))))
def e_modulation_profile():
    # OBS: over the beat period the separation visits both 'together' and 'opposed' states
    from fractions import Fraction as F
    L,seq,tog,opp=Md.profile(F(1,7),F(1,5))
    return bool(tog) and bool(opp)


def e_conservation():
    # A1: total presence of a superposition = sum of source totals (positive combination)
    import random; random.seed(1)
    from fractions import Fraction as F
    for _ in range(120):
        a=F(random.randint(1,20),random.randint(21,40)); b=F(random.randint(1,20),random.randint(21,40))
        oa=Amp.occupancy(Amp.orbit(a,15),8); ob=Amp.occupancy(Amp.orbit(b,15),8)
        if Amp.total_presence(Amp.superpose(oa,ob))!=Amp.total_presence(oa)+Amp.total_presence(ob): return False
    return True
def e_interference_contrast():
    # A2: superposition produces high-presence regions and gaps (positive contrast)
    from fractions import Fraction as F
    S=Amp.superpose(Amp.occupancy(Amp.orbit(F(1,7),24),12), Amp.occupancy(Amp.orbit(F(1,5),24),12))
    return max(S)>min(S)

CLAIMS=[
 ("E1","THM","interlocking exact cycles: two periodic parts return at the lcm of their periods (beat period)","RB1",e_lcm),
 ("E2","THM","a power-of-two lattice is all-dyadic and folds into the single region of the One","RB2",e_dyadic_collapse),
 ("E3","OBS","an odd-denominator lattice folds to occupancy across all regions (the even whole) — measured","measured",e_oddspread),
 ("E4","OBS","under the pairwise coupled fold the ensemble collapses to one region at g = the half-One — measured","measured",e_threshold_clustering),
 ("E5","THM","two interlocking streams give a separation-modulation periodic with the beat period","RB3",e_modulation_periodic),
 ("E6","OBS","over the beat period the separation visits both together (near unison) and opposed (near the half-One) states — measured","measured",e_modulation_profile),
 ("A1","THM","superposition conserves total presence: total(superpose(A,B)) = total(A)+total(B), positive combination, no cancellation","A1",e_conservation),
 ("A2","OBS","interference as density contrast: superposed sources give high-presence regions and gaps (positive magnitudes, no negative cancellation) — measured","measured",e_interference_contrast),
]
