"""Shared frozen registration for four separate ECHEM-005–008 claims."""
from pathlib import Path

from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.chemistry.electrochemical_work_law_v1 import DEPENDENCIES as E005_DEPS, DIMENSIONS as E005_DIMS, EXACT_RESULT as E005_RESULT, OPERATIONAL_WITNESSES as E005_WITNESSES
from sft.chemistry.electrolysis_product_law_v1 import DEPENDENCIES as E006_DEPS, DIMENSIONS as E006_DIMS, EXACT_RESULT as E006_RESULT, OPERATIONAL_WITNESSES as E006_WITNESSES
from sft.chemistry.ionic_conductivity_law_v1 import DEPENDENCIES as E007_DEPS_RAW, DIMENSIONS as E007_DIMS, EXACT_RESULT as E007_RESULT, OPERATIONAL_WITNESSES as E007_WITNESSES
from sft.chemistry.ionic_mobility_transference_law_v1 import DEPENDENCIES as E008_DEPS_RAW, DIMENSIONS as E008_DIMS, EXACT_RESULT as E008_RESULT, OPERATIONAL_WITNESSES as E008_WITNESSES
from sft.engine.canonical import sha256_identity
from sft.engine.source import hash_file

ROOT = Path(__file__).resolve().parents[2]
ANALYSIS_PATH = "experiments/external_sources/chemistry/snapshots/echem-005-008-transport-v1/complete-postseal-analysis-v2.json"
INVENTORY_PATH = "experiments/external_sources/chemistry/snapshots/echem-005-008-transport-v1/source-inventory-v1.json"
ANALYSIS_HASH = "sha256:1448531ff280e386330dce0dd15caa2031d5b520f0f76d1f0f460cd63d302a3e"

AUTHORITIES = (
    ("audits/CHEMISTRY_ECHEM_001_013_FAMILY_BOUNDARY_2026-07-28.json", "sha256:66f3152d791eafc5f677467ef7affd72f6559150be4adf586873a79c6ad473df"),
    ("experiments/external_sources/chemistry/echem_001_013_family_source_identity_registry_v1.json", "sha256:64ec429f537c2b0274cba689a32a65a6f36aebb3ecdc96678efcc49272c63106"),
    ("audits/CHEMISTRY_ECHEM_007_008_DEPENDENCY_IDENTITY_CORRECTION_2026-07-28.json", "sha256:adc848fe891d7ae121c09463ccd6c3ce3d6054f063fce4cbed70ad212962d95b"),
    ("sft/chemistry/electrochemical_work_law_v1.py", "sha256:2f2b1901ca92f2f5e518fc3ee018440aa6df0e9d3dd4464e1975987cfff5b97f"),
    ("sft/chemistry/electrolysis_product_law_v1.py", "sha256:e3b1644f6f8d7abfa40308359e63932d318057aad2a65b96f5b184eb2ebb4e97"),
    ("sft/chemistry/ionic_conductivity_law_v1.py", "sha256:7d74fb8bfe427f607aa8491b0652f7c01077939eaaa30e9d6aab5405b3843dff"),
    ("sft/chemistry/ionic_mobility_transference_law_v1.py", "sha256:f3be3f92e53b2a1ac6e4f641b4a40f5b2c5940aed212c60f2057ea88e04c2b21"),
    ("experiments/external_sources/chemistry/echem_005_target_identities_v1.json", "sha256:a428b42998d2287c1432f7ccead2a41f10d17b6cf9426b2b0e5a59a6368981a7"),
    ("experiments/external_sources/chemistry/echem_006_target_identities_v1.json", "sha256:0db005f92628714b58eb8d40156fc0aeff18dd0163ecad14ca900d8cfc51157c"),
    ("experiments/external_sources/chemistry/echem_007_target_identities_v1.json", "sha256:a519269266aa9b5f136253657c3fc6f5409eaa884e2812b10b858b6597843574"),
    ("experiments/external_sources/chemistry/echem_008_target_identities_v1.json", "sha256:6f7a84294612efa2d3d9e4a7992310e4d8b4eb9e1d4c0c73dbe9927ea5eac35b"),
    ("experiments/sealed_predictions/chemistry_echem_005_electrochemical_work_pre_source_v1.json", "sha256:935005aec0ea440426905e6b286330ec5244b66a1048d752d3976b9b6c443eac"),
    ("experiments/sealed_predictions/chemistry_echem_006_electrolysis_product_pre_source_v1.json", "sha256:f9552fd4768f68867e1519d9b6649e6c3cd028baa37f3cd1d64bcb2c357176e4"),
    ("experiments/sealed_predictions/chemistry_echem_007_ionic_conductivity_pre_source_v1.json", "sha256:c950da3b805ff510084ec0c3d1b3f31ed79303e2a60d649e869130b34886154d"),
    ("experiments/sealed_predictions/chemistry_echem_008_ionic_mobility_transference_pre_source_v1.json", "sha256:59413d705ce5f3e962fd0723d46bf83ef0aba338cf9da62b5c598836da98b856"),
    (INVENTORY_PATH, "sha256:ec6801d6551b7e1a371289b06c12bda56a11524595b26fc92c24a50cc8472335"),
    ("experiments/external_sources/chemistry/snapshots/echem-005-008-transport-v1/complete-postseal-analysis-v1.json", "sha256:b78d59830d3b776017d8d39c6adfe11373d772af57ec6145a823f0568cc4c242"),
    (ANALYSIS_PATH, ANALYSIS_HASH),
    ("tools/seal_chemistry_echem_005_008_predictions_v1.py", "sha256:6166374a93b404e1b417f5c361378735b80842ee1a77b34a22271b04f99602ad"),
    ("tools/capture_chemistry_echem_005_008_sources_v1.py", "sha256:4271bb9182c98dd88df32db480c21eaebe7091866d6e8187ed2a14e879b680cb"),
    ("tools/build_chemistry_echem_005_008_external_v1.py", "sha256:ca83acb81052705cff2332a16a933bac388e90713465cbe731062fe209efe868"),
)
for path, expected in AUTHORITIES:
    if hash_file(ROOT / path) != expected:
        raise ValueError(f"ECHEM-005–008 authority changed: {path}")

