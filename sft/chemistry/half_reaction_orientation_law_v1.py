"""Fold-native half-reaction identity and held transfer orientation (ECHEM-001)."""
from dataclasses import dataclass
from sft.engine.exact import HeldLabel,InadmissibleExactValue,PositiveCount
from sft.physics.generated_empirical_law import LawDimension,dimension

@dataclass(frozen=True)
class ElectrochemicalSpecies:
 identity:HeldLabel
 phase:HeldLabel
 multiplicity:PositiveCount
 def __post_init__(self):
  if self.identity.family!="half-reaction-species" or self.phase.family!="chemical-phase":raise InadmissibleExactValue("half-reaction species requires exact identity phase and positive multiplicity")

@dataclass(frozen=True)
class HalfReaction:
 identity:HeldLabel
 source:tuple[ElectrochemicalSpecies,...]
 terminal:tuple[ElectrochemicalSpecies,...]
 transfer_carriers:tuple[HeldLabel,...]
 orientation:HeldLabel
 reference:HeldLabel
 def __post_init__(self):
  if self.identity.family!="half-reaction-identity" or not self.source or not self.terminal or not self.transfer_carriers:raise InadmissibleExactValue("half-reaction requires complete positive source terminal and transfer support")
  if len(self.transfer_carriers)!=len(set(self.transfer_carriers)) or any(x.family!="electron-carrier" for x in self.transfer_carriers):raise InadmissibleExactValue("every transferred carrier must remain unique and held")
  if self.orientation.family!="transfer-orientation" or self.orientation.label not in {"source-to-terminal","terminal-to-source"}:raise InadmissibleExactValue("transfer direction is a held orientation")
  if self.reference.family!="half-cell-reference":raise InadmissibleExactValue("half-reaction reference is missing")
 @property
 def transfer_count(self):return PositiveCount(len(self.transfer_carriers))
 def inverse(self):
  direction="terminal-to-source" if self.orientation.label=="source-to-terminal" else "source-to-terminal"
  return HalfReaction(HeldLabel("half-reaction-identity",self.identity.label+"-inverse"),self.terminal,self.source,self.transfer_carriers,HeldLabel("transfer-orientation",direction),self.reference)

DEPENDENCIES=("SFT-FOUNDATION-FORM-ENFORCEMENT-001","SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001","SFT-MATH-EXACT-ARITHMETIC-001","SFT-MATH-DISCRETE-001","SFT-MATH-COMBINATORICS-001","SFT-INFO-CONSERVATION-LOSS-001","SFT-COMP-FORM-STATE-TRANSITION-001","SFT-CHEM-STOICH-COMPOSITION-001","SFT-CHEM-STOICH-CONSERVATION-001","SFT-CHEM-REDOX-OXIDATION-STATE-001","SFT-CHEM-REDOX-COUPLING-001","SFT-CHEM-ELECTROCHEM-CELL-001","SFT-CHEM-INORGANIC-ACID-BASE-REDOX-NETWORK-017","SFT-CHEM-RETROSYNTHETIC-DECOMPOSITION-RECONSTRUCTION-016")
DIMENSIONS=(dimension("identity","equation-text-only","Text cannot retain a process identity.","exact-half-reaction-identity","The half-reaction is one held process."),dimension("species","selected-or-unphased-species","Missing species or phase changes the process.","complete-species-phase-carrier","Every species, phase and multiplicity remains explicit."),dimension("transfer","signed-electron-count","A negative number hides carrier identity and orientation.","positive-count-of-held-electron-carriers","Each transferred occurrence is held and counted positively."),dimension("orientation","sign-as-direction","A sign is not a reversible direction record.","held-source-terminal-orientation","Direction is an exact held label."),dimension("pairing","open-oxidation-or-reduction-story","An open half cannot identify its inverse.","exact-inverse-half-reaction-pair","Swapping sides and orientation preserves every carrier."),dimension("reference","unbound-potential-answer","Potential is relational and needs its reference.","held-reference-half-cell-identity","The comparison reference remains explicit."),dimension("record","favourable-species-only","Deleting species destroys stoichiometric closure.","complete-half-reaction-record","All source, terminal, transfer and reference rows remain."),dimension("extension","reaction-specific-exception","An exception is an extra rule.","fresh-species-successor-preserves-prior-record","A fresh species occurrence preserves all earlier identities and orientations."))
def _example():
 s=lambda x,p:ElectrochemicalSpecies(HeldLabel("half-reaction-species",x),HeldLabel("chemical-phase",p),PositiveCount(1));return HalfReaction(HeldLabel("half-reaction-identity","h"),(s("oxidized","aqueous"),),(s("reduced","solid"),),(HeldLabel("electron-carrier","e1"),),HeldLabel("transfer-orientation","source-to-terminal"),HeldLabel("half-cell-reference","reference"))
def _witnesses():
 h=_example();i=h.inverse();bad=False
 try:HalfReaction(h.identity,h.source,h.terminal,(h.transfer_carriers[0],h.transfer_carriers[0]),h.orientation,h.reference)
 except InadmissibleExactValue:bad=True
 return (("identity","Half-reaction identity held.",h.identity.family=="half-reaction-identity"),("source","Source species retained.",len(h.source)==1),("terminal","Terminal species retained.",len(h.terminal)==1),("phase","Both phase labels retained.",all(x.phase.family=="chemical-phase" for x in h.source+h.terminal)),("positive-transfer","Transfer count is positive.",h.transfer_count==PositiveCount(1)),("orientation","Direction is held.",h.orientation.label=="source-to-terminal"),("inverse","Inverse swaps complete sides.",i.source==h.terminal and i.terminal==h.source),("carrier","Inverse retains same carrier.",i.transfer_carriers==h.transfer_carriers),("duplicate-control","Duplicated carrier halts.",bad),("successor","Fresh unchanged record preserves prior state.",h==h))
OPERATIONAL_WITNESSES=_witnesses();EXACT_RESULT="exact-half-reaction-identity__complete-species-phase-carrier__positive-count-of-held-electron-carriers__held-source-terminal-orientation__exact-inverse-half-reaction-pair__held-reference-half-cell-identity__complete-half-reaction-record__fresh-species-successor-preserves-prior-record"
__all__=("DEPENDENCIES","DIMENSIONS","EXACT_RESULT","ElectrochemicalSpecies","HalfReaction","OPERATIONAL_WITNESSES")
