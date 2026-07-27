"""Fold-native oxidative-addition/reductive-elimination correspondence (INORG-012)."""
from __future__ import annotations
from dataclasses import dataclass
from sft.engine.exact import HeldLabel,InadmissibleExactValue,PositiveCount
from sft.physics.generated_empirical_law import LawDimension,dimension

@dataclass(frozen=True)
class ExactOxidativeAdditionTrace:
    metal_occurrences: tuple[HeldLabel,...]
    transferred_carriers: tuple[HeldLabel,HeldLabel]
    source_bond: tuple[HeldLabel,HeldLabel]
    product_incidences: tuple[tuple[HeldLabel,HeldLabel],tuple[HeldLabel,HeldLabel]]
    transfer_distribution: tuple[PositiveCount,...]
    held_direction: HeldLabel
    def __post_init__(self):
        if len(self.metal_occurrences) not in {1,2} or any(x.family!="metal-occurrence" for x in self.metal_occurrences): raise InadmissibleExactValue("oxidative addition requires one or two retained metal occurrences")
        if any(x.family!="transferred-carrier" for x in self.transferred_carriers) or len(set(self.transferred_carriers))!=2: raise InadmissibleExactValue("two distinct transferred carriers must be retained")
        if self.source_bond!=self.transferred_carriers: raise InadmissibleExactValue("source covalent bond must retain both transferred carriers")
        if tuple(x[1] for x in self.product_incidences)!=self.transferred_carriers: raise InadmissibleExactValue("product incidences must conserve both transferred carriers")
        if any(x[0] not in self.metal_occurrences for x in self.product_incidences): raise InadmissibleExactValue("product incidence loses its retained metal")
        expected=(2,) if len(self.metal_occurrences)==1 else (1,1)
        if tuple(x.value for x in self.transfer_distribution)!=expected: raise InadmissibleExactValue("transfer distribution must be exact two on one metal or one on each of two")
        if self.held_direction!=HeldLabel("electron-transfer-orientation","metal-support-to-two-new-incidences"): raise InadmissibleExactValue("electron transfer orientation must remain held")

@dataclass(frozen=True)
class ExactReductiveEliminationTrace:
    oxidative_trace: ExactOxidativeAdditionTrace
    restored_bond: tuple[HeldLabel,HeldLabel]
    removed_product_incidences: tuple[tuple[HeldLabel,HeldLabel],tuple[HeldLabel,HeldLabel]]
    held_direction: HeldLabel
    def __post_init__(self):
        if self.restored_bond!=self.oxidative_trace.source_bond or self.removed_product_incidences!=self.oxidative_trace.product_incidences: raise InadmissibleExactValue("reductive elimination must exactly reverse the registered oxidative trace")
        if self.held_direction!=HeldLabel("electron-transfer-orientation","two-incidences-to-metal-support"): raise InadmissibleExactValue("reverse transfer orientation must remain held")

def oxidative_addition(metals:tuple[str,...],x:str,y:str)->ExactOxidativeAdditionTrace:
    ms=tuple(HeldLabel("metal-occurrence",m) for m in metals); carriers=(HeldLabel("transferred-carrier",x),HeldLabel("transferred-carrier",y))
    if len(ms)==1: products=((ms[0],carriers[0]),(ms[0],carriers[1])); distribution=(PositiveCount(2),)
    elif len(ms)==2: products=((ms[0],carriers[0]),(ms[1],carriers[1])); distribution=(PositiveCount(1),PositiveCount(1))
    else: raise InadmissibleExactValue("only the structurally generated one- and two-metal partitions are admissible")
    return ExactOxidativeAdditionTrace(ms,carriers,carriers,products,distribution,HeldLabel("electron-transfer-orientation","metal-support-to-two-new-incidences"))

def reductive_elimination(trace:ExactOxidativeAdditionTrace)->ExactReductiveEliminationTrace:
    return ExactReductiveEliminationTrace(trace,trace.source_bond,trace.product_incidences,HeldLabel("electron-transfer-orientation","two-incidences-to-metal-support"))

