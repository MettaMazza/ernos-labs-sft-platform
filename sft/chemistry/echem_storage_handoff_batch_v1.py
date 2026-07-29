"""Frozen registration for the ECHEM-013 storage handoff claim."""
from pathlib import Path

from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.chemistry.electrochemical_storage_handoff_law_v1 import DEPENDENCIES, DIMENSIONS, EXACT_RESULT, OPERATIONAL_WITNESSES
from sft.engine.canonical import sha256_identity
from sft.engine.source import hash_file

ROOT = Path(__file__).resolve().parents[2]
ANALYSIS_PATH = "experiments/external_sources/chemistry/echem_013_complete_postseal_analysis_v1.json"
ANALYSIS_HASH = "sha256:d8b99cd7258aaf4c9acc75e98edb457041eb065f378b0ea41a27f914f79060a6"
AUTHORITIES = (
    ("audits/CHEMISTRY_ECHEM_001_013_FAMILY_BOUNDARY_2026-07-28.json", "sha256:66f3152d791eafc5f677467ef7affd72f6559150be4adf586873a79c6ad473df"),
    ("experiments/external_sources/chemistry/echem_001_013_family_source_identity_registry_v1.json", "sha256:64ec429f537c2b0274cba689a32a65a6f36aebb3ecdc96678efcc49272c63106"),
    ("sft/chemistry/electrochemical_storage_handoff_law_v1.py", "sha256:2449e8773a71a2b256096fb603912a3b4ec73e839d6c891d2b496798f254ce74"),
    ("experiments/external_sources/chemistry/echem_013_target_identities_v1.json", "sha256:b5590b443b430b90104bed6bfff1012fbdef81145f19acc8d8734f0be565c221"),
    ("experiments/sealed_predictions/chemistry_echem_013_storage_handoff_pre_source_v1.json", "sha256:1336dd1a70224644ac587699a17ffb202e4be0dda24e0449033af217e906659d"),
    ("experiments/external_sources/materials/snapshots/nist-metal-additive-corrosion.html", "sha256:a1bb9a6bc22eb85fb7a1b3c7d0ac4bc0837d68832b7b7c6f357a68ea6cde0322"),
    ("claims/SFT-CHEM-CELL-POTENTIAL-COMPOSITION-003/certificate.json", "sha256:bad076c5b7573c9cc8fbb87b6a07602b31981e05a14372404cc8fe8a747d7653"),
    ("claims/SFT-MAT-DEGR-CORROSION-001/certificate.json", "sha256:bca77793595dd1e50dcb43c150acb5497b9bc9983c27313a3e3e6965198e5fec"),
    ("claims/SFT-ENG-REQUIREMENT-001/certificate.json", "sha256:66fbe158311817b4529b26ac38ff3be2e35d229e91d6281021873122c7ace1ae"),
    (ANALYSIS_PATH, ANALYSIS_HASH),
    ("tools/seal_chemistry_echem_013_prediction_v1.py", "sha256:d3dc2d18bd32945c447bd665e0b708188a33d98c0df06b7a62fe97f9328bbe80"),
    ("tools/build_chemistry_echem_013_external_v1.py", "sha256:238f17b3433d021af47c382ecc1dad599ecbf02965c242060292e85fa9b7b9e5"),
)
for path, expected in AUTHORITIES:
    if hash_file(ROOT / path) != expected:
        raise ValueError(f"ECHEM-013 authority changed: {path}")


def target(name: str, source: str) -> ChemistryTargetReference:
    return ChemistryTargetReference(f"SFT-CHEM-ECHEM-013-{name}", source, name.casefold().replace("-", " "), ANALYSIS_PATH, ANALYSIS_HASH)


TARGETS = (
    target("CHEMISTRY-OWNER", "SFT-CHEM-CELL-POTENTIAL-COMPOSITION-003"),
    target("MATERIALS-OWNER", "SFT-MAT-DEGR-CORROSION-001"),
    target("ENGINEERING-BOUNDARY", "SFT-ENG-REQUIREMENT-001"),
    target("UNIQUE-OWNERSHIP", "SFT-V3-LIVE-CLAIM-CENSUS"),
    target("DIRECTED-HANDOFF", "SFT-V3-LIVE-DEPENDENCY-GRAPH"),
    target("PAIRED-RECORDS", "SFT-CHEM-MAT-PAIRED-RECEIPTS"),
    target("EXTERNAL-MATERIAL-SURFACE", "NIST-METAL-ADDITIVE-CORROSION"),
    target("NO-DUPLICATE-OWNERSHIP", "SFT-V3-BRANCH-OWNERSHIP-BOUNDARY"),
)

STORAGE_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-ELECTROCHEMICAL-STORAGE-HANDOFF-013", title="Fold electrochemical storage ownership and handoff law",
    statement="Electrochemical storage retains one exact owner per coordinate: Chemistry owns species and reactions, Materials owns bulk response and degradation, and Engineering owns implementation, joined only by explicit directed claim handoffs.",
    dependencies=DEPENDENCIES, generation_rule="Generate the literal product of eight registered storage-handoff decisions.", grammar_boundary="Eight dimensions exhaust subject, Chemistry scope, Materials scope, Engineering scope, ownership, handoff, record and extension.", dimensions=DIMENSIONS, exact_result=EXACT_RESULT,
    induction_base="The first chemical-state coordinate has one Chemistry owner and one admitted source claim.", induction_step="Appending a new coordinate requires one new explicit owner and directed handoff without changing prior ownership.",
    exclusions=("no numerical zero negative irrational imaginary continuum fitted free random or imported native parameter", "no device result source status or application selects ownership", "no duplicated branch ownership or untraced cross-branch use"), operational_witnesses=OPERATIONAL_WITNESSES,
    experiment_id="SFT-EXP-CHEM-ELECTROCHEMICAL-STORAGE-HANDOFF-013", expected_observation_label="complete-electrochemical-storage-handoff-vector", target_rows=TARGETS, observation_registry_path=ANALYSIS_PATH,
    falsification_condition="The claim halts if the survivor is nonunique; any owner, coordinate, admitted receipt, directed handoff, external material record or duplication control is omitted; or an application outcome selects the ownership law.")
STORAGE_SPEC.validate()
COMPLETENESS_CERTIFICATE = sha256_identity((STORAGE_SPEC.claim_id, tuple(row.target_id for row in TARGETS), 3, 2, 97292, EXACT_RESULT))

__all__ = ("ANALYSIS_HASH", "ANALYSIS_PATH", "AUTHORITIES", "COMPLETENESS_CERTIFICATE", "STORAGE_SPEC", "TARGETS")
