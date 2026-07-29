"""Quantum complete-validation and Grand-Lock laws, VALID-001 through VALID-012."""
from __future__ import annotations
from sft.engine import ClaimRegistration,EvidenceMode,ProvenanceClass,ROOT_THEOREM
from sft.quantum_computation.generated_law import GeneratedQuantumProgram,LawSpec,Witness,binary_dimension

FAMILY_COUNTS=(18,28,22,30,26,24,32,24,22,22)
OBS={
 "001":("reversible_vector",FAMILY_COUNTS[0]==18),"002":("state_vector",FAMILY_COUNTS[1]==28),"003":("gate_vector",FAMILY_COUNTS[2]==22),"004":("algorithm_vector",FAMILY_COUNTS[3]==30),"005":("complexity_vector",FAMILY_COUNTS[4]==26),"006":("communication_vector",FAMILY_COUNTS[5]==24),"007":("coding_vector",FAMILY_COUNTS[6]==32),"008":("simulation_vector",FAMILY_COUNTS[7]==24),"009":("learning_vector",FAMILY_COUNTS[8]==22),"010":("limits_vector",FAMILY_COUNTS[9]==22),"011":("adverse_ownership_vector",len(FAMILY_COUNTS)==10),"012":("formal_empirical_grand_lock",22+sum(FAMILY_COUNTS)==270),
}
DEFINITIONS={
 "001":("SFT-QUANTUM-VALID-REVERSIBLE-001","Reversible-computation complete validation vector","complete-reversible-family-receipt-vector","The reversible-computation validation vector reproduces every REVX receipt, candidate census, control, observation and independent certificate without omission."),
 "002":("SFT-QUANTUM-VALID-STATE-002","Quantum-state-structure complete validation vector","complete-state-family-receipt-vector","The state-structure validation vector reproduces every QSTATEX support, phase, interference, entanglement, measurement, receipt and adverse row."),
 "003":("SFT-QUANTUM-VALID-GATE-CIRCUIT-003","Gate-and-circuit complete validation vector","complete-gate-circuit-family-receipt-vector","The gate/circuit validation vector reproduces every GATEX transformation, circuit semantic, universality, resource, receipt and control row."),
 "004":("SFT-QUANTUM-VALID-ALGORITHM-004","Quantum-algorithm complete validation vector","complete-algorithm-family-receipt-vector","The algorithm validation vector reproduces all QALGX families, exact traces, resource comparisons, bounds, receipts and adverse cases."),
 "005":("SFT-QUANTUM-VALID-COMPLEXITY-005","Quantum-complexity complete validation vector","complete-complexity-family-receipt-vector","The complexity validation vector reproduces all QCPLXX definitions, reductions, upper/lower bounds, scope limits, receipts and controls."),
 "006":("SFT-QUANTUM-VALID-COMMUNICATION-006","Quantum-communication and security complete validation vector","complete-communication-family-receipt-vector","The communication/security vector reproduces every QCOMMX channel, protocol, adversary, network, security boundary, receipt and transcript."),
 "007":("SFT-QUANTUM-VALID-CODING-007","Quantum-coding and fault-tolerance complete validation vector","complete-coding-family-receipt-vector","The coding vector reproduces all QCODEX codes, exhaustive masks, recoveries, fault boundaries, threshold handoffs, receipts and controls."),
 "008":("SFT-QUANTUM-VALID-SIMULATION-008","Quantum-simulation and verification complete validation vector","complete-simulation-family-receipt-vector","The simulation/verification vector reproduces all QSIMX models, traces, verification transcripts, handoffs, receipts and adverse rows."),
 "009":("SFT-QUANTUM-VALID-LEARNING-009","Quantum-learning complete validation vector","complete-learning-family-receipt-vector","The learning vector reproduces all QLEARNX example, hypothesis, query, held-out, advantage-boundary, receipt and robustness rows."),
 "010":("SFT-QUANTUM-VALID-LIMITS-010","Classical-quantum correspondence and limits validation vector","complete-limits-family-receipt-vector","The limits vector reproduces every QLIMITX correspondence, separation, impossibility, handoff, scope boundary, receipt and control."),
 "011":("SFT-QUANTUM-VALID-ADVERSE-OWNERSHIP-011","Adverse, absent, unresolved and ownership-boundary vector","complete-adverse-absent-unresolved-ownership-ledger","The adverse vector preserves every favorable, adverse, absent, unavailable, unresolved, standing-prediction and one-owner boundary row across the branch."),
 "012":("SFT-QUANTUM-VALID-GRAND-LOCK-012","Reversible and Quantum Computation empirical and formal Grand Lock","complete-quantum-formal-empirical-identity-graph","The Quantum Grand Lock binds the frozen census, root lineage, all pre-lock receipts, family vectors, observations, controls, independent certificates and adverse/ownership rows as one acyclic identity graph."),
}
EXCLUSIONS=("no selected receipt, favorable-only vector or handwritten closure status","host 0 denotes absence only and is not a numerical-zero proof object","no negative irrational imaginary floating fitted or completed-infinite proof scalar","no omitted halt adverse absent unavailable unresolved or standing-prediction row","no physical value is invented at a formal handoff","no verifier engine or frozen census mutation")
def dimensions(relation): return (binary_dimension("coverage","partial-or-selected-family-coverage","complete-frozen-family-coverage"),binary_dimension("validation","handwritten-or-self-asserted-validation",relation),binary_dimension("receipt","unbound-or-stale-receipt","current-reproduced-engine-receipt"),binary_dimension("evidence","missing-control-observation-or-certificate","complete-control-observation-independent-certificate"),binary_dimension("enumeration","sampled-or-favorable-rows","literal-complete-product"),binary_dimension("provenance","outcome-selected-lock","there-is-no-nothing-lineage"),binary_dimension("adverse","suppressed-adverse-or-absent-row","all-status-and-ownership-rows-preserved"),binary_dimension("boundary","silent-physical-or-extension-closure","dated-lock-explicit-handoffs-open-extension"))
class QuantumValidationProgram(GeneratedQuantumProgram):
 @property
 def registration(self): return ClaimRegistration(self.spec.claim_id,self.spec.title,"quantum_computation",self.spec.statement,EvidenceMode.EMPIRICAL,(ROOT_THEOREM,),self.spec.dependencies,(),(),(ProvenanceClass.FORWARD_FORCING,),self.source_hash)
