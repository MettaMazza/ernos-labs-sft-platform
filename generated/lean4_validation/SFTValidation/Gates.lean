/-!
# Pure whole-model gate semantics

The runtime verifier computes one `ClaimGate` for every live model claim.  A
successful `certify?` call returns a proof-carrying certificate whose type
requires every model gate.  The checker and its certificates are constructive.
-/

namespace SFTValidation

structure ClaimGate where
  identityBound : Bool
  sourceArtifactsBound : Bool
  dependencyClosed : Bool
  candidateEnumerationComplete : Bool
  decisionCoverageComplete : Bool
  exactlyOneSurvivor : Bool
  minimalityPassed : Bool
  namedShapeUniquenessPassed : Bool
  structuralControlsPassed : Bool
  empiricalBoundaryPassed : Bool
  certificateBound : Bool
  receiptAdmitted : Bool
  deriving Repr, DecidableEq

/-- Proof-bearing meaning of acceptance for one live claim. -/
structure ClaimGate.Accepted (gate : ClaimGate) : Prop where
  identityBound : gate.identityBound = true
  sourceArtifactsBound : gate.sourceArtifactsBound = true
  dependencyClosed : gate.dependencyClosed = true
  candidateEnumerationComplete : gate.candidateEnumerationComplete = true
  decisionCoverageComplete : gate.decisionCoverageComplete = true
  exactlyOneSurvivor : gate.exactlyOneSurvivor = true
  minimalityPassed : gate.minimalityPassed = true
  namedShapeUniquenessPassed : gate.namedShapeUniquenessPassed = true
  structuralControlsPassed : gate.structuralControlsPassed = true
  empiricalBoundaryPassed : gate.empiricalBoundaryPassed = true
  certificateBound : gate.certificateBound = true
  receiptAdmitted : gate.receiptAdmitted = true

/--
Construct a kernel-checked certificate precisely when all runtime gate booleans
are true. `PLift` keeps the proof in a computational `Option` without adding an
axiom.
-/
def ClaimGate.certify? (gate : ClaimGate) : Option (PLift gate.Accepted) :=
  if identity : gate.identityBound = true then
    if sourceArtifacts : gate.sourceArtifactsBound = true then
      if dependency : gate.dependencyClosed = true then
        if candidates : gate.candidateEnumerationComplete = true then
          if decisions : gate.decisionCoverageComplete = true then
            if survivor : gate.exactlyOneSurvivor = true then
              if minimality : gate.minimalityPassed = true then
                if shape : gate.namedShapeUniquenessPassed = true then
                  if controls : gate.structuralControlsPassed = true then
                    if empirical : gate.empiricalBoundaryPassed = true then
                      if certificate : gate.certificateBound = true then
                        if receipt : gate.receiptAdmitted = true then
                          some ⟨{
                            identityBound := identity
                            sourceArtifactsBound := sourceArtifacts
                            dependencyClosed := dependency
                            candidateEnumerationComplete := candidates
                            decisionCoverageComplete := decisions
                            exactlyOneSurvivor := survivor
                            minimalityPassed := minimality
                            namedShapeUniquenessPassed := shape
                            structuralControlsPassed := controls
                            empiricalBoundaryPassed := empirical
                            certificateBound := certificate
                            receiptAdmitted := receipt
                          }⟩
                        else none
                      else none
                    else none
                  else none
                else none
              else none
            else none
          else none
        else none
      else none
    else none
  else none

def ClaimGate.accepted (gate : ClaimGate) : Bool :=
  gate.certify?.isSome

theorem ClaimGate.certified_implies_exactlyOneSurvivor
    (gate : ClaimGate) (certificate : PLift gate.Accepted) :
    gate.exactlyOneSurvivor = true :=
  certificate.down.exactlyOneSurvivor

theorem ClaimGate.certified_implies_sourceArtifactsBound
    (gate : ClaimGate) (certificate : PLift gate.Accepted) :
    gate.sourceArtifactsBound = true :=
  certificate.down.sourceArtifactsBound

theorem ClaimGate.certified_implies_completeCoverage
    (gate : ClaimGate) (certificate : PLift gate.Accepted) :
    gate.candidateEnumerationComplete = true ∧
    gate.decisionCoverageComplete = true :=
  ⟨certificate.down.candidateEnumerationComplete,
   certificate.down.decisionCoverageComplete⟩

theorem ClaimGate.certified_implies_dependencyClosure
    (gate : ClaimGate) (certificate : PLift gate.Accepted) :
    gate.dependencyClosed = true :=
  certificate.down.dependencyClosed

end SFTValidation

#print axioms SFTValidation.ClaimGate.certify?
#print axioms SFTValidation.ClaimGate.certified_implies_sourceArtifactsBound
#print axioms SFTValidation.ClaimGate.certified_implies_exactlyOneSurvivor
#print axioms SFTValidation.ClaimGate.certified_implies_completeCoverage
#print axioms SFTValidation.ClaimGate.certified_implies_dependencyClosure
