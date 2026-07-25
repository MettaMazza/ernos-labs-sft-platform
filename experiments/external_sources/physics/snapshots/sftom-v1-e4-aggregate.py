"""B3 — aggregate rule, in the permitted language. Many ones under a pairwise coupled
fold: each one folds (doubles), then is pulled toward its nearest neighbour by a fraction
of the separation, the direction set by ordering (never by a sign). The macro-observable
is how many distinct regions stay occupied — clustering. Measured (OBS); reported as the
system produces it. Magnitudes stay positive parts of the One; counts are scaffolding."""
from fractions import Fraction
from ratio import ONE, fold, take, cast_out, separation

def nearest(p, others):
    best=None; bestsep=None
    for q in others:
        if q==p: continue
        sgap=separation(p,q)
        if bestsep is None or sgap<bestsep: bestsep=sgap; best=q
    return best, bestsep

def step(points, g):
    """Each one folds, then moves a fraction g toward its nearest neighbour along the
       short arc. 'Toward' is forward by g*sep if the neighbour lies ahead the short way,
       else forward by the complement (One minus g*sep) cast out — never a negative move."""
    folded=[fold(p) for p in points]
    out=[]
    for p in folded:
        q,sgap=nearest(p,folded)
        if q is None: out.append(p); continue
        move=g*sgap
        ahead = cast_out(p+sgap)              # going forward by sep from p
        if ahead==q:
            out.append(cast_out(p+move))      # neighbour is ahead: step forward
        else:
            out.append(cast_out(p+take(ONE,move)))  # neighbour is behind: forward by complement
    return out

def occupied_regions(points, regions):
    seen=set()
    for p in points:
        seen.add(int(p*regions) % regions)
    return len(seen)

if __name__=="__main__":
    base=[Fraction(i,21) for i in range(1,21)]    # 20 ones, odd denominator
    print("ones = 20; regions = 12; clustering (occupied regions) after 15 coupled folds:")
    for g in (Fraction(1,10),Fraction(1,3),Fraction(1,2),Fraction(7,10),Fraction(9,10)):
        pts=list(base)
        for _ in range(15): pts=step(pts,g)
        print(f"  g={g} ({float(g):.2f}): occupied regions = {occupied_regions(pts,12)}")
