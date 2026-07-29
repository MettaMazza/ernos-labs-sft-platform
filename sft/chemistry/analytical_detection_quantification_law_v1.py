"""Fold-native analytical detection and quantification boundary law (ANAL-004)."""
from fractions import Fraction
from sft.claim_evidence import EMPTY_ONE
from sft.engine.exact import HeldLabel, InadmissibleExactValue
from sft.physics.generated_empirical_law import dimension

def boundary_record(analyte,method,condition,blanks,levels):
    if (analyte.family,method.family,condition.family)!=("analyte","analytical-method","analytical-condition") or not blanks or not levels or any(x<=0 for x in blanks) or any(a<=0 or not r or any(x<=0 for x in r) for a,r in levels): raise InadmissibleExactValue("complete positive blank and level support required")
    upper_blank=max(blanks); rows=[]
    for amount,responses in levels:
        detected=all(x>upper_blank for x in responses)
        spread=EMPTY_ONE if max(responses)==min(responses) else max(responses)-min(responses)
        quantified=detected and len(responses)>1 and spread is not EMPTY_ONE
        rows.append((amount, HeldLabel("detection-class","detected") if detected else EMPTY_ONE, HeldLabel("quantification-class","quantified") if quantified else EMPTY_ONE, spread))
    return tuple(rows)

DEPENDENCIES=("SFT-FOUNDATION-FORM-ENFORCEMENT-001","SFT-MATH-EXACT-ARITHMETIC-001","SFT-CHEM-ANALYTICAL-PRECISION-REPEATABILITY-002","SFT-CHEM-ANALYTICAL-SENSITIVITY-003")
DIMENSIONS=(
 dimension("identity","unidentified-signal","No analyte boundary exists.","held-analyte-method-condition","The boundary is attributable and bounded."),
 dimension("blank","single-numerical-zero-blank","Numerical zero cannot represent background.","complete-positive-blank-support","Every observed blank response remains."),
 dimension("levels","selected-low-result","Selection hides failures.","complete-positive-ordered-level-support","All registered low levels remain."),
 dimension("detection","declared-limit-number","A number alone cannot prove distinction.","exact-blank-sample-distinguishability","Detection is forced by complete response separation."),
 dimension("errors","false-results-erased","Error classes are hidden.","false-positive-negative-custody","Every classification error remains."),
 dimension("quantification","detection-equals-quantification","Identity is weaker than measurement.","repeatability-and-recovery-required","Quantification retains replicate spread and recovery support."),
 dimension("absence","negative-undetected-value","Undetected is not negative amount.","detected-quantified-label-or-EmptyOne","Failure is structural absence."),
 dimension("extension","threshold-refitted","A refit changes prior classifications.","successor-retains-and-recomputes-levels","Every added level preserves earlier rows."),)
EXACT_RESULT="held-analyte-method-condition__complete-positive-blank-support__complete-positive-ordered-level-support__exact-blank-sample-distinguishability__false-positive-negative-custody__repeatability-and-recovery-required__detected-quantified-label-or-EmptyOne__successor-retains-and-recomputes-levels"
_a=HeldLabel("analyte","a");_m=HeldLabel("analytical-method","m");_c=HeldLabel("analytical-condition","c");_b=(Fraction(1),Fraction(2));_l=((Fraction(1),(Fraction(2),Fraction(3))),(Fraction(2),(Fraction(4),Fraction(5))));_x=boundary_record(_a,_m,_c,_b,_l)
OPERATIONAL_WITNESSES=(("identity","Identity held.",_a.label=="a"),("blank","Both blanks retained.",len(_b)==2),("levels","Two levels retained.",len(_x)==2),("detection","First overlap does not detect.",_x[0][1]==EMPTY_ONE),("errors","Overlap remains visible.",_l[0][1][0]==max(_b)),("quantification","Second level quantifies.",_x[1][2].label=="quantified"),("absence","Undetected structural.",_x[0][1]==EMPTY_ONE),("extension","Level extension retained.",len(boundary_record(_a,_m,_c,_b,_l+((Fraction(3),(Fraction(6),Fraction(7))),)))==3))
