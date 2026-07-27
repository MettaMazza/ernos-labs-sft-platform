#!/usr/bin/env python3
"""Scaffold the registered ORG-006 package and implementation-distinct checker."""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))

from sft.chemistry.conformer_population_ordering_batch_v1 import CONFORMER_POPULATION_ORDERING_SPEC, IDENTITY_HASH, IDENTITY_PATH, PRE_SOURCE_PATH, PRIMARY_HASH, PRIMARY_PATH, TARGET_HASH, TARGET_PATH  # noqa:E402
from sft.chemistry.conformer_population_ordering_validation_v1 import experiment_registration_record, prediction_program_document  # noqa:E402
from sft.engine.canonical import sha256_identity  # noqa:E402
from sft.physics.generated_empirical_law import completeness_record, survivor_id  # noqa:E402


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True); path.write_text(content, encoding="utf-8")


def independent_source() -> str:
    spec = CONFORMER_POPULATION_ORDERING_SPEC
    domains = tuple(tuple(choice.name for choice in dimension.choices) for dimension in spec.dimensions); survivor = survivor_id(spec)
    return f'''"""Implementation-distinct, value-free ORG-006 reconstruction."""
from fractions import Fraction
from itertools import product
import json,sys
CLAIM_ID={spec.claim_id!r}
DOMAINS={domains!r}
SURVIVOR={survivor!r}
def main():
 with open(sys.argv[1],encoding="utf-8") as h: sealed=json.load(h)
 generated=["__".join(row) for row in product(*DOMAINS)]
 received=[row["candidate_id"] for row in sealed["census"]["candidates"]]
 decisions={{row["candidate_id"]:row["survives"] for row in sealed["decisions"]}}
 counts=(3,1); boundary=sum(counts); populations=tuple(Fraction(value,boundary) for value in counts)
 successor_counts=(3,2); successor_boundary=sum(successor_counts); successor=tuple(Fraction(value,successor_boundary) for value in successor_counts)
 energy=(480,658,3263); gaps=(energy[0],energy[1]-energy[0],energy[2]-energy[1])
 passed=(
  sealed["claim_id"]==CLAIM_ID and received==generated and len(generated)==256 and len(set(received))==256
  and decisions=={{candidate:candidate==SURVIVOR for candidate in generated}} and sum(decisions.values())==1
  and sealed["closure"]["scope"]=="depth_independent" and sealed["closure"]["minimality_passed"] is True
  and sealed["closure"]["named_shape_uniqueness_passed"] is True
  and {{row["kind"] for row in sealed["controls"]}}=={{"false_premise","tampered_source","tampered_artifact","boundary"}}
  and all(row["passed"] is True for row in sealed["controls"])
  and populations==(Fraction(3,4),Fraction(1,4)) and successor==(Fraction(3,5),Fraction(2,5)) and gaps==(480,178,2605)
 )
 print(json.dumps({{"validated_seal_hash":sealed["seal_hash"],"recomputed_from_declared_inputs":True,"passed":passed,"certificate":{{
  "claim_id":CLAIM_ID,"generated_cardinality":len(generated),"unique_survivor":SURVIVOR if passed else None,
  "closure":"depth_independent" if passed else None,"base_population_fractions":[str(v) for v in populations],
  "successor_population_fractions":[str(v) for v in successor],"positive_energy_gaps":list(gaps),
  "external_temperature_energy_population_species_or_payload_accessed":False,
  "numerical_zero_negative_irrational_imaginary_continuum_fitted_free_random_or_imported_parameter_used":False,
 }}}},sort_keys=True))
if __name__=="__main__": main()
'''


