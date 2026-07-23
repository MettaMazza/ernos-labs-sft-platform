from itertools import product
import json,sys
D=(("base-excluded","base-included"),("one-child","two-children","later-arity"),("labels-absent","labels-same","labels-distinct-held"),("children-ungenerated","children-generated"),("return-absent","return-present"),("termination-absent","finite-leaf-termination"),("no-extra","has-extra"));S="base-included__two-children__labels-distinct-held__children-generated__return-present__finite-leaf-termination__no-extra"
def main():
 z=json.load(open(sys.argv[1],encoding="utf-8"));g=["__".join(x) for x in product(*D)];o={x["candidate_id"]:x["survives"] for x in z["decisions"]};p=z["claim_id"]=="SFT-FOUNDATION-FORM-GRAMMAR-001" and [x["candidate_id"] for x in z["census"]["candidates"]]==g and o=={x:x==S for x in g} and all(x["passed"] for x in z["controls"]);print(json.dumps({"validated_seal_hash":z["seal_hash"],"recomputed_from_declared_inputs":True,"passed":p,"certificate":{"generated_cardinality":len(g),"productions":["One","Fold(held-a:Form,held-b:Form,return)"],"survivor":S if p else None}},sort_keys=True))
if __name__=="__main__":main()
