"""Shared frozen batch registration for separate ECHEM-002, 003 and 004 claims."""
from pathlib import Path
from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.chemistry.electrode_potential_law_v1 import DEPENDENCIES as E002_DEPS, DIMENSIONS as E002_DIMS, EXACT_RESULT as E002_RESULT, OPERATIONAL_WITNESSES as E002_WITNESSES
from sft.chemistry.cell_potential_composition_law_v1 import DEPENDENCIES as E003_DEPS, DIMENSIONS as E003_DIMS, EXACT_RESULT as E003_RESULT, OPERATIONAL_WITNESSES as E003_WITNESSES
from sft.chemistry.concentration_potential_law_v1 import DEPENDENCIES as E004_DEPS, DIMENSIONS as E004_DIMS, EXACT_RESULT as E004_RESULT, OPERATIONAL_WITNESSES as E004_WITNESSES
from sft.engine.canonical import sha256_identity
from sft.engine.source import hash_file

ROOT = Path(__file__).resolve().parents[2]
ANALYSIS_PATH = "experiments/external_sources/chemistry/snapshots/echem-002-004-agcl-v1/complete-postseal-analysis-v2.json"
PDF_PATH = "experiments/external_sources/chemistry/snapshots/echem-002-004-agcl-v1/nist-agcl-standard-potential-1954.pdf"
INVENTORY_PATH = "experiments/external_sources/chemistry/snapshots/echem-002-004-agcl-v1/source-inventory-v1.json"
ANALYSIS_HASH = "sha256:a6f1c117cfa3fe3f454dd5e86989d2105bc93586ca88370f0e4e541847088216"
AUTHORITIES = (
    ("audits/CHEMISTRY_ECHEM_001_013_FAMILY_BOUNDARY_2026-07-28.json", "sha256:66f3152d791eafc5f677467ef7affd72f6559150be4adf586873a79c6ad473df"),
    ("experiments/external_sources/chemistry/echem_001_013_family_source_identity_registry_v1.json", "sha256:64ec429f537c2b0274cba689a32a65a6f36aebb3ecdc96678efcc49272c63106"),
    ("sft/chemistry/electrode_potential_law_v1.py", "sha256:ca3b67badbb313e135e9231fb4a0db6a17bd3558775407d8aa0efc6285935896"),
    ("sft/chemistry/cell_potential_composition_law_v1.py", "sha256:04cd27e4a5b4e2f1e9f9fdb4927cbc458ef3194c096486fcca16190a55aff886"),
    ("sft/chemistry/concentration_potential_law_v1.py", "sha256:2a4bc0d26396b7153cae23014bfc98c3708b0206aedea9a66e0157a5d2fa4bfc"),
    ("experiments/external_sources/chemistry/echem_002_target_identities_v1.json", "sha256:a2b0c83ce705aeff8bb20371446f27acc5b59e52d8e727698f4a37cbee325fb9"),
    ("experiments/external_sources/chemistry/echem_003_target_identities_v1.json", "sha256:94bfdfcfa5920a285c555c541aecd1e678b92848c06e11305f9bd3a894131e45"),
    ("experiments/external_sources/chemistry/echem_004_target_identities_v1.json", "sha256:30b9bd6af83114eca87e914f888c412d1d540bca731b97dc335daccd7c75c174"),
    ("experiments/sealed_predictions/chemistry_echem_002_electrode_potential_pre_source_v1.json", "sha256:57199514491854ce54165ae100ba7008c0bbd03ac304259aa50e7dccbc3b949f"),
    ("experiments/sealed_predictions/chemistry_echem_003_cell_potential_pre_source_v1.json", "sha256:b87a3450fd9a9596f5f410747fdb223ec8e88005ed1173f965aeee422a3d1a83"),
    ("experiments/sealed_predictions/chemistry_echem_004_concentration_potential_pre_source_v1.json", "sha256:87df635946459c70aa7c7defec2c2af105096838179d846524c8320f861bad39"),
    (INVENTORY_PATH, "sha256:47e583b3cd375da8f3f8a18b900f581b2189dedd0869a8b96dac5984dba32c7d"),
    (PDF_PATH, "sha256:e1ebb99701a17746d9eb417938e435084c05d0cdaa50642279f54b706d2275ab"),
    (ANALYSIS_PATH, ANALYSIS_HASH),
    ("tools/capture_chemistry_echem_002_004_sources_v1.py", "sha256:f0563c786993d92cd429980a75165806ed65539f1069bce221a81e36d6f00790"),
    ("tools/build_chemistry_echem_002_004_external_v1.py", "sha256:8052197458365fb57a6b502b88a9fe1f1d3c6e565c7bf2c4ae7c747600c5633b"),
)
for path, expected in AUTHORITIES:
    if hash_file(ROOT / path) != expected:
        raise ValueError(f"ECHEM-002-004 authority changed: {path}")

