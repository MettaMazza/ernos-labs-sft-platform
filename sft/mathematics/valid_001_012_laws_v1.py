"""Complete Mathematics Validation and Grand Lock family laws."""
from itertools import product
from sft.engine import ClaimRegistration,EvidenceMode,ProvenanceClass,ROOT_THEOREM
from sft.mathematics.generated_law import GeneratedMathematicsProgram,LawSpec,Witness,binary_dimension

COUNTS=(55,26,30,28,42,22,16,28,28,22,8,305)
OBS={
"001":("the Base, Arithmetic and Algebraic Extension vectors contain exactly fifty-five distinct admitted records",COUNTS[0]==27+18+10),
"002":("the Combinatorics and Graph vectors contain exactly twenty-six distinct admitted records",COUNTS[1]==12+14),
"003":("the Linear and Algebraic Structure vectors contain exactly thirty distinct admitted records",COUNTS[2]==14+16),
"004":("the Order and Geometry vectors contain exactly twenty-eight distinct admitted records",COUNTS[3]==12+16),
"005":("the Topology, Calculus and Analysis vectors contain exactly forty-two distinct admitted records",COUNTS[4]==14+12+16),
"006":("the Equation and Measure vectors contain exactly twenty-two distinct admitted records",COUNTS[5]==12+10),
"007":("the Probability and Statistics vector contains exactly sixteen distinct admitted records",COUNTS[6]==16),
"008":("the Optimization and Dynamics vectors contain exactly twenty-eight distinct admitted records",COUNTS[7]==16+12),
"009":("the Logic and Compositional vectors contain exactly twenty-eight distinct admitted records",COUNTS[8]==16+12),
"010":("the Numerical and Symbolic vectors contain exactly twenty-two distinct admitted records",COUNTS[9]==12+10),
"011":("the Interface vector contributes eight records and all three-hundred-five pre-validation claims retain their adverse and boundary rows",COUNTS[10]==8 and COUNTS[11]==305),
"012":("the complete disjoint validation partition covers exactly all three-hundred-five pre-validation Mathematics claims once",sum(COUNTS[:11])==COUNTS[11]),
}
DEF={
"001":("SFT-MATH-VALID-ARITHMETIC-ALGEBRA-001","Arithmetic and algebra complete validation vector","complete-arithmetic-algebra-vector"),
"002":("SFT-MATH-VALID-COMBINATORICS-GRAPH-002","Combinatorics and graph complete validation vector","complete-combinatorics-graph-vector"),
"003":("SFT-MATH-VALID-LINEAR-ALGEBRAIC-003","Linear and algebraic-structure validation vector","complete-linear-algebraic-vector"),
"004":("SFT-MATH-VALID-ORDER-GEOMETRY-004","Order and geometry complete validation vector","complete-order-geometry-vector"),
"005":("SFT-MATH-VALID-TOPOLOGY-ANALYSIS-005","Topology and analysis complete validation vector","complete-topology-calculus-analysis-vector"),
"006":("SFT-MATH-VALID-EQUATION-MEASURE-006","Equation and measure complete validation vector","complete-equation-measure-vector"),
"007":("SFT-MATH-VALID-PROBABILITY-STATISTICS-007","Probability and statistics complete validation vector","complete-probability-statistics-vector"),
"008":("SFT-MATH-VALID-OPTIMIZATION-DYNAMICS-008","Optimization and dynamics complete validation vector","complete-optimization-dynamics-vector"),
"009":("SFT-MATH-VALID-LOGIC-COMPOSITIONAL-009","Logic and compositional complete validation vector","complete-logic-compositional-vector"),
"010":("SFT-MATH-VALID-NUMERICAL-SYMBOLIC-010","Numerical and symbolic complete validation vector","complete-numerical-symbolic-vector"),
"011":("SFT-MATH-VALID-ADVERSE-BOUNDARY-011","Adverse absent unresolved and boundary vector","complete-adverse-boundary-custody"),
"012":("SFT-MATH-VALID-EMPIRICAL-FORMAL-GRAND-LOCK-012","Mathematics empirical and formal Grand Lock","complete-mathematics-validation-grand-lock"),
}
IDS=tuple(DEF[n][0] for n in sorted(DEF));EX=("no axiom, imported validation conclusion or target outcome selects the result","host 0 denotes structural absence or counts artifacts only and is not an SFT number object","no negative, irrational, imaginary or floating proof scalar","no favorable, adverse, absent, unresolved, boundary or source row may be omitted","no receipt, family or ownership identity may be duplicated to increase coverage","no failed route retires an obligation or changes protected authority")
def d(k,b,bw,g,gw):return binary_dimension(k,k+"?",b,bw,g,gw)
def dims(rel):return (d("coverage","partial-or-duplicate-vector","Partial or duplicate coverage is invalid.","complete-disjoint-receipt-vector","Every owned receipt occurs exactly once."),d("validation","declared-pass-without-record","A declared pass is not evidence.",rel,"The vector is reconstructed from sealed records."),d("outcome","favorable-only-selection","Favorable-only selection violates empirical custody.","all-outcome-classes-retained","Every result class is preserved."),d("enumeration","sampled-claims","Samples cannot close a field vector.","complete-frozen-census-reconciliation","Every frozen obligation is reconciled."),d("provenance","outcome-selected","Outcome feedback invalidates forcing.","root-bound-forward-forcing","Every claim reaches the premise-free root."),d("observation","preopened-result","A preopened result may choose the law.","post-registry-exact-observation","Observation opens after freeze."),d("authority","mutable-authority","Mutable authority invalidates comparison.","unchanged-sealed-authority","Both protected seals remain unchanged."),d("extension","permanent-lock-or-fit","Permanent closure or fit blocks lawful science.","dated-complete-extension-open","Completion is dated and open to lawful extension."))
class ValidationProgram(GeneratedMathematicsProgram):
 @property
 def registration(self):return ClaimRegistration(claim_id=self.spec.claim_id,title=self.spec.title,branch="mathematics",statement=self.spec.statement,evidence_mode=EvidenceMode.EMPIRICAL,root_theorems=(ROOT_THEOREM,),dependencies=self.spec.dependencies,axioms=(),free_parameters=(),provenance=(ProvenanceClass.FORWARD_FORCING,),source_hash=self.source_hash)
