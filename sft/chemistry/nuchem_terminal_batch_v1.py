"""Shared frozen registration for four separate NUCHEM-009–012 claims."""
from pathlib import Path

from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.chemistry.radiotracer_custody_law_v1 import DEPENDENCIES as N009_DEPS, DIMENSIONS as N009_DIMS, EXACT_RESULT as N009_RESULT, OPERATIONAL_WITNESSES as N009_WITNESSES
from sft.chemistry.radiochemical_separation_law_v1 import DEPENDENCIES as N010_DEPS, DIMENSIONS as N010_DIMS, EXACT_RESULT as N010_RESULT, OPERATIONAL_WITNESSES as N010_WITNESSES
from sft.chemistry.fission_product_distribution_law_v1 import DEPENDENCIES as N011_DEPS, DIMENSIONS as N011_DIMS, EXACT_RESULT as N011_RESULT, OPERATIONAL_WITNESSES as N011_WITNESSES
from sft.chemistry.radiolysis_network_law_v1 import DEPENDENCIES as N012_DEPS, DIMENSIONS as N012_DIMS, EXACT_RESULT as N012_RESULT, OPERATIONAL_WITNESSES as N012_WITNESSES
from sft.engine.canonical import sha256_identity
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parents[2]
ANALYSIS_PATH = "experiments/external_sources/chemistry/snapshots/nuchem-009-012-radiochemistry-v1/complete-postseal-analysis-v1.json"
INVENTORY_PATH = "experiments/external_sources/chemistry/snapshots/nuchem-009-012-radiochemistry-v1/source-inventory-v1.json"
ANALYSIS_HASH = "sha256:6c993195755f1ddf3c63e1f2404fc0d9a8762378c767c834d69b23b1430dae8c"
AUTHORITIES = (
    ("audits/CHEMISTRY_NUCHEM_001_012_FAMILY_BOUNDARY_2026-07-28.json", "sha256:77cefa7bb8a338c3b0e2de615ee7335c7c18c680423c58ecf336a5420bc4109f"),
    ("experiments/external_sources/chemistry/nuchem_009_012_family_source_identity_registry_v1.json", "sha256:ff9ae4d8616b9e5889028876f217e5d0c356d30fa146dd2b5ae90cb2bab06628"),
    ("sft/chemistry/radiotracer_custody_law_v1.py", "sha256:322bf04ce164fa418956198e076e3e18bd0146c4d924515e7fe738d09388df0e"),
    ("sft/chemistry/radiochemical_separation_law_v1.py", "sha256:a5cee923a57144eab81205f6d00eb46457f4f9668eee05566924486ba7951fc3"),
    ("sft/chemistry/fission_product_distribution_law_v1.py", "sha256:3ac7032706528d449b6d21e172febbb794a16eabe51b30428d6dac469e7f8eb6"),
    ("sft/chemistry/radiolysis_network_law_v1.py", "sha256:99962608fc2d6ddfb52dac69cf9a8cbbedc7f1e50749ce64e872745326177afb"),
    ("experiments/external_sources/chemistry/nuchem_009_target_identities_v1.json", "sha256:8133f5aabc7ec7cfbb5fc9fa38e6776153e5bc2e8f514fd4d1a6d8e1870c5a03"),
    ("experiments/external_sources/chemistry/nuchem_010_target_identities_v1.json", "sha256:77c00ab3050b60c58320a03c7823168d250bea4bdaee744b437c32fe300ad851"),
    ("experiments/external_sources/chemistry/nuchem_011_target_identities_v1.json", "sha256:9e20706647d7cc961875900fd5ec265cc891115a988bee6128b7ab6dd6c7bcca"),
    ("experiments/external_sources/chemistry/nuchem_012_target_identities_v1.json", "sha256:1603b88b918aac72522ae865c78ad10fdcd9b91146d57b9bee5a21ce257190b1"),
    ("experiments/sealed_predictions/chemistry_nuchem_009_pre_source_v1.json", "sha256:73cf904a4d34bbb7dfd0ffe7b52ed3e15c04cc32dac68d631f7c9ab4d3eade29"),
    ("experiments/sealed_predictions/chemistry_nuchem_010_pre_source_v1.json", "sha256:7b4467b104dc19d96d2ce5e56e7ce84ad4dfeec22b7d2f9cd19a18f8681e30cc"),
    ("experiments/sealed_predictions/chemistry_nuchem_011_pre_source_v1.json", "sha256:81482cf2d5aeb17080fdc5f69780838b7ac3910748ac27cf9bf21d0ae96ea204"),
    ("experiments/sealed_predictions/chemistry_nuchem_012_pre_source_v1.json", "sha256:b180a00808ac40571ea6f07b4d7f0a9d6e6d873ded4218431d5ac024fa0454c1"),
    (INVENTORY_PATH, "sha256:6e420b9e739c6899345641ea0091efad147d508f65fec5e956f82c8ec764b071"),
    (ANALYSIS_PATH, ANALYSIS_HASH),
    ("tools/seal_chemistry_nuchem_009_012_predictions_v1.py", "sha256:4cc3b4167b8eee8132f7ab8627d7d064227cf79698e2ed369d441a908200b6d8"),
    ("tools/capture_chemistry_nuchem_009_012_sources_v1.py", "sha256:6d08b87577ca4cc641080c4aa16d083547f0713a779245bd42e162fd6acc7a09"),
    ("tools/build_chemistry_nuchem_009_012_external_v1.py", "sha256:40edf4850c465e100c039cafbc107db66372ba776cca098a6c01405f86d397ec"),
)
for path, expected in AUTHORITIES:
    if hash_file(ROOT / path) != expected: raise ValueError(f"NUCHEM-009–012 authority changed: {path}")


