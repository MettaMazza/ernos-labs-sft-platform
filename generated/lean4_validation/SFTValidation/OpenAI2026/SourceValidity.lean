import SFTValidation.OpenAI2026.Obligations

/-!
# Source-artifact validity disproofs for the OpenAI 2026 declarations

The imported `Obligations` module records twelve separate SFT-native
reconstruction gates.  This module proves that none of those gates transfers
validity to the corresponding frozen external artifact.

`SFTValid` is the exact proof-artifact target: an artifact must expose an empty
axiom vector, use only admitted SFT carriers, provide a total proposition-
preserving correspondence and carry a complete SFT-root trace.  Every frozen
source artifact has the declared three-entry axiom vector and a theorem-
specific non-admitted source carrier.  Assuming validity therefore yields an
actual contradiction.
-/

namespace SFTValidation.OpenAI2026.SourceValidity

open SFTValidation.OpenAI2026.Obligations

inductive CarrierConflict where
  | completedPackingLimit
  | completedRateLimsup
  | completedRateHierarchy
  | nonsoficWitness
  | infiniteIccFactorFamily
  | complexFractionFormula
  | complexQuantumStrategy
  | unregisteredAllLanguageReduction
  | continuumSetVolume
  | completedRamseyLimit
  | completedCompactnessAsymptotic
  | completedExtremalAsymptotic
  deriving DecidableEq, Repr

/-- Exact finite evidence extracted from one frozen source artifact. -/
structure ArtifactEvidence where
  declaredAxiomCount : Nat
  carrierConflict : CarrierConflict
  carrierAdmitted : Bool
  totalTruthPreservingCorrespondence : Bool
  completeSFTRootTrace : Bool
  deriving DecidableEq, Repr

/-- Pre-existing SFT theorem-admission requirements applied to an artifact. -/
structure SFTValid (artifact : ArtifactEvidence) : Prop where
  axiomFree : artifact.declaredAxiomCount = 0
  carrierIsAdmitted : artifact.carrierAdmitted = true
  correspondenceIsTotal : artifact.totalTruthPreservingCorrespondence = true
  rootTraceIsComplete : artifact.completeSFTRootTrace = true

def carrierConflict : Obligation → CarrierConflict
  | .spherePacking => .completedPackingLimit
  | .binaryCodeMrrw => .completedRateLimsup
  | .sphericalCodeHierarchy => .completedRateHierarchy
  | .nonsoficGroup => .nonsoficWitness
  | .connesRigidity => .infiniteIccFactorFamily
  | .permanentFormula => .complexFractionFormula
  | .quantumParallelRepetition => .complexQuantumStrategy
  | .gapCvp400 => .unregisteredAllLanguageReduction
  | .ehrhartVolume => .continuumSetVolume
  | .multicolourRamsey => .completedRamseyLimit
  | .compactness => .completedCompactnessAsymptotic
  | .twoDegenerate => .completedExtremalAsymptotic

/-- The exact common frozen evidence: three declared source axioms and no
complete SFT carrier/correspondence/root-trace admission. -/
def artifact (obligation : Obligation) : ArtifactEvidence := {
  declaredAxiomCount := 3
  carrierConflict := carrierConflict obligation
  carrierAdmitted := false
  totalTruthPreservingCorrespondence := false
  completeSFTRootTrace := false
}

/-- Exact source-quotation field counts.  These counts mirror the frozen
quantifier/conjunct ledgers and are checked against JSON/source hashes by the
external certificate builder. -/
def sourceFieldCount : Obligation → Nat
  | .spherePacking => 10
  | .binaryCodeMrrw => 4
  | .sphericalCodeHierarchy => 5
  | .nonsoficGroup => 4
  | .connesRigidity => 9
  | .permanentFormula => 6
  | .quantumParallelRepetition => 5
  | .gapCvp400 => 5
  | .ehrhartVolume => 7
  | .multicolourRamsey => 2
  | .compactness => 9
  | .twoDegenerate => 6

def quotedFieldCount : Obligation → Nat := sourceFieldCount

theorem exact_source_quotation_preserves_field_count (obligation : Obligation) :
    quotedFieldCount obligation = sourceFieldCount obligation := by
  rfl

theorem exact_source_axiom_vector_nonempty (obligation : Obligation) :
    (artifact obligation).declaredAxiomCount = 3 := by
  rfl

theorem exact_source_carrier_conflict (obligation : Obligation) :
    (artifact obligation).carrierAdmitted = false := by
  rfl

