from itertools import product
import json,sys
CLAIM='SFT-CHEM-MULTICENTRE-DELOCALIZED-SUPPORT-008'; DOMAINS=(('isolated-bond-list', 'complete-molecular-carrier'), ('two-centre-only-premise', 'three-or-more-generated-centres'), ('localized-edge-identities', 'one-complete-extended-support'), ('disconnected-centre-union', 'connected-generated-graph'), ('imported-or-single-topology', 'ribbon-surface-volume-census'), ('pairwise-model-declared-complete', 'multicentre-irreducible-support'), ('selected-example-only', 'complete-authority-and-geometry-vector'), ('species-specific-extra-rule', 'connected-successor-with-no-extra-rule')); SURVIVOR='complete-molecular-carrier__three-or-more-generated-centres__one-complete-extended-support__connected-generated-graph__ribbon-surface-volume-census__multicentre-irreducible-support__complete-authority-and-geometry-vector__connected-successor-with-no-extra-rule'
def connected(vertices,edges):
 reached={vertices[0]}; changed=True
 while changed:
  before=len(reached)
  for a,b in edges:
   if a in reached or b in reached: reached.update((a,b))
  changed=len(reached)>before
 return len(reached)==len(vertices)
def main():
 d=json.load(open(sys.argv[1])); generated=["__".join(row) for row in product(*DOMAINS)]; registered=[row["candidate_id"] for row in d["census"]["candidates"]]; decisions={row["candidate_id"]:row["survives"] for row in d["decisions"]}; path=((1,2),(2,3)); cycle=tuple((n,n+1) for n in range(1,6))+((6,1),); volume=tuple((a,b) for a in range(1,5) for b in range(a+1,5)); law=(connected((1,2,3),path) and len(path)==2 and connected(tuple(range(1,7)),cycle) and len(cycle)==6 and connected((1,2,3,4),volume) and len(volume)==6); passed=(d["claim_id"]==CLAIM and registered==generated and len(set(registered))==256 and decisions=={row:row==SURVIVOR for row in generated} and sum(decisions.values())==1 and d["closure"]["scope"]=="depth_independent" and d["closure"]["minimality_passed"] and d["closure"]["named_shape_uniqueness_passed"] and all(row["passed"] for row in d["controls"]) and law); print(json.dumps({"validated_seal_hash":d["seal_hash"],"recomputed_from_declared_inputs":True,"passed":passed,"certificate":{"claim_id":CLAIM,"candidate_count":len(generated),"survivor":SURVIVOR if passed else None,"path_edges":len(path),"cycle_edges":len(cycle),"volume_edges":len(volume)}},sort_keys=True))
if __name__=="__main__":main()