# This pre-admission resolution changes no law, candidate, target or outcome.
# The exact correction record above preserves both original pre-source seals.
E007_DEPS = tuple("SFT-COMP-CPLX-TIME-SPACE-001" if row == "SFT-COMP-RESOURCE-LAW-001" else row for row in E007_DEPS_RAW)
E008_DEPS = tuple("SFT-INFO-MUTUAL-CONDITIONAL-001" if row == "SFT-INFO-CONDITIONAL-001" else row for row in E008_DEPS_RAW)


def targets(prefix: str, rows: tuple[tuple[str, str], ...]) -> tuple[ChemistryTargetReference, ...]:
    return tuple(ChemistryTargetReference(f"SFT-CHEM-ECHEM-{prefix}-{name}", source_id, name.casefold().replace("-", " "), ANALYSIS_PATH, ANALYSIS_HASH) for name, source_id in rows)


E005_TARGETS = targets("005", (("FARADAY-CUSTODY", "NIST-CODATA-2022-ALL-CONSTANTS"), ("POTENTIAL-VECTOR", "NIST-JRES-AGCL-STANDARD-POTENTIAL-1954"), ("WORK-VECTOR", "NIST-CODATA-AGCL-WORK-CROSS-RECONSTRUCTION"), ("DIRECTION", "IUPAC-GREEN-BOOK-ELECTROCHEMISTRY-2007"), ("EQUILIBRIUM", "IUPAC-GREEN-BOOK-ELECTROCHEMISTRY-2007"), ("UNCERTAINTIES", "NIST-CODATA-AGCL-WORK-CROSS-RECONSTRUCTION"), ("ADVERSE-CONTROLS", "NIST-CODATA-AGCL-WORK-CROSS-RECONSTRUCTION"), ("COMPLETE-SOURCES", "ECHEM-005-SOURCE-INVENTORY")))
E006_TARGETS = targets("006", (("PROCESS-CUSTODY", "NIST-JRES-SILVER-ELECTROCHEMICAL-EQUIVALENT-1980"), ("CHARGE-TIME-VECTOR", "NIST-JRES-SILVER-ELECTROCHEMICAL-EQUIVALENT-1980"), ("PRODUCT-MASS-VECTOR", "NIST-JRES-SILVER-ELECTROCHEMICAL-EQUIVALENT-1980"), ("EQUIVALENT-VECTOR", "NIST-JRES-SILVER-ELECTROCHEMICAL-EQUIVALENT-1980"), ("FARADAY-CROSSCHECK", "NIST-CODATA-2022-ALL-CONSTANTS"), ("CORRECTIONS", "NIST-JRES-SILVER-ELECTROCHEMICAL-EQUIVALENT-1980"), ("UNCERTAINTY-ADVERSE", "NIST-JRES-SILVER-ELECTROCHEMICAL-EQUIVALENT-1980"), ("COMPLETE-SOURCES", "ECHEM-006-SOURCE-INVENTORY")))
E007_TARGETS = targets("007", (("SRM-IDENTITY", "NIST-SRM-3190-CONDUCTIVITY-CERTIFICATE"), ("COMPOSITION", "NIST-SRM-3190-CONDUCTIVITY-CERTIFICATE"), ("CONDITION", "NIST-SRM-3190-CONDUCTIVITY-CERTIFICATE"), ("CERTIFIED-VALUE", "NIST-SRM-3190-CONDUCTIVITY-CERTIFICATE"), ("UNCERTAINTY", "NIST-SRM-3190-CONDUCTIVITY-CERTIFICATE"), ("METHOD", "NIST-SP-260-142-PRIMARY-CONDUCTIVITY"), ("CATALOG-VECTOR", "NIST-SP-260-176-SRM-CATALOG"), ("COMPLETE-SOURCES", "ECHEM-007-SOURCE-INVENTORY")))
E008_TARGETS = targets("008", (("SPECIES", "NBS-JRES-TRANSFERENCE-CONCENTRATION-1931"), ("METHOD", "NBS-JRES-TRANSFERENCE-CONCENTRATION-1931"), ("CONCENTRATION-VECTOR", "NBS-JRES-TRANSFERENCE-CONCENTRATION-1931"), ("TRANSFERENCE-VECTOR", "NBS-JRES-TRANSFERENCE-CONCENTRATION-1931"), ("MOBILITY-RELATION", "NBS-JRES-TRANSFERENCE-CONCENTRATION-1931"), ("PARTITION", "IUPAC-GREEN-BOOK-ELECTROCHEMISTRY-2007"), ("ADVERSE-RESULTS", "NBS-JRES-TRANSFERENCE-CONCENTRATION-1931"), ("COMPLETE-SOURCES", "ECHEM-008-SOURCE-INVENTORY")))


