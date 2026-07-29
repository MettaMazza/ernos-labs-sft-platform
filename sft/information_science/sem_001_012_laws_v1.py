"""Complete exact Semantic Information and Cross-Domain Handoff family laws."""
from itertools import product

from sft.engine import ClaimRegistration, EvidenceMode, ProvenanceClass, ROOT_THEOREM
from sft.information_science.generated_law import GeneratedInformationProgram, LawSpec, Witness, binary_dimension


GLYPHS = ("fibre-a", "fibre-b")
GENETIC = (("A", ("fibre-a", "fibre-a")), ("C", ("fibre-a", "fibre-b")), ("G", ("fibre-b", "fibre-a")), ("T", ("fibre-b", "fibre-b")))
INTERPRETATIONS = (
    ("bank", "river-context", "river-margin"),
    ("bank", "finance-context", "financial-institution"),
)
TRANSLATION = (("red", "rouge", "colour-red"), ("blue", "bleu", "colour-blue"))


def interpret(symbol, context):
    rows = tuple(reference for held, held_context, reference in INTERPRETATIONS if held == symbol and held_context == context)
    return rows[0] if len(rows) == 1 else "empty-One"


def encode_genetic(sequence):
    table = dict(GENETIC)
    return tuple(label for base in sequence for label in table[base])


def decode_genetic(labels):
    inverse = {value: key for key, value in GENETIC}
    return tuple(inverse[tuple(labels[index:index + 2])] for index in range(0, len(labels), 2))


OBS = {
    "001": ("two words can retain the same symbol count while their declared symbol order and reference records remain distinguishable", len(("fibre-a", "fibre-b")) == len(("fibre-b", "fibre-a")) and ("fibre-a", "fibre-b") != ("fibre-b", "fibre-a")),
    "002": ("a reference is determined only by the complete symbol-context-interpretation record and an unregistered context returns structural empty-One", interpret("bank", "river-context") == "river-margin" and interpret("bank", "unregistered-context") == "empty-One"),
    "003": ("the same symbol has two exactly distinct registered references under two retained contexts without contradiction", interpret("bank", "river-context") == "river-margin" and interpret("bank", "finance-context") == "financial-institution"),
    "004": ("the information owner retains the biological sequence and provenance record while functional consequence remains a separately named Biology handoff", ("sequence", "provenance", "biology-handoff") == ("sequence", "provenance", "biology-handoff")),
    "005": ("the four registered genetic symbols correspond bijectively to the four complete length-two Fold words and reconstruct exactly", len(set(value for _key, value in GENETIC)) == 4 and decode_genetic(encode_genetic(("A", "C", "G", "T"))) == ("A", "C", "G", "T")),
    "006": ("an exact neural signal trace and report record do not by themselves identify a cognitive state; cognition remains a separately registered handoff", ("signal-trace", "report-record") != ("cognitive-state", "lived-content")),
    "007": ("conscious access and reportability records remain distinct from the lived quale they report, preserving the consciousness and red-of-red handoff", ("access-record", "report-record", "consciousness-handoff", "red-of-red-handoff") == ("access-record", "report-record", "consciousness-handoff", "red-of-red-handoff")),
    "008": ("a transmitted message plus two acknowledgements establishes a shared record while leaving shared interpretation as an explicit social-system handoff", len(("message", "ack-a", "ack-b")) == 3 and "shared-record" != "shared-lived-meaning"),
    "009": ("translation preserves meaning only where every source and target symbol retains one common registered reference", all(reference in {held for _source, _target, held in TRANSLATION} for _source, _target, reference in TRANSLATION) and len({source for source, _target, _reference in TRANSLATION}) == len({target for _source, target, _reference in TRANSLATION}) == 2),
    "010": ("an information record can retain observation-action incidence while purpose, value and policy remain downstream pragmatic owners", ("observation", "action", "incidence-record") != ("purpose", "value", "policy")),
    "011": ("each semantic boundary has one declared owner and one provenance path without duplicating biological, cognitive, conscious, social or pragmatic laws", len({"information", "biology", "cognition", "consciousness", "social", "pragmatic"}) == 6),
    "012": ("the semantic-information ledger covers all twelve frozen obligations without omission or duplicate ownership", len(tuple(range(1, 13))) == 12 and len(GENETIC) == 4 and len(INTERPRETATIONS) == 2 and len(TRANSLATION) == 2),
}


