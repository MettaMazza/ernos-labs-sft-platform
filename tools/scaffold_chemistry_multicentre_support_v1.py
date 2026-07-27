#!/usr/bin/env python3
"""Scaffold the complete ELEC-008 multicentre-support claim package."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.multicentre_support_batch_v1 import IDENTITY_HASH, IDENTITY_PATH, MULTICENTRE_SUPPORT_SPEC, SOURCE_IDS, TARGET_HASH, TARGET_PATH  # noqa: E402
from sft.chemistry.multicentre_support_validation_v1 import experiment_registration_record, prediction_program_document  # noqa: E402
from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.physics.generated_empirical_law import completeness_record, survivor_id  # noqa: E402


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def claim_registration() -> dict[str, object]:
    spec = MULTICENTRE_SUPPORT_SPEC
    return {"$schema": "../../governance/claim.schema.json", "claim_id": spec.claim_id, "title": spec.title, "branch": "chemistry", "status": "registered", "statement": spec.statement, "dependencies": list(spec.dependencies), "provenance_classes": ["observational_derivation"], "candidate_grammar": {"generator": spec.generation_rule, "boundary": spec.grammar_boundary, "expected_cardinality": 256, "completeness_certificate": sha256_identity(completeness_record(spec))}, "excluded_inputs": list(spec.exclusions), "required_controls": ["false_premise", "tampered_source", "tampered_artifact", "boundary"], "intended_certificate": "Complete 256-form census, unique survivor, connected-successor induction, implementation-distinct reconstruction, capability-closed multicentre law, all four IUPAC topology records, all nine NIST neutral-diborane geometry/bond records, all seven NIST benzene geometry/bond records and all adverse controls.", "empirical_protocol": f"experiments/chemistry/{spec.experiment_id}/registration.json", "registered_by": "Maria Smith", "registration_date": "2026-07-26"}


def experiment_registration() -> dict[str, object]:
    spec = MULTICENTRE_SUPPORT_SPEC
    program, record = prediction_program_document(ROOT), experiment_registration_record(ROOT)
    return {"$schema": "../../../governance/experiment.schema.json", "experiment_id": spec.experiment_id, "claim_id": spec.claim_id, "evidence_mode": "observational_derivation", "development_observations": [{"source_ids": list(SOURCE_IDS), "role": "question-and-complete-test-domain-only", "topologies_species_geometries_and_values_absent_from_survivor_selection": True}], "external_measurement_sources": [{"source_id": SOURCE_IDS[0], "measurement_body": "International Union of Pure and Applied Chemistry", "database": "IUPAC Gold Book 5th edition", "doi": "10.1351/goldbook.08789", "records": 4, "role": "complete-authoritative-delocalization-topology-vector"}, {"source_id": SOURCE_IDS[1], "measurement_body": "National Institute of Standards and Technology", "database": "CCCBDB SRD 101 release 22", "source_uri": "https://cccbdb.nist.gov/expgeom2x.asp?casno=19287457", "records": 9, "role": "complete-neutral-diborane-experimental-geometry-and-bond-vector"}, {"source_id": SOURCE_IDS[2], "measurement_body": "National Institute of Standards and Technology", "database": "CCCBDB SRD 101 release 22", "source_uri": "https://cccbdb.nist.gov/expgeom2x.asp?casno=71432", "records": 7, "role": "complete-benzene-experimental-geometry-and-bond-vector"}], "frozen_relation": {"statement": spec.exact_result, "relation_hash": sha256_identity(spec.exact_result), "dependency_hashes": [sha256_identity(item) for item in spec.dependencies], "candidate_grammar": spec.generation_rule, "exact_domain": spec.grammar_boundary, "targets_did_not_select_survivor": True}, "inputs": [{"input_id": "registered-premise", "value_kind": "held-sealed-derivation", "content_hash": sha256_identity(spec.dependencies)}, {"input_id": "target-identities-only", "path": IDENTITY_PATH, "content_hash": IDENTITY_HASH, "outcomes_absent": True}], "withheld_targets": [{"target_id": row.target_id, "source_id": row.source_id, "snapshot_hash": row.snapshot_hash, "content_withheld_from_prediction": True} for row in spec.target_rows], "absence_boundary": {"native_proof_form": "structural EmptyOne", "display_glyph": "0", "meaning": "absence only", "numerical_zero_admitted": False, "rule": "Categorical source rows use EmptyOne in the magnitude coordinate; decimal inscriptions are exact held post-seal records."}, "prediction_protocol": {"interpreter_id": "sft-v3-capability-closed-fold-interpreter/1", "program_id": program["program_id"], "program_hash": sha256_identity(program), "executor_id": spec.experiment_id + "-prediction-executor", "complete_trace_required": True, "forbidden_capabilities": ["clock", "dynamic_import", "environment", "filesystem_read", "filesystem_write", "foreign_function", "network", "subprocess"]}, "evaluation_protocol": {"evaluator_id": spec.experiment_id + "-post-seal-IUPAC-NIST-evaluator", "comparison_implementation_hash": sha256_identity(("complete-IUPAC-NIST-multicentre-comparator/1", spec.experiment_id)), "metrics": [{"metric_id": "three-centre-bridge", "definition": "Retain the complete neutral-diborane geometry, including distinct outer/bridging B-H distances and B-H-B connectivity.", "all_rows": True}, {"metric_id": "six-centre-cycle", "definition": "Retain the complete benzene geometry and all six equal aromatic links.", "all_rows": True}, {"metric_id": "topology-census", "definition": "Retain IUPAC ribbon, surface and volume delocalization records and the localized-model contrast.", "all_rows": True}], "acceptance_condition": "All 20 rows, all exact values, all topology correspondences and every adverse control pass.", "falsification_condition": spec.falsification_condition}, "custody_protocol": {"identity_registry_hash": IDENTITY_HASH, "withheld_target_registry_hash": TARGET_HASH, "target_release_requires_prediction_seal": True, "cross_platform_exchange_required": True, "hostile_package_audit_required": True}, "retention_policy": "retain-all-twenty-records-all-exact-values-all-source-classes-and-all-adverse-results", "scope_boundary": "The forced result is one connected support word spanning three or more centres and the path/cycle/polyhedral topology census. IUPAC and NIST rows are post-seal external tests; no imported bonding model or measured magnitude selects the law.", "stop_condition": "Halt on any violation; otherwise stop after the complete vector and controls.", "source_hashes": {IDENTITY_PATH: IDENTITY_HASH, TARGET_PATH: TARGET_HASH, **{row.snapshot_path: row.snapshot_hash for row in spec.target_rows}, "experiment-registration-record": sha256_identity(record)}, "registration_date": "2026-07-26", "registered_by": "Maria Smith", "status": "registered"}


def independent_source() -> str:
    spec = MULTICENTRE_SUPPORT_SPEC
    domains = tuple(tuple(choice.name for choice in dimension.choices) for dimension in spec.dimensions)
    return f'''from itertools import product
import json,sys
CLAIM={spec.claim_id!r}; DOMAINS={domains!r}; SURVIVOR={survivor_id(spec)!r}
def connected(vertices,edges):
 reached={{vertices[0]}}; changed=True
 while changed:
  before=len(reached)
  for a,b in edges:
   if a in reached or b in reached: reached.update((a,b))
  changed=len(reached)>before
 return len(reached)==len(vertices)
def main():
 d=json.load(open(sys.argv[1])); generated=["__".join(row) for row in product(*DOMAINS)]; registered=[row["candidate_id"] for row in d["census"]["candidates"]]; decisions={{row["candidate_id"]:row["survives"] for row in d["decisions"]}}; path=((1,2),(2,3)); cycle=tuple((n,n+1) for n in range(1,6))+((6,1),); volume=tuple((a,b) for a in range(1,5) for b in range(a+1,5)); law=(connected((1,2,3),path) and len(path)==2 and connected(tuple(range(1,7)),cycle) and len(cycle)==6 and connected((1,2,3,4),volume) and len(volume)==6); passed=(d["claim_id"]==CLAIM and registered==generated and len(set(registered))==256 and decisions=={{row:row==SURVIVOR for row in generated}} and sum(decisions.values())==1 and d["closure"]["scope"]=="depth_independent" and d["closure"]["minimality_passed"] and d["closure"]["named_shape_uniqueness_passed"] and all(row["passed"] for row in d["controls"]) and law); print(json.dumps({{"validated_seal_hash":d["seal_hash"],"recomputed_from_declared_inputs":True,"passed":passed,"certificate":{{"claim_id":CLAIM,"candidate_count":len(generated),"survivor":SURVIVOR if passed else None,"path_edges":len(path),"cycle_edges":len(cycle),"volume_edges":len(volume)}}}},sort_keys=True))
if __name__=="__main__":main()
'''


def execution_source() -> str:
    spec = MULTICENTRE_SUPPORT_SPEC
    return f'''from pathlib import Path
import sys
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.chemistry.multicentre_support_batch_v1 import MULTICENTRE_SUPPORT_SPEC
from sft.chemistry.multicentre_support_validation_v1 import MulticentreSupportValidator
from sft.verification import ClaimExecution
def build_execution(root:Path):
 s=MULTICENTRE_SUPPORT_SPEC; files=(root/"sft/chemistry/multicentre_support_law_v1.py",root/"sft/chemistry/multicentre_support_batch_v1.py",root/"sft/chemistry/multicentre_support_validation_v1.py",root/"sft/chemistry/generated_law.py",root/"sft/chemistry/generated_observational_law.py",root/"claims/{spec.claim_id}/execution.py",root/"sft/physics/generated_empirical_law.py",root/"sft/claim_evidence/fold_language.py",root/"sft/claim_evidence/custody.py",root/"sft/claim_evidence/hostile.py",root/"sft/engine/isolation.py",root/"sft/engine/empirical.py"); source_hash=build_source_manifest(root,files).manifest_hash; validator=root/"claims/{spec.claim_id}/independent_validator.py"; return ClaimExecution(GeneratedObservationalChemistryProgram(s,source_hash),ExternalCommandValidator("{spec.claim_id.lower()}-independent-python/1",(sys.executable,str(validator)),validator.parent,(validator,)),files,MulticentreSupportValidator(root))
'''


def derivation_note() -> str:
    spec = MULTICENTRE_SUPPORT_SPEC
    return f"""# {spec.title}

