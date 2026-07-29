"""Shared frozen registration for four separate NUCHEM-001–004 claims."""
from pathlib import Path

from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.chemistry.nuclide_chemical_carrier_law_v1 import DEPENDENCIES as N001_DEPS, DIMENSIONS as N001_DIMS, EXACT_RESULT as N001_RESULT, OPERATIONAL_WITNESSES as N001_WITNESSES
from sft.chemistry.radioactive_chemical_transformation_law_v1 import DEPENDENCIES as N002_DEPS, DIMENSIONS as N002_DIMS, EXACT_RESULT as N002_RESULT, OPERATIONAL_WITNESSES as N002_WITNESSES
from sft.chemistry.activity_amount_time_law_v1 import DEPENDENCIES as N003_DEPS, DIMENSIONS as N003_DIMS, EXACT_RESULT as N003_RESULT, OPERATIONAL_WITNESSES as N003_WITNESSES
from sft.chemistry.radioactive_branching_yield_law_v1 import DEPENDENCIES as N004_DEPS, DIMENSIONS as N004_DIMS, EXACT_RESULT as N004_RESULT, OPERATIONAL_WITNESSES as N004_WITNESSES
from sft.engine.canonical import sha256_identity
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parents[2]
ANALYSIS_PATH = "experiments/external_sources/chemistry/snapshots/nuchem-001-004-radioactivity-v1/complete-postseal-analysis-v1.json"
INVENTORY_PATH = "experiments/external_sources/chemistry/snapshots/nuchem-001-004-radioactivity-v1/source-inventory-v1.json"
ANALYSIS_HASH = "sha256:ce2bd2582090dd694dc3ccfe3bd50fec5987fe361609be52282a28f0f530b474"

AUTHORITIES = (
    ("audits/CHEMISTRY_NUCHEM_001_012_FAMILY_BOUNDARY_2026-07-28.json", "sha256:77cefa7bb8a338c3b0e2de615ee7335c7c18c680423c58ecf336a5420bc4109f"),
    ("experiments/external_sources/chemistry/nuchem_001_012_family_source_identity_registry_v1.json", "sha256:9dcc65c3ac597ba67453fe6e7b10b3b33903f7a1d4732081dde8aac7041395d9"),
    ("sft/chemistry/nuclide_chemical_carrier_law_v1.py", "sha256:5b1cba279810bdd761987c7970c717a881142d20a173320131bb07f29e4dc95b"),
    ("sft/chemistry/radioactive_chemical_transformation_law_v1.py", "sha256:4484c0c4efdef922aabd3fa14b9b74756305dfb03c6b3d884d96f661dd5ffd95"),
    ("sft/chemistry/activity_amount_time_law_v1.py", "sha256:186a95d558ac63e883b8af7b60c6c1780fcfb7b042bcfc264d73050ce22f96bd"),
    ("sft/chemistry/radioactive_branching_yield_law_v1.py", "sha256:163218db86c3cbdf11e55babcbcc5a982a3376a4841957f6c6ee05f2dd5ef52c"),
    ("experiments/external_sources/chemistry/nuchem_001_target_identities_v1.json", "sha256:4ca08fe787a69f03c55002905d835c0dcf012a7b8ff31935430693db2cc3f263"),
    ("experiments/external_sources/chemistry/nuchem_002_target_identities_v1.json", "sha256:a9e98d3078a684b6fcad2c64ad764da4f6202bb9a9f8a77d3369479821315b26"),
    ("experiments/external_sources/chemistry/nuchem_003_target_identities_v1.json", "sha256:7f2dbaba26aea9d499aae35ce29a8217e2fdb7c4ef8c60a9d5f4cc453176aa0d"),
    ("experiments/external_sources/chemistry/nuchem_004_target_identities_v1.json", "sha256:cb85154e9f9cbd381cd7824c57e63364117df291dc7f3148bcb507a15c9a8787"),
    ("experiments/sealed_predictions/chemistry_nuchem_001_pre_source_v1.json", "sha256:e6a292d3ea5d8b3afe46e66d65bcdfae056ea40c508ee0bd787794c562bc7104"),
    ("experiments/sealed_predictions/chemistry_nuchem_002_pre_source_v1.json", "sha256:3c3ede4d5d1f516a99e364b51e9462dd86214f5b640ee0008da3558102e39454"),
    ("experiments/sealed_predictions/chemistry_nuchem_003_pre_source_v1.json", "sha256:c16ac68db0ccb2c18515a007a756eac46595b8cbebe6078a1e16be23572ff9d3"),
    ("experiments/sealed_predictions/chemistry_nuchem_004_pre_source_v1.json", "sha256:3c03263c9c780e0888d90e0a4519726640dd9eb9f8ed1084bbc85ed590861ae0"),
    (INVENTORY_PATH, "sha256:c225880187ffd2839a2dc549b5d5466e91d650e4bc68373dd7674a18df34dc52"),
    (ANALYSIS_PATH, ANALYSIS_HASH),
    ("tools/seal_chemistry_nuchem_001_004_predictions_v1.py", "sha256:6845f016fafb3b3e71b1b2acb46dd9bd74828c0c644dce6d807b1997cd19e300"),
    ("tools/capture_chemistry_nuchem_001_004_sources_v1.py", "sha256:e1f689e44b5755ecd4217033f98734a223ccc545de1a212d278fd54e165b0864"),
    ("tools/build_chemistry_nuchem_001_004_external_v1.py", "sha256:76a20c053c17292d27cf4d547a998fa3f9e0058ac3234400d978d322321a9e08"),
)
for path, expected in AUTHORITIES:
    if hash_file(ROOT / path) != expected:
        raise ValueError(f"NUCHEM-001–004 authority changed: {path}")