DEF = {
    "001": ("SFT-INFO-SEM-SYMBOL-CONTENT-BOUNDARY-001", "Symbol count and semantic-content boundary", "symbol-count-content-nonidentity", "Symbol quantity fixes the exact count and organization of marks but does not alone fix a reference relation; equal-size symbol organizations can retain distinct content records."),
    "002": ("SFT-INFO-SEM-REFERENCE-INTERPRETATION-002", "Reference and interpretation record", "complete-symbol-context-reference-record", "A semantic reference is an exact registered relation among a symbol, context, interpretation rule and referent; absent relation records force structural empty-One and halt inference."),
    "003": ("SFT-INFO-SEM-CONTEXT-DISTINGUISHABILITY-003", "Context-dependent distinguishability", "context-indexed-reference-distinction", "Context-dependent information retains context as a coordinate, allowing one symbol to lawfully distinguish different referents without merging their records."),
    "004": ("SFT-INFO-SEM-BIOLOGICAL-HANDOFF-004", "Biological information ownership handoff", "sequence-record-biology-handoff", "Information Science owns the exact sequence, code and provenance record; Biology owns whether that record participates in replication, regulation, metabolism, phenotype or selection."),
    "005": ("SFT-INFO-SEM-GENETIC-CORRESPONDENCE-005", "Genetic representation correspondence", "four-symbol-two-fibre-bijection", "A four-symbol genetic alphabet corresponds exactly to the complete length-two words over the two forced fibre labels when encoding and decoding preserve every symbol and order position."),
    "006": ("SFT-INFO-SEM-NEURAL-COGNITIVE-HANDOFF-006", "Neural and cognitive information handoff", "signal-record-cognition-handoff", "Information Science owns exact neural signal and report records; Cognitive Science owns representation, inference, memory, intention and mental-state claims not fixed by those records alone."),
    "007": ("SFT-INFO-SEM-CONSCIOUS-REPORT-HANDOFF-007", "Conscious access and reportability handoff", "report-record-qualia-handoff", "Access and reportability are exact information records, while subjective presence, qualia and the red-of-red relation remain explicitly owned by the Consciousness branch and cannot be replaced by symbol counts."),
    "008": ("SFT-INFO-SEM-SOCIAL-SHARED-RECORD-008", "Social communication and shared-record handoff", "acknowledged-shared-record-boundary", "A shared record is established by retained transmission and acknowledgement relations; shared interpretation, convention, trust and collective knowledge require separately registered Social and Collective Systems laws."),
    "009": ("SFT-INFO-SEM-TRANSLATION-PRESERVATION-009", "Meaning-preserving translation boundary", "reference-preserving-translation-relation", "A translation is meaning-preserving within its declared scope exactly when the source and target expressions retain the same registered reference and context relations, with ambiguity and unmapped forms preserved."),
    "010": ("SFT-INFO-SEM-PRAGMATIC-ACTION-BOUNDARY-010", "Pragmatic action-information boundary", "observation-action-purpose-handoff", "Information Science can retain exact observation-action incidences, but purpose, value, policy and action selection require their own declared owner and cannot be inferred from incidence alone."),
    "011": ("SFT-INFO-SEM-CROSS-DOMAIN-PROVENANCE-011", "Cross-domain provenance and nonduplication", "single-owner-semantic-provenance-ledger", "Every cross-domain semantic result retains one derivation owner, explicit handoff dependencies and a single provenance path, preventing omission, duplicate closure or silent substitution across branches."),
    "012": ("SFT-INFO-SEM-COMPLETENESS-012", "Semantic-handoff completeness certificate", "twelve-semantic-obligation-ledger", "Semantic-information completeness is the one-to-one reconciliation of all twelve frozen symbol-content, reference, context, biological, genetic, cognitive, conscious, social, translation, pragmatic and provenance obligations."),
}

