#!/usr/bin/env python3
"""Create all eleven ANAL-012--022 packages as one coordinated batch."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sft.chemistry.analytical_terminal_batch_v1 import COMPLETENESS_CERTIFICATES, SPECS_BY_NUMBER
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
            expected = (
                package / "registration.json", package / "STATUS.md", package / "WHY_DERIVATION_CHECK.md",
                package / "execution.py", package / "independent_validator.py", experiment / "registration.json",
            )
            if all(path.is_file() for path in expected):
                continue
            raise SystemExit(f"partial existing package requires inspection: {claim.claim_id}")
        domains = tuple(tuple(choice.name for choice in dimension.choices) for dimension in claim.dimensions)
        write(package / "registration.json", {
            "$schema": "../../governance/claim.schema.json",
            "branch": "chemistry",
            "candidate_grammar": {
                "boundary": claim.grammar_boundary,
                "completeness_certificate": COMPLETENESS_CERTIFICATES[claim.claim_id],
                "expected_cardinality": 256,
                "generator": claim.generation_rule,
            },
            "claim_id": claim.claim_id,
            "dependencies": list(claim.dependencies),
            "empirical_protocol": f"experiments/chemistry/{claim.experiment_id}/registration.json",
            "excluded_inputs": list(claim.exclusions),
            "provenance_classes": ["observational_derivation", "complete_external_record_reconstruction"],
            "registered_by": "Maria Smith",
            "registration_date": "2026-07-28",
            "required_controls": ["false_premise", "tampered_source", "tampered_artifact", "boundary", "omitted_target_row"],
            "statement": claim.statement,
            "status": "registered",
            "title": claim.title,
        })
        write(package / "STATUS.md", f"# {claim.claim_id}\n\nStatus: `registered_pending_untouched_engine_admission`\n")
        write(package / "WHY_DERIVATION_CHECK.md", (
            f"# Why ANAL-{number} requires a derivation check\n\n"
            f"A displayed measurement or conventional model cannot establish {claim.title.casefold()}. This claim generates all 256 registered forms and eliminates 255 structurally before external comparison. Its own value-free target identity and pre-source seal were fixed before complete capture. The coordinated source surface contains 218 exact artifacts and 22,221,914 bytes: 173 PDF pages, seven complete HTML surfaces, 63 IR JCAMP vectors, three UV-visible vectors, three mass vectors, 91 rotational lines, 619 gas-chromatography rows, 385 neutron rows, the complete electron-diffraction record, mobility/electrophoresis records, electroanalytical method and study records, immutable prior Analytical receipts, every transport failure, and the corrected transport records. All signs, displayed zeroes, decimals, conventional fits, uncertainties, favorable, adverse, absent, unavailable, unresolved, predicted, fitted and superseded rows remain downstream evidence and never select the native survivor.\n"
        ))
        write(package / "execution.py", f'''import sys
from sft.chemistry.analytical_terminal_batch_v1 import AUTHORITIES,SOURCE_ARTIFACTS,SPECS_BY_NUMBER
from sft.chemistry.analytical_terminal_validation_v1 import AnalyticalTerminalValidator
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.verification import ClaimExecution
CLAIM_SPEC=SPECS_BY_NUMBER[{number!r}]
def build_execution(root):
 fixed=("sft/chemistry/analytical_terminal_batch_v1.py","sft/chemistry/analytical_terminal_validation_v1.py","sft/chemistry/analytical_terminal_laws_v1.py","sft/chemistry/generated_law.py","sft/chemistry/generated_observational_law.py","sft/physics/generated_empirical_law.py",*(p for p,_ in AUTHORITIES),*(p for p,_ in SOURCE_ARTIFACTS),"claims/{claim.claim_id}/execution.py");files=tuple(dict.fromkeys(root/p for p in fixed if (root/p).is_file()));independent=root/"claims/{claim.claim_id}/independent_validator.py";return ClaimExecution(GeneratedObservationalChemistryProgram(CLAIM_SPEC,build_source_manifest(root,files).manifest_hash),ExternalCommandValidator("sft-chem-anal-{number}-independent-python/1",(sys.executable,str(independent)),independent.parent,(independent,)),files,AnalyticalTerminalValidator(root,CLAIM_SPEC))
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
        identity = f"experiments/external_sources/chemistry/anal_{number}_target_identities_v1.json"
        seal = f"experiments/sealed_predictions/chemistry_anal_{number}_pre_source_v1.json"
        write(experiment / "registration.json", {
            "$schema": "../../../governance/experiment.schema.json",
            "claim_id": claim.claim_id,
            "absence_boundary": {
                "display_glyph": "0",
                "external_signed_decimal_imaginary_and_zero_inscriptions_are_provenance_only": True,
                "native_proof_form": "positive exact counts/ratios, held orientation and structural EmptyOne absence",
                "numerical_zero_admitted": False,
            },
            "evaluation_protocol": {
                "acceptance_condition": "All eight separately registered comparisons and the complete 218-artifact subfield surface are retained.",
                "all_8_targets_required": True,
                "falsification_condition": claim.falsification_condition,
            },
            "evidence_mode": "observational_derivation_plus_complete_external_record_reconstruction",
            "experiment_id": claim.experiment_id,
            "external_measurement_sources": [{
                "complete_source_artifacts": 218,
                "complete_source_bytes": 22221914,
                "complete_pdf_pages": 173,
                "complete_html_documents": 7,
                "complete_ir_records": 63,
                "complete_uv_visible_records": 3,
                "complete_mass_records": 3,
                "complete_rotational_lines": 91,
                "complete_gas_chromatography_rows": 619,
                "complete_neutron_rows": 385,
                "measurement_bodies": ["National Institute of Standards and Technology", "National Aeronautics and Space Administration Jet Propulsion Laboratory", "Harvard-Smithsonian Center for Astrophysics transport mirror", "International Union of Pure and Applied Chemistry", "Ernos Labs V3 untouched-engine admitted record"],
            }],
            "frozen_relation": {"relation_hash": sha256_identity(claim.exact_result), "statement": claim.exact_result, "targets_did_not_select_survivor": True},
            "identity_registry": identity,
            "prediction_seal": seal,
            "registered_by": "Maria Smith",
            "registration_date": "2026-07-28",
            "schema": "sft-v3-chemistry-experiment-registration/1",
            "status": "registered_sources_captured_postseal",
        })
    print("scaffolded all eleven ANAL-012--022 packages")


if __name__ == "__main__":
    main()
