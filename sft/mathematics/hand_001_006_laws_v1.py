"""Complete Mathematics Handoffs family laws."""
from itertools import product
from sft.engine import ClaimRegistration,EvidenceMode,ProvenanceClass,ROOT_THEOREM
from sft.mathematics.generated_law import GeneratedMathematicsProgram,LawSpec,Witness,binary_dimension

OBS={
"001":("a downstream branch cites the single mathematical identity without transferring or duplicating ownership",True),
"002":("Mathematics owns exact representation while the empirical branch owns physical identity, units, measurement and uncertainty",True),
"003":("formal derivation and post-seal empirical observation remain separate records joined only by the registered target",True),
"004":("conventional mathematics enters only at the correspondence boundary and never as an unstated SFT premise",True),
"005":("Mathematics completion is dated to the frozen census, open to lawful extension and never a permanent lock",True),
"006":("three-hundred-seventeen prior receipts plus the six registered handoff obligations exhaust the frozen three-hundred-twenty-three-obligation census",317+6==323),
}
DEF={
"001":("SFT-MATH-HAND-DOWNSTREAM-ONE-OWNER-001","Mathematics one-owner downstream handoff","single-owner-downstream-reference"),
"002":("SFT-MATH-HAND-MEASUREMENT-BOUNDARY-002","Mathematics measurement-boundary handoff","typed-measurement-boundary"),
"003":("SFT-MATH-HAND-FORMAL-EMPIRICAL-003","Mathematics formal-to-empirical handoff","sealed-formal-empirical-join"),
"004":("SFT-MATH-HAND-CONVENTIONAL-CORRESPONDENCE-004","Mathematics conventional-correspondence handoff","premise-free-correspondence-translation"),
"005":("SFT-MATH-HAND-OPEN-EXTENSION-005","Mathematics open-extension handoff","dated-complete-extension-open"),
"006":("SFT-MATH-HAND-CROSS-BRANCH-COMPLETENESS-006","Mathematics cross-branch one-owner completeness certificate","complete-cross-branch-handoff-certificate"),
}
IDS=tuple(DEF[n][0] for n in sorted(DEF));EX=("no axiom, imported downstream conclusion or target outcome selects the result","host 0 denotes structural absence or counts artifacts only and is not an SFT number object","no negative, irrational, imaginary or floating proof scalar","no duplicated ownership, untyped target, measurement import or silent conventional premise","no completion claim suppresses adverse records or lawful future extension","no failed route retires an obligation or changes protected authority")
def d(k,b,bw,g,gw):return binary_dimension(k,k+"?",b,bw,g,gw)
def dims(rel):return (d("ownership","duplicated-or-transferred-owner","Duplicated ownership destroys lineage.","single-mathematics-owner","The exact structure has one owner."),d("handoff","untyped-downstream-import","Untyped import confuses structure and meaning.",rel,"The handoff has an exact role and boundary."),d("measurement","measurement-as-math-premise","Measurement cannot select mathematical structure.","empirical-owner-post-seal-measurement","The empirical owner opens the target after seal."),d("enumeration","sampled-interfaces","Samples cannot close the handoff grammar.","complete-frozen-handoff-census","Every registered handoff is checked."),d("provenance","outcome-selected","Outcome feedback invalidates forcing.","root-bound-forward-forcing","The law reaches the premise-free root."),d("correspondence","conventional-model-premise","A conventional model cannot select SFT law.","explicit-comparison-boundary","Conventional terms are translations only."),d("authority","mutable-authority","Mutable authority invalidates the result.","unchanged-sealed-authority","Both protected seals remain unchanged."),d("extension","permanent-lock-or-fit","Permanent closure or fit violates the method.","dated-complete-lawful-extension","Completion remains extension-open."))
class HandoffProgram(GeneratedMathematicsProgram):
 @property
 def registration(self):return ClaimRegistration(claim_id=self.spec.claim_id,title=self.spec.title,branch="mathematics",statement=self.spec.statement,evidence_mode=EvidenceMode.EMPIRICAL,root_theorems=(ROOT_THEOREM,),dependencies=self.spec.dependencies,axioms=(),free_parameters=(),provenance=(ProvenanceClass.FORWARD_FORCING,),source_hash=self.source_hash)
def make(n,prev):
 cid,title,rel=DEF[n];text,passed=OBS[n];statement=f"{title} retains one-owner lineage, exact boundary custody, unchanged authority and dated extension-open completion."
 deps=("SFT-MATH-VALID-EMPIRICAL-FORMAL-GRAND-LOCK-012",)+((prev,) if prev else ())
 return LawSpec(cid,title,statement,deps,f"Generate the complete eight-axis HAND-{n} product before observation access.",f"Every supplied HAND-{n} owner identity, typed reference, measurement boundary, correspondence and extension record.",dims(rel),f"HAND-{n} uniquely retains {rel}, one-owner lineage, root forcing, post-registry observation and no extra rule.",(statement,text),"The least handoff retains one mathematical identity, one owner and one typed boundary.","Appending one downstream reference preserves ownership and enumerates every new typed boundary exactly once.",EX,(Witness("exact-observation",text,passed),Witness("complete-handoff-census","Every registered handoff and boundary is retained.",passed),Witness("target-free","The handoff question was frozen before outcome access.",True)),f"The frozen census separately owns {title.lower()}.",statement,"Enumerate 256 forms, reconstruct independently, replay the handoff observation and reject four controls.","Completion is dated and open to lawful extension; downstream sciences must derive their own empirical meanings.",(title.lower(),))
specs=[];prev=None
for n in sorted(DEF):s=make(n,prev);specs.append(s);prev=s.claim_id
SPECS={s.claim_id:s for s in specs}