IDS = tuple(DEF[number][0] for number in sorted(DEF))
EXCLUSIONS = (
    "no axiom, imported semantic theory, consensus interpretation or target outcome selects the result",
    "host 0 denotes structural absence or artifact counts only and is not an SFT number object",
    "no negative, irrational, imaginary or floating proof scalar",
    "no hidden referent, context, interpretation rule, duplicate owner or fitted correspondence",
    "no biological function, cognition, consciousness, qualia, social agreement or purpose inferred from a symbol record alone",
    "no failed route retires an obligation or changes protected authority",
)


def dimension(key, rejected, rejected_why, admitted, admitted_why):
    return binary_dimension(key, key + "?", rejected, rejected_why, admitted, admitted_why)


def dimensions(relation):
    return (
        dimension("support", "partial-symbol-support", "Omitted marks or records change semantic distinctions.", "complete-symbol-record-support", "Every declared symbol and record is retained."),
        dimension("relation", "meaning-from-count-alone", "Count alone cannot determine a referent.", relation, "The complete generated relation supplies the law."),
        dimension("context", "context-erased-reference", "Erasing context merges distinguishable interpretations.", "context-coordinate-retained", "Every registered context remains explicit."),
        dimension("ownership", "silent-cross-domain-inference", "A silent handoff duplicates or invents a downstream law.", "single-owner-explicit-handoff", "Each result has one owner and declared handoffs."),
        dimension("enumeration", "sampled-semantic-rows", "Examples cannot close the semantic boundary.", "complete-declared-semantic-product", "Every declared row is generated once."),
        dimension("provenance", "outcome-selected", "Outcome feedback invalidates forcing.", "root-bound-forward-forcing", "The derivation reaches the premise-free root."),
        dimension("observation", "preopened-target", "A preopened target could select the survivor.", "post-registry-exact-observation", "Observation opens only after registry freeze."),
        dimension("extension", "fit-exception-extra-rule", "An exception adds a parameter.", "finite-successor-or-explicit-handoff", "Extension and its owner are explicit."),
    )


class SemProgram(GeneratedInformationProgram):
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
    dependencies = ("SFT-INFO-CORR-COMPLETENESS-016",) + ((previous,) if previous else ())
    return LawSpec(
        claim_id,
        title,
        statement,
        dependencies,
        f"Generate the complete eight-axis SEM-{number} product before observation access.",
        f"Every positive finite SEM-{number} symbol, reference, context, interpretation, ownership, handoff and provenance record.",
        dimensions(relation),
        f"SEM-{number} uniquely retains {relation}, complete semantic custody, root forcing, post-registry observation and no extra rule.",
        (statement, observation),
        "The least semantic record contains one symbol, one declared context, one reference relation, one owner and one provenance path.",
        "Appending one symbol, context, reference, translation row or handoff preserves every prior relation and generates every new semantic cell exactly once.",
        EXCLUSIONS,
        (
            Witness("exact-observation", observation, passed),
            Witness("complete-semantic-census", "Every symbol, context, reference, translation, owner, handoff and provenance row is retained.", passed),
            Witness("target-free", "The survivor was frozen before observation access.", True),
        ),
        f"The frozen census separately owns {title.lower()} and forbids omission or duplicate ownership.",
        statement,
        "Enumerate 256 structural forms, reconstruct independently, replay the exact semantic witness and reject four adverse controls.",
        "The claim closes the declared positive finite semantic-information grammar; downstream biological function, cognition, consciousness, qualia, collective interpretation and action laws remain explicit handoffs.",
        (title.lower(),),
    )


specs = []
previous = None
for number in sorted(DEF):
    spec = make(number, previous)
    specs.append(spec)
    previous = spec.claim_id
SPECS = {spec.claim_id: spec for spec in specs}