def targets(prefix: str, rows: tuple[str, ...], source: str) -> tuple[ChemistryTargetReference, ...]:
    return tuple(ChemistryTargetReference(f"SFT-CHEM-NUCHEM-{prefix}-{name}", source if name != "COMPLETE-SOURCE" else "NUCHEM-009-012-SOURCE-INVENTORY", name.casefold().replace("-", " "), ANALYSIS_PATH, ANALYSIS_HASH) for name in rows)


N009_TARGETS = targets("009", ("TRACER-CHEMISTRY", "OBSERVATION-SUPPORT", "COUNTS", "RECOVERY", "LOCALIZATION", "INFERENCE-BOUNDARY", "ADVERSE-LIMITS", "COMPLETE-SOURCE"), "IAEA-TCS-31-RADIOTRACER-RTD-2008")
N010_TARGETS = targets("010", ("SPECIES", "STREAMS", "BALANCE", "RECOVERY", "DECONTAMINATION", "STAGES", "ADVERSE-UNCERTAINTY", "COMPLETE-SOURCE"), "DOE-OSTI-1580278-HFSLM-ISOTOPE-HARVESTING")
N011_TARGETS = targets("011", ("PHYSICS-HANDOFF", "CHEMICAL-IDENTITY", "PHASE-LOCATION", "DISTRIBUTION", "REDISTRIBUTION", "TIME-SAMPLE", "ADVERSE-DISCREPANCY", "COMPLETE-SOURCE"), "DOE-ORNL-4865-FISSION-PRODUCT-BEHAVIOR-MSRE")
N012_TARGETS = targets("012", ("RESOURCE-HANDOFF", "SPECIES", "NETWORK", "YIELDS", "CONDITIONS", "PARTITION-CLOSURE", "ADVERSE-UNCERTAINTY", "COMPLETE-SOURCE"), "NBS-NSRDS-45-RADIATION-CHEMISTRY-NITROUS-OXIDE")


RADIOTRACER_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-RADIOTRACER-CUSTODY-INFERENCE-009", title="Fold radiotracer custody and inference law",
    statement="A radiotracer retains nuclide and chemical-carrier identity over complete positive ordered observation support; recovery is exact observed per administered custody, unobserved custody is positive or structural absence, and inference cannot exceed observations.",
    dependencies=N009_DEPS, generation_rule="Generate the literal product of eight registered radiotracer decisions.", grammar_boundary="Eight dimensions exhaust identity, support, locations, events, recovery, loss, inference and extension.", dimensions=N009_DIMS, exact_result=N009_RESULT,
    induction_base="One administered tracer and one observation supply the first custody row.", induction_step="Every successor retains identity, all locations and all earlier observations without renormalization.",
    exclusions=("no numerical zero negative irrational imaginary continuum fitted free random or imported native parameter", "no measured recovery localization curve or fitted RTD model selects the survivor", "models and recommendations remain distinct from observations"), operational_witnesses=N009_WITNESSES,
    experiment_id="SFT-EXP-CHEM-RADIOTRACER-CUSTODY-INFERENCE-009", expected_observation_label="complete-radiotracer-custody-inference-vector", target_rows=N009_TARGETS, observation_registry_path=ANALYSIS_PATH,
    falsification_condition="The claim halts if the survivor is nonunique; any tracer, chemistry, detector, location, count, recovery, loss, correction, inference, adverse row, page or byte is omitted; or an external RTD outcome selects the law.")