def targets(prefix: str, rows: tuple[tuple[str, str], ...]) -> tuple[ChemistryTargetReference, ...]:
    return tuple(ChemistryTargetReference(f"SFT-CHEM-NUCHEM-{prefix}-{name}", source, name.casefold().replace("-", " "), ANALYSIS_PATH, ANALYSIS_HASH) for name, source in rows)


N001_TARGETS = targets("001", (("ELEMENT", "NIST-NUCLEAR-PHYSICS-DATA-ISOTOPIC-COMPOSITION"), ("NUCLIDE", "NIST-SRM-4239A-STRONTIUM-90-2022"), ("STATE", "NIST-SRM-4239A-STRONTIUM-90-2022"), ("SPECIES", "NIST-SRM-4239A-STRONTIUM-90-2022"), ("PHASE", "NIST-SRM-4239A-STRONTIUM-90-2022"), ("AMOUNT", "NIST-RADIOACTIVITY-SRMS-GENERAL-INFO-2025"), ("UNCERTAINTY", "NIST-SRM-4239A-STRONTIUM-90-2022"), ("COMPLETE-SOURCES", "NUCHEM-001-004-SOURCE-INVENTORY")))
N002_TARGETS = targets("002", (("PARENT", "NIST-SRM-4239A-STRONTIUM-90-2022"), ("DAUGHTER", "NIST-SRM-4239A-STRONTIUM-90-2022"), ("CHEMICAL-STATES", "NIST-SRM-4239A-STRONTIUM-90-2022"), ("CHANNELS", "NIST-SRM-4324C-URANIUM-232-2025"), ("NETWORK", "NIST-SRM-4324C-URANIUM-232-2025"), ("EQUILIBRIUM", "NIST-SRM-4324C-URANIUM-232-2025"), ("ADVERSE-METHODS", "NUCHEM-001-004-SHARED-SOURCES"), ("COMPLETE-SOURCES", "NUCHEM-001-004-SOURCE-INVENTORY")))
N003_TARGETS = targets("003", (("IDENTITY", "NIST-RADIOACTIVITY-SRMS-GENERAL-INFO-2025"), ("AMOUNT-FORMS", "NIST-RADIOACTIVITY-SRMS-GENERAL-INFO-2025"), ("ACTIVITY-UNIT", "NIST-RADIOACTIVITY-SRMS-GENERAL-INFO-2025"), ("REFERENCE-TIME", "NIST-SRM-4239A-STRONTIUM-90-2022"), ("MASSIC-ACTIVITY", "NIST-SRM-4239A-STRONTIUM-90-2022"), ("UNCERTAINTY", "NIST-SRM-4239A-STRONTIUM-90-2022"), ("TIME-RELATION", "NIST-SRM-4324C-URANIUM-232-2025"), ("COMPLETE-SOURCES", "NUCHEM-001-004-SOURCE-INVENTORY")))
N004_TARGETS = targets("004", (("CHANNELS", "NIST-SRM-4324C-URANIUM-232-2025"), ("DAUGHTERS", "NIST-SRM-4324C-URANIUM-232-2025"), ("BRANCH-FRACTIONS", "NIST-RADIOACTIVITY-SRMS-GENERAL-INFO-2025"), ("CHEMICAL-RECOVERY", "NIST-SRM-4239A-STRONTIUM-90-2022"), ("PARTITION", "NIST-SRM-4324C-URANIUM-232-2025"), ("METHODS", "NIST-SRM-4324C-URANIUM-232-2025"), ("ADVERSE-UNCERTAINTY", "NUCHEM-001-004-SHARED-SOURCES"), ("COMPLETE-SOURCES", "NUCHEM-001-004-SOURCE-INVENTORY")))


