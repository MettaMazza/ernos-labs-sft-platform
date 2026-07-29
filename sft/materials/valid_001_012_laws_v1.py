"""Twelve complete validation-vector laws over the frozen Materials surface."""
from dataclasses import dataclass
import json
from pathlib import Path
from sft.engine import ClaimRegistration,EvidenceMode,ROOT_THEOREM
from sft.physics.structural_constants import StructuralPhysicsProgram,StructuralPhysicsSpec,Witness,binary_axis

ROOT=Path(__file__).resolve().parents[2]
REGISTRY_PATH=ROOT/"census/materials_valid_001_012_dependency_registry_v1.json"
REGISTRY=json.loads(REGISTRY_PATH.read_text())
DEFINITIONS={
"001":("SFT-MAT-VALIDATION-CRYSTALLOGRAPHY-DIFFRACTION-VECTOR-001","Crystallography and diffraction validation vector","crystallography, reciprocal structure, diffraction and disorder"),
"002":("SFT-MAT-VALIDATION-DEFECT-MICROSTRUCTURE-VECTOR-002","Defect and microstructure validation vector","defects, microstructure, interfaces and multiscale organization"),
"003":("SFT-MAT-VALIDATION-PHASE-TRANSFORMATION-VECTOR-003","Phase and transformation validation vector","phase equilibria, transitions, kinetics and metastability"),
"004":("SFT-MAT-VALIDATION-MECHANICAL-TRIBOLOGICAL-VECTOR-004","Mechanical and tribological validation vector","mechanics, fracture, fatigue, creep, tribology and rheology"),
"005":("SFT-MAT-VALIDATION-THERMAL-TRANSPORT-VECTOR-005","Thermal and transport validation vector","thermal transport, capacity, expansion and shock response"),
"006":("SFT-MAT-VALIDATION-ELECTRONIC-IONIC-DIELECTRIC-VECTOR-006","Electronic, ionic and dielectric validation vector","electronic, ionic, dielectric and semiconductor transport"),
"007":("SFT-MAT-VALIDATION-MAGNETIC-SUPERCONDUCTING-TOPOLOGICAL-VECTOR-007","Magnetic, superconducting and topological validation vector","magnetism, spin organization, superconductivity, superfluidity and topology"),
"008":("SFT-MAT-VALIDATION-OPTICAL-PHOTONIC-VECTOR-008","Optical and photonic validation vector","optics, photonics, polarization and exciton response"),
"009":("SFT-MAT-VALIDATION-MATERIAL-CLASS-PROCESSING-VECTOR-009","Material-class and processing validation vector","material classes, composites and complete processing paths"),
"010":("SFT-MAT-VALIDATION-CROSS-SOURCE-REPRODUCIBILITY-VECTOR-010","Cross-source Materials reproducibility vector","independently sourced and cross-source Materials correspondence"),
"011":("SFT-MAT-VALIDATION-ADVERSE-ABSENT-OUT-OF-BOUND-VECTOR-011","Complete adverse, absent and out-of-bound Materials vector","adverse, absent, unavailable, unresolved, tampered and scope-boundary evidence"),
"012":("SFT-MAT-VALIDATION-EMPIRICAL-GRAND-LOCK-012","Materials empirical Grand Lock","the complete pre-VALID Materials empirical surface"),
}
IDS=tuple(DEFINITIONS[n][0] for n in sorted(DEFINITIONS))

@dataclass(frozen=True)
class ValidationSpec(StructuralPhysicsSpec):
 number:str=""
 vector_claim_ids:tuple[str,...]=()
 def validate(self):
  if not self.claim_id.startswith("SFT-MAT-VALIDATION-") or len(self.axes)!=8 or not self.dependencies or not self.vector_claim_ids:raise ValueError("incomplete Materials VALID spec")
  if len(set(self.vector_claim_ids))!=len(self.vector_claim_ids) or len(self.vector_claim_ids)!=REGISTRY["vector_claim_counts"][self.number]:raise ValueError("Materials VALID membership changed")
  for a in self.axes:
   if len(a.choices)!=2:raise ValueError("Materials VALID axis incomplete")
   a.survivor
  if not all(w.passed for w in self.witnesses):raise ValueError("Materials VALID witness failed")