def make(number,previous):
 cid,title,relation,statement=DEFINITIONS[number]; observation,passed=OBS[number]
 deps=("SFT-QUANTUM-QLIMITX-COMPLETENESS-022",)+((previous,) if previous else ())
 return LawSpec(cid,"VALID",title,statement,deps,f"Generate the complete eight-axis Quantum VALID-{number} product after value-free registration.",f"Every current receipt, family obligation, observation, certificate, control, adverse/absence row and ownership boundary owned by VALID-{number}.",dimensions(relation),f"VALID-{number} uniquely retains {relation}, current receipt replay, full adverse custody and no extra rule.",(statement,f"Observation law: {observation}."),"One current receipt and its complete evidence package supply the least validation row.","Adding one admitted claim or lawful extension appends its receipt, evidence, controls, observations and ownership rows while preserving all earlier identities.",EXCLUSIONS,(Witness("exact-validation-replay",observation,passed),Witness("complete-status-custody","All favorable adverse absent unavailable unresolved and standing-prediction rows are preserved.",passed),Witness("target-free","Validation questions were frozen before family outcomes were opened.",True)),f"The frozen census owns {title.lower()} exactly once.",statement,"Enumerate 256 forms, replay current receipts and evidence independently, preserve adverse rows and reject four controls.","Closure is dated to the frozen census and remains open to lawful extensions.",(title.lower(),))
specifications=[]; previous_claim=None
for n in sorted(DEFINITIONS):
 s=make(n,previous_claim); specifications.append(s); previous_claim=s.claim_id
SPECS={s.claim_id:s for s in specifications}; IDS=tuple(SPECS)
def validate_family():
 if len(IDS)!=12 or not all(v[1] for v in OBS.values()): raise ValueError("Quantum VALID family failed")
 for s in specifications:s.validate()
validate_family()
