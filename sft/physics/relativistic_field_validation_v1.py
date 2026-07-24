"""Post-seal authoritative classification of relativistic/field successors."""

from __future__ import annotations

import json
from pathlib import Path

from sft.engine.source import hash_file
from sft.physics.generated_empirical_law import (
    BlindExternalMeasurementValidator,
    EmpiricalPhysicsSpec,
    ExternalTargetRow,
    empirical_dimensions,
)
from sft.physics.relativistic_field_laws_v1 import (
    COULOMB_GAUSS_ID,
    FINITE_LOOP_ID,
    FREE_PHASE_ID,
    FULL_DIRAC_ID,
    LORENTZ_TRANSFER_ID,
    MAXWELL_SPACE_ID,
    OPTICAL_OPERATIONS_ID,
    STATIONARY_ID,
)


DYNAMICS_VALIDATION_ID = "SFT-PHYS-VALIDATION-DYNAMICS-SPECTRA-003"
FIELD_VALIDATION_ID = "SFT-PHYS-VALIDATION-RELATIVISTIC-FIELDS-003"
OPTICS_VALIDATION_ID = "SFT-PHYS-VALIDATION-OPTICAL-OPERATIONS-003"
LOOP_VALIDATION_ID = "SFT-PHYS-VALIDATION-FINITE-LOOPS-003"

SOURCE_ID = "RELATIVISTIC-FIELD-AUTHORITATIVE-1971-2026"
SOURCE_PATH = "experiments/external_sources/physics/snapshots/relativistic-field-source-record.json"
SOURCE_HASH = "sha256:97a7631d956cc2eb8142e64603a1f51ece76944195274a28bbe91498edae0308"

DYNAMICS_LABEL = "discrete-spectra-and-energy-phase-correspondence-confirmed__specific-Fold-normalization-structural-not-a-measured-particle-value"
FIELD_LABEL = "Dirac-Lorentz-invariant-speed-and-Coulomb-inverse-square-correspondence-confirmed__specific-rational-closure-witnesses-structural"
OPTICS_LABEL = "interference-and-nonlinear-frequency-operations-confirmed__held-polarization-supported-by-registered-observables__half-One-normalization-structural"
LOOP_LABEL = "finite-renormalized-radiative-calculations-confirmed__floored-loop-law-is-a-formal-finite-support-boundary-not-a-direct-measurement-of-continuum-nonexistence"

COMPONENTS = {
    "nist-asd-version-history.html": "sha256:a327a34eb1b85ef3f003e8c8f0dbcb0c3fc49f039ee4046546a924fc42118454",
    "nist-codata-2022-allascii.txt": "sha256:77fb90e66c40db3e6eb16630bc9c88e4c7c8beddbe5e71be406f2f26e3f67e67",
    "aps-prl-26-721-source-record.json": "sha256:03840a7b8b64574c764c40eb91ba6e0ee2c413548ff0d317ca5c8334f72308bc",
    "pdg-2025-electroweak-model.pdf": "sha256:8642888a3408d8c57fc673b379325b07f02948135491f64a2e42320e8929320a",
}


def authoritative_record(root: Path) -> dict[str, object]:
    path = root / SOURCE_PATH
    if hash_file(path) != SOURCE_HASH:
        raise ValueError("relativistic-field source record identity changed")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("record_id") != SOURCE_ID or payload.get("formal_seal_boundary", {}).get("sealed_claim_count") != 12:
        raise ValueError("relativistic-field source record boundary changed")
    sources = payload.get("sources")
    if not isinstance(sources, list) or len(sources) != 7:
        raise ValueError("complete relativistic-field source vector requires seven sources")
    for item in sources:
        snapshot = item.get("snapshot")
        if snapshot in COMPONENTS and hash_file(path.parent / snapshot) != COMPONENTS[snapshot]:
            raise ValueError("relativistic-field component snapshot identity changed")
    controls = payload.get("unfavorable_and_scope_controls")
    if not isinstance(controls, list) or len(controls) != 5:
        raise ValueError("complete unfavorable-control vector changed")
    return payload


def classification(root: Path, key: str) -> str:
    record = authoritative_record(root)
    result = record["complete_classification"].get(key)
    if not isinstance(result, str):
        raise ValueError("authoritative classification row is missing")
    return result


_ROOT = Path(__file__).resolve().parents[2]
_dynamics = classification(_ROOT, "dynamics_and_spectra")
_field = classification(_ROOT, "relativistic_and_electromagnetic_fields")
_optics = classification(_ROOT, "optical_operations")
_loops = classification(_ROOT, "finite_loops")


def deps(*formal_ids: str) -> tuple[str, ...]:
    return formal_ids + (
        "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
        "SFT-PHYS-MEAS-TARGET-CUSTODY-001",
        "SFT-PHYS-MEAS-UNCERTAINTY-001",
        "SFT-MATH-EXACT-ARITHMETIC-001",
    )


def target(suffix: str, label: str) -> tuple[ExternalTargetRow, ...]:
    return (ExternalTargetRow(f"RELATIVISTIC-FIELD-{suffix}", SOURCE_ID, "complete registered NIST/CODATA/PDG/APS vector including unfavorable controls", label),)


