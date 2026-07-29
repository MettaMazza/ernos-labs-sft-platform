"""Shared frozen registration for four separate NUCHEM-005–008 claims."""
from pathlib import Path

from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.chemistry.radiochemical_equilibrium_law_v1 import DEPENDENCIES as N005_DEPS, DIMENSIONS as N005_DIMS, EXACT_RESULT as N005_RESULT, OPERATIONAL_WITNESSES as N005_WITNESSES
from sft.chemistry.isotope_exchange_law_v1 import DEPENDENCIES as N006_DEPS, DIMENSIONS as N006_DIMS, EXACT_RESULT as N006_RESULT, OPERATIONAL_WITNESSES as N006_WITNESSES
from sft.chemistry.equilibrium_isotope_fractionation_law_v1 import DEPENDENCIES as N007_DEPS, DIMENSIONS as N007_DIMS, EXACT_RESULT as N007_RESULT, OPERATIONAL_WITNESSES as N007_WITNESSES
from sft.chemistry.kinetic_isotope_fractionation_law_v1 import DEPENDENCIES as N008_DEPS, DIMENSIONS as N008_DIMS, EXACT_RESULT as N008_RESULT, OPERATIONAL_WITNESSES as N008_WITNESSES
from sft.engine.canonical import sha256_identity
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parents[2]
ANALYSIS_PATH = "experiments/external_sources/chemistry/snapshots/nuchem-005-008-isotope-v1/complete-postseal-analysis-v1.json"
INVENTORY_PATH = "experiments/external_sources/chemistry/snapshots/nuchem-005-008-isotope-v1/source-inventory-v1.json"
ANALYSIS_HASH = "sha256:fdadea49308fe7ee400c77ffb2573a3ff436a4cac19d68f0dea633e922019527"

AUTHORITIES = (
    ("audits/CHEMISTRY_NUCHEM_001_012_FAMILY_BOUNDARY_2026-07-28.json", "sha256:77cefa7bb8a338c3b0e2de615ee7335c7c18c680423c58ecf336a5420bc4109f"),
    ("experiments/external_sources/chemistry/nuchem_001_012_family_source_identity_registry_v1.json", "sha256:9dcc65c3ac597ba67453fe6e7b10b3b33903f7a1d4732081dde8aac7041395d9"),
    ("experiments/external_sources/chemistry/nuchem_005_008_family_source_identity_registry_v1.json", "sha256:19b2874fb1bf1300e9f6b60d1e76fe4f32fd00f02a660c9cf35f7dd889ade77b"),
    ("sft/chemistry/radiochemical_equilibrium_law_v1.py", "sha256:517914e1953e8bde79ec94c56001ebd78008fdf84fa0227896d58e1914048a69"),
    ("sft/chemistry/isotope_exchange_law_v1.py", "sha256:8020c83a3cd234074d80695493dd9b615671030fce80bead491fbc26a03a81d4"),
    ("sft/chemistry/equilibrium_isotope_fractionation_law_v1.py", "sha256:b5df27ccdcce7c48864b69d26837f5c34586faab26a0325f9b2d83ddd887eccd"),
    ("sft/chemistry/kinetic_isotope_fractionation_law_v1.py", "sha256:7ee759e8694ce914142c47d0b3b648771090119b81a0a951ed796cdc5ee3d331"),
    ("experiments/external_sources/chemistry/nuchem_005_target_identities_v1.json", "sha256:5aa52d065525eb8f6fad00e7ace2b09b2c73b66216659bc9d0a2918d93791487"),
    ("experiments/external_sources/chemistry/nuchem_006_target_identities_v1.json", "sha256:9ebf33adb3d143519029025bc31b2a7d5a8a9fff6b691457abe2c039844b81b6"),
    ("experiments/external_sources/chemistry/nuchem_007_target_identities_v1.json", "sha256:98fbc69aba91a79c974cd49824febdf8f2c36d76d00e9b75cb75d16498f6a216"),
    ("experiments/external_sources/chemistry/nuchem_008_target_identities_v1.json", "sha256:94a2706d5a1b8a3fcdb69036b4cfb8b1a675acb811c50fbbb74301384f951b99"),
    ("experiments/sealed_predictions/chemistry_nuchem_005_pre_source_v1.json", "sha256:9436a1000ff1efdf8b2f934f9f44024e5fd8862da321ab2182f96fccd0d95a91"),
    ("experiments/sealed_predictions/chemistry_nuchem_006_pre_source_v1.json", "sha256:bcd18bde92a7ee35b3541a0d83ed3ac3cb54c323dd26482d7d3f1bf76f7ea5f8"),
    ("experiments/sealed_predictions/chemistry_nuchem_007_pre_source_v1.json", "sha256:0733d1926431ed8e6f875f13f9fa6a81eee6b509e565c97f5d4491ad6d891944"),
    ("experiments/sealed_predictions/chemistry_nuchem_008_pre_source_v1.json", "sha256:938778dff4ddcc3896f0e4e3be91c878fa346bca3fe51f63f3a8b2c0ae53af1a"),
    (INVENTORY_PATH, "sha256:bd9cc53f97b20a2d92bc26ab28ce2f5eefb71e6b3ee1f02bf840214adaccdaee"),
    (ANALYSIS_PATH, ANALYSIS_HASH),
    ("tools/seal_chemistry_nuchem_005_008_predictions_v1.py", "sha256:d9bf2aee533a522ee16737937fb6c44cfb7a566a467902df13c3285aec703207"),
    ("tools/capture_chemistry_nuchem_005_008_sources_v1.py", "sha256:2ad6dfabff175e1d6f7f9ee97ce18805f1678d0063806802196e653be2f5bfd0"),
    ("tools/build_chemistry_nuchem_005_008_external_v1.py", "sha256:48b3b1673a00035e6cfdc6b29b5d4c9bb03dcf7c16be61d6302f640fb54f56a3"),
)
for path, expected in AUTHORITIES:
    if hash_file(ROOT / path) != expected: raise ValueError(f"NUCHEM-005–008 authority changed: {path}")