Claim: `{spec.claim_id}`  
Chemistry obligation: `SFT-CHEM-OBL-ELEC-008`

## WHY

ELEC-007 establishes a joint relation not reconstructible from independent carrier marginals. ELEC-008 asks the next exact question: when one electron-support identity extends through a molecular graph, can a two-centre bond premise exhaust it? The answer is derived from generated graph support, not imported valence-bond, molecular-orbital, resonance, aromaticity, Hückel or Wade rules.

There is no numerical zero. Structural absence is `EmptyOne`; the glyph `0` denotes absence only. External decimals are held exact positive post-seal ratios, never fitted proof parameters.

## DERIVATION

Two centres define one pair and cannot distinguish multicentre support. Adding the first connected successor produces three retained centres in one Fold word. Any replacement by one localized pair omits a centre; any replacement by several named pair supports destroys the single complete support identity. Therefore a connected three-or-more-centre word is irreducible to one localized two-centre support.

Graph incidence supplies the topology without a chemical prior. A connected acyclic chain has two endpoints and forces ribbon support. Closing its endpoints gives a cycle and forces surface support. Adding an independent connected branch beyond the cycle produces a polyhedral support and forces volume support. Each connected successor preserves every earlier centre and edge while extending the one support word.

The eight-axis grammar enumerates 256 named alternatives. Exactly one survives:

