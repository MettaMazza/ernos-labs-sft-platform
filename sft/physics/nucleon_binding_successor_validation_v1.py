"""Post-seal PDG/NIST comparison for terminal nucleon binding."""

from __future__ import annotations

from fractions import Fraction
import json
from pathlib import Path

from sft.engine.source import hash_file
from sft.physics.generated_empirical_law import (
    BlindExternalMeasurementValidator,
    EmpiricalPhysicsSpec,
    ExternalTargetRow,
    empirical_dimensions,
)
from sft.physics.nucleon_binding_successor_laws_v1 import (
    NUCLEON_BINDING_TERMINAL_ID,
    neutron_proton_order_certificate,
    nucleon_mass_ledger,
)
from sft.physics.prior_value_laws import positive_take


SOURCE_ID = "PDG-NIST-NUCLEON-BINDING-2022-2026"
SOURCE_PATH = "experiments/external_sources/physics/snapshots/nucleon-binding-successor-source-record.json"
SOURCE_HASH = "sha256:2f75c5124ce570fad3becd1ff5901f6062c6dea05b5a41a1892819006fa6290e"
PDG_QUARK_MASS_HASH = "sha256:d544d099aa15739ec83d87711bd4c5b1e0a1032d6f70aaa4847ec78601f7aeae"
NIST_CODATA_HASH = "sha256:77fb90e66c40db3e6eb16630bc9c88e4c7c8beddbe5e71be406f2f26e3f67e67"
MEASURED_LABEL = (
    "sealed-three-colour-uud-udd-singlet-correspondence-passes-PDG"
    "__structural-one-over-128-and-PDG-uud-current-share-both-below-one-percent"
    "__nonidentity-of-those-two-objects-retained__held-residuals-above-99-percent"
    "__down-up-and-neutron-proton-ordering-pass-complete-PDG-NIST-intervals"
)


def authoritative_record(root: Path) -> dict[str, object]:
    path = root / SOURCE_PATH
    if hash_file(path) != SOURCE_HASH:
        raise ValueError("nucleon-binding source record identity changed")
    payload = json.loads(path.read_text(encoding="utf-8"))
    custody = payload.get("custody", {})
    required = {
        "classification": "observational_derivation",
        "development_targets_already_known": True,
        "protocol_classification": "observational-data-informed_target-inaccessible_sealed-prediction",
        "empirical_prediction_protocol": True,
        "target_inaccessible_during_prediction_execution": True,
        "formal_relations_contain_measurement": False,
        "measurements_select_formal_survivors": False,
        "engine_prediction_sealed_before_target_release_within_run": True,
        "complete_reported_uncertainties_retained": True,
        "scheme_boundary_retained": True,
        "structural_fraction_not_conflated_with_current_quark_mass_ratio": True,
    }
    if any(custody.get(key) != value for key, value in required.items()):
        raise ValueError("nucleon-binding custody disclosure changed")
    sources = payload.get("sources", {})
    if set(sources) != {"pdg_quark_model", "pdg_light_quark_masses", "nist_nucleon_masses"}:
        raise ValueError("nucleon-binding source set changed")
    pdg = sources["pdg_light_quark_masses"]
    nist = sources["nist_nucleon_masses"]
    if pdg["snapshot_hash"] != PDG_QUARK_MASS_HASH or hash_file(root / pdg["snapshot_path"]) != PDG_QUARK_MASS_HASH:
        raise ValueError("PDG quark-mass snapshot changed")
    if nist["snapshot_hash"] != NIST_CODATA_HASH or hash_file(root / nist["snapshot_path"]) != NIST_CODATA_HASH:
        raise ValueError("NIST CODATA snapshot changed")
    return payload


def exact_interval(centre: str, uncertainty: str) -> tuple[Fraction, Fraction]:
    c, u = Fraction(centre), Fraction(uncertainty)
    lower = positive_take(c, u)
    if not isinstance(lower, Fraction):
        raise ValueError("external interval exhausted its positive centre")
    return lower, c + u