DYNAMICS_SPEC = EmpiricalPhysicsSpec(
    claim_id=DYNAMICS_VALIDATION_ID,
    title="Post-seal dynamics and spectra comparison",
    statement="The complete NIST ASD and CODATA rows confirm discrete physical energy levels, transitions, wavelengths and energy-frequency carriers. They do not identify the universal dimensionless Fold witness levels as measured atomic energies, and that limitation is retained.",
    dependencies=deps(FREE_PHASE_ID, STATIONARY_ID),
    generation_rule="Generate the complete eight-axis post-seal dynamics/spectra comparison product.",
    grammar_boundary="All registered NIST discrete-spectrum and CODATA energy-frequency rows together with the exact-normalization unfavorable control.",
    dimensions=empirical_dimensions("sealed-Fold-dynamics-versus-complete-NIST-spectrum-vector", "Every favorable phenomenon row and the structural-normalization limitation remain visible."),
    exact_result="Discrete spectra and energy-frequency phase correspondence are externally supported; the particular Fold fractions remain exact structural normalization witnesses, not universal measured atomic energies.",
    induction_base="The NIST discrete-level row is retained with its source identity.",
    induction_step="Transition, wavelength, energy-frequency and scope-control rows append without selecting or rescaling the sealed law.",
    exclusions=("no source access before formal seal", "no claim that NIST measured universal Fold fractions", "no omission of the normalization control"),
    operational_witnesses=(("complete-dynamics-vector", "The favorable and scope-limiting rows remain jointly classified.", _dynamics == DYNAMICS_LABEL),),
    experiment_id="SFT-EXP-PHYS-VALIDATION-DYNAMICS-SPECTRA-003",
    expected_observation_label=DYNAMICS_LABEL,
    target_rows=target("DYNAMICS", DYNAMICS_LABEL),
    source_snapshot_path=SOURCE_PATH,
    source_snapshot_hash=SOURCE_HASH,
    falsification_condition="Authoritative spectra cease to exhibit discrete levels/transitions or the structural Fold normalization is promoted to a direct measured value without a committed measurement.",
)

FIELD_SPEC = EmpiricalPhysicsSpec(
    claim_id=FIELD_VALIDATION_ID,
    title="Post-seal relativistic and electromagnetic field comparison",
    statement="The complete PDG, CODATA and APS record supports Dirac/Lorentz physical structure, one invariant vacuum speed, electric/magnetic observable families and the inverse-square Coulomb exponent. It does not measure the Fold 3/5, 4/5 or four-half closure witnesses as universal particle coordinates.",
    dependencies=deps(FULL_DIRAC_ID, COULOMB_GAUSS_ID, LORENTZ_TRANSFER_ID, MAXWELL_SPACE_ID),
    generation_rule="Generate the complete eight-axis post-seal relativistic/electromagnetic comparison product.",
    grammar_boundary="All registered PDG Dirac/Lorentz, CODATA speed/electromagnetic and APS inverse-square rows plus every rational-witness scope control.",
    dimensions=empirical_dimensions("sealed-relativistic-field-laws-versus-complete-authority-vector", "The complete favorable physical classes and non-measured rational-normalization rows are retained."),
    exact_result="Dirac/Lorentz structure, invariant vacuum speed, electric/magnetic observables and inverse-square Coulomb behavior are externally supported; the exact rational Fold closures remain structural witnesses.",
    induction_base="The APS exponent record and CODATA invariant-speed record retain their exact identities.",
    induction_step="PDG Dirac/Lorentz and electromagnetic rows append while every non-measured Fold normalization remains explicit.",
    exclusions=("no conventional equation selecting the formal law", "no promotion of structural rational witnesses to measured particle values", "no omitted APS uncertainty or CODATA definition boundary"),
    operational_witnesses=(("complete-field-vector", "All confirmed classes and exact scope controls remain present.", _field == FIELD_LABEL),),
    experiment_id="SFT-EXP-PHYS-VALIDATION-RELATIVISTIC-FIELDS-003",
    expected_observation_label=FIELD_LABEL,
    target_rows=target("FIELDS", FIELD_LABEL),
    source_snapshot_path=SOURCE_PATH,
    source_snapshot_hash=SOURCE_HASH,
    falsification_condition="A verified non-invariant vacuum propagation speed, non-inverse-square Coulomb exponent outside the registered bound, or absence of Dirac/Lorentz and electric/magnetic physical classes contradicts the correspondence; a changed source or omitted limitation invalidates the validation receipt.",
)

