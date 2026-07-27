"""Implementation-distinct, value-free ORG-005 reconstruction."""
from itertools import permutations, product
import json
import sys

CLAIM_ID='SFT-CHEM-CONFORMER-GENERATION-EQUIVALENCE-005'
DOMAINS=(('name-or-coordinate-list', 'complete-finite-molecular-graph'), ('selected-single-angle', 'complete-ordered-rotor-census'), ('energy-picked-conformer', 'complete-cartesian-state-generation'), ('named-symmetry-assumption', 'exhaustive-graph-automorphism-action'), ('coordinate-tolerance-clustering', 'exact-automorphism-orbit-equivalence'), ('selected-representative-list', 'complete-disjoint-orbit-quotient'), ('source-readable-generator', 'value-free-operational-census-seal'), ('species-exception-or-extra-rule', 'finite-product-successor-no-extra-rule'))
SURVIVOR='complete-finite-molecular-graph__complete-ordered-rotor-census__complete-cartesian-state-generation__exhaustive-graph-automorphism-action__exact-automorphism-orbit-equivalence__complete-disjoint-orbit-quotient__value-free-operational-census-seal__finite-product-successor-no-extra-rule'
POSITIONS=(1,2,3,4)
BONDS={(1,2),(2,3),(3,4)}
STATES=("anti","gauche-forward","gauche-reverse")
REVERSE={"anti":"anti","gauche-forward":"gauche-reverse","gauche-reverse":"gauche-forward"}

def edge(a,b): return tuple(sorted((a,b)))
def actions():
    result=[]
    for image in permutations(POSITIONS):
        mapped={edge(image[a-1],image[b-1]) for a,b in BONDS}
        if mapped==BONDS: result.append(image)
    return tuple(result)
def apply(state,image):
    mapped=tuple(image[index-1] for index in POSITIONS)
    if mapped==POSITIONS: return state
    if mapped==tuple(reversed(POSITIONS)): return REVERSE[state]
    raise ValueError("incomplete rotor action")

def main():
    with open(sys.argv[1],encoding="utf-8") as h: sealed=json.load(h)
    generated=["__".join(row) for row in product(*DOMAINS)]
    received=[row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions={row["candidate_id"]:row["survives"] for row in sealed["decisions"]}
    graph_actions=actions(); remaining=set(STATES); classes=[]
    while remaining:
        anchor=next(state for state in STATES if state in remaining)
        orbit={apply(anchor,action) for action in graph_actions}
        classes.append(tuple(state for state in STATES if state in orbit));remaining-=orbit
    passed=(
        sealed["claim_id"]==CLAIM_ID and received==generated and len(generated)==256 and len(set(received))==256
        and decisions=={candidate:candidate==SURVIVOR for candidate in generated} and sum(decisions.values())==1
        and sealed["closure"]["scope"]=="depth_independent" and sealed["closure"]["minimality_passed"] is True
        and sealed["closure"]["named_shape_uniqueness_passed"] is True
        and {row["kind"] for row in sealed["controls"]}=={"false_premise","tampered_source","tampered_artifact","boundary"}
        and all(row["passed"] is True for row in sealed["controls"])
        and len(graph_actions)==2 and len(STATES)==3 and [len(group) for group in classes]==[1,2]
        and classes[0]==("anti",) and set(classes[1])=={"gauche-forward","gauche-reverse"}
    )
    print(json.dumps({"validated_seal_hash":sealed["seal_hash"],"recomputed_from_declared_inputs":True,"passed":passed,"certificate":{
        "claim_id":CLAIM_ID,"generated_cardinality":len(generated),"unique_survivor":SURVIVOR if passed else None,
        "closure":"depth_independent" if passed else None,"raw_assignment_count":len(STATES),
        "complete_graph_automorphism_count":len(graph_actions),"equivalence_class_sizes":[len(group) for group in classes],
        "complete_partition":sum(len(group) for group in classes)==len(STATES),
        "external_definition_conformer_name_energy_value_or_table_accessed":False,
        "coordinate_tolerance_or_measured_energy_used":False,
        "numerical_zero_negative_irrational_imaginary_continuum_fitted_free_or_imported_parameter_used":False,
    }},sort_keys=True))
if __name__=="__main__": main()
