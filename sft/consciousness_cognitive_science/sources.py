"""Post-prediction-seal external source identities for Consciousness."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SourceIdentity:
    source_id: str
    body: str
    source_uri: str
    snapshot_name: str
    evidence_class: str
    registered_features: tuple[str, ...]
    adverse_or_boundary_role: str | None = None


SOURCES = (
    SourceIdentity("CONSC-CIE-1931-CMF", "International Commission on Illumination", "https://cie.co.at/datatable/cie-1931-colour-matching-functions-2-degree-observer", "cie-1931-colour-matching-functions.html", "official physical colour-measurement standard", ("colour-matching functions", "standard colorimetric observer", "one nm wavelength steps")),
    SourceIdentity("CONSC-NOREPORT-NETWORKS-2022", "Kronemer et al., Nature Communications", "https://pmc.ncbi.nlm.nih.gov/articles/PMC9707162/", "pmc9707162.html", "primary human report/no-report experiment", ("Report + No-Report Paradigm", "participants", "perceived", "not perceived")),
    SourceIdentity("CONSC-NOREPORT-CRITIQUE-2022", "Duman et al., Frontiers in Human Neuroscience", "https://pmc.ncbi.nlm.nih.gov/articles/PMC9130851/", "pmc9130851.html", "registered methodological adverse evidence", ("report-based paradigms", "no-report paradigms", "alternative interpretations"), "Preserves the finding that no-report indicators do not automatically establish phenomenal occurrence."),
    SourceIdentity("CONSC-SPLIT-INTEGRATION-2023", "de Haan et al., Brain Sciences", "https://pmc.ncbi.nlm.nih.gov/articles/PMC10667445/", "pmc10667445.html", "primary split-brain integration experiment", ("split-brain patient", "two experiments", "automatic processing", "deliberate")),
    SourceIdentity("CONSC-SPLIT-BOUNDARY-2020", "de Haan et al., Neuropsychologia review", "https://pmc.ncbi.nlm.nih.gov/articles/PMC7305066/", "pmc7305066.html", "registered unity-evidence boundary", ("whether dividing the brain divides consciousness", "intermediate results", "measures"), "Preserves disagreement and measurement ambiguity rather than selecting a unity theory."),
    SourceIdentity("CONSC-CHOICE-BLINDNESS-2017", "Sloman et al., PLOS ONE", "https://pmc.ncbi.nlm.nih.gov/articles/PMC5308842/", "pmc5308842.html", "primary introspection and confabulation experiment", ("Choice Blindness Paradigm", "confidence", "confabulate", "manipulated")),
    SourceIdentity("CONSC-DREAM-DATABASE-2025", "Siclari et al., Scientific Data", "https://pmc.ncbi.nlm.nih.gov/articles/PMC12350935/", "pmc12350935.html", "primary open dream EEG and report database", ("DREAM database", "participants", "awakenings", "Experience without recall", "No experience")),
    SourceIdentity("CONSC-ANESTHESIA-RECOVERY-2021", "Mashour et al., eLife", "https://pmc.ncbi.nlm.nih.gov/articles/PMC8163502/", "pmc8163502.html", "primary controlled consciousness-recovery experiment", ("multicenter study", "healthy humans", "general anesthesia", "recovery of consciousness", "cognitive")),
    SourceIdentity("CONSC-ATTENTIONAL-BLINK-2014", "Asplund et al., Psychological Science", "https://pmc.ncbi.nlm.nih.gov/articles/PMC3954951/", "pmc3954951.html", "primary attention-awareness experiment", ("attentional blink", "all-or-none", "likelihood", "precision")),
    SourceIdentity("CONSC-SYNESTHESIA-BATTERY-2007", "Eagleman et al., Journal of Neuroscience Methods", "https://pmc.ncbi.nlm.nih.gov/articles/PMC4118597/", "pmc4118597.html", "primary within-subject qualitative consistency protocol", ("internal consistency task", "three times", "color", "controls")),
    SourceIdentity("CONSC-SYNESTHESIA-COLOUR-2026", "Root et al., Behavior Research Methods", "https://pmc.ncbi.nlm.nih.gov/articles/PMC12960370/", "pmc12960370.html", "open synesthesia colour dataset and protocol", ("publicly available data", "participants", "test–retest consistency", "CIELuv")),
    SourceIdentity("CONSC-SYNESTHETIC-COLOUR-MATCH-2008", "Hong and Blake, Vision Research", "https://pmc.ncbi.nlm.nih.gov/articles/PMC2423348/", "pmc2423348.html", "primary participant-specific colour matching experiment", ("synesthetic color", "asymmetric matching", "spectroradiometer", "observers")),
    SourceIdentity("CONSC-COLOUR-CATEGORY-LEARNING-2010", "Zhou et al., PNAS", "https://pmc.ncbi.nlm.nih.gov/articles/PMC2890491/", "pmc2890491.html", "primary language-category and colour-discrimination control", ("learned categories", "perceptual discrimination", "control group"), "Preserves the adverse fact that public colour categories can alter discrimination and therefore cannot be equated with private qualitative identity."),
    SourceIdentity("CONSC-COGITATE-DATA-2025", "COGITATE Consortium", "https://cogitate-consortium.github.io/cogitate-data/02_overview/", "cogitate-data-overview.html", "open preregistered multimodal adversarial dataset", ("adversarial collaboration", "Experiment 1", "Experiment 2", "fMRI", "M-EEG", "iEEG")),
    SourceIdentity("CONSC-COGITATE-RESULT-2025", "Ferrante et al., Nature", "https://www.nature.com/articles/s41586-025-08888-1", "nature-s41586-025-08888-1.html", "primary preregistered adversarial theory comparison", ("adversarial collaboration", "preregistered", "participants", "functional magnetic resonance imaging", "magnetoencephalography"), "Preserves mixed and theory-adverse results instead of treating any established theory as the SFT law."),
)


FAMILY_SOURCE_IDS = {
    "observation_interior_observation": ("CONSC-NOREPORT-NETWORKS-2022", "CONSC-NOREPORT-CRITIQUE-2022"),
    "access_report_presence": ("CONSC-NOREPORT-NETWORKS-2022", "CONSC-NOREPORT-CRITIQUE-2022", "CONSC-COGITATE-RESULT-2025"),
    "binding_unity": ("CONSC-SPLIT-INTEGRATION-2023", "CONSC-SPLIT-BOUNDARY-2020", "CONSC-COGITATE-RESULT-2025"),
    "subject_perspective_interiority": ("CONSC-SPLIT-INTEGRATION-2023", "CONSC-NOREPORT-CRITIQUE-2022"),
    "self_observation_introspection": ("CONSC-CHOICE-BLINDNESS-2017",),
    "memory_temporal_identity": ("CONSC-DREAM-DATABASE-2025", "CONSC-ANESTHESIA-RECOVERY-2021"),
    "finite_self_model": ("CONSC-CHOICE-BLINDNESS-2017", "CONSC-COGITATE-DATA-2025"),
    "attention_availability": ("CONSC-ATTENTIONAL-BLINK-2014", "CONSC-NOREPORT-NETWORKS-2022"),
    "cognition_inference_representation": ("CONSC-ATTENTIONAL-BLINK-2014", "CONSC-COGITATE-DATA-2025"),
    "substrate_realization": ("CONSC-COGITATE-DATA-2025", "CONSC-COGITATE-RESULT-2025"),
    "qualia_resonance_composition": ("CONSC-SYNESTHESIA-BATTERY-2007", "CONSC-SYNESTHESIA-COLOUR-2026", "CONSC-COLOUR-CATEGORY-LEARNING-2010"),
    "red_of_red": ("CONSC-CIE-1931-CMF", "CONSC-SYNESTHESIA-BATTERY-2007", "CONSC-SYNESTHETIC-COLOUR-MATCH-2008", "CONSC-COLOUR-CATEGORY-LEARNING-2010"),
}


SOURCE_BY_ID = {item.source_id: item for item in SOURCES}
if len(SOURCE_BY_ID) != len(SOURCES):
    raise AssertionError("Consciousness external source identities repeat")
if {source_id for ids in FAMILY_SOURCE_IDS.values() for source_id in ids} - set(SOURCE_BY_ID):
    raise AssertionError("a Consciousness family source identity is unregistered")