def targets(prefix, source_id, names):
    return tuple(ChemistryTargetReference(f"SFT-CHEM-{prefix}-{name}", source_id, name.casefold().replace("-", " "), ANALYSIS_PATH, ANALYSIS_HASH) for name in names)

E002_TARGETS = targets("ECHEM-002", "NIST-JRES-AGCL-STANDARD-POTENTIAL-1954", ("STANDARD-ROWS", "REFERENCE-CONDITION", "DIRECTION-VECTOR", "UNCERTAINTY-VECTOR", "ADVERSE-DIFFERENCE", "MODEL-PROVENANCE", "COMPLETE-PDF"))
E003_TARGETS = targets("ECHEM-003", "NIST-JRES-AGCL-COMPLETE-CELL-1954", ("CELL-CARRIERS", "NO-LIQUID-JUNCTION", "EMF-ROWS", "MOLALITY-DIRECTION", "CORRECTIONS", "REVERSAL-CONVENTION", "COMPLETE-PDF"))
E004_TARGETS = targets("ECHEM-004", "NIST-JRES-AGCL-HCL-CONCENTRATION-SERIES-1954", ("MOLALITY-TEMPERATURE-SUPPORT", "EMF-ROWS", "ACTIVITY-ROWS", "POTENTIAL-DIRECTION", "ACTIVITY-DIRECTION", "MODEL-PROVENANCE", "ADVERSE-BEHAVIOR", "COMPLETE-PDF"))

ELECTRODE_POTENTIAL_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-ELECTRODE-POTENTIAL-CHEMICAL-RELATION-002", title="Fold electrode-potential chemical relation",
    statement="Electrode potential is the exact held above, below or coincident relation between complete half-cell work-per-carrier accounts at one reference and condition.",
    dependencies=E002_DEPS, generation_rule="Generate the literal product of eight registered electrode-potential decisions.",
    grammar_boundary="Eight dimensions exhaust account, reference, condition, normalization, orientation, coincidence, record and extension.", dimensions=E002_DIMS, exact_result=E002_RESULT,
    induction_base="One subject and one reference half-cell under one condition supply the first exact relation.", induction_step="A common exact work-per-carrier successor preserves the relation without an offset.",
    exclusions=("no numerical zero negative irrational imaginary continuum fitted free random or imported native parameter", "no measured standard potential temperature or uncertainty selects the survivor", "least-squares smoothing and adjustable source parameters remain downstream provenance"), operational_witnesses=E002_WITNESSES,
    experiment_id="SFT-EXP-CHEM-ELECTRODE-POTENTIAL-CHEMICAL-RELATION-002", expected_observation_label="complete-electrode-potential-reference-vector", target_rows=E002_TARGETS, observation_registry_path=ANALYSIS_PATH,
    falsification_condition="The claim halts if the survivor is nonunique; any reference, condition, species, phase, potential, uncertainty, adverse discrepancy or NIST page is omitted; or a measured value or fitted source model selects the law.")

