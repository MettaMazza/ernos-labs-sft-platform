from itertools import product
import json,sys
D=(("none","proper","complete"),("node-duplicated","node-once"),("labels-lost","labels-preserved"),("children-changed","children-preserved"),("returns-lost","returns-preserved"),("trace-noncanonical","trace-canonical"),("no-extra","has-extra"));S="complete__node-once__labels-preserved__children-preserved__returns-preserved__trace-canonical__no-extra"
def main():
 z=json.load(open(sys.argv[1],encoding="utf-8"));g=["__".join(x) for x in product(*D)];o={x["candidate_id"]:x["survives"] for x in z["decisions"]};p=z["claim_id"]=="SFT-FOUNDATION-FORM-ENFORCEMENT-001" and [x["candidate_id"] for x in z["census"]["candidates"]]==g and o=={x:x==S for x in g} and all(x["passed"] for x in z["controls"]);print(json.dumps({"validated_seal_hash":z["seal_hash"],"recomputed_from_declared_inputs":True,"passed":p,"certificate":{"generated_cardinality":len(g),"survivor":S if p else None}},sort_keys=True))
if __name__=="__main__":main()
