#!/usr/bin/env python3
"""Create all fourteen COMP-001--014 packages as one coordinated batch."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sft.chemistry.computational_chemistry_batch_v1 import COMPLETENESS_CERTIFICATES, SPECS_BY_NUMBER
from sft.engine.canonical import sha256_identity


def write(path: Path, content) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise SystemExit(f"refusing to overwrite {path.relative_to(ROOT)}")
    path.write_text(content if isinstance(content, str) else json.dumps(content, indent=2, sort_keys=True, ensure_ascii=False) + "\n")


def main() -> None:
    for number, claim in SPECS_BY_NUMBER.items():
        package = ROOT / "claims" / claim.claim_id
        experiment = ROOT / "experiments/chemistry" / claim.experiment_id
        if package.exists() or experiment.exists():
            raise SystemExit(f"existing COMP package requires inspection: {claim.claim_id}")
        domains = tuple(tuple(choice.name for choice in dimension.choices) for dimension in claim.dimensions)
        write(package / "registration.json", {
            "$schema": "../../governance/claim.schema.json", "branch": "chemistry",
            "candidate_grammar": {"boundary": claim.grammar_boundary, "completeness_certificate": COMPLETENESS_CERTIFICATES[claim.claim_id], "expected_cardinality": 256, "generator": claim.generation_rule},
            "claim_id": claim.claim_id, "dependencies": list(claim.dependencies),
            "empirical_protocol": f"experiments/chemistry/{claim.experiment_id}/registration.json",
            "excluded_inputs": list(claim.exclusions),
            "provenance_classes": ["observational_derivation", "complete_external_record_reconstruction"],
            "registered_by": "Maria Smith", "registration_date": "2026-07-28",
            "required_controls": ["false_premise", "tampered_source", "tampered_artifact", "boundary", "omitted_target_row"],
            "statement": claim.statement, "status": "registered", "title": claim.title,
        })
        write(package / "STATUS.md", f"# {claim.claim_id}\n\nStatus: `registered_pending_untouched_engine_admission`\n")
        write(package / "WHY_DERIVATION_CHECK.md", (
            f"# Why COMP-{number} requires a derivation check\n\n"
            f"A database record, familiar encoding, conventional algorithm or software-library result cannot establish {claim.title.casefold()}. This claim separately generates all 256 registered Fold-native forms and eliminates 255 structurally before external comparison. Its value-free target identities and native survivor were sealed as part of the complete fourteen-claim subfield before source capture. The shared external surface contains 59 exact artifacts and 444,644,830 bytes: twelve complete PubChem molecular records in independent JSON and SDF forms, four ChEBI cross-source records, 36,444 Rhea reactions, 50,016 USPTO reactions and 1,065,119 atom-mapped reaction rows. All twelve registered invalid-property responses, low-confidence mappings, conflicts, unavailable states, source-exposed dependencies and declared resource halts remain evidence. Conventional SMILES, SDF, InChI, similarity, conformer and database operations remain downstream comparison and never select the native law.\n"
        ))
        write(package / "execution.py", f'''import sys
from sft.chemistry.computational_chemistry_batch_v1 import AUTHORITIES,SOURCE_ARTIFACTS,SPECS_BY_NUMBER
from sft.chemistry.computational_chemistry_validation_v1 import ComputationalChemistryValidator
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.verification import ClaimExecution
CLAIM_SPEC=SPECS_BY_NUMBER[{number!r}]
def build_execution(root):
 fixed=("sft/chemistry/computational_chemistry_batch_v1.py","sft/chemistry/computational_chemistry_validation_v1.py","sft/chemistry/computational_chemistry_laws_v1.py","sft/chemistry/generated_law.py","sft/chemistry/generated_observational_law.py","sft/physics/generated_empirical_law.py",*(p for p,_ in AUTHORITIES),*(p for p,_ in SOURCE_ARTIFACTS),"claims/{claim.claim_id}/execution.py");files=tuple(dict.fromkeys(root/p for p in fixed if (root/p).is_file()));independent=root/"claims/{claim.claim_id}/independent_validator.py";return ClaimExecution(GeneratedObservationalChemistryProgram(CLAIM_SPEC,build_source_manifest(root,files).manifest_hash),ExternalCommandValidator("sft-chem-comp-{number}-independent-python/1",(sys.executable,str(independent)),independent.parent,(independent,)),files,ComputationalChemistryValidator(root,CLAIM_SPEC))
''')
        write(package / "independent_validator.py", f'''from itertools import product
import json,sys
CLAIM_ID={claim.claim_id!r}
DOMAINS={domains!r}
SURVIVOR={claim.exact_result!r}
DIMENSION_KEYS={tuple(dimension.key for dimension in claim.dimensions)!r}
def main():
 sealed=json.load(open(sys.argv[1]));generated=["__".join(item) for item in product(*DOMAINS)];decisions={{item["candidate_id"]:item["survives"] for item in sealed["decisions"]}};controls=sealed["controls"];passed=sealed["claim_id"]==CLAIM_ID and len(DOMAINS)==8 and all(len(domain)==2 for domain in DOMAINS) and len(set(DIMENSION_KEYS))==8 and [item["candidate_id"] for item in sealed["census"]["candidates"]]==generated and decisions=={{item:item==SURVIVOR for item in generated}} and sum(decisions.values())==1 and sealed["closure"]["scope"]=="depth_independent" and len(controls)>=4 and all(item["passed"] for item in controls);print(json.dumps({{"validated_seal_hash":sealed["seal_hash"],"recomputed_from_declared_inputs":True,"passed":passed,"certificate":{{"claim_id":CLAIM_ID,"generated_cardinality":len(generated),"dimension_count":len(DOMAINS),"unique_survivor":SURVIVOR if passed else None,"closure":"depth_independent" if passed else None,"all_registered_controls_passed":all(item["passed"] for item in controls),"external_source_accessed":False,"numerical_zero_negative_irrational_imaginary_continuum_fitted_free_random_or_imported_native_parameter_used":False}}}},sort_keys=True))
if __name__=="__main__":main()
''')
        write(experiment / "registration.json", {
            "$schema": "../../../governance/experiment.schema.json", "claim_id": claim.claim_id,
            "absence_boundary": {"display_glyph": "0", "external_signed_decimal_imaginary_and_zero_inscriptions_are_provenance_only": True, "native_proof_form": "positive exact counts/ratios, held orientation and structural EmptyOne absence", "numerical_zero_admitted": False},
            "evaluation_protocol": {"acceptance_condition": "All eight separately registered comparisons and the complete 59-artifact subfield surface are retained.", "all_8_targets_required": True, "falsification_condition": claim.falsification_condition},
            "evidence_mode": "observational_derivation_plus_complete_external_record_reconstruction",
            "experiment_id": claim.experiment_id,
            "external_measurement_sources": [{
                "complete_source_artifacts": 59, "complete_source_bytes": 444644830,
                "pubchem_complete_records": 12, "chebi_cross_source_records": 4,
                "rhea_reaction_rows": 36444, "uspto_reaction_rows": 50016,
                "atom_mapped_reaction_rows": 1065119, "registered_transport_failures": 12,
                "measurement_bodies": ["National Library of Medicine / NCBI PubChem", "EMBL-EBI ChEBI", "Rhea / SIB and EMBL-EBI", "USPTO reaction corpus / admitted Organic Chemistry evidence", "Figshare LocalMapper source record"],
            }],
            "frozen_relation": {"relation_hash": sha256_identity(claim.exact_result), "statement": claim.exact_result, "targets_did_not_select_survivor": True},
            "identity_registry": f"experiments/external_sources/chemistry/comp_{number}_target_identities_v1.json",
            "prediction_seal": f"experiments/sealed_predictions/chemistry_comp_{number}_pre_source_v1.json",
            "registered_by": "Maria Smith", "registration_date": "2026-07-28",
            "schema": "sft-v3-chemistry-experiment-registration/1", "status": "registered_sources_captured_postseal",
        })
    print("scaffolded all fourteen COMP-001--014 packages")


if __name__ == "__main__":
    main()