CELL_POTENTIAL_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-CELL-POTENTIAL-COMPOSITION-003", title="Fold cell-potential composition law",
    statement="Two admitted half-cell coordinates at one reference and condition compose by exact positive sum or Take along a held cell path, with EmptyOne at coincidence and exact reversal.",
    dependencies=E003_DEPS, generation_rule="Generate the literal product of eight registered full-cell composition decisions.",
    grammar_boundary="Eight dimensions exhaust carriers, reference, condition, path, composition, coincidence, record and reversal.", dimensions=E003_DIMS, exact_result=E003_RESULT,
    induction_base="Two distinct held half-cells sharing one reference and condition form the first complete cell.", induction_step="Appending a common exact reference context preserves the composed separation and its reversible path.",
    exclusions=("no numerical zero negative irrational imaginary continuum fitted free random or imported native parameter", "no measured EMF molality or temperature selects composition", "all measurement and unapplied-correction records remain downstream provenance"), operational_witnesses=E003_WITNESSES,
    experiment_id="SFT-EXP-CHEM-CELL-POTENTIAL-COMPOSITION-003", expected_observation_label="complete-cell-potential-composition-vector", target_rows=E003_TARGETS, observation_registry_path=ANALYSIS_PATH,
    falsification_condition="The claim halts if the survivor is nonunique; a half-cell, reference, condition, path, EMF row, correction, reverse convention or NIST page is omitted; or a measured value selects composition.")

CONCENTRATION_POTENTIAL_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-CONCENTRATION-DEPENDENT-POTENTIAL-004", title="Fold concentration-dependent potential law",
    statement="A generated activity quotient changes potential by an exact held direction and positive generator-layer-per-carrier ratio; exact standard-state equality is EmptyOne.",
    dependencies=E004_DEPS, generation_rule="Generate the literal product of eight registered concentration-potential decisions.",
    grammar_boundary="Eight dimensions exhaust state, quotient, support, composition, transfer, coincidence, record and extension.", dimensions=E004_DIMS, exact_result=E004_RESULT,
    induction_base="One generated activity layer doubles complete finite support and yields one positive layer per held carrier account.", induction_step="A common generator successor preserves exact layer separation without refitting.",
    exclusions=("no numerical zero negative irrational imaginary continuum fitted free random or imported native parameter", "no imported logarithm Debye-Huckel coefficient smoothing law or measured series selects the survivor", "all conventional source equations fitted terms anomalies and values remain downstream provenance"), operational_witnesses=E004_WITNESSES,
    experiment_id="SFT-EXP-CHEM-CONCENTRATION-DEPENDENT-POTENTIAL-004", expected_observation_label="complete-concentration-activity-potential-vector", target_rows=E004_TARGETS, observation_registry_path=ANALYSIS_PATH,
    falsification_condition="The claim halts if the survivor is nonunique; any molality, temperature, potential, activity, uncertainty, anomaly or NIST page is omitted; or a logarithm, fitted coefficient or measured trend selects the native law.")

for spec in (ELECTRODE_POTENTIAL_SPEC, CELL_POTENTIAL_SPEC, CONCENTRATION_POTENTIAL_SPEC):
    spec.validate()
COMPLETENESS_CERTIFICATES = {spec.claim_id: sha256_identity((spec.claim_id, tuple(row.target_id for row in spec.target_rows), 8, 37013, spec.exact_result)) for spec in (ELECTRODE_POTENTIAL_SPEC, CELL_POTENTIAL_SPEC, CONCENTRATION_POTENTIAL_SPEC)}
__all__ = ("ANALYSIS_HASH", "ANALYSIS_PATH", "AUTHORITIES", "CELL_POTENTIAL_SPEC", "COMPLETENESS_CERTIFICATES", "CONCENTRATION_POTENTIAL_SPEC", "ELECTRODE_POTENTIAL_SPEC", "INVENTORY_PATH", "PDF_PATH")
