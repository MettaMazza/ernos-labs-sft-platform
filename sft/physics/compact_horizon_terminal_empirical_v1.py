"""Post-seal compact-object and horizon-thermodynamics comparison."""

from dataclasses import replace

from sft.engine import ProvenanceClass
from sft.physics.compact_horizon_terminal_law_v1 import theorem_certificate
from sft.physics.generated_empirical_law import (
    EmpiricalPhysicsSpec,
    ExternalTargetRow,
    GeneratedEmpiricalPhysicsProgram,
    empirical_dimensions,
)


CLAIM_ID = "SFT-PHYS-VALIDATION-COMPACT-HORIZON-THERMODYNAMICS-072"
EXPERIMENT_ID = "SFT-EXP-PHYS-VALIDATION-COMPACT-HORIZON-THERMODYNAMICS-072"
SOURCE_PATH = "experiments/external_sources/physics/snapshots/compact-horizon-postseal-source-record.json"
SOURCE_HASH = "sha256:670c9467f5638513c16345de4ce15da834ed46a358ed40371160d951e739921d"
SOURCE_FILES = (
    ("experiments/external_sources/physics/snapshots/nasa-gsfc-white-dwarf-chandrasekhar.html", "sha256:29d25e42773e2b6c5c5f292ef97b6abb28e430f4b6af6336720ee5e3d41aa2a5"),
    ("experiments/external_sources/physics/snapshots/arxiv-2104.00880-psr-j0740-mass.pdf", "sha256:66c7fbaacc06a5fa3513a7d963d2b300b05a0a52552e2358e9f257940f37b47a"),
    ("experiments/external_sources/physics/snapshots/ligo-p1800379-gw170817-remnant.pdf", "sha256:86d4efa4b4c5153799edf278bcd99b10753540337c876fbf505855b8bb949122"),
)
SOURCE_IDS = (
    "NASA-GSFC-WHITE-DWARF-CHANDRASEKHAR",
    "FONSECA-2021-PSR-J0740-MASS",
    "LIGO-VIRGO-2019-GW170817-REMNANT",
)
OBSERVATION_LABEL = "sealed-compact-horizon-law-versus-complete-current-object-boundary"


class ObservationalEmpiricalPhysicsProgram(GeneratedEmpiricalPhysicsProgram):
    @property
    def registration(self):
        return replace(super().registration, provenance=(ProvenanceClass.OBSERVATIONAL_DERIVATION,))


_theorem = theorem_certificate()

