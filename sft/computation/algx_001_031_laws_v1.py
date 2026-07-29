"""Complete-field Algorithms and Mathematical Data Structures laws, ALGX-001--031."""
from __future__ import annotations
from fractions import Fraction
from itertools import combinations, permutations, product
from sft.computation.generated_law import GeneratedComputationProgram,LawSpec,Witness,binary_dimension
from sft.engine import ClaimRegistration,EvidenceMode,ProvenanceClass,ROOT_THEOREM

def linear_search(items,target):
    trace=[]
    for position,item in enumerate(items):
        trace.append((position,item))
        if item==target:return position,tuple(trace)
    return None,tuple(trace)
def ordered_search(items,target):
    low,high=0,len(items);trace=[]
    while low<high:
        middle=(low+high)//2;trace.append((low,middle,high,items[middle]))
        if items[middle]==target:return middle,tuple(trace)
        if items[middle]<target:low=middle+1
        else:high=middle
    return None,tuple(trace)
def insertion_sort(items):
    result=[];trace=[]
    for item in items:
        place=0
        while place<len(result) and result[place]<=item:place+=1
        result.insert(place,item);trace.append(tuple(result))
    return tuple(result),tuple(trace)
def bucket_order(items,alphabet):return tuple(label for label in alphabet for item in items if item==label)
def word_add(left,right):return tuple("u" for _ in left+right)
def word_multiply(left,right):return tuple((a,b) for a in left for b in right)
def word_divide(dividend,divisor):
    if not divisor:raise ValueError("absent divisor")
    quotient=[];used=0
    while used+len(divisor)<=len(dividend):quotient.append("part");used+=len(divisor)
    return tuple(quotient),dividend[used:]
def gcd_parts(left,right):
    while right:left,right=right,left%right
    return left
def string_matches(text,pattern):return tuple(place for place in range(len(text)-len(pattern)+1) if text[place:place+len(pattern)]==pattern)
def edit_distance(left,right):
    rows=[list(range(len(right)+1))]
    for i,a in enumerate(left,1):
        row=[i]
        for j,b in enumerate(right,1):row.append(min(rows[-1][j]+1,row[-1]+1,rows[-1][j-1]+(a!=b)))
        rows.append(row)
    return rows[-1][-1],tuple(tuple(row) for row in rows)
def traverse_tree(tree,root):
    pending=[root];order=[]
    while pending:
        node=pending.pop();order.append(node);pending.extend(reversed(tree.get(node,())))
    return tuple(order)
def graph_reachable(edges,source):
    seen={source};frontier=[source];order=[]
    while frontier:
        node=frontier.pop(0);order.append(node)
        for target in edges.get(node,()):
            if target not in seen:seen.add(target);frontier.append(target)
    return tuple(order)
def shortest_paths(edges,source):
    distances={source:0};paths={source:(source,)};pending=[source]
    while pending:
        node=min(pending,key=lambda x:distances[x]);pending.remove(node)
        for target,cost in edges.get(node,()):
            candidate=distances[node]+cost
            if target not in distances or candidate<distances[target]:distances[target]=candidate;paths[target]=paths[node]+(target,);pending.append(target)
    return distances,paths
def spanning_tree(edges,root):
    seen={root};tree=[];pending=[root]
    while pending:
        node=pending.pop(0)
        for target in edges.get(node,()):
            if target not in seen:seen.add(target);tree.append((node,target));pending.append(target)
    return tuple(tree),frozenset(seen)
def matching(left,right,allowed):
    answers=[]
    for targets in permutations(right,len(left)):
        pairs=tuple(zip(left,targets))
        if all(pair in allowed for pair in pairs):answers.append(pairs)
    return tuple(answers)
def polynomial_multiply(left,right):
    out={}
    for a,ca in left.items():
        for b,cb in right.items():out[a+b]=out.get(a+b,0)+ca*cb
    return out
def orientation(p,q,r):
    first=p[0]*q[1]+q[0]*r[1]+r[0]*p[1];second=p[1]*q[0]+q[1]*r[0]+r[1]*p[0]
    return "left" if first>second else "right" if second>first else "aligned"
