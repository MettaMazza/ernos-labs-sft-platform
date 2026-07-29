"""Shared frozen registration for four separate ECHEM-009–012 claims."""
from pathlib import Path

from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.chemistry.electrode_reaction_rate_law_v1 import DEPENDENCIES as E009_DEPS, DIMENSIONS as E009_DIMS, EXACT_RESULT as E009_RESULT, OPERATIONAL_WITNESSES as E009_WITNESSES
from sft.chemistry.overpotential_polarization_law_v1 import DEPENDENCIES as E010_DEPS, DIMENSIONS as E010_DIMS, EXACT_RESULT as E010_RESULT, OPERATIONAL_WITNESSES as E010_WITNESSES
from sft.chemistry.double_layer_organization_law_v1 import DEPENDENCIES as E011_DEPS, DIMENSIONS as E011_DIMS, EXACT_RESULT as E011_RESULT, OPERATIONAL_WITNESSES as E011_WITNESSES
from sft.chemistry.corrosion_network_law_v1 import DEPENDENCIES as E012_DEPS, DIMENSIONS as E012_DIMS, EXACT_RESULT as E012_RESULT, OPERATIONAL_WITNESSES as E012_WITNESSES
from sft.engine.canonical import sha256_identity
from sft.engine.source import hash_file

ROOT = Path(__file__).resolve().parents[2]
ANALYSIS_PATH = "experiments/external_sources/chemistry/snapshots/echem-009-012-polarization-v1/complete-postseal-analysis-v1.json"
INVENTORY_PATH = "experiments/external_sources/chemistry/snapshots/echem-009-012-polarization-v1/source-inventory-v1.json"
ANALYSIS_HASH = "sha256:9ef756e0ad20505cd5af19f924480b3b39d03826c4737f2850890416fbffdf4c"

AUTHORITIES = (
    ("audits/CHEMISTRY_ECHEM_001_013_FAMILY_BOUNDARY_2026-07-28.json", "sha256:66f3152d791eafc5f677467ef7affd72f6559150be4adf586873a79c6ad473df"),
    ("experiments/external_sources/chemistry/echem_001_013_family_source_identity_registry_v1.json", "sha256:64ec429f537c2b0274cba689a32a65a6f36aebb3ecdc96678efcc49272c63106"),
    ("sft/chemistry/electrode_reaction_rate_law_v1.py", "sha256:7fe03dd7c7b34cb3ca319c363fb41686984e8acfbe51eddf7be4d45d2b7d280b"),
    ("sft/chemistry/overpotential_polarization_law_v1.py", "sha256:8804cd260c74a7b6567e524ac515f340570b0a2f61613ace52c17d375781d4a2"),
    ("sft/chemistry/double_layer_organization_law_v1.py", "sha256:b6f52028558d72b9e995fddd345cf9474c6ae730e7d397c1f268e6562bd61445"),
    ("sft/chemistry/corrosion_network_law_v1.py", "sha256:9584315bafe74ebc5682652994f5a3e289d7967b18812b899e7de2c71dd74ece"),
    ("experiments/external_sources/chemistry/echem_009_target_identities_v1.json", "sha256:007115bfb999c850abb2abd4834f17d5563395bd86c9042f057670a7f3bcc757"),
    ("experiments/external_sources/chemistry/echem_010_target_identities_v1.json", "sha256:5993024e8032cb81604e27e28a5199c1759a500715ddf3da36807db2217e1347"),
    ("experiments/external_sources/chemistry/echem_011_target_identities_v1.json", "sha256:cf2922cbf77d0b70da7813cc2f51d6dbff82550d199dc210bab9de2523e3a863"),
    ("experiments/external_sources/chemistry/echem_012_target_identities_v1.json", "sha256:3227489dc905b226ce8c4e0be9263308c5ad72bc80e4811e242ef97a2553845d"),
    ("experiments/sealed_predictions/chemistry_echem_009_pre_source_v1.json", "sha256:d5d4bfd5988f0fd8d6b81edcc0d81cfa74d77c98f82590b24d4eb11fd6f71b60"),
    ("experiments/sealed_predictions/chemistry_echem_010_pre_source_v1.json", "sha256:f24bcb12e48aac155380ff426a6b64e32b4a4274ca92d78770f4303e2287b2db"),
    ("experiments/sealed_predictions/chemistry_echem_011_pre_source_v1.json", "sha256:dd809a7f1cadc7f14e83b4dfdf54cc15ef7d66792783121acacd98a9896801f5"),
    ("experiments/sealed_predictions/chemistry_echem_012_pre_source_v1.json", "sha256:4a483b5d23af4f193dc1aeaf9442ed6dde16f8c116103e134682e2837da30f99"),
    (INVENTORY_PATH, "sha256:6c26b1511e253b9a909306dad4c2a516c976c4a7f080aff7427574d0466c09a6"),
    (ANALYSIS_PATH, ANALYSIS_HASH),
    ("tools/seal_chemistry_echem_009_012_predictions_v1.py", "sha256:da775dfc907bc34062bd8f7312eefcf711092aa0645d6ebf51c22a798073675b"),
    ("tools/capture_chemistry_echem_009_012_sources_v1.py", "sha256:40297fb8fa45ed8b371f05f178f9754f481a9492fb7d2a206e6d0b4c15c25bc0"),
    ("tools/build_chemistry_echem_009_012_external_v1.py", "sha256:2982c2c9a142768c91664a09cd05646d35f39a2b1fa2878d0cdf5871d06e9b29"),
)
for path, expected in AUTHORITIES:
    if hash_file(ROOT / path) != expected:
        raise ValueError(f"ECHEM-009–012 authority changed: {path}")


