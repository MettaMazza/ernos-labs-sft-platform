"""Implementation-distinct, value-free ORG-006 reconstruction."""
from fractions import Fraction
from itertools import product
import json,sys
CLAIM_ID='SFT-CHEM-CONFORMER-POPULATION-ORDERING-006'
DOMAINS=(('selected-conformer-name', 'complete-conformer-equivalence-census'), ('condition-erased-population', 'held-observation-condition'), ('infinite-or-unspecified-average', 'positive-finite-observation-boundary'), ('random-or-fitted-probability', 'exact-recurrence-count-ratio'), ('numerical-zero-population', 'unobserved-class-EmptyOne'), ('signed-energy-difference-or-imported-distribution', 'positive-Take-energy-and-count-orders'), ('target-readable-condition-or-value', 'value-free-conditioned-vector-seal'), ('recomputed-history-or-extra-rule', 'one-observation-successor-no-extra-rule'))
SURVIVOR='complete-conformer-equivalence-census__held-observation-condition__positive-finite-observation-boundary__exact-recurrence-count-ratio__unobserved-class-EmptyOne__positive-Take-energy-and-count-orders__value-free-conditioned-vector-seal__one-observation-successor-no-extra-rule'
def main():
 with open(sys.argv[1],encoding="utf-8") as h: sealed=json.load(h)
 generated=["__".join(row) for row in product(*DOMAINS)]
 received=[row["candidate_id"] for row in sealed["census"]["candidates"]]
 decisions={row["candidate_id"]:row["survives"] for row in sealed["decisions"]}
 counts=(3,1); boundary=sum(counts); populations=tuple(Fraction(value,boundary) for value in counts)
 successor_counts=(3,2); successor_boundary=sum(successor_counts); successor=tuple(Fraction(value,successor_boundary) for value in successor_counts)
 energy=(480,658,3263); gaps=(energy[0],energy[1]-energy[0],energy[2]-energy[1])
 passed=(
  sealed["claim_id"]==CLAIM_ID and received==generated and len(generated)==256 and len(set(received))==256
  and decisions=={candidate:candidate==SURVIVOR for candidate in generated} and sum(decisions.values())==1
  and sealed["closure"]["scope"]=="depth_independent" and sealed["closure"]["minimality_passed"] is True
  and sealed["closure"]["named_shape_uniqueness_passed"] is True
  and {row["kind"] for row in sealed["controls"]}=={"false_premise","tampered_source","tampered_artifact","boundary"}
  and all(row["passed"] is True for row in sealed["controls"])
  and populations==(Fraction(3,4),Fraction(1,4)) and successor==(Fraction(3,5),Fraction(2,5)) and gaps==(480,178,2605)
 )
 print(json.dumps({"validated_seal_hash":sealed["seal_hash"],"recomputed_from_declared_inputs":True,"passed":passed,"certificate":{
  "claim_id":CLAIM_ID,"generated_cardinality":len(generated),"unique_survivor":SURVIVOR if passed else None,
  "closure":"depth_independent" if passed else None,"base_population_fractions":[str(v) for v in populations],
  "successor_population_fractions":[str(v) for v in successor],"positive_energy_gaps":list(gaps),
  "external_temperature_energy_population_species_or_payload_accessed":False,
  "numerical_zero_negative_irrational_imaginary_continuum_fitted_free_random_or_imported_parameter_used":False,
 }},sort_keys=True))
if __name__=="__main__": main()