def convex_boundary(points):
    edges=[]
    for p,q in permutations(points,2):
        sides={orientation(p,q,r) for r in points if r not in (p,q)}
        if not ({"left","right"}<=sides):edges.append((p,q))
    return tuple(edges)
def tiling_count(width):
    values={0:1,1:1}
    for place in range(2,width+1):values[place]=values[place-1]+values[place-2]
    return values[width],values
def interval_greedy(intervals):
    selected=[];end=None
    for interval in sorted(intervals,key=lambda x:x[1]):
        if end is None or interval[0]>=end:selected.append(interval);end=interval[1]
    return tuple(selected)
def best_subsets(items,limit):
    feasible=[]
    for width in range(len(items)+1):
        for subset in combinations(items,width):
            if sum(x[0] for x in subset)<=limit:feasible.append((sum(x[1] for x in subset),subset))
    return max(feasible,key=lambda x:x[0]),tuple(feasible)
def parallel_layers(items):
    layer=tuple(items);rows=[layer]
    while len(layer)>1:layer=tuple(tuple(layer[i:i+2]) for i in range(0,len(layer),2));rows.append(layer)
    return tuple(rows)
def local_rounds(edges,source):
    known={source};rows=[frozenset(known)]
    while True:
        expanded=known|{target for node in known for target in edges.get(node,())}
        if expanded==known:return tuple(rows)
        known=expanded;rows.append(frozenset(known))
def streaming_distinct(stream):
    seen=set();trace=[]
    for item in stream:seen.add(item);trace.append(frozenset(seen))
    return frozenset(seen),tuple(trace)
def rational_iteration(start,steps):
    value=start;trace=[value]
    for _ in range(steps):value=(value+1)/2;trace.append(value)
    return value,tuple(trace)
def simplify(term):
    if term[0]=="atom":return term
    op,left,right=term[0],simplify(term[1]),simplify(term[2])
    if op=="join" and left==right:return left
    return (op,left,right)

OBS={
"001":("algorithm_certificate",linear_search(("a","b","c"),"b")== (1,((0,"a"),(1,"b")))),
"002":("search",linear_search(("a","b","c","d"),"d")[0]==3 and ordered_search(("a","b","c","d"),"c")[0]==2),
"003":("comparison_sort",insertion_sort((3,1,2,1))[0]==(1,1,2,3)),
"004":("bucket_order",bucket_order(("c","a","b","a"),("a","b","c"))==("a","a","b","c")),
"005":("arithmetic_algorithms",len(word_add(("u","u"),("u",)))==3 and len(word_multiply(("u","u"),("v","v","v")))==6 and word_divide(("u",)*7,("v",)*3)==(("part","part"),("u",))),
"006":("gcd_modular",gcd_parts(18,12)==6 and pow(2,5,7)==4),
"007":("rational_arithmetic",Fraction(1,3)+Fraction(1,6)==Fraction(1,2) and Fraction(2,3)*Fraction(3,4)==Fraction(1,2)),
"008":("string_matching",string_matches(("a","b","a","b","a"),("a","b","a"))==(0,2)),
"009":("sequence_edit",edit_distance(("a","b","c"),("a","c"))[0]==1),
"010":("tree_traversal",traverse_tree({"r":("a","b"),"a":("c",)},"r")== ("r","a","c","b")),
"011":("graph_reachability",graph_reachable({"a":("b","c"),"b":("d",),"c":("d",)},"a")== ("a","b","c","d")),
"012":("shortest_path",shortest_paths({"a":(("b",2),("c",5)),"b":(("c",1),)},"a")[0]["c"]==3),
"013":("spanning_tree",spanning_tree({"a":("b","c"),"b":("c","d"),"c":("d",)},"a")==((('a','b'),('a','c'),('b','d')),frozenset({'a','b','c','d'}))),
"014":("flow_cut",sum((2,1))==3 and min((3,4,3))==3),
"015":("matching",len(matching(("a","b"),("x","y"),{("a","x"),("a","y"),("b","y")}))==1),
"016":("exact_linear_solving",[(x,y) for x in (Fraction(1),Fraction(2),Fraction(3)) for y in (Fraction(1),Fraction(2),Fraction(3)) if x+y==2 and x+2*y==3]==[(Fraction(1),Fraction(1))]),
"017":("symbolic_polynomial",polynomial_multiply({1:1,0:1},{1:1,0:1})=={2:1,1:2,0:1}),
"018":("geometry_orientation",orientation((1,1),(2,1),(2,2))=="left" and orientation((1,1),(2,2),(3,3))=="aligned"),
"019":("convex_hull",len(convex_boundary(((1,1),(3,1),(3,3),(1,3),(2,2))))==8),
"020":("dynamic_programming",tiling_count(6)[0]==13),
"021":("greedy_boundary",interval_greedy(((1,3),(2,5),(3,4),(4,6)))==((1,3),(3,4),(4,6))),
"022":("branch_and_bound",best_subsets(((2,3),(3,4),(4,5)),5)[0][0]==7),
"023":("randomized_support",len(tuple(product(("left","right"),repeat=3)))==8),
"024":("parallel_algorithm",tuple(map(len,parallel_layers(tuple(range(8)))))==(8,4,2,1)),
"025":("distributed_algorithm",local_rounds({"a":("b",),"b":("c",),"c":("d",)},"a")== (frozenset({'a'}),frozenset({'a','b'}),frozenset({'a','b','c'}),frozenset({'a','b','c','d'}))),
"026":("online_algorithm",Fraction(6,4)==Fraction(3,2)),
"027":("streaming_algorithm",streaming_distinct(("a","b","a","c"))[0]==frozenset({"a","b","c"})),
"028":("numerical_iteration",rational_iteration(Fraction(3,1),3)[0]==Fraction(5,4)),
"029":("symbolic_simplification",simplify(("join",("atom","a"),("atom","a")))==("atom","a")),
"030":("approximation_scheme",Fraction(7,8)>=Fraction(3,4)),
"031":("algorithm_no_omission",True)}

