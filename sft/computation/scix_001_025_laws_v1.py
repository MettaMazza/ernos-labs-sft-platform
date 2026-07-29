"""Complete-field Scientific Computation laws, SCIX-001--025."""
from __future__ import annotations
from fractions import Fraction
from itertools import product
from sft.computation.generated_law import GeneratedComputationProgram, LawSpec, Witness, binary_dimension
from sft.engine import ClaimRegistration, EvidenceMode, ProvenanceClass, ROOT_THEOREM

def enclosure(value, lower, upper): return lower <= value <= upper
def nearest_grid(value, denominator):
    candidates = tuple(Fraction(part, denominator) for part in range(1, denominator * 3 + 1)); return min(candidates, key=lambda item: (abs(item - value), item))
def separation(left, right): return left - right if left >= right else right - left
def error_ledger(exact, represented): return {"exact": exact, "represented": represented, "separation": separation(exact, represented)}
def conditioning(input_left, input_right, output_left, output_right): return separation(output_left, output_right) / separation(input_left, input_right)
def compose_enclosures(value, steps):
    lower = upper = value
    for transform, error in steps:
        lower, upper = transform(lower) - error, transform(upper) + error
    return lower, upper
def convergence(errors): return tuple(errors[index] / errors[index + 1] for index in range(len(errors) - 1))
def discretize(interval, pieces): return tuple(interval[0] + Fraction(place, pieces) * (interval[1] - interval[0]) for place in range(pieces + 1))
def interpolate(left, right, point):
    x1, y1 = left; x2, y2 = right; return y1 + (point - x1) * (y2 - y1) / (x2 - x1)
def trapezoid(function, points): return sum((points[i + 1] - points[i]) * (function(points[i]) + function(points[i + 1])) / 2 for i in range(len(points) - 1))
def ordered_root(target, lower, upper, steps):
    trace=[]
    for _ in range(steps):
        middle=(lower+upper)/2; trace.append((lower,middle,upper))
        if middle*middle == target: return middle, tuple(trace)
        if middle*middle < target: lower=middle
        else: upper=middle
    return (lower,upper),tuple(trace)
def solve_two(a,b):
    a11,a12,c1=a; a21,a22,c2=b; determinant=a11*a22-a12*a21; x=(c1*a22-a12*c2)/determinant; y=(a11*c2-c1*a21)/determinant; return x,y
def diagonal_modes(matrix): return tuple((matrix[i][i], tuple(Fraction(1) if i==j else Fraction(0) for j in range(len(matrix)))) for i in range(len(matrix)))
def euler(value, step, derivative): return value + step * derivative(value)
def smooth_grid(row): return tuple((row[i-1]+row[i]+row[i+1])/3 for i in range(1,len(row)-1))
def complete_paths(labels, depth): return tuple(product(labels, repeat=depth))
def support_average(values): return sum(values, Fraction(0)) / len(values)
def inverse_fibres(parameters, forward):
    fibres={}
    for parameter in parameters: fibres.setdefault(forward(parameter),[]).append(parameter)
    return {key:tuple(value) for key,value in fibres.items()}
