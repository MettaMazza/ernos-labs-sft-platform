"""Frozen POLY-001--013 registrations for quantitative Polymer Chemistry."""

from __future__ import annotations

import json
from pathlib import Path

from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.chemistry.polymer_chemistry_laws_v1 import LAW_ROWS
from sft.engine.canonical import sha256_identity
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parents[2]
ANALYSIS_PATH = "experiments/external_sources/chemistry/snapshots/poly-001-013-whole-subfield-v1/complete-postseal-analysis-v2.json"
ANALYSIS_HASH = "sha256:45339f7906d657fa4369e84f51c5ada77932f6b3e60c3f59857113084034c81c"
SOURCE_PAIRS = {
    "001": ("NIST-SRM-2888-POLYSTYRENE-CERTIFICATION", "NIST-PRECISION-DEUTERATED-POLYETHYLENE"),
    "002": ("NIST-SRM-2888-POLYSTYRENE-CERTIFICATION", "NIST-QUINTUPLE-DETECTOR-COPOLYMER"),
    "003": ("NIST-SRM-2888-POLYSTYRENE-CERTIFICATION", "NIST-SRM-2886-POLYETHYLENE-CERTIFICATION"),
    "004": ("NIST-SRM-2886-POLYETHYLENE-CERTIFICATION", "NIST-MONODISPERSE-PAMS-KINETIC-NETWORK"),
    "005": ("NIST-STOCHASTIC-PHOTOPOLYMER-NETWORK-GROWTH", "NIST-MONODISPERSE-PAMS-KINETIC-NETWORK"),
    "006": ("NIST-STOCHASTIC-PHOTOPOLYMER-NETWORK-GROWTH", "NIST-CROSSLINKED-PHOTOPOLYMER-CONVERSION"),
    "007": ("NIST-RING-OPENING-COPOLYMER-SEQUENCE", "NIST-PRECISION-DEUTERATED-POLYETHYLENE"),
    "008": ("NIST-BRANCH-PLACEMENT-DILUTE-SOLUTION", "NIST-MACROMOLECULAR-ARCHITECTURES"),
    "009": ("NIST-THERMOREVERSIBLE-GELATION-PERCOLATION", "NIST-BRIDGING-GELATION"),
    "010": ("NIST-QUINTUPLE-DETECTOR-COPOLYMER", "NIST-BRANCH-PLACEMENT-DILUTE-SOLUTION"),
    "011": ("NIST-PVOH-IONIC-LIQUID-GELATION", "NIST-CROSSLINKED-PHOTOPOLYMER-CONVERSION"),
    "012": ("NIST-POLYMER-PYROLYSIS-NETWORK", "NIST-POLYMER-DEPOLYMERIZATION-KINETICS"),
    "013": ("NIST-CROSSLINKED-PHOTOPOLYMER-CONVERSION", "NIST-POLYMER-PROCESSING-METROLOGY"),
}

AUTHORITIES = (
    ("audits/CHEMISTRY_POLY_001_013_WHOLE_SUBFIELD_BATCH_BOUNDARY_2026-07-28.json", "sha256:392e3aef3ab902705571c23dc4b68dec29753b2b3870a5e8cc33079beba766b9"),
    ("audits/CHEMISTRY_POLY_SOURCE_RECONSTRUCTION_RETRY_2026-07-28.json", "sha256:75571159d0e5bbe9d2565651abeae873dac9f98e3815d79f2464c6023a39eadd"),
    ("sft/chemistry/polymer_chemistry_laws_v1.py", "sha256:3004a82f739aac163eabbd6e598af608f3e8e2258563e72857e2c4281da54158"),
    ("experiments/external_sources/chemistry/snapshots/poly-001-013-whole-subfield-v1/source-inventory-v1.json", "sha256:f6c0131276c1923c6be16a77423c3fb30ae8484744bb3cf002bcec51f81c5996"),
    ("experiments/external_sources/chemistry/snapshots/poly-001-013-quantitative-addendum-v1/source-inventory-v1.json", "sha256:3af4a15fa05c6b901bcc0fd0b80ecceac39b684f888c681117908ccfad6e14e2"),
    (ANALYSIS_PATH, ANALYSIS_HASH),
)
IDENTITY_HASHES = {
    "001": "sha256:1ab2551c204bea1ead268a95c67b88988d98e85d17f5d5536acfb94a1fba49d9",
    "002": "sha256:38879f16bc1f55b2e7b9ed336d07530d2300d19eb1bc798f807f7b78b04ffc08",
    "003": "sha256:39a115e3c0899c373b235123d17fe1c8a7181b6ee34ed79926cdf8e00ab62d11",
    "004": "sha256:75f259262d9d346ebc3d0fb764d0f3f31a0a41c9d63945cb800008fefe135c60",
    "005": "sha256:b2c8a81c5936068bd4d8225d38098502d47a27cc077820e99335e8420c66b8cf",
    "006": "sha256:eb2912340b46836447b774e58ac8bc3ee67d6054ad1bb8c3eef4dc3905d8c865",
    "007": "sha256:52d73a35e9aa99a495f75f34f6d24f5f54a6b42b12a71be1d321d653e61ce32c",
    "008": "sha256:ad802f9d918ad2e806109d4aeef788a041ab75e516e755c3c25866553a30c2a7",
    "009": "sha256:58502613081ab07b37923e83bbd0f3496f98554913a4de30d2903a32ff671e91",
    "010": "sha256:fe1606d98ef68278244a302ec00b90f6e838f483b2befb3eb7c125dc455ec301",
    "011": "sha256:b1c1273e01dfc2527da9e9c2b059b89d7838763d27d4d88a68d0d493a8398a61",
    "012": "sha256:70cdc8d95da6ba8bf7e25edf4cc82b9c6e0065d62e8e88428304fe17c90126a8",
    "013": "sha256:e71d2421435c6b3cddaa326362e5c09ef73ec9c9b07465e750ff779cfa92d025",
}
for path, expected in AUTHORITIES:
    if hash_file(ROOT / path) != expected:
        raise ValueError(f"POLY-001--013 authority changed: {path}")