def external_intervals(root: Path) -> dict[str, tuple[Fraction, Fraction]]:
    sources = authoritative_record(root)["sources"]
    quarks = sources["pdg_light_quark_masses"]["reported_record"]
    nucleons = sources["nist_nucleon_masses"]["reported_record"]
    return {
        "up": exact_interval(quarks["up_mass_MeV"], quarks["up_total_uncertainty_MeV"]),
        "down": exact_interval(quarks["down_mass_MeV"], quarks["down_total_uncertainty_MeV"]),
        "proton": exact_interval(nucleons["proton_mass_energy_MeV"], nucleons["proton_standard_uncertainty_MeV"]),
        "neutron": exact_interval(nucleons["neutron_mass_energy_MeV"], nucleons["neutron_standard_uncertainty_MeV"]),
        "difference": exact_interval(nucleons["neutron_proton_difference_MeV"], nucleons["difference_standard_uncertainty_MeV"]),
    }


def uud_current_mass_fraction_interval(root: Path) -> tuple[Fraction, Fraction]:
    rows = external_intervals(root)
    up, down, proton = rows["up"], rows["down"], rows["proton"]
    return (binary_times(up[0]) + down[0]) / proton[1], (binary_times(up[1]) + down[1]) / proton[0]


def binary_times(value: Fraction) -> Fraction:
    return value + value


def nucleon_binding_classification(root: Path) -> str:
    sources = authoritative_record(root)["sources"]
    model = sources["pdg_quark_model"]["reported_record"]
    if (model["colour_count"], model["minimal_baryon_constituent_count"], model["baryon_class"]) != (3, 3, "qqq"):
        raise ValueError("PDG baryon composition correspondence changed")
    if model["physical_state_class"] != "colour singlet" or model["up_charge"] != "positive 2/3" or model["down_charge"] != "opposed 1/3":
        raise ValueError("PDG colour/charge correspondence changed")

    quark_record = sources["pdg_light_quark_masses"]["reported_record"]
    if (quark_record["scheme"], quark_record["scale_GeV"], quark_record["active_flavour_theory"]) != ("MSbar", "2", "NL=4"):
        raise ValueError("PDG quark scheme/scale boundary changed")
    rows = external_intervals(root)
    if rows["down"][0] <= rows["up"][1]:
        raise ValueError("complete PDG down/up intervals no longer order")

    current = uud_current_mass_fraction_interval(root)
    ledger = nucleon_mass_ledger()
    if current[1] >= Fraction(1, 100):
        raise ValueError("complete PDG uud current-mass fraction is not below one percent")
    measured_held_lower = positive_take(Fraction(1, 1), current[1])
    if not isinstance(measured_held_lower, Fraction) or measured_held_lower <= Fraction(99, 100):
        raise ValueError("complete measured residual is not above ninety-nine percent")
    if ledger["bare"] >= Fraction(1, 100) or ledger["held_cycle"] <= Fraction(99, 100):
        raise ValueError("sealed structural dominance class changed")
    if current[0] <= ledger["bare"] <= current[1]:
        raise ValueError("structural fraction was improperly conflated with PDG current-mass fraction")

    proton, neutron, direct = rows["proton"], rows["neutron"], rows["difference"]
    if neutron[0] <= proton[1]:
        raise ValueError("complete NIST neutron/proton intervals no longer order")
    propagated = positive_take(neutron[0], proton[1]), positive_take(neutron[1], proton[0])
    if not all(isinstance(value, Fraction) for value in propagated):
        raise ValueError("NIST propagated mass difference failed positivity")
    if propagated[0] > direct[0] or propagated[1] < direct[1]:
        raise ValueError("NIST direct mass difference left the propagated mass intervals")
    if neutron_proton_order_certificate()["net_neutron_surplus_lower"] <= 0:
        raise ValueError("sealed neutron/proton ordering certificate changed")
    return MEASURED_LABEL


