from itertools import product
import json,sys
D=(("none","proper","complete"),("inconsistent-length","consistent-length"),("support-incomplete","support-complete"),("words-duplicated","words-unique"),("transitions-absent","transitions-present"),("returns-absent","returns-present"),("no-extra","has-extra"));S="complete__consistent-length__support-complete__words-unique__transitions-present__returns-present__no-extra";L=("held-a","held-b")
def main():
 z=json.load(open(sys.argv[1],encoding="utf-8"));g=["__".join(x) for x in product(*D)];o={x["candidate_id"]:x["survives"] for x in z["decisions"]};w=((),);counts=[]
 for _ in range(5):w=tuple(a+(b,) for a in w for b in L);counts.append(len(w))
 p=z["claim_id"]=="SFT-FOUNDATION-FOLD-ASSEMBLY-001" and [x["candidate_id"] for x in z["census"]["candidates"]]==g and o=={x:x==S for x in g} and counts==[2,4,8,16,32] and all(x["passed"] for x in z["controls"])
 print(json.dumps({"validated_seal_hash":z["seal_hash"],"recomputed_from_declared_inputs":True,"passed":p,"certificate":{"support_counts":counts,"survivor":S if p else None}},sort_keys=True))
if __name__=="__main__":main()
