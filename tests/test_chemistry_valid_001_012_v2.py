import json
from sft.chemistry.valid_001_012_laws_v2 import REGISTRY,ROOT,SPECS
from sft.chemistry.valid_001_012_external_v2 import load_vector
from sft.physics.structural_constants import candidate_rows,survivor_id
def test_products():
 for s in SPECS.values():
  r=candidate_rows(s);assert len(r)==256;assert sum(x["candidate_id"]==survivor_id(s) for x in r)==1
def test_memberships():
 assert tuple(REGISTRY["vector_claim_counts"][f"{n:03d}"] for n in range(1,13))==(14,13,18,21,26,17,39,33,15,129,263,263)
def test_vector():
 d=load_vector(ROOT);assert d["base_admitted_chemistry_claim_count"]==263;assert d["empirically_compared_claim_count"]==255;assert d["formal_only_explicit_boundary_count"]==8;assert d["base_measurement_line_count"]==26486;assert d["base_source_identity_occurrence_count"]==1177
def test_all_rows_present():
 d=load_vector(ROOT);assert len(d["claims"])==263;assert all(r["model_admitted"] and r["all_rows_preserved"] for r in d["claims"])