NUCLEON_BINDING_EMPIRICAL_SPEC = EmpiricalPhysicsSpec(
    claim_id=NUCLEON_BINDING_TERMINAL_ID,
    title="Terminal nucleon binding and ordering post-seal PDG/NIST comparison",
    statement=(
        "Observation informed the explicit nucleon successor. The PDG three-colour qqq record, complete "
        "scheme-bound u/d mass intervals and NIST proton/neutron mass-energy intervals remain capability-closed "
        "until the exact structural ledger and ordering seal; all uncertainties and the nonconflation boundary are retained."
    ),
    dependencies=(
        NUCLEON_BINDING_TERMINAL_ID,
        "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
        "SFT-PHYS-MEAS-TARGET-CUSTODY-001",
        "SFT-PHYS-MEAS-UNCERTAINTY-001",
        "SFT-MATH-EXACT-ARITHMETIC-001",
    ),
    generation_rule="Generate the complete eight-axis post-seal composition, dominance, ordering, source, scheme, custody and row-retention product.",
    grammar_boundary="The complete registered PDG quark-model and light-mass records plus NIST proton, neutron and direct mass-difference intervals, including all standard uncertainties and scheme/status disclosures.",
    dimensions=empirical_dimensions(
        "sealed-nucleon-composition-ledger-and-ordering-versus-complete-PDG-NIST-vector",
        "Every composition, dominance, nonconflation, scheme, ordering and complete interval row remains visible.",
    ),
    exact_result=(
        "PDG independently corresponds to a three-colour qqq singlet; both sealed 1/128 and the complete PDG "
        "uud current-mass fraction are below 1/100 while remaining explicitly non-identical objects; both "
        "residuals exceed 99/100; complete PDG d/u and NIST neutron/proton intervals preserve the sealed ordering."
    ),
    induction_base="The first complete qqq record and one exact positive interval per light flavour and nucleon establish the source-bound comparison.",
    induction_step="Each source revision appends a new receipt and cannot rewrite the sealed ledger, scheme boundary, uncertainty endpoints, nonconflation disclosure or predecessor evidence.",
    exclusions=(
        "no target readable by the executable law",
        "no measured nucleon or quark mass selecting the survivor",
        "no equality claim between structural 1/128 and a scheme-dependent quark-mass ratio",
        "no floating-point interval decision",
        "no omitted uncertainty, scheme disclosure, source row or unfavorable control",
    ),
    operational_witnesses=((
        "target-free-ledger-and-order",
        "The exact structural dominance and neutron/proton ordering exist before source release.",
        nucleon_mass_ledger()["bare"] == Fraction(1, 128)
        and nucleon_mass_ledger()["held_cycle"] == Fraction(127, 128)
        and neutron_proton_order_certificate()["net_neutron_surplus_lower"] > Fraction(1, 1000),
    ),),
    experiment_id="SFT-EXP-PHYS-NUCLEON-BINDING-TERMINAL-005",
    expected_observation_label=MEASURED_LABEL,
    target_rows=(
        ExternalTargetRow("PDG-THREE-COLOUR-QQQ-SINGLET", SOURCE_ID, "PDG 2025 Quark Model complete colour-singlet and baryon composition rows", MEASURED_LABEL),
        ExternalTargetRow("PDG-LIGHT-QUARK-MASS-DOMINANCE", SOURCE_ID, "PDG 2025 MSbar 2 GeV u/d mass values with complete total uncertainties and scheme boundary", MEASURED_LABEL),
        ExternalTargetRow("NIST-NUCLEON-MASS-ORDERING", SOURCE_ID, "NIST CODATA 2022 proton, neutron and direct difference energy-equivalent rows", MEASURED_LABEL),
    ),
    source_snapshot_path=SOURCE_PATH,
    source_snapshot_hash=SOURCE_HASH,
    falsification_condition=(
        "The claim fails if qqq colour closure differs, either complete dominance inequality fails, structural "
        "and scheme-dependent quantities are conflated, d/u or neutron/proton intervals cease to order, the "
        "direct mass difference leaves propagated intervals, a source/uncertainty changes, or target access precedes sealing."
    ),
)


class NucleonBindingValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()

    def validate(self, sealed):
        validation = BlindExternalMeasurementValidator(self.root, NUCLEON_BINDING_EMPIRICAL_SPEC).validate(sealed)
        if nucleon_binding_classification(self.root) != MEASURED_LABEL or not validation.passed:
            raise ValueError("nucleon-binding authoritative classification changed")
        return validation


NUCLEON_BINDING_EMPIRICAL_SPEC.validate()


__all__ = (
    "MEASURED_LABEL",
    "NUCLEON_BINDING_EMPIRICAL_SPEC",
    "NucleonBindingValidator",
    "SOURCE_HASH",
    "SOURCE_ID",
    "SOURCE_PATH",
    "authoritative_record",
    "external_intervals",
    "nucleon_binding_classification",
    "uud_current_mass_fraction_interval",
)