def targets(prefix: str, rows: tuple[tuple[str, str], ...]) -> tuple[ChemistryTargetReference, ...]:
    return tuple(ChemistryTargetReference(f"SFT-CHEM-NUCHEM-{prefix}-{name}", source, name.casefold().replace("-", " "), ANALYSIS_PATH, ANALYSIS_HASH) for name, source in rows)


N005_TARGETS = targets("005", (("PARENT-DAUGHTER", "NIST-SRM-4239A-STRONTIUM-90-2022"), ("TIME-SUPPORT", "NUCHEM-005-NIST-SRM-PAIR"), ("ACTIVITY", "NUCHEM-005-NIST-SRM-PAIR"), ("RATIO-REGIME", "NUCHEM-005-NIST-SRM-PAIR"), ("TRANSIENT", "NIST-SRM-4324C-URANIUM-232-2025"), ("SECULAR", "NUCHEM-005-NIST-SRM-PAIR"), ("ADVERSE-METHODS", "NUCHEM-005-008-SHARED-SOURCES"), ("COMPLETE-SOURCES", "NUCHEM-005-008-SOURCE-INVENTORY")))
N006_TARGETS = targets("006", (("ISOTOPES", "USGS-WRIR-02-4172-ISOTOPE-EQUILIBRIUM-CONSTANTS"), ("CARRIERS", "USGS-WRIR-02-4172-ISOTOPE-EQUILIBRIUM-CONSTANTS"), ("CONSERVATION", "USGS-WRIR-02-4172-ISOTOPE-EQUILIBRIUM-CONSTANTS"), ("EXCHANGE-QUOTIENT", "USGS-WRIR-02-4172-ISOTOPE-EQUILIBRIUM-CONSTANTS"), ("EQUILIBRIUM", "USGS-WRIR-02-4172-ISOTOPE-EQUILIBRIUM-CONSTANTS"), ("MULTISPECIES", "USGS-WRIR-02-4172-ISOTOPE-EQUILIBRIUM-CONSTANTS"), ("ADVERSE-ASSUMPTIONS", "NUCHEM-005-008-SHARED-SOURCES"), ("COMPLETE-SOURCES", "NUCHEM-005-008-SOURCE-INVENTORY")))
N007_TARGETS = targets("007", (("ISOTOPE-RATIOS", "USGS-PP-440-KK-STABLE-ISOTOPE-FRACTIONATION"), ("PHASES", "USGS-PP-440-KK-STABLE-ISOTOPE-FRACTIONATION"), ("FACTORS", "USGS-PP-440-KK-STABLE-ISOTOPE-FRACTIONATION"), ("ORIENTATION", "USGS-PP-440-KK-STABLE-ISOTOPE-FRACTIONATION"), ("TEMPERATURE", "USGS-PP-440-KK-STABLE-ISOTOPE-FRACTIONATION"), ("EQUILIBRIUM", "USGS-WRIR-02-4172-ISOTOPE-EQUILIBRIUM-CONSTANTS"), ("ADVERSE-UNAVAILABLE", "NUCHEM-005-008-SHARED-SOURCES"), ("COMPLETE-SOURCES", "NUCHEM-005-008-SOURCE-INVENTORY")))
N008_TARGETS = targets("008", (("REACTION-PATH", "NBS-RP729-ELECTROLYTIC-HYDROGEN-OXYGEN-FRACTIONATION-1934"), ("TIME-RESOURCE", "NBS-RP729-ELECTROLYTIC-HYDROGEN-OXYGEN-FRACTIONATION-1934"), ("PRODUCTS", "NBS-RP729-ELECTROLYTIC-HYDROGEN-OXYGEN-FRACTIONATION-1934"), ("RATES", "NBS-RP729-ELECTROLYTIC-HYDROGEN-OXYGEN-FRACTIONATION-1934"), ("FACTOR", "NBS-RP729-ELECTROLYTIC-HYDROGEN-OXYGEN-FRACTIONATION-1934"), ("STEADY-STATE", "NBS-RP729-ELECTROLYTIC-HYDROGEN-OXYGEN-FRACTIONATION-1934"), ("ADVERSE-CORRECTIONS", "NUCHEM-005-008-SHARED-SOURCES"), ("COMPLETE-SOURCES", "NUCHEM-005-008-SOURCE-INVENTORY")))


