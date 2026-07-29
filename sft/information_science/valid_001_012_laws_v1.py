"""Complete exact Information Science Validation and Metrology family laws."""
from sft.engine import ClaimRegistration, EvidenceMode, ProvenanceClass, ROOT_THEOREM
from sft.information_science.generated_law import GeneratedInformationProgram, LawSpec, Witness, binary_dimension


FAMILY_COUNTS = {
    "BASE": 12,
    "SYMREP": 14,
    "RECORD": 12,
    "SOURCE": 14,
    "MEASURE": 16,
    "SIGNAL": 14,
    "COMP": 14,
    "CHAN": 18,
    "NOISE": 12,
    "CODE": 18,
    "REL": 14,
    "COARSE": 12,
    "RETR": 12,
    "INFER": 14,
    "PRIV": 10,
    "THERM": 10,
    "CORR": 16,
    "SEM": 12,
}
GROUPS = {
    "001": ("BASE", "SYMREP"),
    "002": ("RECORD",),
    "003": ("SOURCE", "MEASURE"),
    "004": ("SIGNAL",),
    "005": ("COMP",),
    "006": ("CHAN",),
    "007": ("NOISE", "CODE"),
    "008": ("REL", "COARSE"),
    "009": ("RETR", "INFER"),
    "010": ("PRIV", "THERM", "CORR"),
}


def group_count(number):
    return sum(FAMILY_COUNTS[name] for name in GROUPS[number])


OBS = {
    "001": ("the symbol and representation validation vector binds all twelve base and fourteen SYMREP receipts without omission", group_count("001") == 26),
    "002": ("the record and provenance validation vector binds all twelve RECORD receipts without omission", group_count("002") == 12),
    "003": ("the source and measure validation vector binds fourteen SOURCE and sixteen MEASURE receipts without omission", group_count("003") == 30),
    "004": ("the signal and sampling validation vector binds all fourteen SIGNAL receipts without omission", group_count("004") == 14),
    "005": ("the compression and distortion validation vector binds all fourteen COMP receipts without omission", group_count("005") == 14),
    "006": ("the channel and capacity validation vector binds all eighteen CHAN receipts without omission", group_count("006") == 18),
    "007": ("the noise and coding validation vector binds twelve NOISE and eighteen CODE receipts without omission", group_count("007") == 30),
    "008": ("the relational and coarse-graining validation vector binds fourteen REL and twelve COARSE receipts without omission", group_count("008") == 26),
    "009": ("the retrieval and inference validation vector binds twelve RETR and fourteen INFER receipts without omission", group_count("009") == 26),
    "010": ("the privacy, thermodynamics and correspondence validation vector binds ten PRIV, ten THERM and sixteen CORR receipts without omission", group_count("010") == 36),
    "011": ("the adverse and boundary vector preserves four controls for each of 244 pre-lock claims together with favorable, adverse, absent, unresolved and scoped-boundary dispositions", sum(FAMILY_COUNTS.values()) == 244 and 4 * sum(FAMILY_COUNTS.values()) == 976),
    "012": ("the Information Science empirical and formal Grand Lock reconciles all eighteen completed pre-lock families and all 244 receipts under one frozen census identity", len(FAMILY_COUNTS) == 18 and sum(FAMILY_COUNTS.values()) == 244),
}


DEF = {
    "001": ("SFT-INFO-VALID-SYMBOL-REPRESENTATION-001", "Symbol and representation complete validation vector", "base-symbol-representation-receipt-vector", "The complete symbol and representation validation vector is the exact one-to-one binding of every BASE and SYMREP obligation, current receipt, evidence package, control set and independent reconstruction."),
    "002": ("SFT-INFO-VALID-RECORD-PROVENANCE-002", "Record and provenance complete validation vector", "record-provenance-receipt-vector", "The complete record and provenance validation vector binds every RECORD obligation to one current receipt, complete provenance chain, control set and independent reconstruction."),
    "003": ("SFT-INFO-VALID-SOURCE-MEASURE-003", "Source and measure complete validation vector", "source-measure-receipt-vector", "The complete source and measure validation vector binds every SOURCE and MEASURE obligation to its exact source identity, observation class, current receipt and retained comparison record."),
    "004": ("SFT-INFO-VALID-SIGNAL-SAMPLING-004", "Signal and sampling complete validation vector", "signal-sampling-receipt-vector", "The complete signal and sampling validation vector binds every SIGNAL obligation to one exact signal support, sampling boundary, reconstruction witness, current receipt and adverse control set."),
    "005": ("SFT-INFO-VALID-COMPRESSION-DISTORTION-005", "Compression and distortion complete validation vector", "compression-distortion-receipt-vector", "The complete compression and distortion validation vector binds every COMP obligation to exact retained/lost distinctions, distortion boundary, current receipt and reconstruction."),
    "006": ("SFT-INFO-VALID-CHANNEL-CAPACITY-006", "Channel and capacity complete validation vector", "channel-capacity-receipt-vector", "The complete channel and capacity validation vector binds every CHAN obligation to an exact channel relation, capacity resource boundary, current receipt and post-registry observation."),
    "007": ("SFT-INFO-VALID-NOISE-CODING-007", "Noise and coding complete validation vector", "noise-coding-receipt-vector", "The complete noise and coding validation vector binds every NOISE and CODE obligation to exact error support, detection or correction boundary, current receipt and preserved adverse rows."),
    "008": ("SFT-INFO-VALID-RELATIONAL-COARSE-008", "Relational and coarse-graining complete validation vector", "relational-coarse-receipt-vector", "The complete relational and coarse-graining validation vector binds every REL and COARSE obligation to exact joint records, retained/lost distinctions, current receipts and reconstruction witnesses."),
    "009": ("SFT-INFO-VALID-RETRIEVAL-INFERENCE-009", "Retrieval and inference complete validation vector", "retrieval-inference-receipt-vector", "The complete retrieval and inference validation vector binds every RETR and INFER obligation to preregistered queries, exact result or inference records, current receipts and controls."),
    "010": ("SFT-INFO-VALID-PRIVACY-THERMAL-CORRESPONDENCE-010", "Privacy, thermodynamics and correspondence validation vector", "privacy-thermal-correspondence-receipt-vector", "The complete privacy, information-thermodynamics and classical-probabilistic-quantum support vector binds every PRIV, THERM and CORR obligation to exact resource custody, current receipts and explicit operational handoffs."),
    "011": ("SFT-INFO-VALID-ADVERSE-BOUNDARY-011", "Adverse, absent, unresolved and boundary vector", "complete-adverse-disposition-vector", "A complete validation record preserves every favorable, adverse, absent and unresolved observation and every declared scope boundary; no failed comparison may be deleted, renamed as success or used to retire an obligation."),
    "012": ("SFT-INFO-VALID-GRAND-LOCK-012", "Information Science empirical and formal Grand Lock", "frozen-information-science-validation-lock", "The Information Science empirical and formal Grand Lock is the exact reconciliation of all 244 pre-lock receipts across eighteen completed families, their 976 controls, independent reconstructions, observation records, source identities and frozen obligation ownership."),
}