WORK_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-ELECTROCHEMICAL-WORK-REACTION-DIRECTION-005", title="Fold electrochemical work and reaction-direction correspondence",
    statement="Electrochemical work is the exact positive product of counted transferred carriers and held potential separation, with separate chemical/electrical path direction and structural EmptyOne equilibrium.",
    dependencies=E005_DEPS, generation_rule="Generate the literal product of eight registered electrochemical-work decisions.", grammar_boundary="Eight dimensions exhaust custody, carrier, potential, composition, direction, equilibrium, record and reversal.", dimensions=E005_DIMS, exact_result=E005_RESULT,
    induction_base="One transferred carrier across one positive held separation supplies the first work account.", induction_step="Appending one carrier composes one more exact potential-separation part while retaining both paths.",
    exclusions=("no numerical zero negative irrational imaginary continuum fitted free random or imported native parameter", "no potential Faraday work or equilibrium outcome selects the survivor", "all conventional signs historical disagreements and uncertainties remain downstream provenance"), operational_witnesses=E005_WITNESSES,
    experiment_id="SFT-EXP-CHEM-ELECTROCHEMICAL-WORK-REACTION-DIRECTION-005", expected_observation_label="complete-electrochemical-work-reaction-direction-vector", target_rows=E005_TARGETS, observation_registry_path=ANALYSIS_PATH,
    falsification_condition="The claim halts if the survivor is nonunique; any carrier, path, potential, work, equilibrium, uncertainty, disagreement or source page is omitted; or an external value selects the law.")