def targets(prefix: str, rows: tuple[tuple[str, str], ...]) -> tuple[ChemistryTargetReference, ...]:
    return tuple(ChemistryTargetReference(f"SFT-CHEM-ECHEM-{prefix}-{name}", source, name.casefold().replace("-", " "), ANALYSIS_PATH, ANALYSIS_HASH) for name, source in rows)


E009_TARGETS = targets("009", (("REACTION-INTERFACE", "NBS-JRES-GALVANIC-COUPLES-1950"), ("CURRENT-POTENTIAL", "NBS-JRES-GALVANIC-COUPLES-1950"), ("ANODIC-CATHODIC", "NBS-JRES-GALVANIC-COUPLES-1950"), ("RATE-CORRESPONDENCE", "NBS-JRES-IRON-CORROSION-1957"), ("CONDITIONS", "NBS-JRES-IRON-CORROSION-1957"), ("RAW-VECTOR", "NBS-JRES-IRON-CORROSION-1957"), ("ADVERSE-MODELS", "ECHEM-009-012-SHARED-SOURCES"), ("COMPLETE-SOURCES", "ECHEM-009-012-SOURCE-INVENTORY")))
E010_TARGETS = targets("010", (("EQUILIBRIUM-REFERENCE", "NBS-JRES-GALVANIC-COUPLES-1950"), ("POLARIZATION-DIRECTION", "NBS-JRES-GALVANIC-COUPLES-1950"), ("POTENTIAL-DISTANCE", "NBS-JRES-IRON-CORROSION-1957"), ("CURRENT-RESPONSE", "NBS-JRES-IRON-CORROSION-1957"), ("CURVE-VECTOR", "NBS-JRES-IRON-CORROSION-1957"), ("REVERSAL-BREAKS", "NBS-JRES-GALVANIC-COUPLES-1950"), ("IR-DROP-UNCERTAINTY", "NBS-JRES-IRON-CORROSION-1957"), ("COMPLETE-SOURCES", "ECHEM-009-012-SOURCE-INVENTORY")))
E011_TARGETS = targets("011", (("INTERFACE", "NIST-GRAPHENE-DOUBLE-LAYER-2020"), ("COMPOSITIONS", "NIST-GRAPHENE-DOUBLE-LAYER-2020"), ("SPATIAL-SUPPORT", "NIST-GRAPHENE-DOUBLE-LAYER-2020"), ("APPLIED-POTENTIAL", "NIST-GRAPHENE-DOUBLE-LAYER-2020"), ("SURFACE-POTENTIAL", "NIST-GRAPHENE-DOUBLE-LAYER-2020"), ("POTENTIAL-DROP", "NIST-GRAPHENE-DOUBLE-LAYER-2020"), ("MODEL-PROVENANCE", "NIST-GRAPHENE-DOUBLE-LAYER-2020"), ("COMPLETE-SOURCE", "ECHEM-011-SOURCE-INVENTORY")))
E012_TARGETS = targets("012", (("MATERIAL-ENVIRONMENT", "NBS-JRES-IRON-CORROSION-1957"), ("ANODIC-CATHODIC-NETWORK", "NBS-JRES-IRON-CORROSION-1957"), ("CORROSION-POTENTIAL", "NBS-JRES-IRON-CORROSION-1957"), ("CORROSION-CURRENT", "NBS-JRES-IRON-CORROSION-1957"), ("MASS-LOSS-RATE", "NBS-JRES-IRON-CORROSION-1957"), ("POLARIZATION-CONTROL", "NBS-JRES-GALVANIC-COUPLES-1950"), ("ADVERSE-UNCERTAINTY", "NBS-JRES-IRON-CORROSION-1957"), ("COMPLETE-SOURCES", "ECHEM-009-012-SOURCE-INVENTORY")))