class ValidationProgram(StructuralPhysicsProgram):
 @property
 def registration(self):return ClaimRegistration(claim_id=self.spec.claim_id,title=self.spec.title,branch="materials",statement=self.spec.statement,evidence_mode=EvidenceMode.EMPIRICAL,root_theorems=(ROOT_THEOREM,),dependencies=self.spec.dependencies,axioms=(),free_parameters=(),provenance=self.spec.provenance,source_hash=self.source_hash)

EX=("no target value, outcome, match rate or measurement selects the validation law","no fitted threshold, favorable-only sample or omitted member","no formal-only standing boundary relabelled as a measured outcome","no finite-complete claim relabelled depth-independent or conversely","no numerical absence, negative, irrational, imaginary, floating, fitted or free proof magnitude","no first failed route retires an obligation","no engine, verifier, prior receipt, certificate or admitted claim change")
def axes(relation):return (binary_axis("authority","What is validated?","selected-headline","A headline omits the evidence surface.","complete-receipt-bound-membership","Every registered member retains its receipt and evidence files."),binary_axis("relation","What relation survives?","aggregate-score-or-fit","A score or fit can hide distinct failures.",relation,"The complete typed vector is retained member by member."),binary_axis("custody","When is evidence opened?","outcomes-in-forcing","Outcome access may select the law.","sealed-law-then-capability-closed-release","The law emits only a membership-completeness prediction before target release."),binary_axis("results","Which rows survive?","favourable-only","Selective evidence invalidates the vector.","favourable-adverse-absent-unavailable-unresolved","All status classes remain source-custodied."),binary_axis("closure","How is claim scope retained?","single-universal-scope","That overwrites finite boundaries.","each-declared-closure-scope-held","Finite-complete and depth-independent claims retain their actual types."),binary_axis("formal","How are unmeasured formal rows treated?","invented-empirical-success","That fabricates data.","explicit-formal-standing-boundary","Formal-only rows remain unmeasured or operational as registered."),binary_axis("controls","What falsifies completeness?","omission-tolerated","A missing row cannot close a vector.","omission-tamper-and-boundary-halt","Any missing or changed identity, row, seal or control halts."),binary_axis("extension","Can this permanently close Materials?","permanent-lock","A dated vector cannot bar discovery.","dated-complete-extension-open","Later lawful claims require a successor vector."))
def make(number,previous):
 cid,title,scope=DEFINITIONS[number];members=tuple(REGISTRY["vector_claim_ids"][number]);deps=members+((previous,) if previous else ());count=len(members)
 return ValidationSpec(claim_id=cid,title=title,statement=f"The complete frozen {scope} vector retains every one of its {count} named Materials claim memberships, current receipts, controls, target-custody records, sources, measurements, adverse rows and explicit formal-only boundaries without aggregate scoring or omission.",dependencies=deps,evidence_mode=EvidenceMode.EMPIRICAL,generation_rule=f"Generate the complete eight-axis VALID-{number} evidence-preservation product before capability-closed release of its frozen vector.",grammar_boundary=f"Exactly the {count} value-free claim identities registered for Materials VALID-{number}, their current receipt-bound evidence and all result classes.",axes=axes(f"complete-valid-{number}-typed-evidence-vector"),exact_result=f"VALID-{number} uniquely requires a complete member-by-member, receipt-bound, post-seal evidence vector across all {count} registered claims, retaining actual closure scopes, all outcomes and every explicit unmeasured boundary.",induction_base="The first registered member retains its identity, receipt, controls, evidence status and declared scope.",induction_step="Appending the next registered member preserves every earlier row and adds its complete distinct record; omission, duplication or changed identity halts.",exclusions=EX,witnesses=(Witness("count",f"All {count} registered members are present.",count==REGISTRY["vector_claim_counts"][number]),Witness("unique","No member identity is duplicated.",len(set(members))==count),Witness("value-free","The dependency registry contains no target content.",REGISTRY["target_content_present"] is False)),number=number,vector_claim_ids=members)
specs=[];previous=None
for number in sorted(DEFINITIONS):
 spec=make(number,previous);specs.append(spec);previous=spec.claim_id
SPECS={s.claim_id:s for s in specs}