ELECTROLYSIS_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-ELECTROLYSIS-PRODUCT-AMOUNT-006", title="Fold electrolysis and product-amount law",
    statement="Electrolysis product amount is the exact transferred-carrier to stoichiometric-carrier ratio with complete product, path and remainder custody.",
    dependencies=E006_DEPS, generation_rule="Generate the literal product of eight registered electrolysis-product decisions.", grammar_boundary="Eight dimensions exhaust custody, charge, stoichiometry, amount, remainder, absence, record and composition.", dimensions=E006_DIMS, exact_result=E006_RESULT,
    induction_base="One positive carrier occurrence against one positive product demand supplies the first exact amount.", induction_step="Like carrier batches compose by exact counted addition without changing the product law.",
    exclusions=("no numerical zero negative irrational imaginary continuum fitted free random or imported native parameter", "no coulometer mass current time Faraday or fitted correction selects the survivor", "every correction uncertainty adverse comparison and historical value remains downstream provenance"), operational_witnesses=E006_WITNESSES,
    experiment_id="SFT-EXP-CHEM-ELECTROLYSIS-PRODUCT-AMOUNT-006", expected_observation_label="complete-electrolysis-product-amount-vector", target_rows=E006_TARGETS, observation_registry_path=ANALYSIS_PATH,
    falsification_condition="The claim halts if the survivor is nonunique; any run, charge, time, mass, correction, uncertainty, adverse comparison or source page is omitted; or an external equivalent selects the law.")

CONDUCTIVITY_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-IONIC-CONDUCTIVITY-RELATION-007", title="Fold ionic conductivity relation",
    statement="Ionic conductivity is the exact positive sum of every species-resolved carried distinction per finite held path resource under one composition and condition.",
    dependencies=E007_DEPS, generation_rule="Generate the literal product of eight registered ionic-conductivity decisions.", grammar_boundary="Eight dimensions exhaust carrier, direction, composition, condition, path, aggregation, record and extension.", dimensions=E007_DIMS, exact_result=E007_RESULT,
    induction_base="One observed ionic carrier over one positive path resource supplies the first exact response.", induction_step="Appending one distinct positive species contribution increases the exact total without refitting prior terms.",
    exclusions=("no numerical zero negative irrational imaginary continuum fitted free random or imported native parameter", "no certified conductivity composition temperature or uncertainty selects the survivor", "continuum source equations remain downstream provenance"), operational_witnesses=E007_WITNESSES,
    experiment_id="SFT-EXP-CHEM-IONIC-CONDUCTIVITY-RELATION-007", expected_observation_label="complete-species-resolved-ionic-conductivity-vector", target_rows=E007_TARGETS, observation_registry_path=ANALYSIS_PATH,
    falsification_condition="The claim halts if the survivor is nonunique; any ion, composition, temperature, cell, value, unit, uncertainty, method, catalog row or source page is omitted; or a measured value selects the law.")

MOBILITY_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-IONIC-MOBILITY-TRANSFERENCE-008", title="Fold ionic mobility and transference law",
    statement="Each ionic mobility is an exact positive traversal-per-carrier-resource ratio and each transference part is that species contribution divided by the complete total, summing exactly to One.",
    dependencies=E008_DEPS, generation_rule="Generate the literal product of eight registered mobility-transference decisions.", grammar_boundary="Eight dimensions exhaust identity, direction, mobility, composition, partition, whole, absence and record.", dimensions=E008_DIMS, exact_result=E008_RESULT,
    induction_base="One mobile species forms the complete One partition of its first finite transport record.", induction_step="Appending a distinct positive carrier repartitions the complete exact total while retaining every prior species contribution.",
    exclusions=("no numerical zero negative irrational imaginary continuum fitted free random or imported native parameter", "no transference mobility concentration direction or anomaly selects the survivor", "all conventional derivatives fits and unresolved results remain downstream provenance"), operational_witnesses=E008_WITNESSES,
    experiment_id="SFT-EXP-CHEM-IONIC-MOBILITY-TRANSFERENCE-008", expected_observation_label="complete-ionic-mobility-transference-vector", target_rows=E008_TARGETS, observation_registry_path=ANALYSIS_PATH,
    falsification_condition="The claim halts if the survivor is nonunique; any species, direction, concentration, mobility, transference, anomaly, absent row or source page is omitted; or a measured value selects the law.")

SPECS = (WORK_SPEC, ELECTROLYSIS_SPEC, CONDUCTIVITY_SPEC, MOBILITY_SPEC)
for spec in SPECS:
    spec.validate()
COMPLETENESS_CERTIFICATES = {spec.claim_id: sha256_identity((spec.claim_id, tuple(row.target_id for row in spec.target_rows), 519, 1754402, spec.exact_result)) for spec in SPECS}

__all__ = ("ANALYSIS_HASH", "ANALYSIS_PATH", "AUTHORITIES", "COMPLETENESS_CERTIFICATES", "CONDUCTIVITY_SPEC", "ELECTROLYSIS_SPEC", "INVENTORY_PATH", "MOBILITY_SPEC", "SPECS", "WORK_SPEC")