RATE_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-ELECTRODE-REACTION-RATE-009", title="Fold electrode reaction-rate law",
    statement="Electrode reaction rate is an exact positive count of forward and reverse reaction events per positive counted resource, retaining reaction, interface, condition, potential orientation and structural balance.",
    dependencies=E009_DEPS, generation_rule="Generate the literal product of eight registered electrode-rate decisions.", grammar_boundary="Eight dimensions exhaust reaction custody, events, resource, potential, net, balance, record and extension.", dimensions=E009_DIMS, exact_result=E009_RESULT,
    induction_base="One counted electrode event over one counted resource interval supplies the first exact rate.", induction_step="Appending one event recomputes the exact ledger rate without an exchange-current fit.",
    exclusions=("no numerical zero negative irrational imaginary continuum fitted free random or imported native parameter", "no external current potential curve or rate selects the survivor", "all external signs fits discontinuities and IR drops remain downstream provenance"), operational_witnesses=E009_WITNESSES,
    experiment_id="SFT-EXP-CHEM-ELECTRODE-REACTION-RATE-009", expected_observation_label="complete-electrode-reaction-rate-vector", target_rows=E009_TARGETS, observation_registry_path=ANALYSIS_PATH,
    falsification_condition="The claim halts if the survivor is nonunique; any reaction, interface, event direction, resource, current, potential, condition, adverse record or source page is omitted; or an external curve selects the law.")

POLARIZATION_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-OVERPOTENTIAL-POLARIZATION-010", title="Fold overpotential and polarization law",
    statement="Polarization is an ordered finite current-potential response about one held equilibrium reference, with anodic, cathodic and equilibrium sides separated from positive exact magnitudes.",
    dependencies=E010_DEPS, generation_rule="Generate the literal product of eight registered polarization decisions.", grammar_boundary="Eight dimensions exhaust reference, orientation, magnitude, current, equilibrium, curve, condition and record.", dimensions=E010_DIMS, exact_result=E010_RESULT,
    induction_base="One equilibrium point supplies the structural reference without a numerical-zero magnitude.", induction_step="Appending the next scan point retains its ordinal, side, potential distance, current and common condition.",
    exclusions=("no numerical zero negative irrational imaginary continuum fitted free random or imported native parameter", "no external polarization value or fitted line selects the survivor", "all scan reversals breaks hysteresis IR drops and uncertainties remain downstream provenance"), operational_witnesses=E010_WITNESSES,
    experiment_id="SFT-EXP-CHEM-OVERPOTENTIAL-POLARIZATION-010", expected_observation_label="complete-overpotential-polarization-vector", target_rows=E010_TARGETS, observation_registry_path=ANALYSIS_PATH,
    falsification_condition="The claim halts if the survivor is nonunique; any equilibrium, scan direction, point, reversal, break, IR drop, uncertainty or source page is omitted; or an external curve selects the law.")

