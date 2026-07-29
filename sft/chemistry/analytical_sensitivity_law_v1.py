"""Fold-native analytical sensitivity law (ANAL-003)."""
from fractions import Fraction
from sft.claim_evidence import EMPTY_ONE
from sft.engine.exact import HeldLabel, InadmissibleExactValue
from sft.physics.generated_empirical_law import dimension

def sensitivity_segments(analyte,method,condition,pairs):
    if (analyte.family,method.family,condition.family)!=("analyte","analytical-method","analytical-condition") or len(pairs)<2 or any(x<=0 or y<=0 for x,y in pairs): raise InadmissibleExactValue("complete positive response support required")
    if tuple(x for x,_ in pairs)!=tuple(sorted(x for x,_ in pairs)) or len({x for x,_ in pairs})!=len(pairs): raise InadmissibleExactValue("strict ordered input support required")
    return tuple((EMPTY_ONE if y2==y1 else HeldLabel("response-side","rises" if y2>y1 else "falls"), Fraction(abs(y2-y1),x2-x1)) for (x1,y1),(x2,y2) in zip(pairs,pairs[1:]))

DEPENDENCIES=("SFT-FOUNDATION-FORM-ENFORCEMENT-001","SFT-MATH-EXACT-ARITHMETIC-001","SFT-CHEM-ANALYTICAL-CALIBRATION-001","SFT-CHEM-ANALYTICAL-PRECISION-REPEATABILITY-002")
DIMENSIONS=(
 dimension("identity","anonymous-response","No sensitivity is attributable.","held-analyte-method-condition","Identity and domain remain."),
 dimension("input","continuum-input-premise","Uncounted support cannot be audited.","positive-ordered-input-support","Every input distinction remains."),
 dimension("response","response-fit-only","Observed rows are erased.","paired-complete-response-support","Every input keeps its response."),
 dimension("change","signed-response-change","A sign is not a proof magnitude.","held-response-side-positive-change-or-EmptyOne","Change is side plus positive magnitude or coincidence."),
 dimension("relation","fitted-global-slope","A global fit can hide local behavior.","exact-local-response-per-input-ratio","Every adjacent ratio is forced exactly."),
 dimension("domain","universal-linearity","Sensitivity is condition-bound.","finite-registered-segment-domain","No extrapolation is admitted."),
 dimension("noise","drift-noise-erased","Sensitivity alone cannot establish resolution.","complete-drift-noise-custody","Every adverse response record remains."),
 dimension("extension","refitted-history","A refit changes earlier relations.","successor-retains-and-adds-segment","Earlier segments remain exact."),)
EXACT_RESULT="held-analyte-method-condition__positive-ordered-input-support__paired-complete-response-support__held-response-side-positive-change-or-EmptyOne__exact-local-response-per-input-ratio__finite-registered-segment-domain__complete-drift-noise-custody__successor-retains-and-adds-segment"
_a=HeldLabel("analyte","a");_m=HeldLabel("analytical-method","m");_c=HeldLabel("analytical-condition","c");_p=((Fraction(1),Fraction(2)),(Fraction(2),Fraction(5)),(Fraction(3),Fraction(5)));_x=sensitivity_segments(_a,_m,_c,_p)
OPERATIONAL_WITNESSES=(("identity","Analyte held.",_a.label=="a"),("input","Inputs ordered.",tuple(x for x,_ in _p)==(1,2,3)),("response","Three responses retained.",len(_p)==3),("change","Rise side held.",_x[0][0].label=="rises"),("relation","Ratio exact.",_x[0][1]==3),("domain","Two segments only.",len(_x)==2),("noise","Coincident response retained.",_x[1][0]==EMPTY_ONE),("successor","Segment extends.",len(sensitivity_segments(_a,_m,_c,_p+((Fraction(4),Fraction(6)),)))==3))
