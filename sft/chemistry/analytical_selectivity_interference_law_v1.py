"""Fold-native analytical selectivity and interference-matrix law (ANAL-005)."""
from fractions import Fraction
from sft.claim_evidence import EMPTY_ONE
from sft.engine.exact import HeldLabel, InadmissibleExactValue
from sft.physics.generated_empirical_law import dimension

def interference_matrix(analyte,method,condition,analyte_only,rows):
    if (analyte.family,method.family,condition.family)!=("analyte","analytical-method","analytical-condition") or analyte_only<=0 or not rows or any(i.family!="interferent" or pure<=0 or mixed<=0 for i,pure,mixed in rows): raise InadmissibleExactValue("complete positive interference matrix required")
    if len({i for i,_,_ in rows})!=len(rows): raise InadmissibleExactValue("interferent identities must be distinct")
    return tuple((i,EMPTY_ONE if mixed==analyte_only else (HeldLabel("interference-side","raises" if mixed>analyte_only else "lowers"),abs(mixed-analyte_only)),Fraction(mixed,analyte_only),pure) for i,pure,mixed in rows)

DEPENDENCIES=("SFT-FOUNDATION-FORM-ENFORCEMENT-001","SFT-MATH-EXACT-ARITHMETIC-001","SFT-CHEM-ANALYTICAL-SELECTIVITY-001","SFT-CHEM-ANALYTICAL-SENSITIVITY-003","SFT-CHEM-ANALYTICAL-DETECTION-QUANTIFICATION-004")
DIMENSIONS=(
 dimension("identity","response-without-analyte","No target is attributable.","held-analyte-method-condition","Analyte and domain remain held."),
 dimension("matrix","selected-interferent","Selection can hide interference.","complete-declared-interferent-matrix","Every tested component remains."),
 dimension("baselines","mixture-only-result","Attribution is impossible.","analyte-and-interferent-baselines-held","Pure-component responses remain."),
 dimension("mixtures","accepted-mixtures-only","Adverse mixtures disappear.","all-analyte-interferent-mixtures-held","Every mixture response remains."),
 dimension("comparison","signed-bias-scalar","A sign alone loses response custody.","held-side-positive-distance-or-EmptyOne","Interference is side plus positive distance or coincidence."),
 dimension("selectivity","universal-specificity-label","Selectivity is method-bound.","exact-response-distinguishability-class","Every interferent receives an exact class."),
 dimension("adverse","false-positive-rows-erased","Erasure inflates selectivity.","favorable-adverse-error-rows-retained","All outcomes remain."),
 dimension("extension","matrix-renormalized","Prior comparisons disappear.","successor-retains-and-adds-interferent","New components extend the complete matrix."),)
EXACT_RESULT="held-analyte-method-condition__complete-declared-interferent-matrix__analyte-and-interferent-baselines-held__all-analyte-interferent-mixtures-held__held-side-positive-distance-or-EmptyOne__exact-response-distinguishability-class__favorable-adverse-error-rows-retained__successor-retains-and-adds-interferent"
_a=HeldLabel("analyte","a");_m=HeldLabel("analytical-method","m");_c=HeldLabel("analytical-condition","c");_r=((HeldLabel("interferent","i1"),Fraction(1),Fraction(5)),(HeldLabel("interferent","i2"),Fraction(2),Fraction(6)));_x=interference_matrix(_a,_m,_c,Fraction(5),_r)
OPERATIONAL_WITNESSES=(("identity","Analyte held.",_a.label=="a"),("matrix","Two interferents retained.",len(_x)==2),("baselines","Pure rows positive.",tuple(x[3] for x in _x)==(1,2)),("mixtures","Mixtures retained.",tuple(x[2] for x in _x)==(1,Fraction(6,5))),("comparison","Coincidence structural.",_x[0][1]==EMPTY_ONE),("selectivity","Second row raises.",_x[1][1][0].label=="raises"),("adverse","Adverse row retained.",_x[1][1][1]==1),("extension","Matrix extends.",len(interference_matrix(_a,_m,_c,Fraction(5),_r+((HeldLabel("interferent","i3"),Fraction(1),Fraction(4)),)))==3))