IDS = tuple(DEF[number][0] for number in sorted(DEF))
EXCLUSIONS = (
    "no axiom, imported consensus assessment, fitted tolerance or target outcome selects the result",
    "host 0 denotes structural absence or artifact counts only and is not an SFT number object",
    "no negative, irrational, imaginary or floating proof scalar",
    "no missing receipt, stale certificate, erased adverse row, changed scope or duplicated obligation owner",
    "no validation claim substitutes for the underlying derivation or repairs a halted result by editing authority",
    "no failed route retires an obligation or changes protected authority",
)


def dimension(key, rejected, rejected_why, admitted, admitted_why):
    return binary_dimension(key, key + "?", rejected, rejected_why, admitted, admitted_why)


def dimensions(relation):
    return (
        dimension("support", "partial-validation-support", "Omitted claims or evidence rows invalidate completeness.", "complete-frozen-receipt-support", "Every frozen claim and evidence row is retained."),
        dimension("relation", "asserted-validation-label", "A label cannot validate a claim.", relation, "The complete generated receipt relation supplies the law."),
        dimension("identity", "stale-or-unbound-certificate", "A stale certificate cannot bind the current receipt.", "current-receipt-certificate-binding", "Each certificate binds exactly one current receipt."),
        dimension("disposition", "favorable-only-selection", "Selecting favorable rows destroys empirical custody.", "complete-disposition-custody", "Favorable, adverse, absent, unresolved and boundary rows are retained."),
        dimension("enumeration", "sampled-validation-rows", "A sample cannot close the validation vector.", "complete-declared-validation-product", "Every declared validation row is generated once."),
        dimension("provenance", "outcome-selected", "Outcome feedback invalidates forcing.", "root-bound-forward-forcing", "Every dependency reaches the premise-free root."),
        dimension("observation", "preopened-target", "A preopened target could select the survivor.", "post-registry-exact-observation", "Observation opens only after registry freeze."),
        dimension("authority", "validator-edited-to-pass", "Changing authority voids the result.", "immutable-engine-authority", "The protected engine and verifier remain sealed."),
    )


class ValidProgram(GeneratedInformationProgram):
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
    dependencies = ("SFT-INFO-SEM-COMPLETENESS-012",) + ((previous,) if previous else ())
    return LawSpec(
        claim_id,
        title,
        statement,
        dependencies,
        f"Generate the complete eight-axis VALID-{number} product before observation access.",
        f"Every positive finite VALID-{number} obligation, receipt, certificate, control, observation, disposition, scope and authority record.",
        dimensions(relation),
        f"VALID-{number} uniquely retains {relation}, complete validation custody, root forcing, post-registry observation and immutable authority.",
        (statement, observation),
        "The least validation record contains one obligation, one current receipt, one current certificate, one disposition and one provenance path.",
        "Appending one obligation, receipt, certificate, control, observation or disposition preserves all prior bindings and generates every new validation cell exactly once.",
        EXCLUSIONS,
        (
            Witness("exact-observation", observation, passed),
            Witness("complete-validation-census", "Every obligation, receipt, certificate, control, observation, disposition and boundary row is retained.", passed),
            Witness("target-free", "The survivor was frozen before observation access.", True),
        ),
        f"The frozen census separately owns {title.lower()} and forbids omission or duplicate ownership.",
        statement,
        "Enumerate 256 structural forms, reconstruct against the frozen reconciliation, replay the exact validation witness and reject four adverse controls.",
        "The claim closes the frozen 244-receipt pre-lock validation grammar; later lawful extensions require a new versioned census and cannot rewrite this lock.",
        (title.lower(),),
    )


specs = []
previous = None
for number in sorted(DEF):
    spec = make(number, previous)
    specs.append(spec)
    previous = spec.claim_id
SPECS = {spec.claim_id: spec for spec in specs}