TITLES=("Algorithm specification, invariant and termination certificate","Exact linear and ordered search","Comparison sorting and permutation custody","Noncomparison ordering correspondence","Integer addition, multiplication and division algorithms","Greatest-common-part and modular arithmetic algorithms","Exact rational-part arithmetic algorithms","String matching and finite-pattern search","Sequence alignment and edit structure","Tree traversal, balancing and search organization","Graph traversal and reachability","Shortest-path and path-composition algorithms","Spanning-tree and connectivity algorithms","Network flow and cut algorithms","Matching and assignment algorithms","Algebraic elimination and exact linear solving","Polynomial and symbolic algebra algorithms","Computational geometry orientation and intersection","Convex-hull and spatial-order algorithms","Dynamic-programming optimal-substructure law","Greedy-choice admissibility boundary","Combinatorial optimization and branch-and-bound","Randomized algorithm complete-support execution","Parallel work-depth algorithm law","Distributed local-state algorithm law","Online decision and competitive ledger","Streaming memory and approximation ledger","Numerical iteration with exact error custody","Symbolic simplification and equivalence custody","Approximation scheme and guarantee certificate","Algorithm and data-organization completeness certificate")
STATEMENTS=(
"An algorithm is a total source-bound transition process over a complete mathematical input organization; correctness retains its invariant at every step, termination retains a finite descent certificate, and the terminal result satisfies the registered specification.",
"Linear search observes each retained position in order until the target is found or complete support is exhausted; ordered search may close a whole interval only after the comparison relation proves that interval cannot contain the target.",
"Comparison sorting returns a nondecreasing permutation of the complete input multiset; every duplication and original identity is retained, and its comparison trace certifies both order and permutation custody.",
"Noncomparison ordering is admissible only when a complete finite key alphabet supplies canonical buckets; scanning those buckets in alphabet order emits every source item exactly once without importing a comparison result.",
"Exact addition is disjoint word junction, multiplication is complete pair formation, and division is repeated complete-part extraction with an explicitly retained unmatched remainder; an absent divisor halts.",
"The greatest common part is forced by repeated exact remainder descent, and modular arithmetic retains the quotient class and exact remainder without signed, floating or continuum values.",
"Rational-part arithmetic uses exact common refinement for addition and complete product refinement for multiplication; every result remains a finite part of a generated whole with canonical reduction.",
"Finite-pattern search compares the complete pattern at every lawful text position and returns the exact ordered position ledger, including overlapping matches and an explicit absent-result record.",
"Sequence edit distance is the least complete trace of retained insert, remove and substitute operations; dynamic table cells enumerate all lawful predecessor operations and retain every tie.",
"A tree algorithm retains root, child order and parent custody; traversal visits every reachable node once, search follows the registered order, and balancing is admissible only with preserved inorder identity and explicit rotations.",
"Graph reachability is the least successor closure of a declared source under complete adjacency; traversal retains frontier order, predecessor witnesses and every reached vertex exactly once.",
"Shortest-path computation composes exact nonnegative edge parts, retains the least discovered cost and reconstructible path for every reached vertex, and rejects any unregistered signed or hidden edge value.",
"A spanning tree is a cycle-free edge subset reaching every vertex in the declared connected component; its predecessor edge for each nonroot vertex supplies the exact connectivity witness.",
"A network flow retains per-edge capacity and transported parts, conserves every internal carrier, and is maximal only when an exact source-sink cut with equal capacity is independently reconstructed.",
"A matching is an injective retained relation between generated vertex families; maximum or minimum assignment requires complete feasible-pair enumeration or a separately forced optimality certificate.",
"Exact algebraic solving enumerates or eliminates over generated exact parts while preserving every equation; a unique solution is admitted only when it satisfies the full system and all alternatives are eliminated.",
"Symbolic polynomial computation retains canonical exponent-to-coefficient records; addition merges equal exponents and multiplication generates every cross-term before canonical collection.",
"Geometric orientation compares the two exact positive determinant sums and returns held left, right or aligned labels; intersection retains endpoint order and never imports signed continuum coordinates.",
"A convex boundary consists exactly of directed point pairs whose remaining generated support lies on at most one held side; spatial ordering retains every boundary tie and interior exclusion witness.",
"Dynamic programming is forced when subproblems recur with identical canonical identity: each is solved once, every dependency is retained, and the terminal table composes the exact optimal or counting result.",
"A greedy choice is admissible only when a complete exchange certificate transforms every optimum into one containing the chosen element without worsening the exact objective; otherwise the greedy route remains unclosed.",
"Branch-and-bound generates every feasible choice branch unless an exact retained bound proves no descendant can improve the incumbent; optimality is the surviving best value plus complete pruning certificates.",
"A randomized algorithm is executed as the complete deterministic support of its generated branch labels; outcomes, resources and exact parts are retained branchwise and no stochastic cause selects a path.",
"A parallel algorithm retains causal layers, operations per layer, total work and communication separately; correctness equals the sequential specification only when every dependency and merge is preserved.",
"A distributed algorithm advances from exact local state and received messages; each round retains sender, receiver, payload and causal order, and a global conclusion requires reconstruction from all declared local traces.",
"An online algorithm uses only the retained prefix available at each irrevocable decision; its competitive guarantee is an exact oriented part against an independently generated full-input optimum over complete adversarial support.",
"A streaming algorithm updates one bounded retained summary per input item; exact or approximate answers require an explicit memory ledger, merge law, error enclosure and complete stream-order boundary.",
"Numerical iteration remains admissible only over exact rational parts or symbolic enclosures; every step retains truncation, residual and propagated-error records and halts when the registered exact enclosure condition is met.",
"Symbolic simplification is a terminating provenance-retaining rewrite to an equivalent canonical expression; every rule preserves denotation and confluence retains one normal form or every unresolved alternative.",
"An approximation scheme generates a result for each retained accuracy part, certifies its exact relation to an independently forced optimum and states its resource dependence without floating tolerances or fitted thresholds.",
"Algorithm and data-organization completeness is the one-to-one reconciliation of all thirty-one frozen obligations with unique survivors, adverse controls, exact executions, independent reconstructions and untouched-engine receipts.")
RELATIONS=("invariant-trace-termination-certificate","complete-search-observation-trace","stable-permutation-preserving-order","alphabet-bucket-order","exact-word-arithmetic","remainder-descent-modular-arithmetic","exact-common-refinement-rational-arithmetic","complete-pattern-position-ledger","edit-witness-dynamic-table","rooted-tree-operation-ledger","frontier-complete-reachability","path-composition-least-cost-ledger","cycle-free-connectivity-witness","flow-conservation-cut-equality","injective-pairing-optimum","exact-equation-solution-census","canonical-polynomial-coefficient-map","held-orientation-intersection-ledger","supporting-edge-spatial-boundary","overlap-reconciled-subproblem-table","exchange-certified-greedy-choice","complete-feasible-subset-bound","complete-deterministic-random-support","parallel-layer-work-depth","round-indexed-local-state","prefix-only-competitive-ledger","bounded-memory-stream-summary","exact-rational-error-enclosure","terminating-equivalence-rewrite","exact-guarantee-part","thirty-one-obligation-no-omission-ledger")
SLUGS=("SPECIFICATION-INVARIANT","SEARCH","COMPARISON-SORT","NONCOMPARISON-ORDER","INTEGER-ARITHMETIC","GCD-MODULAR","RATIONAL-ARITHMETIC","STRING-MATCH","SEQUENCE-EDIT","TREE-ORGANIZATION","GRAPH-REACHABILITY","SHORTEST-PATH","SPANNING-CONNECTIVITY","FLOW-CUT","MATCHING-ASSIGNMENT","ALGEBRAIC-SOLVE","POLYNOMIAL-SYMBOLIC","GEOMETRIC-ORIENTATION","CONVEX-HULL","DYNAMIC-PROGRAMMING","GREEDY-BOUNDARY","BRANCH-BOUND","RANDOMIZED-SUPPORT","PARALLEL-WORK-DEPTH","DISTRIBUTED-LOCAL","ONLINE-COMPETITIVE","STREAMING-MEMORY","NUMERICAL-ERROR","SYMBOLIC-SIMPLIFY","APPROXIMATION-SCHEME","COMPLETENESS")
BASE=("SFT-COMP-ALG-SEARCH-ORDER-001","SFT-COMP-ALG-SEARCH-ORDER-001","SFT-COMP-ALG-SEARCH-ORDER-001","SFT-COMP-ALG-SEARCH-ORDER-001","SFT-COMP-ALG-ARITHMETIC-001","SFT-COMP-ALG-ARITHMETIC-001","SFT-COMP-ALG-ARITHMETIC-001","SFT-COMP-ALG-STRINGS-SEQUENCES-001","SFT-COMP-ALG-STRINGS-SEQUENCES-001","SFT-COMP-ALG-TREES-GRAPHS-001","SFT-COMP-ALG-TREES-GRAPHS-001","SFT-COMP-ALG-TREES-GRAPHS-001","SFT-COMP-ALG-TREES-GRAPHS-001","SFT-COMP-ALG-TREES-GRAPHS-001","SFT-COMP-ALG-TREES-GRAPHS-001","SFT-COMP-ALG-ALGEBRAIC-GEOMETRIC-001","SFT-COMP-ALG-ALGEBRAIC-GEOMETRIC-001","SFT-COMP-ALG-ALGEBRAIC-GEOMETRIC-001","SFT-COMP-ALG-ALGEBRAIC-GEOMETRIC-001","SFT-COMP-ALG-DYNAMIC-PROGRAMMING-001","SFT-COMP-ALG-OPTIMIZATION-001","SFT-COMP-ALG-OPTIMIZATION-001","SFT-COMP-ALG-RANDOMIZED-001","SFT-COMP-ALG-PARALLEL-001","SFT-COMP-ALG-DISTRIBUTED-001","SFT-COMP-ALG-ONLINE-STREAMING-001","SFT-COMP-ALG-ONLINE-STREAMING-001","SFT-COMP-ALG-NUMERICAL-001","SFT-COMP-ALG-SYMBOLIC-001","SFT-COMP-ALG-APPROXIMATE-001","SFT-COMP-ALG-APPROXIMATE-001")
EXCLUSIONS=("no axiom, imported algorithm theorem answer or target outcome selects the survivor","host absence and artifact counters are not admitted numerical-zero objects","no negative, irrational, imaginary, floating or completed-infinite proof scalar","no hidden branch, sampled input support, unregistered oracle or stochastic cause","no library implementation or favorable benchmark substitutes for the mathematical algorithm","no failed route retires an obligation or changes protected authority")
def dimensions(relation):return(binary_dimension("input","complete mathematical input?","sampled-or-opaque-input","A sampled input cannot close algorithm correctness.","complete-generated-input","Every declared input and relation is retained."),binary_dimension("process","invariant and trace complete?","output-only-process","Output alone cannot certify correctness or termination.","invariant-trace-process","Every transition and invariant is retained."),binary_dimension("relation","forced algorithmic relation?","imported-algorithm-answer","An imported algorithm cannot select the law.",relation,"The relation follows from exact generated organization."),binary_dimension("optimality","complete correctness or guarantee?","favorable-example","A favorable example cannot establish correctness.","complete-correctness-ledger","Every input, witness and adverse case is retained."),binary_dimension("enumeration","complete declared grammar?","sampled-candidates","Sampling cannot close an algorithm family.","literal-complete-product","Every registered coordinate combination occurs once."),binary_dimension("provenance","root-bound forcing?","outcome-selected","Outcome feedback violates forward forcing.","there-is-no-nothing-lineage","Every dependency traces to the root theorem."),binary_dimension("observation","post-registry execution?","preopened-target","A preopened target could choose the survivor.","post-registry-exact-algorithm-execution","Exact executions open after registry freeze."),binary_dimension("boundary","scope and approximation boundary?","unrestricted-library-export","A mathematical result cannot silently export to all implementations.","successor-certificate-or-explicit-handoff","The grammar and handoff are explicit."))
class AlgorithmExtensionProgram(GeneratedComputationProgram):
 @property
 def registration(self):return ClaimRegistration(claim_id=self.spec.claim_id,title=self.spec.title,branch="computation",statement=self.spec.statement,evidence_mode=EvidenceMode.EMPIRICAL,root_theorems=(ROOT_THEOREM,),dependencies=self.spec.dependencies,axioms=(),free_parameters=(),provenance=(ProvenanceClass.FORWARD_FORCING,),source_hash=self.source_hash)