OPTICS_SPEC = EmpiricalPhysicsSpec(
    claim_id=OPTICS_VALIDATION_ID,
    title="Post-seal optical-operation comparison",
    statement="NIST experimental records support photon interference, polarization observables and nonlinear sum, difference, second-, third- and four-wave mixing classes. The exact half-One support normalization remains a sealed Fold relation rather than an imported susceptibility or measured universal amplitude.",
    dependencies=deps(OPTICAL_OPERATIONS_ID, MAXWELL_SPACE_ID),
    generation_rule="Generate the complete eight-axis post-seal optical-operation comparison product.",
    grammar_boundary="Every registered NIST interference, polarization and nonlinear-mixing row together with the normalization and material-response controls.",
    dimensions=empirical_dimensions("sealed-optical-operations-versus-complete-NIST-vector", "All operation classes and non-equated coefficient boundaries remain visible."),
    exact_result="Interference, transverse polarization observables and nonlinear frequency mixing are externally supported; the Fold half-One is not asserted to equal every physical amplitude or susceptibility coefficient.",
    induction_base="The NIST photon-interference observation is retained.",
    induction_step="Polarization and each nonlinear frequency-operation row append without fitting a coefficient or deleting material conditions.",
    exclusions=("no imported optical amplitude", "no fitted nonlinear susceptibility", "no claim that every material realizes every operation at the same strength"),
    operational_witnesses=(("complete-optics-vector", "Interference, mixing and the coefficient boundary remain jointly classified.", _optics == OPTICS_LABEL),),
    experiment_id="SFT-EXP-PHYS-VALIDATION-OPTICAL-OPERATIONS-003",
    expected_observation_label=OPTICS_LABEL,
    target_rows=target("OPTICS", OPTICS_LABEL),
    source_snapshot_path=SOURCE_PATH,
    source_snapshot_hash=SOURCE_HASH,
    falsification_condition="Controlled optical experiments cease to exhibit interference or conservation-governed nonlinear mixing, or the validation silently equates a structural Fold share with an unmeasured universal amplitude.",
)

LOOP_SPEC = EmpiricalPhysicsSpec(
    claim_id=LOOP_VALIDATION_ID,
    title="Post-seal finite-loop and renormalization-boundary comparison",
    statement="PDG retains finite renormalized radiative calculations and schemes, providing correspondence for finite observable loop receipts. These calculations do not directly measure whether the substrate is fundamentally finite, so the V3 law remains a finite generated-support theorem rather than a claimed empirical disproof of every continuum representation.",
    dependencies=deps(FINITE_LOOP_ID),
    generation_rule="Generate the complete eight-axis post-seal finite-loop comparison product.",
    grammar_boundary="The registered PDG renormalized-calculation row and the explicit distinction between finite generated-support proof and unmeasured substrate ontology.",
    dimensions=empirical_dimensions("sealed-finite-loop-law-versus-PDG-radiative-calculation", "Finite calculational correspondence and the non-measurement of substrate continuity are retained together."),
    exact_result="Finite renormalized radiative observable calculations correspond to exact finite loop receipts; the absence of completed continuum support is a formal Fold boundary, not a directly measured ontology claim.",
    induction_base="One PDG renormalized radiative calculation class is retained.",
    induction_step="Each further finite observable calculation can append without turning calculational success into a measurement of continuum or finite ontology.",
    exclusions=("no fitted counterterm in the Fold derivation", "no claim that PDG directly measured substrate finiteness", "no completed infinite support admitted"),
    operational_witnesses=(("complete-loop-vector", "Correspondence and ontology boundary remain jointly classified.", _loops == LOOP_LABEL),),
    experiment_id="SFT-EXP-PHYS-VALIDATION-FINITE-LOOPS-003",
    expected_observation_label=LOOP_LABEL,
    target_rows=target("LOOPS", LOOP_LABEL),
    source_snapshot_path=SOURCE_PATH,
    source_snapshot_hash=SOURCE_HASH,
    falsification_condition="A generated finite exact loop census diverges, an unregistered subtraction is required inside the Fold proof, or the validation misstates a conventional calculation as direct measurement of substrate ontology.",
)


VALIDATION_SPECS = (DYNAMICS_SPEC, FIELD_SPEC, OPTICS_SPEC, LOOP_SPEC)


class CompleteRecordValidator:
    def __init__(self, root: Path, spec: EmpiricalPhysicsSpec, key: str, expected: str):
        self.root = root.resolve()
        self.spec = spec
        self.key = key
        self.expected = expected

    def validate(self, sealed):
        if classification(self.root, self.key) != self.expected:
            raise ValueError("authoritative relativistic-field classification changed")
        return BlindExternalMeasurementValidator(self.root, self.spec).validate(sealed)


VALIDATOR_BY_ID = {
    DYNAMICS_VALIDATION_ID: lambda root: CompleteRecordValidator(root, DYNAMICS_SPEC, "dynamics_and_spectra", DYNAMICS_LABEL),
    FIELD_VALIDATION_ID: lambda root: CompleteRecordValidator(root, FIELD_SPEC, "relativistic_and_electromagnetic_fields", FIELD_LABEL),
    OPTICS_VALIDATION_ID: lambda root: CompleteRecordValidator(root, OPTICS_SPEC, "optical_operations", OPTICS_LABEL),
    LOOP_VALIDATION_ID: lambda root: CompleteRecordValidator(root, LOOP_SPEC, "finite_loops", LOOP_LABEL),
}

for _spec in VALIDATION_SPECS:
    _spec.validate()


__all__ = ("VALIDATION_SPECS", "VALIDATOR_BY_ID", "authoritative_record", "classification")