CARRIER_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-NUCLEAR-CHEMICAL-CARRIER-001", title="Fold nuclide chemical-carrier law",
    statement="A chemical nuclide carrier retains element, positive nucleon count, nuclear state, chemical species, phase and positive occurrence as one exact identity vector.",
    dependencies=N001_DEPS, generation_rule="Generate the literal product of eight registered carrier decisions.", grammar_boundary="Eight dimensions exhaust element, nuclide, state, species, phase, occurrence, record and extension.", dimensions=N001_DIMS, exact_result=N001_RESULT,
    induction_base="One held nuclide occurrence supplies the first exact chemical carrier.", induction_step="A fresh occurrence retains every identity coordinate while extending the positive occurrence count.",
    exclusions=("no numerical zero negative irrational imaginary continuum fitted free random or imported native parameter", "no external nuclide table chemical matrix activity or uncertainty selects the survivor", "unreported nuclear state is retained as unreported rather than inferred"), operational_witnesses=N001_WITNESSES,
    experiment_id="SFT-EXP-CHEM-NUCLEAR-CHEMICAL-CARRIER-001", expected_observation_label="complete-nuclide-chemical-carrier-vector", target_rows=N001_TARGETS, observation_registry_path=ANALYSIS_PATH,
    falsification_condition="The claim halts if the survivor is nonunique; any element, nuclide, state, species, phase, occurrence, uncertainty, adverse or unavailable row, page or byte is omitted; or an external value selects the law.")

TRANSFORMATION_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-RADIOACTIVE-CHEMICAL-TRANSFORMATION-002", title="Fold radioactive chemical-transformation network",
    statement="A radioactive chemical transformation is a complete directed network retaining parent, daughter, both chemical species, channel and positive counted events, with structural absence and reconstructive extension.",
    dependencies=N002_DEPS, generation_rule="Generate the literal product of eight registered transformation decisions.", grammar_boundary="Eight dimensions exhaust parent, daughter, chemistry, channel, events, network, absence and extension.", dimensions=N002_DIMS, exact_result=N002_RESULT,
    induction_base="One held parent/daughter chemical edge supplies the first directed transformation.", induction_step="A distinct successor edge preserves the prior network and adds its held channel and counted events.",
    exclusions=("no numerical zero negative irrational imaginary continuum fitted free random or imported native parameter", "no external decay chain or equilibrium record selects the survivor", "no source assumption or disagreement is suppressed"), operational_witnesses=N002_WITNESSES,
    experiment_id="SFT-EXP-CHEM-RADIOACTIVE-CHEMICAL-TRANSFORMATION-002", expected_observation_label="complete-radioactive-chemical-transformation-vector", target_rows=N002_TARGETS, observation_registry_path=ANALYSIS_PATH,
    falsification_condition="The claim halts if the survivor is nonunique; any parent, daughter, chemical state, channel, edge, equilibrium, assumption, disagreement, page or byte is omitted; or an external network selects the law.")

