"""Frozen registrations for the separate ANAL-009--011 claims."""

from pathlib import Path

from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.chemistry.raman_transition_intensity_law_v1 import (
    DEPENDENCIES as A9_DEPS, DIMENSIONS as A9_DIMS, EXACT_RESULT as A9_RESULT,
    OPERATIONAL_WITNESSES as A9_WITNESSES,
)
from sft.chemistry.fluorescence_yield_lifetime_law_v1 import (
    DEPENDENCIES as A10_DEPS, DIMENSIONS as A10_DIMS, EXACT_RESULT as A10_RESULT,
    OPERATIONAL_WITNESSES as A10_WITNESSES,
)
from sft.chemistry.phosphorescence_intersystem_law_v1 import (
    DEPENDENCIES as A11_DEPS, DIMENSIONS as A11_DIMS, EXACT_RESULT as A11_RESULT,
    OPERATIONAL_WITNESSES as A11_WITNESSES,
)
from sft.engine.canonical import sha256_identity
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parents[2]
ANALYSIS_PATH = "experiments/external_sources/chemistry/snapshots/anal-009-011-photoluminescence-v1/complete-postseal-analysis-v1.json"
ANALYSIS_HASH = "sha256:1f6c5dc5b6ef598d38b1f3857b677e9188f3b35d36d0bb821e68b03d8c3566eb"
AUTHORITIES = (
    ("audits/CHEMISTRY_ANAL_001_022_FAMILY_BOUNDARY_2026-07-28.json", "sha256:605cddeba92d16b319a24297668554cc206e625f5289cded52577ca887248260"),
    ("audits/CHEMISTRY_ANAL_009_011_PHOTOLUMINESCENCE_FAMILY_BOUNDARY_2026-07-28.json", "sha256:abd1218984c3238bf2e0234cd14642140c3a51461c6a0a08315798e5cc053f87"),
    ("experiments/external_sources/chemistry/anal_009_011_photoluminescence_family_source_identity_registry_v1.json", "sha256:56a97fb99d5e8e3ea34f6ce2da2d35a5bf40b8ec11bba33ac0cda4337a29ffee"),
    ("experiments/external_sources/chemistry/anal_009_011_source_transport_addendum_v1.json", "sha256:48c16145e6c72d6661a0fd5b997a62e1009dc405cd5e59bd25eb583612215681"),
    ("sft/chemistry/raman_transition_intensity_law_v1.py", "sha256:b8d8ce4740521931e64588335268302023407ed1b7f01b672f85899fe8e80566"),
    ("sft/chemistry/fluorescence_yield_lifetime_law_v1.py", "sha256:754e99e4a11edf4c20aa0eb277f3a388eee512937e3c7298e622417f7dd9facb"),
    ("sft/chemistry/phosphorescence_intersystem_law_v1.py", "sha256:36f3aa37be7ed7cfea20be8d789640e4156e249bcbfc098156ec6c2854bba3e6"),
    ("experiments/external_sources/chemistry/anal_009_target_identities_v1.json", "sha256:59f114b3e9b20f13a3be811fbea54233410d70d7ba8b7f44800af289361482cb"),
    ("experiments/external_sources/chemistry/anal_010_target_identities_v1.json", "sha256:f41465a32adc40721f2e94f2318e45bafd0254a90139b4e07030f6cb970f2bfc"),
    ("experiments/external_sources/chemistry/anal_011_target_identities_v1.json", "sha256:191ee56fbeb3c7ae7f4229a7770700fd8b7a6be196f1b4985cd39cd0e58f3817"),
    ("experiments/sealed_predictions/chemistry_anal_009_pre_source_v1.json", "sha256:97a2badefd0519dd5a09456509052715f041a090c7aa6a8d17545084d48745e5"),
    ("experiments/sealed_predictions/chemistry_anal_010_pre_source_v1.json", "sha256:031795365ba9c851efd248db8bdcbe511508acd45b725e1cdceb0d4f188bc040"),
    ("experiments/sealed_predictions/chemistry_anal_011_pre_source_v1.json", "sha256:7b15df79150cf4f81a518a349441d599ee492df9a1917623dbc23da095e9a800"),
    ("experiments/external_sources/chemistry/snapshots/anal-009-011-photoluminescence-v1/source-inventory-v1.json", "sha256:5f81a4c8a0dafb2f56d1f6953bb3ff25b7500e89a55df021945fae94c46a3539"),
    (ANALYSIS_PATH, ANALYSIS_HASH),
    ("tools/capture_chemistry_anal_009_011_sources_v1.py", "sha256:72431e3705ee23247d398c5c68e2d351f4fc00c4aaa6897869144aecc571d05b"),
    ("tools/build_chemistry_anal_009_011_external_v1.py", "sha256:5031f56535ef0a4ca908fe596ccb57a5d3a95a534a88585b7db05d70f806f95c"),
    ("experiments/external_sources/chemistry/snapshots/anal-009-011-photoluminescence-v1/nist-raman-standards.html", "sha256:4859c291440dfe2ff29a09959b19dd6cc49bf3613419fed8d6b3a807b8f1984b"),
    ("experiments/external_sources/chemistry/snapshots/anal-009-011-photoluminescence-v1/nist-srm-2241-certificate.pdf", "sha256:13915961ce4c6f8f3cdbd0f29e808378311134da367e64fb68d608082e77a755"),
    ("experiments/external_sources/chemistry/snapshots/anal-009-011-photoluminescence-v1/nist-srm-2242a-product.html", "sha256:6f9592f36bf54821eaa92cf356b7367e5674732fb6667c3a2a0ffd334f40a023"),
    ("experiments/external_sources/chemistry/snapshots/anal-009-011-photoluminescence-v1/nist-srm-2242a-certificate.pdf", "sha256:0251be4d706bf7995bfb498b388ea5b7f83198e908404d5ad543028f8d126105"),
    ("experiments/external_sources/chemistry/snapshots/anal-009-011-photoluminescence-v1/iupac-fluorescence-standards-2010.html", "sha256:43a60fbe481e09e8ecacd4a3b3d1ba6c28d4130ad881b953a224a760b04a0809"),
    ("experiments/external_sources/chemistry/snapshots/anal-009-011-photoluminescence-v1/iupac-photoluminescence-quantum-yield-2011.pdf", "sha256:56c0200dd81f9fe5f5069c1c35f73b9e985131b120ffbf01b5779547538dac9c"),
    ("experiments/external_sources/chemistry/snapshots/anal-009-011-photoluminescence-v1/nist-srm-2941a-product.html", "sha256:b0b6c98e738e5fadede807904439a563dfe441b4c93ea8e7aa663143862f910a"),
    ("experiments/external_sources/chemistry/snapshots/anal-009-011-photoluminescence-v1/nist-srm-2941a-certificate.pdf", "sha256:eabaa9e03c882ba9b90a39f22fd6f58384d16c14604857a3d3b1a259ae4ffe31"),
    ("experiments/external_sources/chemistry/snapshots/anal-009-011-photoluminescence-v1/nist-ir-7458-fluorescence-guide.pdf", "sha256:ebbf94956e62fae6ec89c6d404e780f4a6bdc94675036c1b37204b7652f24deb"),
    ("experiments/external_sources/chemistry/snapshots/anal-009-011-photoluminescence-v1/uc-fluorescence-lifetime-standards-2007.pdf", "sha256:8b3f88fd661a37c945f16b4803b255c04020315e0c9c7689aaafbe691913edf7"),
    ("experiments/external_sources/chemistry/snapshots/anal-009-011-photoluminescence-v1/nist-pash-phosphorescence-identity.html", "sha256:09e1211c7774ad102c5c1ca82eb556d71ba35be0c0fbe707d318b4b810326810"),
    ("experiments/external_sources/chemistry/snapshots/anal-009-011-photoluminescence-v1/nlm-pash-phosphorescence-article.xml", "sha256:91614ab4059c889600314f105d1fa311f3b417d2bff4d1e4d9124ae23fa7f520"),
    ("experiments/external_sources/chemistry/snapshots/anal-009-011-photoluminescence-v1/iupac-phosphorescence-lifetime.html", "sha256:86bf5d7ea1bb32e0fa70b0877abadd1050eca6dfa5634a342e089993f19c48d9"),
    ("experiments/external_sources/chemistry/snapshots/anal-009-011-photoluminescence-v1/nist-srm-2242a-product-linked-1.xlsx", "sha256:63259c6407b4b2e92ff016fc8e910ec1d4ac4f3be6d396ae511fc66ce2f761ea"),
    ("experiments/external_sources/chemistry/snapshots/anal-009-011-photoluminescence-v1/nist-srm-2941a-product-linked-1.xlsx", "sha256:8a338c3e8bcd86312b0784d26c03c0e48713bb46dd659d4431949969be15a3af"),
    ("experiments/external_sources/chemistry/snapshots/anal-009-011-photoluminescence-v1/pmc6688180-oa-manifest.xml", "sha256:60a932ee77ee81908ba0f3dd1f80dbe3407bfa7a9770a974e1a73b9d85cdc8cf"),
)
for path, expected in AUTHORITIES:
    if hash_file(ROOT / path) != expected:
        raise ValueError(f"ANAL-009--011 authority changed: {path}")


