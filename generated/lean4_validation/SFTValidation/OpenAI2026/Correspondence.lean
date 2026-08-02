import Std

/-!
# Exact source/SFT correspondence primitives for the OpenAI 2026 obligations

This module supplies only the shared constructive machinery.  It does not
assert any of the twelve mathematical conclusions.  A theorem-specific module
must still provide its object encodings, predicate preservation and mathematical
proof or actual negation.

`GeneratedOrdinal.base` is the structural initial position corresponding to a
source `Nat` zero.  It is a constructor, not an SFT numerical-null scalar.
-/

namespace SFTValidation.OpenAI2026.Correspondence

/-- Structural initial position followed by indefinitely repeatable successor. -/
inductive GeneratedOrdinal where
  | base
  | next (predecessor : GeneratedOrdinal)
  deriving DecidableEq, Repr

def GeneratedOrdinal.toNat : GeneratedOrdinal → Nat
  | .base => 0
  | .next predecessor => predecessor.toNat + 1

def GeneratedOrdinal.ofNat : Nat → GeneratedOrdinal
  | 0 => .base
  | n + 1 => .next (ofNat n)

@[simp] theorem GeneratedOrdinal.toNat_ofNat (n : Nat) :
    (GeneratedOrdinal.ofNat n).toNat = n := by
  induction n with
  | zero => rfl
  | succ n ih =>
      change (GeneratedOrdinal.ofNat n).toNat + 1 = n + 1
      rw [ih]

@[simp] theorem GeneratedOrdinal.ofNat_toNat (n : GeneratedOrdinal) :
    GeneratedOrdinal.ofNat n.toNat = n := by
  induction n with
  | base => rfl
  | next predecessor ih =>
      change GeneratedOrdinal.next (GeneratedOrdinal.ofNat predecessor.toNat) =
        GeneratedOrdinal.next predecessor
      rw [ih]

/-- A bijection between an admissible source carrier and its SFT-native carrier. -/
structure ExactEncoding (Source Native : Type) where
  encode : Source → Native
  decode : Native → Source
  decodeEncode : ∀ source, decode (encode source) = source
  encodeDecode : ∀ native, encode (decode native) = native

def ordinalEncoding : ExactEncoding Nat GeneratedOrdinal where
  encode := GeneratedOrdinal.ofNat
  decode := GeneratedOrdinal.toNat
  decodeEncode := GeneratedOrdinal.toNat_ofNat
  encodeDecode := GeneratedOrdinal.ofNat_toNat

/-- Predicate preservation on every admitted encoded object. -/
def PreservesPredicate {Source Native : Type}
    (encoding : ExactEncoding Source Native)
    (sourcePredicate : Source → Prop) (nativePredicate : Native → Prop) : Prop :=
  ∀ source, sourcePredicate source ↔ nativePredicate (encoding.encode source)

theorem forall_iff_of_preserves
    {Source Native : Type} (encoding : ExactEncoding Source Native)
    {sourcePredicate : Source → Prop} {nativePredicate : Native → Prop}
    (preserves : PreservesPredicate encoding sourcePredicate nativePredicate) :
    (∀ source, sourcePredicate source) ↔ ∀ native, nativePredicate native := by
  constructor
  · intro sourceProof native
    have translated := (preserves (encoding.decode native)).mp
      (sourceProof (encoding.decode native))
    simpa [encoding.encodeDecode native] using translated
  · intro nativeProof source
    exact (preserves source).mpr (nativeProof (encoding.encode source))

theorem exists_iff_of_preserves
    {Source Native : Type} (encoding : ExactEncoding Source Native)
    {sourcePredicate : Source → Prop} {nativePredicate : Native → Prop}
    (preserves : PreservesPredicate encoding sourcePredicate nativePredicate) :
    (∃ source, sourcePredicate source) ↔ ∃ native, nativePredicate native := by
  constructor
  · rintro ⟨source, proof⟩
    exact ⟨encoding.encode source, (preserves source).mp proof⟩
  · rintro ⟨native, proof⟩
    refine ⟨encoding.decode native, ?_⟩
    apply (preserves (encoding.decode native)).mpr
    simpa [encoding.encodeDecode native] using proof

