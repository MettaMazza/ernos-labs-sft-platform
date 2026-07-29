"""Complete observational successor for formal new-sector Claims 088-094."""

from dataclasses import replace

from sft.engine import ProvenanceClass
from sft.physics.generated_empirical_law import EmpiricalPhysicsSpec, ExternalTargetRow, GeneratedEmpiricalPhysicsProgram, empirical_dimensions
from sft.physics.new_sector_complete_family_law_v1 import category_clean_particle_census, no_extra_boundary, sector_beta_slope, sector_phenotype, smithion_search_signatures


CLAIM_ID = "SFT-PHYS-VALIDATION-NEW-SECTOR-COMPLETE-FAMILY-095"
EXPERIMENT_ID = "SFT-EXP-PHYS-NEW-SECTOR-COMPLETE-FAMILY-095"
SOURCE_PATH = "experiments/external_sources/physics/snapshots/new-sector-complete-family-source-record-2026-07-28.json"
SOURCE_HASH = "sha256:6174396364e66e1367accedb5b46d67eaa1e8a1290084c35850df27f3def63e7"
PREREGISTRATION_PATH = "experiments/physics/SFT-EXP-PHYS-NEW-SECTOR-COMPLETE-FAMILY-095/source_identity_preregistration.json"
PREREGISTRATION_HASH = "sha256:c3162c7624c47f7bce5c4f4043fba4c919d8eb827b39b608fc0c2870b5c6c75b"
SOURCE_FILES = (
    ("experiments/external_sources/physics/snapshots/pdg-force-sector-anchor-record.json", "sha256:bb37e82e9515ff526cbaad742167c16ac1960b7bfca32d8b39dd4384c73b7341"),
    ("experiments/external_sources/physics/snapshots/pdg-2025-qcd.pdf", "sha256:7cbb5c5ef1d217fd0a13544db36d031e600f4e4df7309af6c859a0b988ed6ada"),
    ("experiments/external_sources/physics/snapshots/pdg-2025-electroweak-model.pdf", "sha256:8642888a3408d8c57fc673b379325b07f02948135491f64a2e42320e8929320a"),
    ("experiments/external_sources/physics/snapshots/pdg-2025-summary-tables.html", "sha256:ae10b6a7c6fefb8a6d90d35dc341d3ae8284a1e3cf2c94c656ae2e8957df4d56"),
    ("experiments/external_sources/physics/snapshots/pdg-searches-hypothetical-particles-2025.html", "sha256:3192c4c07b4640739641897ef445f62a1b99b58a385e6b47c83effa75a51e95c"),
    ("experiments/external_sources/physics/snapshots/atlas-dark-sector-jets-2025.html", "sha256:8ac85050941384d0fa3e820178d8fea9f8b3955576d1e976c155fcb3bd1bbb9d"),
    ("experiments/external_sources/physics/snapshots/dark-smithion-lfv-postseal-source-record.json", "sha256:ed0dba82cdd49f67258eb152466a629d9086804197d2c56bcfdc49e2849345f3"),
    ("experiments/external_sources/physics/snapshots/planck-2018-density-abstract-record.json", "sha256:274e0189de5846ce0b8c2d7b83ae06c72587cf8325d4d2b2338e88dd0a74a88f"),
    ("experiments/external_sources/physics/snapshots/arxiv-1606.09251-sparc.pdf", "sha256:d089215877213661e40965543ee7e05736619082ad16d95e65ec059029588c63"),
    ("experiments/external_sources/physics/snapshots/arxiv-2504.15711-megii-lfv.pdf", "sha256:0efbf99543c92d340eb7b07f40e6fea580b7746caab26c9233d3e30e8b71a5b6"),
    ("experiments/external_sources/physics/snapshots/arxiv-0908.2381-babar-tau-lfv.pdf", "sha256:ba3e1352f4c14b1867e06f6436b4a6b1e1980cd55ce52d9a9454bd618ed70015"),
)
SOURCE_IDS = (
    "PDG-FORCE-SECTOR-ANCHORS-2025",
    "PDG-SUMMARY-TABLES-2025",
    "PDG-SEARCHES-HYPOTHETICAL-PARTICLES-2025",
    "ATLAS-DARK-SECTOR-JETS-2025",
    "DARK-SMITHION-STANDING-RECORD-2026",
)
OBSERVATION_LABEL = "complete-new-sector-record__known-three-eight-anchors__known-fermion-categories__outside-list-classes-searched-not-confirmed__dark-jets-and-missing-momentum-searched__penta-hepta-and-smithions-remain-standing"


class ObservationalEmpiricalPhysicsProgram(GeneratedEmpiricalPhysicsProgram):
    @property
    def registration(self):
        return replace(super().registration, provenance=(ProvenanceClass.OBSERVATIONAL_DERIVATION,))


