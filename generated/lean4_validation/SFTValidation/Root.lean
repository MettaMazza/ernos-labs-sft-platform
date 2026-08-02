import Std

/-!
# Smithian Fold Theory operational root

This module formalizes the exact two-class operational boundary registered by
`SFT-ROOT-THERE-IS-NO-NOTHING`:

* no presentation supplies no operational counterexample;
* a presentation is an occurrence and therefore is not operational nothing.

The type has exactly these two constructors.  `survives` implements the
registered decision, and `uniqueSurvivor` proves that the presented-occurrence
class is the sole survivor.  The proof is closed and constructive.
-/

namespace SFTValidation.OperationalRoot

/-- The complete registered operational challenge partition. -/
inductive ChallengeClass where
  | unpresentedAbsence
  | presentedOccurrence
  deriving DecidableEq, Repr

/-- The registered operational forcing decision. -/
def survives : ChallengeClass → Bool
  | .unpresentedAbsence => false
  | .presentedOccurrence => true

/-- A presented challenge carries an identifiable occurrence. -/
structure Presentation where
  occurrenceIdentity : Unit

/-- Occurrence supplied by the act of presentation itself. -/
inductive Occurrence where
  | ofPresentation : Presentation → Occurrence

/-- The occurrence whose identity is supplied by a particular presentation. -/
def OccurrenceOf (presentation : Presentation) :=
  { occurrence : Occurrence // occurrence = Occurrence.ofPresentation presentation }

/-- Every presented operational challenge supplies an occurrence. -/
theorem presentationIsOccurrence : ∀ presentation : Presentation, Nonempty (OccurrenceOf presentation) := by
  intro presentation
  exact ⟨⟨Occurrence.ofPresentation presentation, rfl⟩⟩

/-- The unpresented-absence class cannot survive the operational boundary. -/
theorem unpresentedAbsenceRejected :
    survives .unpresentedAbsence = false := by
  rfl

/-- The presented-occurrence class survives the operational boundary. -/
theorem presentedOccurrenceSurvives :
    survives .presentedOccurrence = true := by
  rfl

/-- The two constructors exhaust the registered operational grammar. -/
theorem challengePartitionComplete (candidate : ChallengeClass) :
    candidate = .unpresentedAbsence ∨ candidate = .presentedOccurrence := by
  cases candidate <;> simp

/-- Closed proposition expressing one and only one surviving class. -/
def HasUniqueSurvivor : Prop :=
  ∃ candidate : ChallengeClass,
    survives candidate = true ∧
    ∀ other : ChallengeClass, survives other = true → other = candidate

/-- `presentedOccurrence` is the unique surviving operational class. -/
theorem uniqueSurvivor : HasUniqueSurvivor := by
  refine ⟨.presentedOccurrence, rfl, ?_⟩
  intro candidate candidateSurvives
  cases candidate with
  | unpresentedAbsence =>
      change false = true at candidateSurvives
      cases candidateSurvives
  | presentedOccurrence => rfl

/-- Closed exact result exported for the whole-model verification layer. -/
theorem rootExactResult :
    survives .presentedOccurrence = true ∧
    survives .unpresentedAbsence = false ∧
    HasUniqueSurvivor := by
  exact ⟨presentedOccurrenceSurvives, unpresentedAbsenceRejected, uniqueSurvivor⟩

end SFTValidation.OperationalRoot

#print axioms SFTValidation.OperationalRoot.presentationIsOccurrence
#print axioms SFTValidation.OperationalRoot.uniqueSurvivor
#print axioms SFTValidation.OperationalRoot.rootExactResult
