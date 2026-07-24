"""Post-seal IUPAC bindings for reaction, kinetics and equilibrium."""
from __future__ import annotations
import json
from pathlib import Path
from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.chemistry.reaction_kinetics_derivation import REACTION_KINETICS_BLUEPRINTS
from sft.engine.canonical import sha256_identity
from sft.engine.source import hash_file
ROOT=Path(__file__).resolve().parent.parent.parent
DERIVATION_PATH="sft/chemistry/reaction_kinetics_derivation.py"
DERIVATION_HASH="sha256:e9d1d1c9ad3b85bf255ed26366e3b7faca2b13304d8b8902012ce00fd80c2f71"
PRE_SOURCE_SEAL_PATH="experiments/sealed_predictions/chemistry_reaction_kinetics_batch_1_pre_source.json"
PRE_SOURCE_PAYLOAD_HASH="sha256:d6086a65f24088d03fba86125405fe384473d645fceea026a0bc0b272d98cdd5"
OBSERVATION_REGISTRY_PATH="experiments/external_sources/chemistry/observations_reaction_kinetics_batch_1.json"
SOURCE_RECORDS={
"SFT-CHEM-RXN-IDENTITY-001":("chemical-reaction-iupac-composite","IUPAC-GOLD-BOOK-CHEMICAL-REACTION-COMPOSITE-2026","C01033","experiments/external_sources/chemistry/snapshots/goldbook-terms/C01033.json","sha256:83d7891114ad65c012ce2e35f4021beaee6a37d4473c416170d6643db4dc7347"),
"SFT-CHEM-RXN-MECHANISM-001":("reaction-mechanism-iupac-composite","IUPAC-GOLD-BOOK-REACTION-MECHANISM-COMPOSITE-2026","M03804","experiments/external_sources/chemistry/snapshots/goldbook-terms/M03804.json","sha256:b84ddab1f13dbc71482ed3f7653eeab3e2cfe5b7ffba64c30ef9d08513d6be33"),
"SFT-CHEM-RXN-INTERMEDIATE-001":("reaction-intermediate-iupac-i03096","IUPAC-GOLD-BOOK-I03096-2026","I03096","experiments/external_sources/chemistry/snapshots/goldbook-terms/I03096.json","sha256:9de39353e9af29cbe1b9dcb7f7972e2125378129e82924805f5d97696d93fd4a"),
"SFT-CHEM-KIN-ACTIVATION-001":("activation-barrier-iupac-composite","IUPAC-GOLD-BOOK-ACTIVATION-COMPOSITE-2026","G02631","experiments/external_sources/chemistry/snapshots/goldbook-terms/G02631.json","sha256:c51e2c7167603bd633c54e11d238728c7313aa8584662ea4bfc3c3a4bf97a04c"),
"SFT-CHEM-KIN-RATE-001":("reaction-rate-iupac-composite","IUPAC-GOLD-BOOK-REACTION-RATE-COMPOSITE-2026","R05147","experiments/external_sources/chemistry/snapshots/goldbook-terms/R05147.json","sha256:4f61cb4a9d72b0266dd464f84a2349aee57aec161521fb2466bcf8febed361fe"),
"SFT-CHEM-KIN-ORDER-001":("reaction-order-iupac-o04322","IUPAC-GOLD-BOOK-O04322-2026","O04322","experiments/external_sources/chemistry/snapshots/goldbook-terms/O04322.json","sha256:acb0c1bcc39fca71b9fad77cfbc8813c6ffdc1728be3943d56dcd7631c90b9f4"),
"SFT-CHEM-EQ-CHEMICAL-001":("chemical-equilibrium-iupac-composite","IUPAC-GOLD-BOOK-CHEMICAL-EQUILIBRIUM-COMPOSITE-2026","C01023","experiments/external_sources/chemistry/snapshots/goldbook-terms/C01023.json","sha256:8720b60c684dd7869500da1577be0f0a91f2362e02420d755fbbd1abbad6582b")}
def validate_pre_source_seal():
    if hash_file(ROOT/DERIVATION_PATH)!=DERIVATION_HASH: raise ValueError("reaction/kinetics derivation changed after seal")
    seal=json.loads((ROOT/PRE_SOURCE_SEAL_PATH).read_text(encoding="utf-8")); claimed=seal.pop("sealed_payload_hash",None)
    if claimed!=PRE_SOURCE_PAYLOAD_HASH or sha256_identity(seal)!=PRE_SOURCE_PAYLOAD_HASH: raise ValueError("reaction/kinetics seal invalid")
    expected=[{"claim_id":r.claim_id,"exact_result":r.exact_result,"predicted_observation_label":r.predicted_observation_label} for r in REACTION_KINETICS_BLUEPRINTS]
    if seal.get("claim_predictions")!=expected or seal.get("external_source_identities_selected") is not False or seal.get("external_target_content_opened") is not False: raise ValueError("reaction/kinetics pre-source boundary invalid")
def _bind(b):
    tid,sid,code,path,digest=SOURCE_RECORDS[b.claim_id]
    return EmpiricalChemistrySpec(claim_id=b.claim_id,title=b.title,statement=b.statement,dependencies=b.dependencies,generation_rule=b.generation_rule,grammar_boundary=b.grammar_boundary,dimensions=b.dimensions,exact_result=b.exact_result,induction_base=b.induction_base,induction_step=b.induction_step,exclusions=b.exclusions,operational_witnesses=b.operational_witnesses,experiment_id=b.experiment_id,expected_observation_label=b.predicted_observation_label,target_rows=(ChemistryTargetReference(tid,sid,f"official IUPAC source set anchored at {code}",path,digest),),observation_registry_path=OBSERVATION_REGISTRY_PATH,falsification_condition=b.falsification_condition)
validate_pre_source_seal()
REACTION_KINETICS_BATCH_1_SPECS=tuple(_bind(r) for r in REACTION_KINETICS_BLUEPRINTS)
for _spec in REACTION_KINETICS_BATCH_1_SPECS: _spec.validate()
__all__=("REACTION_KINETICS_BATCH_1_SPECS","validate_pre_source_seal")