RADIOCHEMICAL_EQUILIBRIUM_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-RADIOCHEMICAL-EQUILIBRIUM-005", title="Fold transient and secular radiochemical-equilibrium law",
    statement="Radiochemical equilibrium is an exact persistent parent/daughter activity-ratio class over complete positive ordered resource intervals: persistent non-One is transient, persistent One is secular, and nonpersistent recurrence is structural absence.",
    dependencies=N005_DEPS, generation_rule="Generate the literal product of eight registered equilibrium decisions.", grammar_boundary="Eight dimensions exhaust identity, support, activity, ratio, transient, secular, record and extension.", dimensions=N005_DIMS, exact_result=N005_RESULT,
    induction_base="One exact parent/daughter activity pair supplies the first held ratio.", induction_step="Each successor interval preserves identities and recomputes the complete ratio recurrence.",
    exclusions=("no numerical zero negative irrational imaginary continuum fitted free random or imported native parameter", "no measured activity time support or conventional decay model selects the survivor", "qualitative equilibrium records cannot fabricate an unavailable numerical time series"), operational_witnesses=N005_WITNESSES,
    experiment_id="SFT-EXP-CHEM-RADIOCHEMICAL-EQUILIBRIUM-005", expected_observation_label="complete-radiochemical-equilibrium-vector", target_rows=N005_TARGETS, observation_registry_path=ANALYSIS_PATH,
    falsification_condition="The claim halts if the survivor is nonunique; any parent, daughter, interval, activity, regime, assumption, uncertainty, unavailable row, page or byte is omitted; or an external equilibrium label selects the law.")

ISOTOPE_EXCHANGE_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-ISOTOPE-EXCHANGE-006", title="Fold isotope-exchange reaction law",
    statement="Isotope exchange preserves exact element, isotope and carrier identities and all positive isotope/carrier totals, carries direction as a held positive excess, and forces its exchange quotient by cross-products.",
    dependencies=N006_DEPS, generation_rule="Generate the literal product of eight registered exchange decisions.", grammar_boundary="Eight dimensions exhaust identity, carriers, inventory, conservation, direction, quotient, equilibrium and extension.", dimensions=N006_DIMS, exact_result=N006_RESULT,
    induction_base="One complete two-isotope two-carrier inventory supplies the first exchange state.", induction_step="Each successor preserves identities and all isotope and carrier totals.",
    exclusions=("no numerical zero negative irrational imaginary continuum fitted free random or imported native parameter", "no external alpha table equilibrium constant or species result selects the survivor", "every nonideality assumption and unavailable row remains"), operational_witnesses=N006_WITNESSES,
    experiment_id="SFT-EXP-CHEM-ISOTOPE-EXCHANGE-006", expected_observation_label="complete-isotope-exchange-vector", target_rows=N006_TARGETS, observation_registry_path=ANALYSIS_PATH,
    falsification_condition="The claim halts if the survivor is nonunique; any isotope, carrier, conservation, quotient, example condition, nonideality, adverse row, page or byte is omitted; or an external quotient selects the law.")

