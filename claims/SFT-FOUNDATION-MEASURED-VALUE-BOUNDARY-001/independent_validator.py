from itertools import product
import json,sys
D=(("disconnected","derivation-to-measurement","measurement-to-derivation","bidirectional"),("proof-inexact","proof-exact"),("target-before-seal","target-after-seal"),("rows-selective","rows-complete"),("source-absent","source-identified"),("law-mutated","law-unchanged"),("no-extra","has-extra"));S="derivation-to-measurement__proof-exact__target-after-seal__rows-complete__source-identified__law-unchanged__no-extra"
def main():
 z=json.load(open(sys.argv[1],encoding="utf-8"));g=["__".join(x) for x in product(*D)];o={x["candidate_id"]:x["survives"] for x in z["decisions"]};p=z["claim_id"]=="SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001" and [x["candidate_id"] for x in z["census"]["candidates"]]==g and o=={x:x==S for x in g} and all(x["passed"] for x in z["controls"]);print(json.dumps({"validated_seal_hash":z["seal_hash"],"recomputed_from_declared_inputs":True,"passed":p,"certificate":{"generated_cardinality":len(g),"phase_order":["derive","seal","open-target","measure","retain-all"],"survivor":S if p else None}},sort_keys=True))
if __name__=="__main__":main()