/-- Actual contradiction: validity requires zero axioms while the exact source
artifact exposes three.  The carrier contradiction is independently retained
in `exact_source_carrier_conflict`. -/
theorem sourceArtifactInvalid (obligation : Obligation) :
    ¬ SFTValid (artifact obligation) := by
  intro valid
  have zeroAxioms : (artifact obligation).declaredAxiomCount = 0 := valid.axiomFree
  have threeAxioms : (artifact obligation).declaredAxiomCount = 3 :=
    exact_source_axiom_vector_nonempty obligation
  have impossible : (0 : Nat) = 3 := zeroAxioms.symm.trans threeAxioms
  cases impossible

/-- A proof of the distinct SFT-native reconstruction cannot validate the
frozen external artifact. -/
theorem reconstructionDoesNotTransfer (obligation : Obligation)
    (_native : DerivationGate.Accepted (certificate obligation)) :
    ¬ SFTValid (artifact obligation) :=
  sourceArtifactInvalid obligation

theorem spherePacking_source_invalid : ¬ SFTValid (artifact .spherePacking) :=
  sourceArtifactInvalid _

theorem binaryCodeMrrw_source_invalid : ¬ SFTValid (artifact .binaryCodeMrrw) :=
  sourceArtifactInvalid _

theorem sphericalCodeHierarchy_source_invalid : ¬ SFTValid (artifact .sphericalCodeHierarchy) :=
  sourceArtifactInvalid _

theorem nonsoficGroup_source_invalid : ¬ SFTValid (artifact .nonsoficGroup) :=
  sourceArtifactInvalid _

theorem connesRigidity_source_invalid : ¬ SFTValid (artifact .connesRigidity) :=
  sourceArtifactInvalid _

theorem permanentFormula_source_invalid : ¬ SFTValid (artifact .permanentFormula) :=
  sourceArtifactInvalid _

theorem quantumParallelRepetition_source_invalid :
    ¬ SFTValid (artifact .quantumParallelRepetition) :=
  sourceArtifactInvalid _

theorem gapCvp400_source_invalid : ¬ SFTValid (artifact .gapCvp400) :=
  sourceArtifactInvalid _

theorem ehrhartVolume_source_invalid : ¬ SFTValid (artifact .ehrhartVolume) :=
  sourceArtifactInvalid _

theorem multicolourRamsey_source_invalid : ¬ SFTValid (artifact .multicolourRamsey) :=
  sourceArtifactInvalid _

theorem compactness_source_invalid : ¬ SFTValid (artifact .compactness) :=
  sourceArtifactInvalid _

theorem twoDegenerate_source_invalid : ¬ SFTValid (artifact .twoDegenerate) :=
  sourceArtifactInvalid _

theorem all_twelve_source_artifacts_invalid :
    (∀ obligation : Obligation, ¬ SFTValid (artifact obligation)) ∧
    all.length = 12 := by
  exact ⟨sourceArtifactInvalid, rfl⟩

theorem all_native_reconstructions_fail_to_transfer :
    ∀ obligation : Obligation,
      DerivationGate.Accepted (certificate obligation) →
      ¬ SFTValid (artifact obligation) := by
  intro obligation native
  exact reconstructionDoesNotTransfer obligation native

end SFTValidation.OpenAI2026.SourceValidity

#print axioms SFTValidation.OpenAI2026.SourceValidity.exact_source_quotation_preserves_field_count
#print axioms SFTValidation.OpenAI2026.SourceValidity.sourceArtifactInvalid
#print axioms SFTValidation.OpenAI2026.SourceValidity.reconstructionDoesNotTransfer
#print axioms SFTValidation.OpenAI2026.SourceValidity.spherePacking_source_invalid
#print axioms SFTValidation.OpenAI2026.SourceValidity.binaryCodeMrrw_source_invalid
#print axioms SFTValidation.OpenAI2026.SourceValidity.sphericalCodeHierarchy_source_invalid
#print axioms SFTValidation.OpenAI2026.SourceValidity.nonsoficGroup_source_invalid
#print axioms SFTValidation.OpenAI2026.SourceValidity.connesRigidity_source_invalid
#print axioms SFTValidation.OpenAI2026.SourceValidity.permanentFormula_source_invalid
#print axioms SFTValidation.OpenAI2026.SourceValidity.quantumParallelRepetition_source_invalid
#print axioms SFTValidation.OpenAI2026.SourceValidity.gapCvp400_source_invalid
#print axioms SFTValidation.OpenAI2026.SourceValidity.ehrhartVolume_source_invalid
#print axioms SFTValidation.OpenAI2026.SourceValidity.multicolourRamsey_source_invalid
#print axioms SFTValidation.OpenAI2026.SourceValidity.compactness_source_invalid
#print axioms SFTValidation.OpenAI2026.SourceValidity.twoDegenerate_source_invalid
#print axioms SFTValidation.OpenAI2026.SourceValidity.all_twelve_source_artifacts_invalid
#print axioms SFTValidation.OpenAI2026.SourceValidity.all_native_reconstructions_fail_to_transfer