EQUILIBRIUM_FRACTIONATION_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-EQUILIBRIUM-ISOTOPE-FRACTIONATION-007", title="Fold equilibrium isotope-fractionation law",
    statement="Equilibrium isotope fractionation is the exact ratio of two positive heavy-per-light phase ratios, with held enrichment or structural coincidence, exchange balance and a stable factor.",
    dependencies=N007_DEPS, generation_rule="Generate the literal product of eight registered fractionation decisions.", grammar_boundary="Eight dimensions exhaust identity, phases, inventory, ratios, factor, orientation, equilibrium and extension.", dimensions=N007_DIMS, exact_result=N007_RESULT,
    induction_base="One complete two-isotope two-phase inventory supplies the first exact factor.", induction_step="Every successor retains the complete phase vector and recomputes the exact ratio of ratios.",
    exclusions=("no numerical zero negative irrational imaginary continuum fitted free random or imported native parameter", "no measured fitted calculated inferred or estimated alpha value selects the survivor", "external signed deltas remain downstream measurement inscriptions"), operational_witnesses=N007_WITNESSES,
    experiment_id="SFT-EXP-CHEM-EQUILIBRIUM-ISOTOPE-FRACTIONATION-007", expected_observation_label="complete-equilibrium-isotope-fractionation-vector", target_rows=N007_TARGETS, observation_registry_path=ANALYSIS_PATH,
    falsification_condition="The claim halts if the survivor is nonunique; any isotope ratio, phase, factor, orientation, temperature, fit, estimate, discrepancy, unavailable row, page or byte is omitted; or an external factor selects the law.")

KINETIC_FRACTIONATION_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-KINETIC-ISOTOPE-FRACTIONATION-008", title="Fold kinetic isotope-fractionation law",
    statement="Kinetic isotope fractionation retains one reaction and two isotope identities over complete positive ordered resources, forces exact product rates and their factor, and records faster class and remainder without signed or negative native values.",
    dependencies=N008_DEPS, generation_rule="Generate the literal product of eight registered kinetic decisions.", grammar_boundary="Eight dimensions exhaust identity, support, events, rates, factor, orientation, inventory and extension.", dimensions=N008_DIMS, exact_result=N008_RESULT,
    induction_base="One isotope-resolved product interval supplies the first exact rate pair.", induction_step="Each successor preserves the path and recomputes the complete rate and remainder vector.",
    exclusions=("no numerical zero negative irrational imaginary continuum fitted free random or imported native parameter", "no measured kinetic response correction curve or conventional kinetic model selects the survivor", "every flow reversal loss estimate correction uncertainty limitation and unreported cell remains"), operational_witnesses=N008_WITNESSES,
    experiment_id="SFT-EXP-CHEM-KINETIC-ISOTOPE-FRACTIONATION-008", expected_observation_label="complete-kinetic-isotope-fractionation-vector", target_rows=N008_TARGETS, observation_registry_path=ANALYSIS_PATH,
    falsification_condition="The claim halts if the survivor is nonunique; any reaction path, resource point, product, rate, factor, steady state, correction, loss, estimate, limitation, unreported row, page or byte is omitted; or an external response selects the law.")

SPECS = (RADIOCHEMICAL_EQUILIBRIUM_SPEC, ISOTOPE_EXCHANGE_SPEC, EQUILIBRIUM_FRACTIONATION_SPEC, KINETIC_FRACTIONATION_SPEC)
for spec in SPECS: spec.validate()
COMPLETENESS_CERTIFICATES = {spec.claim_id: sha256_identity((spec.claim_id, tuple(row.target_id for row in spec.target_rows), 266, 1, 410095, spec.exact_result)) for spec in SPECS}

__all__ = ("ANALYSIS_HASH", "ANALYSIS_PATH", "AUTHORITIES", "COMPLETENESS_CERTIFICATES", "EQUILIBRIUM_FRACTIONATION_SPEC", "INVENTORY_PATH", "ISOTOPE_EXCHANGE_SPEC", "KINETIC_FRACTIONATION_SPEC", "RADIOCHEMICAL_EQUILIBRIUM_SPEC", "SPECS")