SPEC = EmpiricalPhysicsSpec(
    claim_id=CLAIM_ID,
    title="Blind compact-object and horizon-thermodynamics validation",
    statement=(
        "Claim 071 sealed q^4 exclusion support against q^6 gravity, the exact two-family pre-horizon census, "
        "quarter-area information support and mT=1/16 before the compact-object targets opened. NASA's complete "
        "white-dwarf summary identifies electron degeneracy and the 7/5-solar-mass dimensional limit. The primary "
        "PSR J0740+6620 timing record measures 52/25 +/- 7/100 solar masses, placing a neutral-fermion-supported "
        "object strictly above the white-dwarf limit. The complete LIGO-Virgo GW170817 remnant analysis retains "
        "conditional upper boundaries 267/100 and 61/20 solar masses and explicitly identifies their model "
        "conditions. The earlier immutable horizon validation remains unchanged: horizon-scale shadow and ringdown "
        "are observed, while direct Hawking radiation, temperature and information reconstruction are not. That "
        "non-observation is a standing test boundary and is never counted as confirmation of mT=1/16."
    ),
    dependencies=(
        "SFT-PHYS-COMPACT-HORIZON-THERMODYNAMICS-TERMINAL-071",
        "SFT-PHYS-VALIDATION-GRAVITY-HORIZONS-003",
        "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
        "SFT-PHYS-MEAS-TARGET-CUSTODY-001",
        "SFT-PHYS-MEAS-UNCERTAINTY-001",
        "SFT-MATH-EXACT-ARITHMETIC-001",
    ),
    generation_rule=(
        "Generate the complete eight-axis product of sealed compact carrier, complete object-family vector, source "
        "custody, dimensional-role separation, conditional-limit retention, Hawking standing-test status, target "
        "inaccessibility and no-extra-rule."
    ),
    grammar_boundary=(
        "The sealed Claim 071 receipt; all NASA white-dwarf rows; the full PSR J0740 mass, uncertainty, credibility "
        "and method record; both conditional LIGO-Virgo remnant limits; the immutable prior horizon-validation "
        "boundary; all three source snapshots; and no target access before seal."
    ),
    dimensions=empirical_dimensions(
        OBSERVATION_LABEL,
        "Retain the complete dimensional mass ordering, every uncertainty and condition, and the unmeasured Hawking boundary without treating absence as agreement.",
    ),
    exact_result=(
        "The external dimensional record contains the 7/5-solar-mass electron-degenerate limit. The independently "
        "measured neutral-fermion-supported PSR J0740 mass interval is [201/100,215/100] solar masses, wholly above "
        "7/5. The conditional merger-remnant upper records 267/100 and 61/20 solar masses are both above that "
        "measured interval and remain explicitly model-assisted rather than direct TOV measurements. Together with "
        "the earlier horizon-scale shadow/ringdown receipt, the post-seal record supports the ordered finite "
        "white-dwarf, neutron-star and horizon-endpoint classes. No direct astrophysical Hawking-radiation or "
        "temperature measurement exists in the registered vector, so the exact mT=1/16 law remains an unconfirmed, "
        "falsifiable prediction rather than a rewarded absence."
    ),
    induction_base="The sealed two-family theorem exists before the first external white-dwarf mass-limit row is released.",
    induction_step="Each measured or conditional compact-object row is appended once with its role and uncertainty; no row can alter the formal survivor or convert an unmeasured thermal prediction into a match.",
    exclusions=(
        "no compact-object mass, uncertainty, merger condition, horizon image or Hawking status in formal survivor selection",
        "no fitted mass coefficient, equation-of-state choice, tolerance, temperature scale or target-selected correction",
        "no white-dwarf theory summary relabelled as direct mass measurement",
        "no observed neutron-star mass relabelled as the unknown maximum mass",
        "no conditional merger bound relabelled as a direct TOV measurement",
        "no Hawking non-observation rewarded as confirmation and no signed external coordinate imported as a Fold proof scalar",
    ),
    operational_witnesses=(
        ("formal-exclusion", "The q^4/q^6 scaling was sealed before target release.", _theorem["all_exclusion_scalings_close"]),
        ("formal-endpoints", "Exactly two pre-horizon families were sealed before target release.", _theorem["two_pre_horizon_families"]),
        ("formal-horizon", "The reference radius, quarter-area and mT relation were sealed before target release.", _theorem["reference_cross_closes"] and _theorem["all_evaporation_traces_close"]),
    ),
    experiment_id=EXPERIMENT_ID,
    expected_observation_label=OBSERVATION_LABEL,
    target_rows=(
        ExternalTargetRow("WHITE-DWARF-LIMIT", SOURCE_IDS[0], "electron degeneracy and complete reported 7/5 solar-mass limit", OBSERVATION_LABEL),
        ExternalTargetRow("PSR-J0740-MASS", SOURCE_IDS[1], "mass, uncertainty, credibility and timing method", OBSERVATION_LABEL),
        ExternalTargetRow("GW170817-REMNANT-LIMITS", SOURCE_IDS[2], "both conditional remnant limits and all model boundaries", OBSERVATION_LABEL),
    ),
    source_snapshot_path=SOURCE_PATH,
    source_snapshot_hash=SOURCE_HASH,
    falsification_condition=(
        "Reject if any source changes; the measured neutral-fermion object no longer lies above the complete "
        "white-dwarf limit; either conditional remnant row is omitted or stripped of its condition; Hawking "
        "non-observation is counted as confirmation; target data select or modify Claim 071; an external signed "
        "coordinate becomes a Fold proof scalar; or any hostile control passes incorrectly."
    ),
)


SPEC.validate()


__all__ = (
    "CLAIM_ID", "EXPERIMENT_ID", "OBSERVATION_LABEL", "ObservationalEmpiricalPhysicsProgram",
    "SOURCE_FILES", "SOURCE_HASH", "SOURCE_IDS", "SOURCE_PATH", "SPEC",
)