SEPARATION_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-RADIOCHEMICAL-SEPARATION-DECONTAMINATION-010", title="Fold radiochemical separation and decontamination law",
    statement="Radiochemical separation retains target and contaminant identities across complete feed/product/waste streams, conserves each species exactly, forces recovery and decontamination ratios by counts, and composes only balanced stages.",
    dependencies=N010_DEPS, generation_rule="Generate the literal product of eight registered separation decisions.", grammar_boundary="Eight dimensions exhaust identity, streams, inventory, balance, recovery, decontamination, absence and extension.", dimensions=N010_DIMS, exact_result=N010_RESULT,
    induction_base="One complete feed/product/waste ledger supplies the first exact separation.", induction_step="Each successor stage consumes exactly the retained output and preserves every species balance.",
    exclusions=("no numerical zero negative irrational imaginary continuum fitted free random or imported native parameter", "no measured recovery extraction factor or selected successful run chooses the survivor", "the adverse one-percent run and every limit remain"), operational_witnesses=N010_WITNESSES,
    experiment_id="SFT-EXP-CHEM-RADIOCHEMICAL-SEPARATION-DECONTAMINATION-010", expected_observation_label="complete-radiochemical-separation-decontamination-vector", target_rows=N010_TARGETS, observation_registry_path=ANALYSIS_PATH,
    falsification_condition="The claim halts if the survivor is nonunique; any species, stream, balance, recovery, decontamination, stage, detection limit, uncertainty, adverse result, page or byte is omitted; or an external separation value selects the law.")

FISSION_PRODUCT_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-FISSION-PRODUCT-CHEMICAL-DISTRIBUTION-011", title="Fold fission-product chemical-distribution law",
    statement="Physics supplies fission-product identities; Chemistry retains every nuclide, species, phase and location with positive events, partitions the complete support exactly and permits only explicit identity-conserving chemical redistribution.",
    dependencies=N011_DEPS, generation_rule="Generate the literal product of eight registered fission-product decisions.", grammar_boundary="Eight dimensions exhaust handoff, identity, support, events, partition, chemistry, boundary and extension.", dimensions=N011_DIMS, exact_result=N011_RESULT,
    induction_base="One physics-supplied product with one complete chemical row supplies the first partition.", induction_step="Every successor retains all products and samples; a nuclide change requires a new physics handoff.",
    exclusions=("no numerical zero negative irrational imaginary continuum fitted free random or imported native parameter", "Chemistry cannot select fission-product existence or use an inventory model to choose the survivor", "all missing balances and conjectures remain unresolved evidence"), operational_witnesses=N011_WITNESSES,
    experiment_id="SFT-EXP-CHEM-FISSION-PRODUCT-CHEMICAL-DISTRIBUTION-011", expected_observation_label="complete-fission-product-chemical-distribution-vector", target_rows=N011_TARGETS, observation_registry_path=ANALYSIS_PATH,
    falsification_condition="The claim halts if the survivor is nonunique; any supplied product, species, phase, location, sample, distribution, transfer, inventory basis, uncontrolled condition, discrepancy, page or byte is omitted; or an external chemical grouping selects the law.")

RADIOLYSIS_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-RADIATION-CHEMISTRY-REACTION-NETWORK-012", title="Fold radiation-chemistry reaction-network law",
    statement="Physics supplies positive deposited resource; Chemistry retains complete medium/reactant/product/channel identity, counted product events, exact product-per-resource yields, complete channel partition and explicit reaction or structural termination.",
    dependencies=N012_DEPS, generation_rule="Generate the literal product of eight registered radiolysis decisions.", grammar_boundary="Eight dimensions exhaust handoff, identity, network, events, yield, partition, closure and extension.", dimensions=N012_DIMS, exact_result=N012_RESULT,
    induction_base="One deposited-resource handoff and one chemical product event supply the first yield row.", induction_step="Every successor retains all channels and recomputes yields and the complete partition without a kinetic fit.",
    exclusions=("no numerical zero negative irrational imaginary continuum fitted free random or imported native parameter", "no preferred G value reaction table or conventional radiolysis model selects the survivor", "all corrections tentative classifications missing results nonlinearities and unreliable rows remain"), operational_witnesses=N012_WITNESSES,
    experiment_id="SFT-EXP-CHEM-RADIATION-CHEMISTRY-REACTION-NETWORK-012", expected_observation_label="complete-radiation-chemistry-reaction-network-vector", target_rows=N012_TARGETS, observation_registry_path=ANALYSIS_PATH,
    falsification_condition="The claim halts if the survivor is nonunique; any resource, species, channel, event, yield, condition, reaction, correction, tentative or adverse row, page or byte is omitted; or an external G value selects the law.")

SPECS = (RADIOTRACER_SPEC, SEPARATION_SPEC, FISSION_PRODUCT_SPEC, RADIOLYSIS_SPEC)
for spec in SPECS: spec.validate()
COMPLETENESS_CERTIFICATES = {spec.claim_id: sha256_identity((spec.claim_id, tuple(row.target_id for row in spec.target_rows), 370, 837013, spec.exact_result)) for spec in SPECS}

__all__ = ("ANALYSIS_HASH", "ANALYSIS_PATH", "AUTHORITIES", "COMPLETENESS_CERTIFICATES", "FISSION_PRODUCT_SPEC", "INVENTORY_PATH", "RADIOLYSIS_SPEC", "RADIOTRACER_SPEC", "SEPARATION_SPEC", "SPECS")