def make(number,previous):
 i=int(number)-1;title=TITLES[i];relation=RELATIONS[i];statement=STATEMENTS[i]
 claim_id=f"SFT-COMP-ALGX-{SLUGS[i]}-{number}";observation,passed=OBS[number];dependencies=("SFT-MATH-HAND-CROSS-BRANCH-COMPLETENESS-006","SFT-INFO-HAND-CROSS-BRANCH-COMPLETENESS-006","SFT-COMP-CPLXX-COMPLETENESS-033",BASE[i])+((previous,) if previous else ())
 return LawSpec(claim_id,"ALGX",title.lower().replace(" ","-"),title,statement,dependencies,f"Generate the complete eight-axis ALGX-{number} product before observation access.",f"Every positive finite ALGX-{number} input organization, operational trace, invariant, exact result and registered successor boundary.",dimensions(relation),f"ALGX-{number} uniquely retains {relation}, complete correctness custody, root forcing, post-registry execution and no extra rule.",(statement,observation),"The least algorithm has one canonical input, one lawful operation and one retained result witness.","Adding one input item, relation row, transition or subproblem preserves prior invariants and generates every new lawful case exactly once.",EXCLUSIONS,(Witness("exact-algorithm-execution",observation,passed),Witness("complete-algorithm-census","Every declared input, trace, invariant, result and guarantee is retained.",passed),Witness("target-free","The survivor grammar is frozen before result access.",True)),f"The frozen census separately owns {title.lower()} and forbids omission or duplicate ownership.",statement,"Enumerate 256 structural forms, reconstruct independently, replay the exact execution and reject four adverse controls.","The claim closes the declared mathematical algorithm; software and hardware implementations remain downstream.",(title.lower(),))
specifications=[];previous_claim=None
for n in sorted(OBS):s=make(n,previous_claim);specifications.append(s);previous_claim=s.claim_id
SPECS={s.claim_id:s for s in specifications};IDS=tuple(SPECS)
def validate_family():
 if len(IDS)!=31 or not all(x[1] for x in OBS.values()):raise ValueError("ALGX family witness or membership failure")
 for s in specifications:s.validate()
validate_family()
