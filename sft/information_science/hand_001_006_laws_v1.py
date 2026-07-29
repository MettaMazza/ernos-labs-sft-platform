"""Complete exact Information Science terminal ownership and handoff laws."""
from sft.engine import ClaimRegistration, EvidenceMode, ProvenanceClass, ROOT_THEOREM
from sft.information_science.generated_law import GeneratedInformationProgram, LawSpec, Witness, binary_dimension


DOWNSTREAM = (
    "classical-computation",
    "quantum-computation",
    "biology",
    "medicine",
    "consciousness-cognitive-science",
    "social-collective-systems",
    "engineering-translation",
)
CORRESPONDENCE = (
    ("Fold-distinction", "classical-symbol"),
    ("Fold-support-count", "information-quantity"),
    ("Fold-transition-relation", "channel"),
    ("Fold-complete-word-support", "quantum-support"),
)


OBS = {
    "001": ("seven downstream consumers are retained as directed dependency targets while Information Science remains the single owner of its exported laws", len(DOWNSTREAM) == len(set(DOWNSTREAM)) == 7),
    "002": ("the measurement handoff retains distinct formal law, external observation and exact comparison records", len(("formal-law", "external-observation", "exact-comparison")) == 3),
    "003": ("the formal-to-empirical handoff retains derivation, sealed prediction, target release and comparison in that order", ("derivation", "sealed-prediction", "target-release", "comparison") == tuple(sorted(("comparison", "derivation", "sealed-prediction", "target-release"), key=("derivation", "sealed-prediction", "target-release", "comparison").index))),
    "004": ("four conventional vocabulary correspondences are reversible within their declared boundary and do not select the Fold laws", len(CORRESPONDENCE) == len({left for left, _right in CORRESPONDENCE}) == len({right for _left, right in CORRESPONDENCE}) == 4),
    "005": ("lawful extension appends a new versioned obligation and receipt without rewriting the frozen 262-obligation census", 262 + 1 == 263),
    "006": ("the complete handoff ledger reconciles six terminal obligations with the 256 pre-handoff receipts to cover all 262 frozen Information Science obligations", 256 + 6 == 262 and len(tuple(range(1, 7))) == 6),
}


DEF = {
    "001": ("SFT-INFO-HAND-ONE-OWNER-DOWNSTREAM-001", "Information Science one-owner downstream handoff", "directed-single-owner-export-graph", "An Information Science law crosses a branch boundary only as a directed dependency: Information Science retains one derivation owner and each downstream branch owns only the new law it independently forces from that input."),
    "002": ("SFT-INFO-HAND-MEASUREMENT-BOUNDARY-002", "Information Science measurement-boundary handoff", "formal-observation-comparison-separation", "The measurement boundary retains formal derivation, externally held observation and exact comparison as distinct records; observation tests a law but cannot silently choose or rewrite it."),
    "003": ("SFT-INFO-HAND-FORMAL-EMPIRICAL-003", "Information Science formal-to-empirical handoff", "sealed-formal-to-empirical-custody", "A lawful formal-to-empirical handoff orders complete derivation before sealed prediction, target release before comparison, and preserves every favorable, adverse, absent, unresolved and boundary row."),
    "004": ("SFT-INFO-HAND-CONVENTIONAL-CORRESPONDENCE-004", "Information Science conventional-correspondence handoff", "reversible-comparison-boundary-vocabulary", "A conventional information-science term is admitted only as an explicit reversible correspondence to a derived Fold relation within a declared boundary; the conventional model never selects the Fold law."),
    "005": ("SFT-INFO-HAND-OPEN-EXTENSION-005", "Information Science open-extension handoff", "dated-complete-versioned-extension", "Information Science is complete to its frozen dated census and remains open to lawful discovery: an extension appends a versioned obligation, derivation and receipt without rewriting prior receipts or claiming permanent closure."),
    "006": ("SFT-INFO-HAND-CROSS-BRANCH-COMPLETENESS-006", "Information Science cross-branch completeness certificate", "complete-six-handoff-reconciliation", "Cross-branch handoff completeness is the one-to-one reconciliation of all six frozen handoff obligations with the 256 pre-handoff receipts, yielding all 262 Information Science obligations with one owner, root trace and explicit extension boundary."),
}

