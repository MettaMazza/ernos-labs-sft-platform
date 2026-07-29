"""Twelve complete validation-vector laws over the frozen Chemistry surface."""
from dataclasses import dataclass
import json
from pathlib import Path
from sft.engine import ClaimRegistration,EvidenceMode,ROOT_THEOREM
from sft.physics.structural_constants import StructuralPhysicsProgram,StructuralPhysicsSpec,Witness,binary_axis

ROOT=Path(__file__).resolve().parents[2]
REGISTRY_PATH=ROOT/"census/chemistry_valid_001_012_dependency_registry_v2.json"
REGISTRY=json.loads(REGISTRY_PATH.read_text())
DEFINITIONS={
"001":("SFT-CHEM-VALIDATION-MOLECULAR-GEOMETRY-VECTOR-001","Substantial molecular geometry validation vector","molecular geometry, incidence, structure and diffraction"),
"002":("SFT-CHEM-VALIDATION-THERMOCHEMICAL-VECTOR-002","Substantial thermochemical validation vector","thermochemical state, energy, enthalpy and heat/work"),
"003":("SFT-CHEM-VALIDATION-EQUILIBRIUM-VECTOR-003","Substantial equilibrium validation vector","chemical, solution and phase equilibrium"),
"004":("SFT-CHEM-VALIDATION-KINETIC-VECTOR-004","Substantial kinetic validation vector","rate, mechanism, intermediate and catalytic dynamics"),
"005":("SFT-CHEM-VALIDATION-SPECTROSCOPY-VECTOR-005","Substantial spectroscopy validation vector","rotational, vibrational, electronic, NMR, Raman and emission spectroscopy"),
"006":("SFT-CHEM-VALIDATION-ELECTROCHEMICAL-VECTOR-006","Substantial electrochemical validation vector","redox, electrode, cell and coupled electrochemical transport"),
"007":("SFT-CHEM-VALIDATION-INORGANIC-COORDINATION-VECTOR-007","Substantial inorganic and coordination validation vector","inorganic, coordination, organometallic and Smithium structure"),
"008":("SFT-CHEM-VALIDATION-ORGANIC-REACTION-VECTOR-008","Substantial organic-reaction validation vector","organic identity, stereochemistry, reaction and mechanism"),
"009":("SFT-CHEM-VALIDATION-POLYMER-VECTOR-009","Substantial polymer validation vector","polymer size, network, sequence, architecture, phase and degradation"),
"010":("SFT-CHEM-VALIDATION-CROSS-SOURCE-REPRODUCIBILITY-VECTOR-010","Cross-source Chemistry reproducibility vector","independently sourced and cross-source chemical correspondence"),
"011":("SFT-CHEM-VALIDATION-ADVERSE-OUT-OF-BOUND-VECTOR-011","Complete adverse and out-of-bound Chemistry vector","adverse, absent, unavailable, unresolved, tampered and scope-boundary evidence"),
"012":("SFT-CHEM-VALIDATION-EMPIRICAL-GRAND-LOCK-012","Chemistry empirical Grand Lock","the complete pre-VALID Chemistry empirical and formal-boundary surface"),
}
IDS=tuple(DEFINITIONS[n][0] for n in sorted(DEFINITIONS))

@dataclass(frozen=True)
class ValidationSpec(StructuralPhysicsSpec):
 number:str=""
 vector_claim_ids:tuple[str,...]=()
 def validate(self):
  if not self.claim_id.startswith("SFT-CHEM-VALIDATION-") or len(self.axes)!=8 or not self.dependencies or not self.vector_claim_ids:raise ValueError("incomplete Chemistry VALID spec")
  if len(set(self.vector_claim_ids))!=len(self.vector_claim_ids) or len(self.vector_claim_ids)!=REGISTRY["vector_claim_counts"][self.number]:raise ValueError("Chemistry VALID membership changed")
  for a in self.axes:
   if len(a.choices)!=2:raise ValueError("Chemistry VALID axis incomplete")
   a.survivor
  if not all(w.passed for w in self.witnesses):raise ValueError("Chemistry VALID witness failed")