def targets(number: str, names: tuple[str, ...], sources: tuple[str, ...]):
    return tuple(
        ChemistryTargetReference(
            f"SFT-CHEM-ANAL-{number}-{name}",
            "ANAL-009-011-COMPLETE-SOURCE-INVENTORY" if name == "COMPLETE-SOURCE" else sources[index % len(sources)],
            name.casefold().replace("-", " "), ANALYSIS_PATH, ANALYSIS_HASH,
        )
        for index, name in enumerate(names)
    )


A9_TARGETS = targets("009", (
    "IDENTITY", "EXCITATION-CONDITION", "COMPLETE-SHIFT-SUPPORT", "COMPLETE-INTENSITY-VECTOR",
    "COEFFICIENT-RECONSTRUCTION", "UNCERTAINTY-BOUND", "STATUS-ADVERSE-ABSENT", "COMPLETE-SOURCE",
), ("NIST-RAMAN-RELATIVE-INTENSITY-STANDARDS", "NIST-SRM-2241-RAMAN-785-NM", "NIST-SRM-2242A-RAMAN-532-NM"))
A10_TARGETS = targets("010", (
    "IDENTITY-STATE-CHANNEL", "EMISSION-SUPPORT", "COMPLETE-QUANTUM-YIELD-VECTOR", "COMPLETE-LIFETIME-VECTOR",
    "COMPLETE-CHANNEL-PARTITION", "UNCERTAINTY-CONDITION", "STATUS-ADVERSE-ABSENT", "COMPLETE-SOURCE",
), ("IUPAC-FLUORESCENCE-STANDARDS-2010", "IUPAC-PHOTOLUMINESCENCE-QUANTUM-YIELD-2011", "NIST-SRM-2941A-FLUORESCENCE-GREEN", "NIST-IR-7458-FLUORESCENCE-GUIDE", "NIST-NLM-PASH-PHOSPHORESCENCE-2018"))
A11_TARGETS = targets("011", (
    "IDENTITY-SPIN-PATH", "INTERSYSTEM-TRANSITION", "COMPLETE-EMISSION-SUPPORT", "COMPLETE-LIFETIME-VECTOR",
    "TEMPERATURE-SOLVENT-CONDITION", "OBSERVED-NONOBSERVED-PARTITION", "STATUS-ADVERSE-ABSENT", "COMPLETE-SOURCE",
), ("NIST-NLM-PASH-PHOSPHORESCENCE-2018", "IUPAC-PHOSPHORESCENCE-LIFETIME"))