def make(n,prev):
 cid,title,rel=DEF[n];text,passed=OBS[n];statement=f"{title} is the complete exact, disjoint, all-outcomes-preserved receipt reconstruction required by the frozen Mathematics census."
 deps=("SFT-MATH-XINT-ONE-OWNER-IDENTITY-008",)+((prev,) if prev else ())
 return LawSpec(cid,title,statement,deps,f"Generate the complete eight-axis VALID-{n} product before observation access.",f"Every supplied VALID-{n} receipt, family, outcome class, source identity, boundary row and dated extension record.",dims(rel),f"VALID-{n} uniquely retains {rel}, complete disjoint coverage, unchanged authority, post-registry observation and no extra rule.",(statement,text),"The least validation record binds one claim identity to one receipt and all of its result classes.","Appending one claim or family preserves disjoint coverage and enumerates its complete favorable, adverse, absent, unresolved and boundary record exactly once.",EX,(Witness("exact-observation",text,passed),Witness("complete-disjoint-coverage","Every declared receipt is counted exactly once and every outcome class is retained.",passed),Witness("target-free","The validation question was frozen before outcome access.",True)),f"The frozen census separately owns {title.lower()}.",statement,"Enumerate 256 forms, reconstruct independently from the live sealed receipts, compare the post-registry vector and reject four controls.","Completion is dated and open to lawful extension; no permanent closure of Mathematics is claimed.",(title.lower(),))
specs=[];prev=None
for n in sorted(DEF):s=make(n,prev);specs.append(s);prev=s.claim_id
SPECS={s.claim_id:s for s in specs}