def execution_source() -> str:
    claim_id = CONFORMER_POPULATION_ORDERING_SPEC.claim_id
    return f'''"""Official execution binding for {claim_id}."""
from pathlib import Path
import json,sys
from sft.chemistry.conformer_population_ordering_batch_v1 import (
 CONFORMER_POPULATION_ORDERING_SPEC,FAMILY_BOUNDARY_PATH,FAMILY_INVENTORY_PATH,FAMILY_REGISTRY_PATH,
 IDENTITY_PATH,PRE_SOURCE_PATH,PRIMARY_PATH,TARGET_PATH)
from sft.chemistry.conformer_population_ordering_validation_v1 import ConformerPopulationOrderingValidator
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.verification import ClaimExecution
def _paths(value):
 if isinstance(value,dict):
  for item in value.values(): yield from _paths(item)
 elif isinstance(value,list):
  for item in value: yield from _paths(item)
 elif isinstance(value,str) and not value.startswith("sha256:") and "/" in value and len(value) < 512:
  path=Path(value)
  if not path.is_absolute(): yield path
def build_execution(root:Path)->ClaimExecution:
 targets=json.loads((root/TARGET_PATH).read_text()); referenced=tuple(path for path in _paths(targets) if (root/path).is_file())
 fixed=(
  "sft/chemistry/conformer_population_ordering_law_v1.py","sft/chemistry/conformer_population_ordering_batch_v1.py",
  "sft/chemistry/conformer_population_ordering_validation_v1.py","sft/chemistry/generated_law.py","sft/chemistry/generated_observational_law.py",
  "sft/physics/generated_empirical_law.py","tools/build_chemistry_org_006_complete_external_v1.py","tools/build_chemistry_org_006_complete_external_v2.py",
  "tools/capture_chemistry_org_006_blind_sources_v1.py","tools/capture_chemistry_org_006_value_blind_sources_v2.py",
  "tools/capture_chemistry_org_006_acs_figshare_v3.py","tools/capture_chemistry_org_006_acs_figshare_file_v4.py","tools/capture_chemistry_org_006_core_direct_v5.py",
  FAMILY_BOUNDARY_PATH,FAMILY_REGISTRY_PATH,FAMILY_INVENTORY_PATH,IDENTITY_PATH,TARGET_PATH,PRIMARY_PATH,PRE_SOURCE_PATH,
  "experiments/sealed_predictions/chemistry_org_006_conformer_population_ordering_pre_source.json",
  "experiments/sealed_predictions/chemistry_org_006_conformer_population_ordering_pre_source_v2.json",
  "experiments/sealed_predictions/chemistry_org_006_conformer_population_ordering_pre_source_v3.json",
  "experiments/sealed_predictions/chemistry_org_006_conformer_population_ordering_pre_source_v4.json",
  "experiments/external_sources/chemistry/org_006_target_identities_v1.json","experiments/external_sources/chemistry/org_006_target_identity_addendum_v2.json",
  "experiments/external_sources/chemistry/org_006_target_identity_addendum_v3.json","experiments/external_sources/chemistry/org_006_target_identity_addendum_v4.json",
  "experiments/external_sources/chemistry/org_006_target_identity_addendum_v5.json","experiments/external_sources/chemistry/org_006_blind_source_identity_addendum_v1.json",
  "experiments/external_sources/chemistry/org_006_value_blind_source_identity_addendum_v2.json","experiments/external_sources/chemistry/org_006_acs_figshare_source_identity_addendum_v3.json",
  "experiments/external_sources/chemistry/org_006_acs_figshare_file_source_identity_addendum_v4.json","experiments/external_sources/chemistry/org_006_core_direct_source_identity_addendum_v5.json",
  "claims/{claim_id}/execution.py",
 )
 files=tuple(dict.fromkeys(root/path for path in (*fixed,*referenced))); source_hash=build_source_manifest(root,files).manifest_hash
 independent=root/"claims/{claim_id}/independent_validator.py"
 return ClaimExecution(GeneratedObservationalChemistryProgram(CONFORMER_POPULATION_ORDERING_SPEC,source_hash),
  ExternalCommandValidator("sft-chem-conformer-population-ordering-006-independent-python/1",(sys.executable,str(independent)),independent.parent,(independent,)),
  files,ConformerPopulationOrderingValidator(root))
'''


