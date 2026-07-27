"""Fold-native resolved vibronic, rovibronic and spin composition law."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Union
from sft.claim_evidence import PositiveRatio
from sft.claim_evidence.fold_language import EmptyOne
from sft.engine.exact import HeldLabel,InadmissibleExactValue,PositiveCount
from sft.physics.generated_empirical_law import LawDimension,dimension
ExactCoordinate=Union[PositiveRatio,EmptyOne]
@dataclass(frozen=True)
class ResolvedRovibronicState:
 carrier:HeldLabel
 isotope_support:tuple[HeldLabel,...]
 electronic_state:HeldLabel
 spin_multiplicity:PositiveCount
 vibrational_coordinate:ExactCoordinate
 rotational_coordinate:ExactCoordinate
 transition_record:HeldLabel
 source_record:HeldLabel
 def __post_init__(self):
  if self.carrier.family!="molecular-carrier" or not self.isotope_support or any(x.family!="molecular-isotope" for x in self.isotope_support):raise InadmissibleExactValue("resolved state requires carrier and isotope support")
  if self.electronic_state.family!="molecular-electronic-state":raise InadmissibleExactValue("electronic state erased")
  if not isinstance(self.vibrational_coordinate,(PositiveRatio,EmptyOne)) or not isinstance(self.rotational_coordinate,(PositiveRatio,EmptyOne)):raise InadmissibleExactValue("spectral coordinates must be positive exact or EmptyOne")
  if self.transition_record.family!="molecular-transition-record" or self.source_record.family!="resolved-spectrum-record":raise InadmissibleExactValue("resolved records must remain held")
 def joint_key(self):return (self.carrier.label,tuple(x.label for x in self.isotope_support),self.electronic_state.label,self.spin_multiplicity.value,repr(self.vibrational_coordinate),repr(self.rotational_coordinate),self.transition_record.label,self.source_record.label)
DEPENDENCIES=("SFT-FOUNDATION-FORM-ENFORCEMENT-001","SFT-MATH-EXACT-ARITHMETIC-001","SFT-MATH-DISCRETE-001","SFT-INFO-SYMBOL-DISTINCTION-001","SFT-QUANTUM-STATE-COMPOSITION-001","SFT-PHYS-MOLECULAR-SPECTROSCOPY-TERMINAL-005","SFT-CHEM-ROVIBRONIC-COMPOSITION-001","SFT-CHEM-MOLECULAR-STATE-TRANSITION-009","SFT-CHEM-SELECTION-RULE-STRUCTURE-010","SFT-CHEM-NUCLEAR-ELECTRONIC-COMPOSITION-012")
DIMENSIONS:tuple[LawDimension,...]=(
 dimension("carrier","detached-spectral-row","A row detached from its molecule is not a chemical state.","retained-molecular-and-isotope-carrier","Every coordinate remains bound to one isotopologue carrier."),
 dimension("electronic","transition-name-without-electronic-state","A transition name alone erases its endpoint state.","retained-electronic-state-designation","The full electronic designation remains held."),
 dimension("vibration","continuum-vibration-or-erasure","A continuum coordinate or erasure is not an exact generated state.","positive-vibrational-coordinate-or-EmptyOne","Resolved vibration is exact positive support or structural absence."),
 dimension("rotation","signed-rotation-or-erasure","Signed continuum rotation or erasure loses resolved structure.","positive-rotational-coordinate-or-EmptyOne","Resolved rotation is exact positive support or structural absence."),
 dimension("spin","spin-erased-molecular-state","Erasing multiplicity merges singlet and triplet records.","retained-positive-spin-multiplicity","Every term retains its positive whole multiplicity."),
 dimension("composition","independent-coordinate-list","A list without joint identity permits unlawful recombination.","finite-vibronic-rovibronic-spin-product","All coordinates form one finite joint state."),
 dimension("observation","endpoint-only-transition","Endpoints alone erase the measured transition record and unresolved boundary.","retained-transition-and-band-record","Transition designation and band record remain held, including absence."),
 dimension("record","selected-resolved-lines","Selected lines cannot establish complete resolved composition.","complete-resolved-spectrum-surface","Every registered state row and source cell is retained."),
)
def _witnesses():
 from sft.claim_evidence.fold_language import EMPTY_ONE
 state=ResolvedRovibronicState(HeldLabel("molecular-carrier","H2"),(HeldLabel("molecular-isotope","protium"),HeldLabel("molecular-isotope","protium")),HeldLabel("molecular-electronic-state","X-singlet-sigma-g"),PositiveCount(1),PositiveRatio.from_pair(4401213,1000),PositiveRatio.from_pair(608530,10000),HeldLabel("molecular-transition-record","source-absence"),HeldLabel("resolved-spectrum-record","X-row"))
 bad=False
 try:ResolvedRovibronicState(state.carrier,state.isotope_support,HeldLabel("wrong","X"),PositiveCount(1),EMPTY_ONE,EMPTY_ONE,state.transition_record,state.source_record)
 except InadmissibleExactValue:bad=True
 return (("joint-key","A complete resolved state has one exact joint key.",len(state.joint_key())==8),("spin-positive","Spin multiplicity is a positive whole.",state.spin_multiplicity.value==1),("erasure-control","An erased electronic family rejects.",bad))
OPERATIONAL_WITNESSES=_witnesses()
EXACT_RESULT="retained-molecular-and-isotope-carrier__retained-electronic-state-designation__positive-vibrational-coordinate-or-EmptyOne__positive-rotational-coordinate-or-EmptyOne__retained-positive-spin-multiplicity__finite-vibronic-rovibronic-spin-product__retained-transition-and-band-record__complete-resolved-spectrum-surface"
__all__=("DEPENDENCIES","DIMENSIONS","EXACT_RESULT","OPERATIONAL_WITNESSES","ResolvedRovibronicState")