SPEC = EmpiricalPhysicsSpec(
    claim_id=CLAIM_ID,
    title="Complete measured new-sector, particle-census and Smithion search record",
    statement="Seven sealed V3 laws are compared with the complete registered PDG, ATLAS, Planck, SPARC, MEG II and BaBar record. Known sector counts and known particle categories are retained; outside-list classes remain searched hypotheses; collider dark-jet and missing-momentum signatures are active with model-dependent exclusions; and all penta/hepta carrier, slope and Smithion measurements remain explicit standing tests rather than fabricated discoveries or retired claims.",
    dependencies=(
        "SFT-PHYS-PENTA-COMPLETE-PHENOTYPE-088",
        "SFT-PHYS-HEPTA-COMPLETE-PHENOTYPE-089",
        "SFT-PHYS-PENTA-BETA-SLOPE-090",
        "SFT-PHYS-HEPTA-BETA-SLOPE-091",
        "SFT-PHYS-CATEGORY-CLEAN-PARTICLE-CENSUS-092",
        "SFT-PHYS-NO-EXTRA-SECTOR-PARTICLE-BOUNDARY-093",
        "SFT-PHYS-SMITHION-INTERACTION-SEARCH-SIGNATURES-094",
        "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
        "SFT-PHYS-MEAS-TARGET-CUSTODY-001",
        "SFT-PHYS-MEAS-UNCERTAINTY-001",
        "SFT-MATH-EXACT-ARITHMETIC-001",
    ),
    generation_rule="Generate the complete eight-axis product of the seven sealed new-sector laws, five source identities, complete favorable/adverse/absent/searched/unresolved retention, observational provenance, measurement separation and no-extra-rule closure.",
    grammar_boundary="Formal Claims 088-094; all five registered source identities and eleven captured artifacts; every known-sector, known-particle, outside-list-search, collider-signature, abundance, gravitating-support, null and unmeasured-standing-prediction row; and all 256 comparison forms.",
    dimensions=empirical_dimensions("sealed-new-sector-complete-family-versus-five-source-observation-vector", "The seven-claim formal family remains fixed while all known anchors, search categories, model-dependent limits, non-observation and standing-prediction rows are retained."),
    exact_result="The known external anchors reproduce three weak carriers, three colour charges and eight gluons and retain the known lepton/quark categories used in the 110-kind census. PDG lists axion-like, heavy-neutral-lepton and supersymmetric classes as search subjects, not confirmed additions in this record. ATLAS searches semi-visible/emerging confining dark jets and missing momentum and reports model-dependent exclusions, establishing the relevance of the sealed signature classes but not the specific 24/48 inventories, slopes 4/6 or a Smithion discovery. The existing dark record supports exact 27/5 abundance correspondence and additional gravitating support while retaining no registered Smithion mass. Thus every penta/hepta quantity remains a precise standing test; current non-observation neither confirms nor retires it.",
    induction_base="The seven formal predecessors seal the complete penta/hepta phenotype, slopes, inventory, boundary and signatures before this combined record is assembled.",
    induction_step="Each source and row is appended once with its identity and result type; a search, limit, null or absence cannot be relabelled as either a measured new sector or a retirement.",
    exclusions=(
        "no PDG, ATLAS, cosmology or null-search row visible to the formal survivor decision",
        "no known-sector count imported to select p-squared-less-One",
        "no searched hypothetical class relabelled as a confirmed fundamental kind",
        "no model-dependent collider exclusion generalized to every SFT signature",
        "no unobserved penta/hepta carrier, beta slope or Smithion mass represented as measured",
        "no current non-observation represented as retirement of a standing prediction",
        "no numerical-zero, negative, irrational, imaginary, floating or completed-infinite magnitude in the formal derivation",
    ),
    operational_witnesses=(
        ("phenotypes", "Penta/hepta mediator and pair counts remain exact.", (sector_phenotype(5)["mediators"], sector_phenotype(7)["mediators"], sector_phenotype(5)["confinement_pair_count"], sector_phenotype(7)["confinement_pair_count"]) == (24, 48, 2, 3)),
        ("slopes", "The two independently sealed slopes remain four and six.", (sector_beta_slope(5), sector_beta_slope(7)) == (4, 6)),
        ("census", "The category-clean census totals 110.", category_clean_particle_census()["category_clean_total"] == 110),
        ("boundary", "Prime eleven and all five outside-list falsifiers remain held.", no_extra_boundary()["first_excluded_prime"] == 11 and len(no_extra_boundary()["outside_list_falsifiers"]) == 5),
        ("signatures", "The two confining jet classes retain 24 and 48 carriers.", tuple(row["confining_jet_carriers"] for row in smithion_search_signatures().values()) == (24, 48)),
    ),
    experiment_id=EXPERIMENT_ID,
    expected_observation_label=OBSERVATION_LABEL,
    target_rows=tuple(ExternalTargetRow(target_id, source_id, description, OBSERVATION_LABEL) for target_id, source_id, description in (
        ("KNOWN-SECTOR-CARRIER-ANCHORS", SOURCE_IDS[0], "Complete known-sector counts plus unmeasured new-sector boundary"),
        ("KNOWN-FERMION-KIND-INVENTORY", SOURCE_IDS[1], "Known gauge/Higgs, lepton and quark summary categories"),
        ("OUTSIDE-LIST-SEARCH-STATUS", SOURCE_IDS[2], "Axion-like, heavy-neutral-lepton and supersymmetric search categories"),
        ("CONFINING-JET-AND-MISSING-MOMENTUM-SEARCH", SOURCE_IDS[3], "Semi-visible and emerging dark jets, missing momentum and model-dependent exclusions"),
        ("SMITHION-ABUNDANCE-GRAVITY-AND-MEASUREMENT-STATUS", SOURCE_IDS[4], "Abundance, gravitating support and no-registered-Smithion-mass boundary"),
    )),
    source_snapshot_path=SOURCE_PATH,
    source_snapshot_hash=SOURCE_HASH,
    falsification_condition="Reject if any formal receipt, preregistration, artifact or row changes; if a known count/category, searched hypothesis, collider signature/limit, abundance/gravity row or unmeasured-standing status is omitted; if a search is relabelled as discovery; if non-observation is relabelled as retirement; or if observation alters a formal survivor.",
)


SPEC.validate()


__all__ = ("CLAIM_ID", "EXPERIMENT_ID", "OBSERVATION_LABEL", "ObservationalEmpiricalPhysicsProgram", "PREREGISTRATION_HASH", "PREREGISTRATION_PATH", "SOURCE_FILES", "SOURCE_HASH", "SOURCE_IDS", "SOURCE_PATH", "SPEC")