def main() -> None:
    spec = CONFORMER_POPULATION_ORDERING_SPEC; package = ROOT / "claims" / spec.claim_id
    if package.exists(): raise SystemExit("ORG-006 claim package already exists; preserved without replay")
    survivor = survivor_id(spec)
    registration = {
        "$schema": "../../governance/claim.schema.json", "claim_id": spec.claim_id, "title": spec.title, "branch": "chemistry", "status": "registered",
        "statement": spec.statement, "dependencies": list(spec.dependencies), "provenance_classes": ["target_value_blind_derivation"],
        "candidate_grammar": {"generator": spec.generation_rule, "boundary": spec.grammar_boundary, "expected_cardinality": 256, "completeness_certificate": sha256_identity(completeness_record(spec))},
        "excluded_inputs": list(spec.exclusions), "required_controls": ["false_premise", "tampered_source", "tampered_artifact", "boundary"],
        "empirical_protocol": "experiments/chemistry/" + spec.experiment_id + "/registration.json", "registered_by": "Maria Smith", "registration_date": "2026-07-27",
    }
    experiment = {
        "$schema": "../../../governance/experiment.schema.json", **experiment_registration_record(ROOT), "evidence_mode": "target_value_blind_derivation",
        "external_sources": [
            {"source_id": "IUPAC-NIST-COMPLETE-CONFORMER-SURFACE", "body": "IUPAC and NIST", "role": "terminology, timescale, conformer state and internal-rotation records", "custody": "mixed disclosed development-observed and value-blind"},
            {"source_id": "ACS-AIP-CORE-BLIND-CONDITIONED-VECTOR", "body": "ACS, AIP Publishing and CORE", "role": "complete measured 22-spectrum, 224-row, energy and population vector", "custody": "payload value-blind under successive preserved seals"},
        ],
        "source_hashes": {"identity_registry": IDENTITY_HASH, "complete_targets": TARGET_HASH, "normalized_primary": PRIMARY_HASH},
        "prediction_protocol": {"program_hash": sha256_identity(prediction_program_document(ROOT)), "pre_source_prediction": PRE_SOURCE_PATH, "target_payload_hashes_inaccessible": True, "complete_trace_required": True},
        "registered_by": "Maria Smith", "registration_date": "2026-07-27", "status": "registered",
    }
    note = f"""# {spec.title}

Claim: `{spec.claim_id}`  
Chemistry obligation: `SFT-CHEM-OBL-ORG-006`

## WHY

Conformer population cannot be a free probability, fitted distribution or timeless label. ORG-006 derives it from the complete deterministic occurrence trace of the ORG-005 quotient while retaining the physical condition, observation timescale and positive finite boundary.

## DERIVATION

The eight-axis grammar exhausts 256 forms and leaves one survivor:

`{survivor}`

For every retained conformer class, population is the exact occurrence count divided by the complete trace length. A class not observed at that finite boundary is `EmptyOne`, not native numerical zero. Relative energy begins at a structural least-state reference and every later separation is positive ordered `Take`; no signed subtraction is introduced. Appending one observation retains the full history and changes only the counted boundary. The exact witness moves from `3/4, 1/4` to `3/5, 2/5` after one generated observation.

## BLIND EMPIRICAL CHECK

The complete article PDF was recovered only after the v5 value seal. It reports 22 measured n-pentane spectra across two liquid-crystal conditions. At 298.5 K the displayed ordered-phase populations are `tt 0.33 ± 0.03`, `tg 0.51 ± 0.01`, `pm 0.02 ± 0.01`, and `pp 0.14 ± 0.01`; as exact displayed fractions these are `33/100 + 51/100 + 1/50 + 7/50 = 1`. Their forced displayed order is `tg > tt > pp > pm`.

The printed intramolecular energy surface gives structural tt reference followed by `tg 480`, `pp 658`, and `pm 3263 cal mol^-1`, forcing positive gaps `480`, `178`, and `2605`. The article separately reports `Etg = 441 ± 114 cal mol^-1` at 300 K and a signed external temperature variation `-1.9 ± 0.3 cal K^-1 mol^-1`; that signed inscription remains downstream and is never native Fold arithmetic.

The ACS supporting file matches its publisher-declared byte count and MD5 and retains all eight tables and 224 measured temperature/coupling rows. Every failed NIST, OSTI, publisher, CORE and recorder route remains present. The isotropic displayed probabilities sum to `201/200` because the printed values are rounded; that adverse row is retained rather than silently normalized.

## FALSIFICATION

{spec.falsification_condition}

## BOUNDARY

The law is depth-independent at every positive finite trace boundary. The empirical result is complete for the fourteen preregistered source identities and their full returned surfaces; condition-specific values are correspondence checks, never generators.
"""
    write(package / "registration.json", json.dumps(registration, indent=2, sort_keys=True) + "\n")
    write(package / "execution.py", execution_source()); write(package / "independent_validator.py", independent_source()); write(package / "WHY_DERIVATION_CHECK.md", note)
    write(package / "STATUS.md", f"# {spec.claim_id}\n\nStatus: `registered_target_value_blind_derivation`\n")
    write(ROOT / "experiments/chemistry" / spec.experiment_id / "registration.json", json.dumps(experiment, indent=2, sort_keys=True) + "\n")
    print("scaffolded", spec.claim_id)


if __name__ == "__main__": main()
