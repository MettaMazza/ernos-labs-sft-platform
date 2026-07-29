import json
from sft.materials.valid_001_012_laws_v1 import REGISTRY,ROOT,SPECS
from sft.materials.valid_001_012_external_v1 import load_vector
from sft.physics.structural_constants import candidate_rows,survivor_id
def test_products():
 for s in SPECS.values():
  r=candidate_rows(s);assert len(r)==256;assert sum(x["candidate_id"]==survivor_id(s) for x in r)==1
def test_memberships():
 assert tuple(REGISTRY["vector_claim_counts"][f"{n:03d}"] for n in range(1,13))==(8,9,10,14,7,12,12,10,22,62,271,271)
def test_vector():
 d=load_vector(ROOT);assert d["base_admitted_materials_claim_count"]==271;assert d["empirically_compared_claim_count"]==271;assert d["formal_only_explicit_boundary_count"]==0;assert d["base_measurement_line_count"]==1040;assert d["base_source_identity_occurrence_count"]==334
def test_all_rows_present():
 d=load_vector(ROOT);assert len(d["claims"])==271;assert all(r["model_admitted"] and r["all_rows_preserved"] for r in d["claims"])
