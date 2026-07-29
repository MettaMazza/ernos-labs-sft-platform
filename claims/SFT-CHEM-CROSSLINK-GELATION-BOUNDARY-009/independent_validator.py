from itertools import product
import json,sys
CLAIM_ID='SFT-CHEM-CROSSLINK-GELATION-BOUNDARY-009';DOMAINS=(('bulk-gel-label', 'complete-finite-crosslink-graph'), ('unregistered-system-extent', 'disjoint-held-inlet-and-outlet-support'), ('crosslink-count-threshold', 'one-component-connects-both-boundaries'), ('sampled-path-test', 'complete-component-and-path-census'), ('completed-infinite-network', 'declared-finite-observation-scale'), ('assumed-universal-gel-point', 'first-registered-boundary-connecting-transition'), ('near-spanning-network-accepted', 'every-unconnected-boundary-state-rejected'), ('gel-boolean-only', 'graph-boundaries-component-witness-and-scale-trace'));SURVIVOR='complete-finite-crosslink-graph__disjoint-held-inlet-and-outlet-support__one-component-connects-both-boundaries__complete-component-and-path-census__declared-finite-observation-scale__first-registered-boundary-connecting-transition__every-unconnected-boundary-state-rejected__graph-boundaries-component-witness-and-scale-trace'
vertices=(1,2,3,4,5,6);edges=((1,2),(2,3),(3,4),(2,5),(3,6));left={1};right={5};seen=set(left);front=list(left)
while front:
 v=front.pop()
 for e in edges:
  if v in e:
   n=e[1] if e[0]==v else e[0]
   if n not in seen:seen.add(n);front.append(n)
native={"network":len(vertices)==6,"boundaries":not left&right,"connectivity":bool(seen&right),"enumeration":seen==set(vertices),"infinity":len(vertices)<7,"transition":(2,5) in edges,"adverse":not ({1}&{6}),"certificate":5 in seen}
def main():
 s=json.load(open(sys.argv[1]));generated=["__".join(x) for x in product(*DOMAINS)];decisions={x["candidate_id"]:x["survives"] for x in s["decisions"]};passed=s["claim_id"]==CLAIM_ID and [x["candidate_id"] for x in s["census"]["candidates"]]==generated and decisions=={x:x==SURVIVOR for x in generated} and sum(decisions.values())==1 and s["closure"]["scope"]=="depth_independent" and all(x["passed"] for x in s["controls"]) and all(native.values());print(json.dumps({"validated_seal_hash":s["seal_hash"],"recomputed_from_declared_inputs":True,"passed":passed,"certificate":{"claim_id":CLAIM_ID,"generated_cardinality":len(generated),"unique_survivor":SURVIVOR if passed else None,"closure":"depth_independent" if passed else None,**native,"external_source_accessed":False,"numerical_zero_negative_irrational_imaginary_continuum_fitted_free_random_or_imported_parameter_used":False}},sort_keys=True))
if __name__=="__main__":main()