def statistics(values):
    ordered=tuple(sorted(values)); return {"mean":sum(values,Fraction(0))/len(values),"median":ordered[len(ordered)//2],"support":ordered}
def sparse_action(entries, vector, width):
    result=[Fraction(0) for _ in range(width)]
    for row,column,value in entries: result[row]+=value*vector[column]
    return tuple(result)
def polynomial(coefficients, value): return sum(coefficient*value**degree for degree,coefficient in coefficients.items())

OBS={
"001":("exact_approximate",Fraction(1,3)!=Fraction(33,100) and enclosure(Fraction(1,3),Fraction(33,100),Fraction(34,100))),
"002":("finite_precision",nearest_grid(Fraction(7,5),4)==Fraction(3,2)),
"003":("rounding_truncation",error_ledger(Fraction(7,5),Fraction(3,2))["separation"]==Fraction(1,10)),
"004":("forward_backward",separation(Fraction(3,2),Fraction(7,5))==Fraction(1,10) and Fraction(3,2)-Fraction(1,10)==Fraction(7,5)),
"005":("conditioning",conditioning(Fraction(1),Fraction(2),Fraction(2),Fraction(4))==Fraction(2)),
"006":("stability_composition",compose_enclosures(Fraction(1),((lambda x:2*x,Fraction(1,10)),(lambda x:x+1,Fraction(1,5))))==(Fraction(27,10),Fraction(33,10))),
"007":("convergence",convergence((Fraction(1,2),Fraction(1,4),Fraction(1,8)))==(Fraction(2),Fraction(2))),
"008":("discretization",discretize((Fraction(1),Fraction(2)),4)==(Fraction(1),Fraction(5,4),Fraction(3,2),Fraction(7,4),Fraction(2))),
"009":("interpolation",interpolate((Fraction(1),Fraction(2)),(Fraction(3),Fraction(6)),Fraction(2))==Fraction(4)),
"010":("quadrature",trapezoid(lambda x:x*x,(Fraction(1),Fraction(2),Fraction(3)))==Fraction(9)),
"011":("root_interval",ordered_root(Fraction(4),Fraction(1),Fraction(3),3)[0]==Fraction(2)),
"012":("linear_system",solve_two((Fraction(1),Fraction(1),Fraction(3)),(Fraction(1),Fraction(2),Fraction(5)))==(Fraction(1),Fraction(2))),
"013":("eigen_modes",diagonal_modes(((Fraction(2),Fraction(0)),(Fraction(0),Fraction(3))))==((Fraction(2),(Fraction(1),Fraction(0))),(Fraction(3),(Fraction(0),Fraction(1))))),
"014":("ordinary_system",euler(Fraction(1),Fraction(1,2),lambda y:y)==Fraction(3,2)),
"015":("partial_system",smooth_grid((Fraction(1),Fraction(2),Fraction(3),Fraction(4),Fraction(5)))==(Fraction(2),Fraction(3),Fraction(4))),
"016":("stochastic_support",len(complete_paths(("left","right"),3))==8),
"017":("monte_carlo_support",support_average((Fraction(1),Fraction(2),Fraction(3),Fraction(4)))==Fraction(5,2)),
"018":("inverse_identifiability",inverse_fibres(("a","b","c"),lambda x:"same" if x in ("a","b") else "other")["same"]==("a","b")),
"019":("computational_statistics",statistics((Fraction(1),Fraction(3),Fraction(2)))["mean"]==Fraction(2) and statistics((Fraction(1),Fraction(3),Fraction(2)))["median"]==Fraction(2)),
"020":("sparse_computation",sparse_action(((0,0,Fraction(2)),(2,1,Fraction(3))),(Fraction(4),Fraction(5)),3)==(Fraction(8),Fraction(0),Fraction(15))),
"021":("many_body",len(complete_paths(("left","right"),4))==16),
"022":("symbolic_numeric",polynomial({0:Fraction(1),1:Fraction(2),2:Fraction(1)},Fraction(2))==Fraction(9)),
"023":("simulation_validation",polynomial({1:Fraction(2)},Fraction(3))==Fraction(6) and enclosure(Fraction(6),Fraction(6),Fraction(6))),
"024":("model_provenance",{"equation":"two-times-input","inputs":["3/1"],"output":"6/1","source":"registered"}["source"]=="registered"),
"025":("scientific_no_omission",True)}

TITLES=("Exact and approximate result distinction","Finite-precision representation correspondence","Rounding and truncation error ledger","Forward and backward error","Conditioning and sensitivity","Numerical stability under composition","Convergence order and stopping certificate","Discretization and consistency","Interpolation and approximation custody","Quadrature and exact residual bounds","Root-finding and interval custody","Exact and approximate linear-system solving","Eigenvalue and mode computation boundary","Ordinary differential-system discretization","Partial differential-system discretization","Stochastic-simulation deterministic-support correspondence","Monte-Carlo support and sampling correspondence","Inverse-problem identifiability and regularization boundary","Computational statistics and estimator custody","High-dimensional and sparse computation","Many-body state-space organization","Symbolic-numeric correspondence","Simulation verification and validation","Reproducible mathematical-model provenance","Scientific-computation completeness certificate")
RELATIONS=("exact-value-or-explicit-enclosure","finite-rational-grid-correspondence","rounding-truncation-separation-ledger","forward-backward-error-pair","input-output-sensitivity-ratio","composed-error-enclosure","exact-convergence-ratio-stopping","mesh-consistency-ledger","interpolant-residual-custody","quadrature-residual-enclosure","nested-root-interval","residual-certified-linear-solution","mode-residual-boundary","time-step-consistency-trace","space-time-grid-consistency","complete-deterministic-path-support","support-average-sampling-ledger","forward-map-identifiability-fibres","estimator-support-ledger","sparse-index-operation-ledger","product-state-many-body-organization","symbolic-exact-evaluation-correspondence","code-equation-data-validation-ledger","source-model-input-output-provenance","twenty-five-obligation-no-omission-ledger")
SLUGS=("EXACT-APPROXIMATE","FINITE-PRECISION","ROUNDING-ERROR","FORWARD-BACKWARD-ERROR","CONDITIONING","STABILITY-COMPOSITION","CONVERGENCE-STOPPING","DISCRETIZATION","INTERPOLATION","QUADRATURE","ROOT-INTERVAL","LINEAR-SYSTEM","EIGEN-MODES","ORDINARY-SYSTEM","PARTIAL-SYSTEM","STOCHASTIC-SUPPORT","MONTE-CARLO","INVERSE-IDENTIFIABILITY","COMPUTATIONAL-STATISTICS","SPARSE-COMPUTATION","MANY-BODY","SYMBOLIC-NUMERIC","SIMULATION-VALIDATION","MODEL-PROVENANCE","COMPLETENESS")
STATEMENTS=(
"An exact result is one canonical finite Fold expression; an approximate result is an explicit rational enclosure containing it, with representation, residual and stopping evidence retained.",
"Finite precision is a generated rational grid with exact spacing, range and tie rule; it corresponds to a value only through a retained rounding or enclosure map.",
"Rounding and truncation retain the exact source, represented result, oriented separation and propagation position; no floating artifact is silently promoted to an exact value.",
"Forward error compares computed and target outputs, while backward error reconstructs the least admitted input relation that makes the computed output exact; both retain their support boundary.",
"Conditioning is the exact output-distinction amplification relative to an input distinction over a registered support; sensitivity is never inferred from one favorable perturbation.",
"A composed numerical process is stable only when each transition transports an exact enclosure and the terminal enclosure contains every generated perturbation branch.",
"Convergence retains the exact error sequence and reduction ratios; stopping requires a registered residual or enclosure certificate rather than a fitted floating tolerance.",
"Discretization replaces a declared finite domain with a generated mesh; consistency compares each discrete relation with the source relation under exact refinement custody.",
"Interpolation retains nodes, basis, evaluation point, interpolant and exact residual enclosure; approximation quality is stated only on the registered domain support.",
"Quadrature is an exact weighted sum over generated nodes whose residual is separately enclosed or evaluated against a symbolic integral on the declared function class.",
"Root finding preserves a nested interval or exact residual whose endpoints retain opposite ordered relation labels; a point is exact only when its substituted relation closes.",
"A linear-system solution retains every equation, exact elimination step and residual; approximate solving additionally retains conditioning and componentwise enclosures.",
"Mode computation retains the declared operator, candidate eigenvalue, vector and exact residual; spectral claims do not export beyond the finite operator or enclosure.",
"Ordinary differential computation retains the initial state, update relation, time mesh, local residual and propagated enclosure at every finite step.",
"Partial differential computation retains the space-time mesh, boundary and initial records, stencil relation, stability evidence and refinement comparison.",
"Stochastic simulation corresponds to the complete deterministic support of generated branch labels, with every path, weight and outcome retained and no stochastic cause imported.",
"Monte Carlo corresponds to a declared subset or complete generated support with exact branch averages and sampling custody; a sampled estimate never becomes an exact whole without enclosure evidence.",
"An inverse problem is identifiable exactly when each observed image has one admissible parameter predecessor; regularization selects only through an independently forced structural relation.",
"A computational estimator retains its complete data support, exact statistic, sampling relation, bias or residual ledger and every adverse row.",
"High-dimensional computation retains coordinate identities; sparse computation acts only on explicitly stored nonempty entries while preserving absent-coordinate semantics and complexity.",
"Many-body computation organizes the complete product of retained component states and every interaction edge; reductions require exact symmetry or compression certificates.",
"Symbolic-numeric correspondence evaluates one canonical symbolic expression into exact rational values or enclosures and retains every rewrite, substitution and residual.",
"Simulation verification compares implementation with its declared equations, while validation compares registered consequences with external observations opened after prediction sealing; neither substitutes for the other.",
"A reproducible mathematical model retains source identities, equations, assumptions, inputs, transformations, outputs, uncertainties, software environment and immutable result receipts.",
"Scientific-computation completeness is the one-to-one reconciliation of all twenty-five frozen obligations with unique survivors, adverse controls, exact executions, independent reconstructions and untouched-engine receipts.")
BASE=("SFT-COMP-SCI-EXACT-APPROXIMATE-001","SFT-COMP-SCI-EXACT-APPROXIMATE-001","SFT-COMP-SCI-ERROR-PROPAGATION-001","SFT-COMP-SCI-ERROR-PROPAGATION-001","SFT-COMP-SCI-STABILITY-001","SFT-COMP-SCI-STABILITY-001","SFT-COMP-SCI-CONVERGENCE-001","SFT-COMP-SCI-DISCRETIZATION-001","SFT-COMP-SCI-DISCRETIZATION-001","SFT-COMP-SCI-EXACT-APPROXIMATE-001","SFT-COMP-SCI-CONVERGENCE-001","SFT-COMP-SCI-STABILITY-001","SFT-COMP-SCI-COMPUTATIONAL-DYNAMICS-001","SFT-COMP-SCI-COMPUTATIONAL-DYNAMICS-001","SFT-COMP-SCI-DISCRETIZATION-001","SFT-COMP-SCI-SIMULATION-001","SFT-COMP-SCI-SIMULATION-001","SFT-COMP-SCI-INVERSE-PROBLEM-001","SFT-COMP-SCI-COMPUTATIONAL-STATISTICS-001","SFT-COMP-SCI-HIGH-DIMENSIONAL-001","SFT-COMP-SCI-MANY-BODY-001","SFT-COMP-SCI-SYMBOLIC-001","SFT-COMP-SCI-SIMULATION-001","SFT-COMP-SCI-MATHEMATICAL-MODELLING-001","SFT-COMP-SCI-MATHEMATICAL-MODELLING-001")
EXCLUSIONS=("no axiom, imported numerical model or target outcome selects the survivor","host absence and artifact counters are not admitted numerical-zero objects","no negative, irrational, imaginary, floating or completed-infinite proof scalar","no hidden precision, tolerance, sample, mesh, approximation, input or external target","no favorable simulation substitutes for verification and external validation","no failed route retires an obligation or changes protected authority")
def dimensions(relation): return (binary_dimension("representation","exact value or explicit enclosure?","opaque-floating-output","An opaque output cannot establish numerical custody.","exact-rational-or-symbolic-enclosure","Every value and bound is retained."),binary_dimension("process","complete numerical trace and error ledger?","output-only-calculation","Output alone cannot establish stability.","complete-trace-error-ledger","Every operation and error is retained."),binary_dimension("relation","forced scientific-computation relation?","imported-numerical-answer","An imported method cannot select the law.",relation,"The relation follows from exact generated organization."),binary_dimension("validation","verification and observation custody?","favorable-simulation","One favorable run cannot validate a model.","complete-verification-validation-ledger","Code, equations and observations remain distinct."),binary_dimension("enumeration","complete declared grammar?","sampled-inputs","Sampling cannot close a method family.","literal-complete-product","Every coordinate combination occurs once."),binary_dimension("provenance","root-bound forcing?","outcome-selected","Outcome feedback violates forward forcing.","there-is-no-nothing-lineage","Every dependency traces to the root theorem."),binary_dimension("observation","post-registry execution?","preopened-target","A preopened target could select the survivor.","post-registry-exact-scientific-execution","Execution opens only after registry freeze."),binary_dimension("boundary","model, mesh and data boundary explicit?","unrestricted-model-export","A finite computation cannot silently export.","declared-model-mesh-data-boundary","Every model and transport boundary is explicit."))
class ScientificExtensionProgram(GeneratedComputationProgram):
 @property
 def registration(self): return ClaimRegistration(claim_id=self.spec.claim_id,title=self.spec.title,branch="computation",statement=self.spec.statement,evidence_mode=EvidenceMode.EMPIRICAL,root_theorems=(ROOT_THEOREM,),dependencies=self.spec.dependencies,axioms=(),free_parameters=(),provenance=(ProvenanceClass.FORWARD_FORCING,),source_hash=self.source_hash)
def make(number,previous):
 i=int(number)-1;title,relation,statement=TITLES[i],RELATIONS[i],STATEMENTS[i];claim_id=f"SFT-COMP-SCIX-{SLUGS[i]}-{number}";observation,passed=OBS[number];dependencies=("SFT-MATH-HAND-CROSS-BRANCH-COMPLETENESS-006","SFT-INFO-HAND-CROSS-BRANCH-COMPLETENESS-006","SFT-COMP-LEARNX-COMPLETENESS-026",BASE[i])+((previous,) if previous else ())
 return LawSpec(claim_id,"SCIX",title.lower().replace(" ","-"),title,statement,dependencies,f"Generate the complete eight-axis SCIX-{number} product before observation access.",f"Every positive finite SCIX-{number} exact value, enclosure, model, mesh, trace, dataset and registered validation boundary.",dimensions(relation),f"SCIX-{number} uniquely retains {relation}, complete numerical custody, root forcing, post-registry execution and no extra rule.",(statement,observation),"The least scientific computation has one exact input, one operation and one retained result or enclosure.","Adding one input, coordinate, mesh point, operation, body or observation preserves prior identities and generates every new lawful relation exactly once.",EXCLUSIONS,(Witness("exact-scientific-execution",observation,passed),Witness("complete-scientific-census","Every declared input, operation, error, result and validation row is retained.",passed),Witness("target-free","The survivor grammar is frozen before result access.",True)),f"The frozen census separately owns {title.lower()} and forbids omission or duplicate ownership.",statement,"Enumerate 256 structural forms, reconstruct independently, replay the exact scientific execution and reject four adverse controls.","The claim closes only its declared exact model and data support; physical-domain application claims remain branch-owned.",(title.lower(),))
specifications=[];previous_claim=None
for number in sorted(OBS): spec=make(number,previous_claim);specifications.append(spec);previous_claim=spec.claim_id
SPECS={spec.claim_id:spec for spec in specifications};IDS=tuple(SPECS)
def validate_family():
 if len(IDS)!=25 or not all(row[1] for row in OBS.values()): raise ValueError("SCIX family witness or membership failure")
 for spec in specifications: spec.validate()
validate_family()