class ValidationProgram(StructuralPhysicsProgram):
 @property
 def registration(self):return ClaimRegistration(claim_id=self.spec.claim_id,title=self.spec.title,branch="chemistry",statement=self.spec.statement,evidence_mode=EvidenceMode.EMPIRICAL,root_theorems=(ROOT_THEOREM,),dependencies=self.spec.dependencies,axioms=(),free_parameters=(),provenance=self.spec.provenance,source_hash=self.source_hash)

EX=("no target value, outcome, match rate or measurement selects the validation law","no fitted threshold, favorable-only sample or omitted member","no formal-only standing boundary relabelled as a measured outcome","no finite-complete claim relabelled depth-independent or conversely","no numerical absence, negative, irrational, imaginary, floating, fitted or free proof magnitude","no first failed route retires an obligation","no engine, verifier, prior receipt, certificate or admitted claim change")
def axes(relation):return (binary_axis("authority","What is validated?","selected-headline","A headline omits the evidence surface.","complete-receipt-bound-membership","Every registered member retains its receipt and evidence files."),binary_axis("relation","What relation survives?","aggregate-score-or-fit","A score or fit can hide distinct failures.",relation,"The complete typed vector is retained member by member."),binary_axis("custody","When is evidence opened?","outcomes-in-forcing","Outcome access may select the law.","sealed-law-then-capability-closed-release","The law emits only a membership-completeness prediction before target release."),binary_axis("results","Which rows survive?","favourable-only","Selective evidence invalidates the vector.","favourable-adverse-absent-unavailable-unresolved","All status classes remain source-custodied."),binary_axis("closure","How is claim scope retained?","single-universal-scope","That overwrites finite boundaries.","each-declared-closure-scope-held","Finite-complete and depth-independent claims retain their actual types."),binary_axis("formal","How are unmeasured formal rows treated?","invented-empirical-success","That fabricates data.","explicit-formal-standing-boundary","Formal-only rows remain unmeasured or operational as registered."),binary_axis("controls","What falsifies completeness?","omission-tolerated","A missing row cannot close a vector.","omission-tamper-and-boundary-halt","Any missing or changed identity, row, seal or control halts."),binary_axis("extension","Can this permanently close Chemistry?","permanent-lock","A dated vector cannot bar discovery.","dated-complete-extension-open","Later lawful claims require a successor vector."))
def make(number,previous):
 cid,title,scope=DEFINITIONS[number];members=tuple(REGISTRY["vector_claim_ids"][number]);deps=members+((previous,) if previous else ());count=len(members)
 return ValidationSpec(claim_id=cid,title=title,statement=f"The complete frozen {scope} vector retains every one of its {count} named Chemistry claim memberships, current receipts, controls, target-custody records, sources, measurements, adverse rows and explicit formal-only boundaries without aggregate scoring or omission.",dependencies=deps,evidence_mode=EvidenceMode.EMPIRICAL,generation_rule=f"Generate the complete eight-axis VALID-{number} evidence-preservation product before capability-closed release of its frozen vector.",grammar_boundary=f"Exactly the {count} value-free claim identities registered for Chemistry VALID-{number}, their current receipt-bound evidence and all result classes.",axes=axes(f"complete-valid-{number}-typed-evidence-vector"),exact_result=f"VALID-{number} uniquely requires a complete member-by-member, receipt-bound, post-seal evidence vector across all {count} registered claims, retaining actual closure scopes, all outcomes and every explicit unmeasured boundary.",induction_base="The first registered member retains its identity, receipt, controls, evidence status and declared scope.",induction_step="Appending the next registered member preserves every earlier row and adds its complete distinct record; omission, duplication or changed identity halts.",exclusions=EX,witnesses=(Witness("count",f"All {count} registered members are present.",count==REGISTRY["vector_claim_counts"][number]),Witness("unique","No member identity is duplicated.",len(set(members))==count),Witness("value-free","The dependency registry contains no target content.",REGISTRY["target_content_present"] is False)),number=number,vector_claim_ids=members)
specs=[];previous=None
for number in sorted(DEFINITIONS):
 spec=make(number,previous);specs.append(spec);previous=spec.claim_id
SPECS={s.claim_id:s for s in specs}
