"""Post-seal IUPAC bindings for thermochemistry, phase and photochemistry."""
from __future__ import annotations
import json
from pathlib import Path
from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.chemistry.thermochemistry_derivation import THERMOCHEMISTRY_BLUEPRINTS
from sft.engine.canonical import sha256_identity
from sft.engine.source import hash_file
ROOT=Path(__file__).resolve().parent.parent.parent
DERIVATION_PATH="sft/chemistry/thermochemistry_derivation.py"
DERIVATION_HASH="sha256:2f8e10639b626a3108429b920806dff78a7292ec750a7c74c9a35a43d3c7cdd2"
PRE_SOURCE_SEAL_PATH="experiments/sealed_predictions/chemistry_thermochemistry_batch_1_pre_source.json"
PRE_SOURCE_PAYLOAD_HASH="sha256:58e46c68b49f729d29d799de0b50b9f8459034cbc8bf3027e61beecb751dfa04"
OBSERVATION_REGISTRY_PATH="experiments/external_sources/chemistry/observations_thermochemistry_batch_1.json"
SOURCE_RECORDS={
"SFT-CHEM-THERMO-REACTION-001":("reaction-thermochemistry-iupac-composite","IUPAC-GOLD-BOOK-REACTION-THERMOCHEMISTRY-COMPOSITE-2026","S05923","experiments/external_sources/chemistry/snapshots/goldbook-terms/S05923.json","sha256:e976fc5090d3344af00af1a64fea3bc564f126f53d920a0387c1fbf56ba07bf6"),
"SFT-CHEM-THERMO-DIRECTION-001":("reaction-direction-iupac-composite","IUPAC-GOLD-BOOK-REACTION-DIRECTION-COMPOSITE-2026","A00178","experiments/external_sources/chemistry/snapshots/goldbook-terms/A00178.json","sha256:29e64f1b53aba905340496145e5393f853b118f32684689de8e79c573e2642ef"),
"SFT-CHEM-PHASE-CHEMICAL-001":("chemical-phase-iupac-composite","IUPAC-GOLD-BOOK-CHEMICAL-PHASE-COMPOSITE-2026","P04528","experiments/external_sources/chemistry/snapshots/goldbook-terms/P04528.json","sha256:c903c27903b67f47a61403a4de408c23bb21c50100ee37e5d05e9a8aa168c4eb"),
"SFT-CHEM-SOLUTION-EQUILIBRIUM-001":("solution-equilibrium-iupac-composite","IUPAC-GOLD-BOOK-SOLUTION-EQUILIBRIUM-COMPOSITE-2026","14656","experiments/external_sources/chemistry/snapshots/goldbook-terms/14656.json","sha256:bd07661ff6120f150e0a53e67a72b1e212293bf96bfad41628c1e8f7ec9ffdcb"),
"SFT-CHEM-PHOTOCHEM-001":("photochemistry-iupac-composite","IUPAC-GOLD-BOOK-PHOTOCHEMISTRY-COMPOSITE-2026","P04585","experiments/external_sources/chemistry/snapshots/goldbook-terms/P04585.json","sha256:5e052ba4dda35e0152ec2de28c4d90a748933bd99a82481d5b0b31d9f0c0ed3d")}
def validate_pre_source_seal():
    if hash_file(ROOT/DERIVATION_PATH)!=DERIVATION_HASH: raise ValueError("thermochemistry derivation changed after seal")
    seal=json.loads((ROOT/PRE_SOURCE_SEAL_PATH).read_text(encoding="utf-8")); claimed=seal.pop("sealed_payload_hash",None)
    if claimed!=PRE_SOURCE_PAYLOAD_HASH or sha256_identity(seal)!=PRE_SOURCE_PAYLOAD_HASH: raise ValueError("thermochemistry seal invalid")
    expected=[{"claim_id":r.claim_id,"exact_result":r.exact_result,"predicted_observation_label":r.predicted_observation_label} for r in THERMOCHEMISTRY_BLUEPRINTS]
    if seal.get("claim_predictions")!=expected or seal.get("external_source_identities_selected") is not False or seal.get("external_target_content_opened") is not False: raise ValueError("thermochemistry pre-source boundary invalid")
def _bind(b):
    tid,sid,code,path,digest=SOURCE_RECORDS[b.claim_id]
    return EmpiricalChemistrySpec(claim_id=b.claim_id,title=b.title,statement=b.statement,dependencies=b.dependencies,generation_rule=b.generation_rule,grammar_boundary=b.grammar_boundary,dimensions=b.dimensions,exact_result=b.exact_result,induction_base=b.induction_base,induction_step=b.induction_step,exclusions=b.exclusions,operational_witnesses=b.operational_witnesses,experiment_id=b.experiment_id,expected_observation_label=b.predicted_observation_label,target_rows=(ChemistryTargetReference(tid,sid,f"official IUPAC source set anchored at {code}",path,digest),),observation_registry_path=OBSERVATION_REGISTRY_PATH,falsification_condition=b.falsification_condition)
validate_pre_source_seal()
THERMOCHEMISTRY_BATCH_1_SPECS=tuple(_bind(r) for r in THERMOCHEMISTRY_BLUEPRINTS)
for _spec in THERMOCHEMISTRY_BATCH_1_SPECS: _spec.validate()
__all__=("THERMOCHEMISTRY_BATCH_1_SPECS","validate_pre_source_seal")
