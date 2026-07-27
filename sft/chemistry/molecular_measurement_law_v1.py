"""Fold-native molecular quantum-state measurement-reduction law."""
from __future__ import annotations
from dataclasses import dataclass
from sft.engine.exact import HeldLabel,InadmissibleExactValue
from sft.physics.generated_empirical_law import LawDimension,dimension
@dataclass(frozen=True)
class MolecularObservationMap:
 prepared_state:HeldLabel
 probe_class:HeldLabel
 retained_coordinates:tuple[HeldLabel,...]
 closed_coordinates:tuple[HeldLabel,...]
 outcome_record:HeldLabel
 post_observation_state:HeldLabel
 instrument:HeldLabel
 condition:HeldLabel
 def __post_init__(self):
  expected=((self.prepared_state,"prepared-molecular-state"),(self.probe_class,"molecular-observation-class"),(self.outcome_record,"molecular-readout-record"),(self.post_observation_state,"post-observation-molecular-state"),(self.instrument,"measurement-instrument"),(self.condition,"measurement-condition"))
  if any(x.family!=family for x,family in expected):raise InadmissibleExactValue("observation boundary lost a required held family")
  if not self.retained_coordinates:raise InadmissibleExactValue("an observation must retain at least one declared coordinate")
  if any(x.family!="retained-molecular-coordinate" for x in self.retained_coordinates) or any(x.family!="closed-molecular-coordinate" for x in self.closed_coordinates):raise InadmissibleExactValue("retained and closed coordinates require distinct families")
  if {x.label for x in self.retained_coordinates}&{x.label for x in self.closed_coordinates}:raise InadmissibleExactValue("one coordinate cannot be both retained and closed")
 def reconstructs(self,coordinate:str)->bool:return coordinate in {x.label for x in self.retained_coordinates}
DEPENDENCIES=("SFT-FOUNDATION-FORM-ENFORCEMENT-001","SFT-MATH-DISCRETE-001","SFT-INFO-SYMBOL-DISTINCTION-001","SFT-INFO-CONSERVATION-LOSS-001","SFT-COMP-FORM-STATE-TRANSITION-001","SFT-QUANTUM-MEASUREMENT-001","SFT-CHEM-MOLECULAR-STATE-TRANSITION-009","SFT-CHEM-RESOLVED-ROVIBRONIC-SPIN-COMPOSITION-013")
DIMENSIONS:tuple[LawDimension,...]=(
 dimension("preparation","outcome-without-prepared-state","An outcome alone cannot identify the state presented to the probe.","retained-pre-observation-state","Every observation begins with one held prepared state."),
 dimension("probe","stochastic-collapse-premise","A stochastic collapse postulate imports an ungenerated law and numerical probability.","exact-generated-observation-class","The probe is one exact generated observation class."),
 dimension("retention","all-or-nothing-observation","All-or-nothing readout hides which distinctions survive.","explicit-retained-coordinate-set","Every surviving coordinate is named in the record."),
 dimension("closure","silent-predecessor-erasure","Silent erasure makes later reconstruction claims untestable.","explicit-closed-coordinate-set","Every distinction closed by observation is separately named."),
 dimension("record","unrecorded-measurement-result","A result without a retained record cannot be repeated or audited.","retained-finite-readout-record","Each readout has one exact held record."),
 dimension("poststate","undefined-or-destroyed-poststate","An undefined post-state breaks process composition.","retained-post-observation-state","Observation ends in one declared molecular state."),
 dimension("reconstruction","recover-unrecorded-predecessor","A merged predecessor cannot be recovered without a retained distinction.","record-bounded-reconstruction","Only coordinates carried by the record reconstruct."),
 dimension("replication","selected-successful-readouts","Successful readouts alone erase failures and state changes.","complete-repeat-and-adverse-record","Every preparation, readout, recovery, failure and boundary row remains."),
)
def _witnesses():
 m=MolecularObservationMap(HeldLabel("prepared-molecular-state","CaH-J-one"),HeldLabel("molecular-observation-class","quantum-logic-projection"),(HeldLabel("retained-molecular-coordinate","rotational-manifold"),),(HeldLabel("closed-molecular-coordinate","unrecorded-pre-probe-path"),),HeldLabel("molecular-readout-record","atomic-fluorescence-record"),HeldLabel("post-observation-molecular-state","CaH-J-one-reprojected"),HeldLabel("measurement-instrument","Ca-plus-logic-ion"),HeldLabel("measurement-condition","registered-trap-condition"));bad=False
 try:MolecularObservationMap(m.prepared_state,m.probe_class,m.retained_coordinates,(HeldLabel("closed-molecular-coordinate","rotational-manifold"),),m.outcome_record,m.post_observation_state,m.instrument,m.condition)
 except InadmissibleExactValue:bad=True
 return (("retained-reconstruction","A recorded rotational manifold reconstructs.",m.reconstructs("rotational-manifold")),("closed-boundary","An unrecorded predecessor path does not reconstruct.",not m.reconstructs("unrecorded-pre-probe-path")),("overlap-control","Retained/closed overlap rejects.",bad))
OPERATIONAL_WITNESSES=_witnesses()
EXACT_RESULT="retained-pre-observation-state__exact-generated-observation-class__explicit-retained-coordinate-set__explicit-closed-coordinate-set__retained-finite-readout-record__retained-post-observation-state__record-bounded-reconstruction__complete-repeat-and-adverse-record"
__all__=("DEPENDENCIES","DIMENSIONS","EXACT_RESULT","MolecularObservationMap","OPERATIONAL_WITNESSES")