def spec(claim, title, statement, deps, dims, result, witnesses, experiment, label, rows, boundary, base, step):
    return EmpiricalChemistrySpec(
        claim_id=claim, title=title, statement=statement, dependencies=deps,
        generation_rule="Generate the literal product of eight registered photoluminescence-custody decisions.",
        grammar_boundary=boundary, dimensions=dims, exact_result=result,
        induction_base=base, induction_step=step,
        exclusions=(
            "no numerical zero negative irrational imaginary continuum fitted free random or imported native parameter",
            "no external coefficient fit value formula threshold prominent line or favorable row chooses the survivor",
            "all measured favorable adverse absent unavailable unresolved error bound condition unit and transport disclosures remain",
        ),
        operational_witnesses=witnesses, experiment_id=experiment,
        expected_observation_label=label, target_rows=rows,
        observation_registry_path=ANALYSIS_PATH,
        falsification_condition=(
            "The claim halts if its survivor is nonunique; any registered value, line, coefficient, curve, condition, "
            "unit, uncertainty, adverse, absent, unavailable, unresolved or source surface is omitted; the separate "
            "reconstruction disagrees; or an external result selects the native law. " + boundary
        ),
    )


RAMAN_SPEC = spec(
    "SFT-CHEM-RAMAN-TRANSITION-INTENSITY-009", "Fold Raman transition and intensity law",
    "Held molecular transitions force a held Raman side, exact positive shift/intensity support and complete conditioned line custody.",
    A9_DEPS, A9_DIMS, A9_RESULT, A9_WITNESSES, "SFT-EXP-CHEM-RAMAN-TRANSITION-INTENSITY-009",
    "complete-raman-transition-intensity-vector", A9_TARGETS,
    "Eight dimensions exhaust carrier, states, polarizability, position, intensity, condition, custody and extension.",
    "One held molecular transition supplies the first exact Raman-side record.",
    "Every successor appends a complete conditioned line without changing prior evidence.",
)
FLUORESCENCE_SPEC = spec(
    "SFT-CHEM-FLUORESCENCE-YIELD-LIFETIME-010", "Fold fluorescence yield and lifetime law",
    "A held excitation forces a complete radiative/nonradiative partition, exact counted yield and finite lifetime custody.",
    A10_DEPS, A10_DIMS, A10_RESULT, A10_WITNESSES, "SFT-EXP-CHEM-FLUORESCENCE-YIELD-LIFETIME-010",
    "complete-fluorescence-yield-lifetime-vector", A10_TARGETS,
    "Eight dimensions exhaust carrier, transition, channels, emission, yield, lifetime, custody and extension.",
    "One held excitation and terminal channel supply the first exact channel record.",
    "Every successor retains prior counts and extends the complete channel partition.",
)
PHOSPHORESCENCE_SPEC = spec(
    "SFT-CHEM-PHOSPHORESCENCE-INTERSYSTEM-011", "Fold phosphorescence intersystem law",
    "Held distinct spin states force a complete excitation-intersystem-emission path with exact observed or structural-absence custody.",
    A11_DEPS, A11_DIMS, A11_RESULT, A11_WITNESSES, "SFT-EXP-CHEM-PHOSPHORESCENCE-INTERSYSTEM-011",
    "complete-phosphorescence-intersystem-vector", A11_TARGETS,
    "Eight dimensions exhaust carrier, spin, path, emission, yield, lifetime, custody and extension.",
    "One held distinct-spin intersystem path supplies the first observed-or-absent record.",
    "Every successor appends one complete path without changing earlier evidence.",
)
SPECS = (RAMAN_SPEC, FLUORESCENCE_SPEC, PHOSPHORESCENCE_SPEC)
for item in SPECS:
    item.validate()

COMPLETENESS_CERTIFICATES = {
    item.claim_id: sha256_identity((item.claim_id, tuple(target.target_id for target in item.target_rows), 16, 73, item.exact_result))
    for item in SPECS
}

__all__ = (
    "ANALYSIS_HASH", "ANALYSIS_PATH", "AUTHORITIES", "COMPLETENESS_CERTIFICATES",
    "FLUORESCENCE_SPEC", "PHOSPHORESCENCE_SPEC", "RAMAN_SPEC", "SPECS",
)