theorem and_iff_of_iff {P Q Pn Qn : Prop}
    (hp : P ↔ Pn) (hq : Q ↔ Qn) :
    (P ∧ Q) ↔ (Pn ∧ Qn) := by
  constructor
  · rintro ⟨p, q⟩
    exact ⟨hp.mp p, hq.mp q⟩
  · rintro ⟨p, q⟩
    exact ⟨hp.mpr p, hq.mpr q⟩

theorem implication_iff_of_iff {P Q Pn Qn : Prop}
    (hp : P ↔ Pn) (hq : Q ↔ Qn) :
    (P → Q) ↔ (Pn → Qn) := by
  constructor
  · intro sourceImplication nativePremise
    exact hq.mp (sourceImplication (hp.mpr nativePremise))
  · intro nativeImplication sourcePremise
    exact hq.mpr (nativeImplication (hp.mp sourcePremise))

theorem not_iff_of_iff {P Pn : Prop} (hp : P ↔ Pn) :
    (¬ P) ↔ (¬ Pn) := by
  constructor
  · intro notSource nativeProof
    exact notSource (hp.mpr nativeProof)
  · intro notNative sourceProof
    exact notNative (hp.mp sourceProof)

/-- Exact structural order on generated ordinals. -/
def GeneratedOrdinal.le (left right : GeneratedOrdinal) : Prop :=
  left.toNat ≤ right.toNat

/-- Constructive threshold semantics for `eventually atTop`. -/
def EventuallyNat (predicate : Nat → Prop) : Prop :=
  ∃ threshold : Nat, ∀ index : Nat, threshold ≤ index → predicate index

def EventuallyGenerated (predicate : GeneratedOrdinal → Prop) : Prop :=
  ∃ threshold : GeneratedOrdinal,
    ∀ index : GeneratedOrdinal, GeneratedOrdinal.le threshold index → predicate index

theorem eventually_iff_generated
    {sourcePredicate : Nat → Prop} {nativePredicate : GeneratedOrdinal → Prop}
    (preserves : PreservesPredicate ordinalEncoding sourcePredicate nativePredicate) :
    EventuallyNat sourcePredicate ↔ EventuallyGenerated nativePredicate := by
  constructor
  · rintro ⟨threshold, sourceProof⟩
    refine ⟨GeneratedOrdinal.ofNat threshold, ?_⟩
    intro index later
    have laterNat : threshold ≤ index.toNat := by
      change (GeneratedOrdinal.ofNat threshold).toNat ≤ index.toNat at later
      rw [GeneratedOrdinal.toNat_ofNat] at later
      exact later
    have translated :=
      (preserves index.toNat).mp (sourceProof index.toNat laterNat)
    change nativePredicate (GeneratedOrdinal.ofNat index.toNat) at translated
    rw [GeneratedOrdinal.ofNat_toNat] at translated
    exact translated
  · rintro ⟨threshold, nativeProof⟩
    refine ⟨threshold.toNat, ?_⟩
    intro index later
    apply (preserves index).mpr
    apply nativeProof (GeneratedOrdinal.ofNat index)
    change threshold.toNat ≤ (GeneratedOrdinal.ofNat index).toNat
    rw [GeneratedOrdinal.toNat_ofNat]
    exact later

/--
An exact generated convergence certificate. `Tolerance` can be instantiated by
positive rational parts; `close` is theorem-specific and contains no metric
axiom here.
-/
def GeneratedTendsto
    (Tolerance Value : Type)
    (sequence : GeneratedOrdinal → Value)
    (limit : Value)
    (close : Tolerance → Value → Value → Prop) : Prop :=
  ∀ tolerance : Tolerance,
    ∃ threshold : GeneratedOrdinal,
      ∀ index : GeneratedOrdinal,
        GeneratedOrdinal.le threshold index →
          close tolerance (sequence index) limit