DOUBLE_LAYER_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-DOUBLE-LAYER-INTERFACIAL-CHARGE-011", title="Fold double-layer interfacial-charge organization",
    statement="An electric double layer is a complete finite ordered interface support with held electrolyte, carrier identities and opposed sides, exact positive potential separation and counted carrier-per-potential organization.",
    dependencies=E011_DEPS, generation_rule="Generate the literal product of eight registered double-layer decisions.", grammar_boundary="Eight dimensions exhaust interface, support, carrier, orientation, potential, capacitance, coincidence and record.", dimensions=E011_DIMS, exact_result=E011_RESULT,
    induction_base="One interface layer with one held carrier supplies the first finite support.", induction_step="Appending one ranked layer retains every prior layer and recomputes counted carrier support per held separation.",
    exclusions=("no numerical zero negative irrational imaginary continuum fitted free random or imported native parameter", "no external potential capacitance or numerical model selects the survivor", "all fit parameters screening hysteresis and resolution limits remain downstream provenance"), operational_witnesses=E011_WITNESSES,
    experiment_id="SFT-EXP-CHEM-DOUBLE-LAYER-INTERFACIAL-CHARGE-011", expected_observation_label="complete-double-layer-interfacial-charge-vector", target_rows=E011_TARGETS, observation_registry_path=ANALYSIS_PATH,
    falsification_condition="The claim halts if the survivor is nonunique; any interface, composition, layer, carrier, potential, surface response, model provenance, limit or source page is omitted; or an external value selects the law.")

CORROSION_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-CORROSION-REACTION-NETWORK-012", title="Fold coupled corrosion reaction-network law",
    statement="Corrosion is a coupled anodic-cathodic network under one retained material and environment, with exact counted path rates, synchronized support, held excess orientation and structural balance.",
    dependencies=E012_DEPS, generation_rule="Generate the literal product of eight registered corrosion-network decisions.", grammar_boundary="Eight dimensions exhaust material, network, events, resource, coupling, orientation, balance and record.", dimensions=E012_DIMS, exact_result=E012_RESULT,
    induction_base="One anodic and one cathodic event on common material/environment support form the first coupled network.", induction_step="Appending path events recomputes exact synchronized and excess rates while retaining both paths.",
    exclusions=("no numerical zero negative irrational imaginary continuum fitted free random or imported native parameter", "no external corrosion current mass loss or fitted ratio selects the survivor", "all discrepancies estimates controls and IR drops remain downstream provenance"), operational_witnesses=E012_WITNESSES,
    experiment_id="SFT-EXP-CHEM-CORROSION-REACTION-NETWORK-012", expected_observation_label="complete-corrosion-reaction-network-vector", target_rows=E012_TARGETS, observation_registry_path=ANALYSIS_PATH,
    falsification_condition="The claim halts if the survivor is nonunique; any material, environment, reaction path, potential, current, rate, mass loss, discrepancy, control or source page is omitted; or an external result selects the law.")

SPECS = (RATE_SPEC, POLARIZATION_SPEC, DOUBLE_LAYER_SPEC, CORROSION_SPEC)
for spec in SPECS:
    spec.validate()
COMPLETENESS_CERTIFICATES = {spec.claim_id: sha256_identity((spec.claim_id, tuple(row.target_id for row in spec.target_rows), 73, 156376, spec.exact_result)) for spec in SPECS}

__all__ = ("ANALYSIS_HASH", "ANALYSIS_PATH", "AUTHORITIES", "COMPLETENESS_CERTIFICATES", "CORROSION_SPEC", "DOUBLE_LAYER_SPEC", "INVENTORY_PATH", "POLARIZATION_SPEC", "RATE_SPEC", "SPECS")