def _targets(number: str) -> tuple[ChemistryTargetReference, ...]:
    path = ROOT / f"experiments/external_sources/chemistry/poly_{number}_target_identities_v1.json"
    if hash_file(path) != IDENTITY_HASHES[number]:
        raise ValueError(f"POLY-{number} target identities changed")
    target_ids = tuple(json.loads(path.read_text())["target_ids"])
    sources = SOURCE_PAIRS[number]
    return tuple(
        ChemistryTargetReference(target_id, sources[index % 2], target_id.rsplit("-", 1)[-1].casefold(), ANALYSIS_PATH, ANALYSIS_HASH)
        for index, target_id in enumerate(target_ids)
    )


def _spec(number: str) -> EmpiricalChemistrySpec:
    law = LAW_ROWS[number]
    return EmpiricalChemistrySpec(
        claim_id=law["claim_id"],
        title=law["title"],
        statement=law["statement"],
        dependencies=law["dependencies"],
        generation_rule=f"Generate the literal product of the eight frozen POLY-{number} decisions.",
        grammar_boundary=f"The eight POLY-{number} dimensions exhaust the registered carrier, operation, boundary and certificate distinctions.",
        dimensions=law["dimensions"],
        exact_result=law["result"],
        induction_base=f"One complete finite POLY-{number} carrier supplies the first registered witness.",
        induction_step="Every successor retains all earlier carriers, distinctions, paths, resources and ownership boundaries before appending one lawful transition.",
        exclusions=(
            "no numerical zero negative irrational imaginary continuum fitted free random or imported native parameter",
            "no measured polymer value equation distribution trend or favorable row selects the survivor",
            "no first extraction failure source defect adverse row or unresolved record retires an obligation",
        ),
        operational_witnesses=law["operational_witnesses"],
        experiment_id=f"SFT-EXP-CHEM-POLY-{number}",
        expected_observation_label=f"complete-poly-{number}-postseal-source-vector",
        target_rows=_targets(number),
        observation_registry_path=ANALYSIS_PATH,
        falsification_condition=f"POLY-{number} halts if its survivor is nonunique; a registered target, source byte, measured value, unit, uncertainty, adverse, absent, unavailable, inconsistent or unresolved row is omitted; a source outcome selects the native law; or the reconstruction retry is erased.",
    )


SPECS = tuple(_spec(number) for number in LAW_ROWS)
SPEC_BY_NUMBER = {number: spec for number, spec in zip(LAW_ROWS, SPECS)}
for _specification in SPECS:
    _specification.validate()
COMPLETENESS_CERTIFICATES = {
    spec.claim_id: sha256_identity((spec.claim_id, tuple(row.target_id for row in spec.target_rows), 21, 104, spec.exact_result, ANALYSIS_HASH))
    for spec in SPECS
}

__all__ = ("ANALYSIS_HASH", "ANALYSIS_PATH", "AUTHORITIES", "COMPLETENESS_CERTIFICATES", "SPECS", "SPEC_BY_NUMBER")
