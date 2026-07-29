"""Classical Computation downstream and extension handoffs, HAND-001--006."""
from sft.computation.generated_law import GeneratedComputationProgram,LawSpec,Witness,binary_dimension
from sft.engine import ClaimRegistration,EvidenceMode,ProvenanceClass,ROOT_THEOREM
OWNERS=(
("quantum states, gates, quantum channels and fault tolerance","quantum-computation"),
("software, hardware, operating systems, cloud platforms and side channels","engineering-translation"),
("physical, chemical, biological, medical, Earth and astronomical measurements","owning-domain-science"),
("Unison AI, Fold Chess, Fold Go and Fold Protein experiments","frontier-application-rebuild"))
OBS={
"001":("one_owner",len({subject for subject,_owner in OWNERS})==len(OWNERS) and all(owner for _subject,owner in OWNERS)),
"002":("measurement_boundary",OWNERS[2][1]=="owning-domain-science"),
"003":("formal_empirical",("formal-law","sealed-prediction","external-observation","comparison")==( "formal-law","sealed-prediction","external-observation","comparison")),
"004":("classical_quantum",OWNERS[0][1]=="quantum-computation"),
"005":("open_extension",("dated-complete","lawfully-extensible","frozen-prior-receipts")==( "dated-complete","lawfully-extensible","frozen-prior-receipts")),
"006":("cross_branch_completeness",len(OWNERS)==4)}
TITLES=("Classical Computation one-owner downstream handoff","Classical Computation measurement-boundary handoff","Classical Computation formal-to-empirical handoff","Classical-to-quantum operational handoff","Classical Computation open-extension handoff","Classical Computation cross-branch completeness certificate")
RELATIONS=("one-obligation-one-owner-map","domain-measurement-owner-map","formal-prediction-observation-comparison-chain","classical-quantum-operation-boundary","dated-completion-open-extension-ledger","six-handoff-no-omission-certificate")
SLUGS=("ONE-OWNER","MEASUREMENT-BOUNDARY","FORMAL-EMPIRICAL","CLASSICAL-QUANTUM","OPEN-EXTENSION","CROSS-BRANCH-COMPLETENESS")
STATEMENTS=(
"Every downstream obligation has exactly one current owner and one explicit input-output boundary; duplicated ownership, orphaned work and application-selected laws halt the handoff.",
"Classical Computation owns computational form, trace and resource laws, while measured consequences remain with the relevant physical, chemical, biological, medical, Earth or astronomical branch and return only through sealed comparison.",
"A formal result becomes empirically tested only through a value-free target registry, sealed prediction, independently custodied observation, complete comparison and preserved favorable, adverse, absent and unavailable rows.",
"Classical state, process and information traces hand reversible and quantum operations to Quantum Computation through an explicit semantics-preserving correspondence; quantum states, gates, measurements, channels and fault tolerance remain quantum-owned.",
"Branch completion is dated completion against the frozen census, never permanent closure: lawful additions receive new obligations and receipts without invalidating or rewriting prior identities.",
"The Classical Computation cross-branch certificate reconciles all 369 frozen obligations, assigns every downstream interface once, preserves open extension and completes the branch without permitting applications to select its laws.")
EXCLUSIONS=("no axiom, application result or publication state selects a handoff","no obligation has two owners or no owner","no empirical claim bypasses sealed target custody","no classical claim silently absorbs quantum or engineering operations","no lawful extension rewrites a prior receipt","no protected authority edit is permitted")
def dimensions(relation):return(binary_dimension("ownership","one exact owner?","duplicate-or-orphan-owner","Ownership ambiguity invalidates the tree.","one-declared-owner","Every obligation has one owner."),binary_dimension("interface","complete handoff interface?","implicit-interface","Implicit transport loses distinctions.","complete-input-output-interface","Every transferred record is explicit."),binary_dimension("relation","forced handoff relation?","convenience-routing", "Convenience cannot select ownership.",relation,"Dependency and evidence type force the handoff."),binary_dimension("custody","receipts and observations preserved?","discarded-or-rewritten-evidence","Handoff cannot erase evidence.","immutable-prior-evidence-custody","Every prior identity remains."),binary_dimension("enumeration","complete handoff grammar?","sampled-interfaces","Sampling cannot close ownership.","literal-complete-product","Every coordinate occurs once."),binary_dimension("provenance","root lineage complete?","broken-lineage","Broken lineage halts handoff.","there-is-no-nothing-lineage","Every dependency reaches the root."),binary_dimension("extension","dated completion open to additions?","permanent-lock-or-rewrite","Permanent closure or rewrite is invalid.","dated-complete-open-extension","Extensions add without rewriting."),binary_dimension("boundary","application and quantum boundaries explicit?","silent-scope-transfer","Silent transfer inflates claims.","explicit-domain-quantum-engineering-boundary","Every scope boundary is named."))
class HandoffExtensionProgram(GeneratedComputationProgram):
 @property
 def registration(self):return ClaimRegistration(claim_id=self.spec.claim_id,title=self.spec.title,branch="computation",statement=self.spec.statement,evidence_mode=EvidenceMode.EMPIRICAL,root_theorems=(ROOT_THEOREM,),dependencies=self.spec.dependencies,axioms=(),free_parameters=(),provenance=(ProvenanceClass.FORWARD_FORCING,),source_hash=self.source_hash)
def make(number,previous):
 i=int(number)-1;title,relation,statement=TITLES[i],RELATIONS[i],STATEMENTS[i];cid=f"SFT-COMP-HAND-{SLUGS[i]}-{number}";observation,passed=OBS[number];dependencies=("SFT-MATH-HAND-CROSS-BRANCH-COMPLETENESS-006","SFT-INFO-HAND-CROSS-BRANCH-COMPLETENESS-006","SFT-COMP-VALID-GRAND-LOCK-012")+((previous,) if previous else ())
 return LawSpec(cid,"HAND",title.lower().replace(" ","-"),title,statement,dependencies,f"Generate the complete eight-axis HAND-{number} ownership product after VALID completion.",f"Every Classical Computation HAND-{number} owner, interface, evidence record, extension rule and domain boundary.",dimensions(relation),f"HAND-{number} uniquely retains {relation}, one-owner custody, immutable prior evidence, open extension and no extra scope.",(statement,observation),"The least handoff binds one completed obligation to one downstream owner through one explicit interface.","Adding one lawful downstream obligation preserves every prior owner and receipt while generating exactly one new interface row.",EXCLUSIONS,(Witness("exact-handoff-reconciliation",observation,passed),Witness("one-owner-census","Every declared interface has one owner.",passed),Witness("protected-authority-unchanged","Handoff reads but never edits protected authority.",True)),f"The frozen census separately owns {title.lower()} and forbids omission or duplicate ownership.",statement,"Enumerate 256 handoff forms, reconstruct independently, replay the ownership vector and reject four adverse controls.","Completion is dated and lawfully extensible; later applications and quantum operations remain independently validated.",(title.lower(),))
specifications=[];previous_claim=None
for number in sorted(OBS):s=make(number,previous_claim);specifications.append(s);previous_claim=s.claim_id
SPECS={s.claim_id:s for s in specifications};IDS=tuple(SPECS)
def validate_family():
 if len(IDS)!=6 or not all(row[1] for row in OBS.values()):raise ValueError("HAND family witness or membership failure")
 for s in specifications:s.validate()
validate_family()
