"""Post-seal authority bindings for catalysis, networks and interfaces."""
from __future__ import annotations
import json
from pathlib import Path
from sft.chemistry.catalysis_interfaces_derivation import CATALYSIS_INTERFACE_BLUEPRINTS
from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.engine.canonical import sha256_identity
from sft.engine.source import hash_file
ROOT=Path(__file__).resolve().parent.parent.parent
DERIVATION_PATH="sft/chemistry/catalysis_interfaces_derivation.py"
DERIVATION_HASH="sha256:92cb7099db038b0b6ecc13f58504a7b9ff8c5872990b24f4ae1e5cdca0a3b37a"
PRE_SOURCE_SEAL_PATH="experiments/sealed_predictions/chemistry_catalysis_interfaces_batch_1_pre_source.json"
PRE_SOURCE_PAYLOAD_HASH="sha256:9c3921021511b019f9cb9aee9e5aba33269dc06318df591da32c9cbb8490206f"
OBSERVATION_REGISTRY_PATH="experiments/external_sources/chemistry/observations_catalysis_interfaces_batch_1.json"
SOURCE_RECORDS={
"SFT-CHEM-CAT-CATALYST-001":("catalyst-authority-composite","CHEM-AUTHORITY-CATALYST-COMPOSITE-2026","C00876","experiments/external_sources/chemistry/snapshots/goldbook-terms/C00876.json","sha256:a960e78123592da7dd8ad054b65a590961706c25e22a578f9088f91fb3c89e5e"),
"SFT-CHEM-CAT-PATHWAY-001":("catalytic-pathway-authority-composite","CHEM-AUTHORITY-CATALYTIC-PATHWAY-COMPOSITE-2026","C00876","experiments/external_sources/chemistry/snapshots/goldbook-terms/C00876.json","sha256:a960e78123592da7dd8ad054b65a590961706c25e22a578f9088f91fb3c89e5e"),
"SFT-CHEM-CAT-SELECTIVITY-001":("catalytic-selectivity-iupac-composite","IUPAC-GOLD-BOOK-CATALYTIC-SELECTIVITY-COMPOSITE-2026","S05563","experiments/external_sources/chemistry/snapshots/goldbook-terms/S05563.json","sha256:72489fb0beb2453befdf2628aa48d7fe5a18f8a8ce4e09573c09b3bb464d7506"),
"SFT-CHEM-NET-REACTION-001":("reaction-network-iupac-composite","IUPAC-GOLD-BOOK-REACTION-NETWORK-COMPOSITE-2026","C01210","experiments/external_sources/chemistry/snapshots/goldbook-terms/C01210.json","sha256:f7949843026a8fe090e71f1d952633b8c63eb8277ad6b067b4bcaf5babf3598d"),
"SFT-CHEM-NET-AUTOCATALYSIS-001":("autocatalysis-iupac-composite","IUPAC-GOLD-BOOK-AUTOCATALYSIS-COMPOSITE-2026","A00525","experiments/external_sources/chemistry/snapshots/goldbook-terms/A00525.json","sha256:cd6e2b68b8eefaa71fd7212cb577bd9996810a0d64771508748f7d3599469b06"),
"SFT-CHEM-SURFACE-ADSORPTION-001":("adsorption-iupac-composite","IUPAC-GOLD-BOOK-ADSORPTION-COMPOSITE-2026","A00155","experiments/external_sources/chemistry/snapshots/goldbook-terms/A00155.json","sha256:8d8d32d4fad6f36f8be4aeed8056bac1efb3ef5f9d03c3ec26fddaade7cce582"),
"SFT-CHEM-COLLOID-DISPERSION-001":("colloidal-dispersion-iupac-composite","IUPAC-GOLD-BOOK-COLLOIDAL-DISPERSION-COMPOSITE-2026","C01174","experiments/external_sources/chemistry/snapshots/goldbook-terms/C01174.json","sha256:a8261e1400d58c847f37722d7c1cb39f782a97844d847648156bf01dfad7a636"),
"SFT-CHEM-INTERFACE-TRANSFER-001":("interface-transfer-iupac-composite","IUPAC-GOLD-BOOK-INTERFACE-TRANSFER-COMPOSITE-2026","P04536","experiments/external_sources/chemistry/snapshots/goldbook-terms/P04536.json","sha256:b60eba64e32f00b5bcb7ecf818b25abc53208476546555ae05349a52cbd7e7b6")}
def validate_pre_source_seal():
    if hash_file(ROOT/DERIVATION_PATH)!=DERIVATION_HASH: raise ValueError("catalysis/interfaces derivation changed after seal")
    seal=json.loads((ROOT/PRE_SOURCE_SEAL_PATH).read_text(encoding="utf-8")); claimed=seal.pop("sealed_payload_hash",None)
    if claimed!=PRE_SOURCE_PAYLOAD_HASH or sha256_identity(seal)!=PRE_SOURCE_PAYLOAD_HASH: raise ValueError("catalysis/interfaces seal invalid")
    expected=[{"claim_id":r.claim_id,"exact_result":r.exact_result,"predicted_observation_label":r.predicted_observation_label} for r in CATALYSIS_INTERFACE_BLUEPRINTS]
    if seal.get("claim_predictions")!=expected or seal.get("external_source_identities_selected") is not False or seal.get("external_target_content_opened") is not False: raise ValueError("catalysis/interfaces pre-source boundary invalid")
def _bind(b):
    tid,sid,code,path,digest=SOURCE_RECORDS[b.claim_id]
    return EmpiricalChemistrySpec(claim_id=b.claim_id,title=b.title,statement=b.statement,dependencies=b.dependencies,generation_rule=b.generation_rule,grammar_boundary=b.grammar_boundary,dimensions=b.dimensions,exact_result=b.exact_result,induction_base=b.induction_base,induction_step=b.induction_step,exclusions=b.exclusions,operational_witnesses=b.operational_witnesses,experiment_id=b.experiment_id,expected_observation_label=b.predicted_observation_label,target_rows=(ChemistryTargetReference(tid,sid,f"authority source set anchored at {code}",path,digest),),observation_registry_path=OBSERVATION_REGISTRY_PATH,falsification_condition=b.falsification_condition)
validate_pre_source_seal()
CATALYSIS_INTERFACES_BATCH_1_SPECS=tuple(_bind(r) for r in CATALYSIS_INTERFACE_BLUEPRINTS)
for _spec in CATALYSIS_INTERFACES_BATCH_1_SPECS: _spec.validate()
__all__=("CATALYSIS_INTERFACES_BATCH_1_SPECS","validate_pre_source_seal")