/-- Source-natural presentation of the same modulus certificate. -/
def NatTendsto
    (Tolerance Value : Type)
    (sequence : Nat → Value)
    (limit : Value)
    (close : Tolerance → Value → Value → Prop) : Prop :=
  ∀ tolerance : Tolerance,
    ∃ threshold : Nat,
      ∀ index : Nat, threshold ≤ index → close tolerance (sequence index) limit

theorem tendsto_iff_generated
    {Tolerance Value : Type} (sequence : Nat → Value) (limit : Value)
    (close : Tolerance → Value → Value → Prop) :
    NatTendsto Tolerance Value sequence limit close ↔
      GeneratedTendsto Tolerance Value
        (fun index => sequence index.toNat) limit close := by
  constructor
  · intro sourceProof tolerance
    obtain ⟨threshold, afterThreshold⟩ := sourceProof tolerance
    refine ⟨GeneratedOrdinal.ofNat threshold, ?_⟩
    intro index later
    apply afterThreshold index.toNat
    change (GeneratedOrdinal.ofNat threshold).toNat ≤ index.toNat at later
    rw [GeneratedOrdinal.toNat_ofNat] at later
    exact later
  · intro nativeProof tolerance
    obtain ⟨threshold, afterThreshold⟩ := nativeProof tolerance
    refine ⟨threshold.toNat, ?_⟩
    intro index later
    have laterGenerated :
        GeneratedOrdinal.le threshold (GeneratedOrdinal.ofNat index) := by
      change threshold.toNat ≤ (GeneratedOrdinal.ofNat index).toNat
      rw [GeneratedOrdinal.toNat_ofNat]
      exact later
    have translated :=
      afterThreshold (GeneratedOrdinal.ofNat index) laterGenerated
    change close tolerance (sequence (GeneratedOrdinal.ofNat index).toNat) limit at translated
    rw [GeneratedOrdinal.toNat_ofNat] at translated
    exact translated

/-- Exact enclosure names used by theorem-specific real translations. -/
structure ExactEnclosureName (Bound : Type) [LE Bound] where
  lower : GeneratedOrdinal → Bound
  upper : GeneratedOrdinal → Bound
  ordered : ∀ stage, lower stage ≤ upper stage
  lowerNested : ∀ stage, lower stage ≤ lower (.next stage)
  upperNested : ∀ stage, upper (.next stage) ≤ upper stage

/-- A relation is preserved exactly, not merely approximated or renamed. -/
def PreservesRelation
    {Source Native : Type} (encoding : ExactEncoding Source Native)
    (sourceRelation : Source → Source → Prop)
    (nativeRelation : Native → Native → Prop) : Prop :=
  ∀ left right,
    sourceRelation left right ↔
      nativeRelation (encoding.encode left) (encoding.encode right)

theorem relation_at_encoded_iff
    {Source Native : Type} (encoding : ExactEncoding Source Native)
    {sourceRelation : Source → Source → Prop}
    {nativeRelation : Native → Native → Prop}
    (preserves : PreservesRelation encoding sourceRelation nativeRelation)
    (left right : Source) :
    sourceRelation left right ↔
      nativeRelation (encoding.encode left) (encoding.encode right) :=
  preserves left right

end SFTValidation.OpenAI2026.Correspondence

#print axioms SFTValidation.OpenAI2026.Correspondence.GeneratedOrdinal.toNat_ofNat
#print axioms SFTValidation.OpenAI2026.Correspondence.GeneratedOrdinal.ofNat_toNat
#print axioms SFTValidation.OpenAI2026.Correspondence.forall_iff_of_preserves
#print axioms SFTValidation.OpenAI2026.Correspondence.exists_iff_of_preserves
#print axioms SFTValidation.OpenAI2026.Correspondence.implication_iff_of_iff
#print axioms SFTValidation.OpenAI2026.Correspondence.not_iff_of_iff
#print axioms SFTValidation.OpenAI2026.Correspondence.eventually_iff_generated
#print axioms SFTValidation.OpenAI2026.Correspondence.tendsto_iff_generated