`{survivor_id(spec)}`

Base: {spec.induction_base}

Successor: {spec.induction_step}

## CHECK

The sealed predictor contains only the minimum positive centre count, one complete extended support, connectedness, the ribbon/surface/volume graph census, irreducibility and the connected-successor law. It contains no species, topology example, bond length, angle, point group or measured target.

After sealing, the complete 20-record vector is opened. Four IUPAC Gold Book records independently state the localized-bond contrast and ribbon, surface and volume delocalization modes. Nine NIST CCCBDB neutral-diborane records preserve the full experimental internal-coordinate and bond-count surface: `r(B–H)_outer = 1.200 Å`, `r(B–H)_bridge = 1.320 Å`, and `∠B–H–B = 83.8°` retain one measured hydrogen centre connected to both boron centres. Seven NIST benzene records retain `D6h`, `r(C–C) = 1.397 Å`, and six `C:C` links, matching one equal six-centre cycle rather than a selected localized edge.

The geometry magnitudes test physical realization after sealing; they do not choose or fit the graph law. Two-centre, disconnected, incomplete-word, topology-mismatch, numerical-zero, omitted-row, selected-source, changed-value and tampered-source controls reject.

## FALSIFICATION

{spec.falsification_condition}
"""


def main() -> None:
    spec = MULTICENTRE_SUPPORT_SPEC
    claim = ROOT / "claims" / spec.claim_id
    write(claim / "registration.json", json.dumps(claim_registration(), indent=2, sort_keys=True) + "\n")
    write(claim / "execution.py", execution_source())
    write(claim / "independent_validator.py", independent_source())
    write(claim / "WHY_DERIVATION_CHECK.md", derivation_note())
    write(claim / "STATUS.md", f"# {spec.claim_id}\n\nStatus: `registered_observational_derivation`\n")
    experiment = ROOT / "experiments" / "chemistry" / spec.experiment_id
    write(experiment / "registration.json", json.dumps(experiment_registration(), indent=2, sort_keys=True) + "\n")
    print("scaffolded", spec.claim_id)


if __name__ == "__main__":
    main()
