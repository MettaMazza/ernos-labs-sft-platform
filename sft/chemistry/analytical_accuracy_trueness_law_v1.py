"""Fold-native analytical accuracy and trueness law (ANAL-001)."""
from dataclasses import dataclass
from fractions import Fraction
from sft.claim_evidence import EMPTY_ONE
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import dimension

@dataclass(frozen=True)
class ReferenceComparison:
    measurand: HeldLabel; method: HeldLabel; observed: Fraction; reference: Fraction; rank: PositiveCount
    def __post_init__(self):
        if (self.measurand.family,self.method.family)!=("measurand","analytical-method") or self.observed <= 0 or self.reference <= 0: raise InadmissibleExactValue("positive held comparison required")
    @property
    def discrepancy(self):
        if self.observed == self.reference: return EMPTY_ONE
        return (HeldLabel("comparison-side", "above" if self.observed > self.reference else "below"), abs(self.observed-self.reference))

def comparison_record(rows):
    if not rows or tuple(x.rank.value for x in rows)!=tuple(range(1,len(rows)+1)) or len({(x.measurand,x.method) for x in rows})!=1: raise InadmissibleExactValue("complete ordered traceable comparison required")
    return tuple((x.observed,x.reference,x.discrepancy) for x in rows)

DEPENDENCIES=("SFT-FOUNDATION-FORM-ENFORCEMENT-001","SFT-MATH-EXACT-ARITHMETIC-001","SFT-CHEM-MEAS-UNCERTAINTY-001","SFT-CHEM-MEAS-TRACEABILITY-001","SFT-CHEM-ANALYTICAL-SAMPLE-001","SFT-CHEM-ANALYTICAL-CALIBRATION-001")
DIMENSIONS=(
 dimension("reference","nominal-value-premise","A name is not a reference.","traceable-reference-identity","Reference identity and provenance remain held."),
 dimension("measurand","result-without-measurand","No comparison identity exists.","held-sample-measurand-method","Sample, measurand and method remain."),
 dimension("support","selected-result","Selection hides variation.","complete-ordered-result-support","Every registered result remains."),
 dimension("comparison","signed-error-scalar","A sign is not a native proof value.","held-side-positive-distance-or-EmptyOne","Discrepancy is side plus positive distance or coincidence."),
 dimension("trueness","declared-accurate-label","A label cannot force trueness.","exact-observed-reference-relation","The relation is recomputed from exact values."),
 dimension("uncertainty","single-certain-value","Alternatives are hidden.","complete-exact-uncertainty-support","Every registered uncertainty bound remains."),
 dimension("boundary","universal-method-accuracy","Accuracy is method and material bound.","registered-material-method-boundary","The comparison domain remains explicit."),
 dimension("extension","renormalized-new-results","Renormalization erases custody.","successor-retains-and-recomputes-all-results","Every successor retains and recomputes."),)
EXACT_RESULT="traceable-reference-identity__held-sample-measurand-method__complete-ordered-result-support__held-side-positive-distance-or-EmptyOne__exact-observed-reference-relation__complete-exact-uncertainty-support__registered-material-method-boundary__successor-retains-and-recomputes-all-results"
_m=HeldLabel("measurand","analyte-a");_a=HeldLabel("analytical-method","method-a");_r=(ReferenceComparison(_m,_a,Fraction(101,10),Fraction(10),PositiveCount(1)),ReferenceComparison(_m,_a,Fraction(10),Fraction(10),PositiveCount(2)))
OPERATIONAL_WITNESSES=(("reference","Reference positive.",_r[0].reference==10),("measurand","Identity held.",_r[0].measurand==_m),("support","Rows ordered.",tuple(x.rank.value for x in _r)==(1,2)),("comparison","Side and distance exact.",_r[0].discrepancy[1]==Fraction(1,10)),("trueness","Coincidence structural.",_r[1].discrepancy==EMPTY_ONE),("uncertainty","Exact values retained.",all(isinstance(x.observed,Fraction) for x in _r)),("boundary","Method held.",len({x.method for x in _r})==1),("successor","Complete record retained.",len(comparison_record(_r))==2))