ACTIVITY_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-ACTIVITY-AMOUNT-TIME-003", title="Fold activity–amount–time law",
    statement="Activity is the exact positive ratio of counted transformations to counted resource intervals for a held nuclide species, while retained amount is positive Take or structural absence.",
    dependencies=N003_DEPS, generation_rule="Generate the literal product of eight registered activity decisions.", grammar_boundary="Eight dimensions exhaust identity, amount, events, time, activity, remaining amount, record and extension.", dimensions=N003_DIMS, exact_result=N003_RESULT,
    induction_base="One counted transformation over one counted interval supplies the first activity ledger.", induction_step="A successor updates event and interval counts exactly and recomputes activity and retained amount.",
    exclusions=("no numerical zero negative irrational imaginary continuum fitted free random or imported native parameter", "no measured activity half-life reference time or unit selects the survivor", "all decimal conventional continuum and signed inscriptions remain downstream provenance"), operational_witnesses=N003_WITNESSES,
    experiment_id="SFT-EXP-CHEM-ACTIVITY-AMOUNT-TIME-003", expected_observation_label="complete-activity-amount-time-vector", target_rows=N003_TARGETS, observation_registry_path=ANALYSIS_PATH,
    falsification_condition="The claim halts if the survivor is nonunique; any identity, amount form, event, interval, activity, reference time, uncertainty, correction, adverse or unavailable row, page or byte is omitted; or a measurement selects the law.")

BRANCHING_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-RADIOACTIVE-BRANCHING-CHEMICAL-YIELD-004", title="Fold radioactive branching chemical-yield law",
    statement="Radioactive chemical yield retains every held decay channel and daughter species, positive branch and recovered event counts, exact recovery ratios and a complete branch partition of One.",
    dependencies=N004_DEPS, generation_rule="Generate the literal product of eight registered branching decisions.", grammar_boundary="Eight dimensions exhaust channel, daughter, events, recovery, yield, partition, record and extension.", dimensions=N004_DIMS, exact_result=N004_RESULT,
    induction_base="One held channel with counted events and recoveries supplies the first exact yield row.", induction_step="A fresh channel preserves prior rows and repartitions the complete positive event total.",
    exclusions=("no numerical zero negative irrational imaginary continuum fitted free random or imported native parameter", "no external branch fraction daughter list or recovery result selects the survivor", "an unavailable numerical branch fraction remains unavailable and is never fabricated or renormalized"), operational_witnesses=N004_WITNESSES,
    experiment_id="SFT-EXP-CHEM-RADIOACTIVE-BRANCHING-CHEMICAL-YIELD-004", expected_observation_label="complete-radioactive-branching-chemical-yield-vector", target_rows=N004_TARGETS, observation_registry_path=ANALYSIS_PATH,
    falsification_condition="The claim halts if the survivor is nonunique; any channel, daughter, branch, recovery, method, assumption, discrepancy, uncertainty, unavailable row, page or byte is omitted; or external outcomes select the law.")

SPECS = (CARRIER_SPEC, TRANSFORMATION_SPEC, ACTIVITY_SPEC, BRANCHING_SPEC)
for spec in SPECS:
    spec.validate()
COMPLETENESS_CERTIFICATES = {spec.claim_id: sha256_identity((spec.claim_id, tuple(row.target_id for row in spec.target_rows), 8, 2, 34442, spec.exact_result)) for spec in SPECS}

__all__ = ("ACTIVITY_SPEC", "ANALYSIS_HASH", "ANALYSIS_PATH", "AUTHORITIES", "BRANCHING_SPEC", "CARRIER_SPEC", "COMPLETENESS_CERTIFICATES", "INVENTORY_PATH", "SPECS", "TRANSFORMATION_SPEC")