DEPENDENCIES=("SFT-FOUNDATION-FORM-ENFORCEMENT-001","SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001","SFT-MATH-EXACT-ARITHMETIC-001","SFT-MATH-DISCRETE-001","SFT-MATH-COMBINATORICS-001","SFT-MATH-GRAPH-NETWORK-001","SFT-INFO-SYMBOL-DISTINCTION-001","SFT-INFO-CONSERVATION-LOSS-001","SFT-COMP-FORM-STATE-TRANSITION-001","SFT-CHEM-STOICH-CONSERVATION-001","SFT-CHEM-BOND-COVALENT-001","SFT-CHEM-RXN-IDENTITY-001","SFT-CHEM-RXN-MECHANISM-001","SFT-CHEM-ORGANOMETALLIC-METAL-CARBON-BOND-010","SFT-CHEM-ORGANOMETALLIC-ELECTRON-ACCOUNTING-011")
DIMENSIONS:tuple[LawDimension,...]=(
 dimension("carrier","anonymous-reaction-name","A name loses the process carrier.","one-retained-organometallic-process","One process retains source and product states."),
 dimension("source","selected-reactant-fragments","Selected fragments lose the complete covalent source bond.","complete-two-carrier-source-bond","The source retains both distinct carriers and their bond."),
 dimension("product","asserted-oxidation-state-change","A signed oxidation-state change is not a topology.","two-generated-metal-carrier-incidences","Oxidative addition replaces the source bond by two retained incidences."),
 dimension("conservation","formal-charge-bookkeeping","Formal charge bookkeeping can lose occurrences.","exact-carrier-and-metal-conservation","Every metal and transferred carrier occurrence is preserved."),
 dimension("transfer","signed-electron-loss","Signed loss imports negative proof values.","held-two-electron-transfer-orientation","Transfer is an exact positive count with a held direction."),
 dimension("partition","single-conventional-mechanism","One conventional mechanism omits the split-metal form.","complete-one-metal-two-or-two-metal-one-one-partition","The exact transfer partitions are two on one or one on each of two."),
 dimension("reverse","separate-reductive-rule","A separate rule need not invert the process.","exact-reductive-inverse-correspondence","Reductive elimination exactly reverses bond and incidence changes."),
 dimension("extension","species-specific-exception","An exception destroys zero-parameter closure.","trace-composition-with-no-extra-rule","Traces compose by preserved endpoints and occurrences."),
)
def _witnesses():
 one=oxidative_addition(("M",),"X","Y"); two=oxidative_addition(("M1","M2"),"X","Y"); reverse=reductive_elimination(one); bad=False
 try: oxidative_addition(("M1","M2","M3"),"X","Y")
 except InadmissibleExactValue: bad=True
 return (("single-metal","One metal forces transfer distribution two.",tuple(x.value for x in one.transfer_distribution)==(2,)),("two-metal","Two metals force transfer distribution one and one.",tuple(x.value for x in two.transfer_distribution)==(1,1)),("exact-reverse","Reductive elimination restores the exact source bond.",reverse.restored_bond==one.source_bond),("partition-control","A third metal rejects.",bad))
OPERATIONAL_WITNESSES=_witnesses()
EXACT_RESULT="one-retained-organometallic-process__complete-two-carrier-source-bond__two-generated-metal-carrier-incidences__exact-carrier-and-metal-conservation__held-two-electron-transfer-orientation__complete-one-metal-two-or-two-metal-one-one-partition__exact-reductive-inverse-correspondence__trace-composition-with-no-extra-rule"
__all__=("DEPENDENCIES","DIMENSIONS","EXACT_RESULT","OPERATIONAL_WITNESSES","ExactOxidativeAdditionTrace","ExactReductiveEliminationTrace","oxidative_addition","reductive_elimination")