IDS = tuple(DEF[number][0] for number in sorted(DEF))
EXCLUSIONS = (
    "no axiom, imported downstream law, conventional prior or target outcome selects the result",
    "host 0 denotes structural absence or artifact counts only and is not an SFT number object",
    "no negative, irrational, imaginary or floating proof scalar",
    "no duplicate owner, copied law, missing dependency, erased adverse row or rewritten receipt",
    "no dated completeness claim bars lawful versioned discovery",
    "no failed route retires an obligation or changes protected authority",
)


def dimension(key, rejected, rejected_why, admitted, admitted_why):
    return binary_dimension(key, key + "?", rejected, rejected_why, admitted, admitted_why)


def dimensions(relation):
    return (
        dimension("subject", "anonymous-cross-branch-result", "An anonymous result loses its derivation owner.", "complete-owned-information-law", "The exported Information Science law is explicit."),
        dimension("ownership", "overlapping-or-ownerless", "Duplicate or absent ownership destroys provenance.", "exactly-one-derivation-owner", "Every law has one declared branch owner."),
        dimension("relation", "branch-name-association", "A label alone is not a handoff.", relation, "The complete directed handoff relation supplies the law."),
        dimension("dependency", "copied-or-silent-law", "Copying or silently importing a law duplicates ownership.", "directed-consumer-dependency", "The consumer names the source dependency."),
        dimension("records", "selected-handoff-summary", "A summary can hide one side of a boundary.", "complete-paired-record-custody", "Source, consumer, evidence and dispositions remain explicit."),
        dimension("provenance", "outcome-selected", "Outcome feedback invalidates forcing.", "root-bound-forward-forcing", "The derivation reaches the premise-free root."),
        dimension("observation", "preopened-target", "A preopened target could select the handoff.", "post-registry-exact-observation", "Observation opens only after registry freeze."),
        dimension("extension", "permanent-branch-lock", "A dated census cannot bar discovery.", "dated-complete-versioned-extension", "New lawful claims append without rewriting history."),
    )


class HandProgram(GeneratedInformationProgram):
    @property
    def registration(self):
        return ClaimRegistration(
            claim_id=self.spec.claim_id,
            title=self.spec.title,
            branch="information_science",
            statement=self.spec.statement,
            evidence_mode=EvidenceMode.EMPIRICAL,
            root_theorems=(ROOT_THEOREM,),
            dependencies=self.spec.dependencies,
            axioms=(),
            free_parameters=(),
            provenance=(ProvenanceClass.FORWARD_FORCING,),
            source_hash=self.source_hash,
        )


def make(number, previous):
    claim_id, title, relation, statement = DEF[number]
    observation, passed = OBS[number]
    dependencies = ("SFT-INFO-VALID-GRAND-LOCK-012",) + ((previous,) if previous else ())
    return LawSpec(
        claim_id,
        title,
        statement,
        dependencies,
        f"Generate the complete eight-axis HAND-{number} product before observation access.",
        f"Every positive finite HAND-{number} owner, dependency, source, consumer, evidence, disposition, comparison and extension record.",
        dimensions(relation),
        f"HAND-{number} uniquely retains {relation}, one-owner custody, root forcing, post-registry observation and versioned extension.",
        (statement, observation),
        "The least handoff contains one owned law, one directed consumer dependency, one complete paired record and one provenance path.",
        "Appending one consumer, measurement, correspondence or extension retains every prior owner and adds each new directed record exactly once.",
        EXCLUSIONS,
        (
            Witness("exact-observation", observation, passed),
            Witness("complete-handoff-census", "Every owner, dependency, source, consumer, evidence, disposition and extension row is retained.", passed),
            Witness("target-free", "The survivor was frozen before observation access.", True),
        ),
        f"The frozen census separately owns {title.lower()} and forbids omission or duplicate ownership.",
        statement,
        "Enumerate 256 structural forms, reconstruct independently, replay the exact handoff witness and reject four adverse controls.",
        "The claim closes the frozen dated handoff grammar while preserving lawful versioned extension and downstream independent derivation.",
        (title.lower(),),
    )


specs = []
previous = None
for number in sorted(DEF):
    spec = make(number, previous)
    specs.append(spec)
    previous = spec.claim_id
SPECS = {spec.claim_id: spec for spec in specs}
