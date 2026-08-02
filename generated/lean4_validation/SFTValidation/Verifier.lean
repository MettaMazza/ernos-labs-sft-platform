import SFTValidation.Gates
import SFTValidation.JsonUtil

namespace SFTValidation

open Lean

structure Issue where
  claimId : String
  check : String
  detail : String
  deriving Repr

structure ClaimIndexRow where
  claimId : String
  branch : String
  closureStatus : String
  receiptHash : String
  receiptPath : String
  modelAdmitted : Bool
  deriving Repr

structure RegistrationEvidence where
  identityMatches : Bool
  branchMatches : Bool
  dependencies : Array String
  dependenciesUnique : Bool
  dependenciesPrior : Bool
  rootShape : Bool
  requiredControls : Array String
  empiricalProtocol : Option String
  empiricalProtocolExists : Bool
  grammarBound : Bool
  deriving Repr

structure EnumerationEvidence where
  identityMatches : Bool
  expectedCardinality : Nat
  actualCardinality : Nat
  candidateIds : Std.HashSet String
  candidateIdsUnique : Bool
  recordsBound : Bool
  grammarBoundary : String
  completenessHashBound : Bool
  deriving Repr

structure DecisionEvidence where
  identityMatches : Bool
  artifactName : String
  actualCardinality : Nat
  decisionIds : Std.HashSet String
  decisionIdsUnique : Bool
  recordsBound : Bool
  survivorCount : Nat
  survivorId : Option String
  closureScope : String
  closureBoundary : String
  minimalityPassed : Bool
  namedShapeUniquenessPassed : Bool
  closureHashesBound : Bool
  deriving Repr

structure ControlEvidence where
  identityMatches : Bool
  actualCardinality : Nat
  kinds : Std.HashSet String
  kindsUnique : Bool
  allPassed : Bool
  recordsBound : Bool
  baseControlsPresent : Bool
  deriving Repr

structure EmpiricalEvidence where
  artifactPresent : Bool
  identityMatches : Bool
  passed : Bool
  custodyPreserved : Bool
  isolationPreserved : Bool
  rowsPreserved : Bool
  hashesBound : Bool
  deriving Repr

structure CertificateEvidence where
  identityMatches : Bool
  closureMatches : Bool
  hashesBound : Bool
  optionalPassFlags : Bool
  lineageReceiptExists : Bool
  lineageReceiptMatches : Bool
  lineageDiffersFromCurrent : Bool
  deriving Repr

structure ReceiptEvidence where
  identityMatches : Bool
  hashMatches : Bool
  admitted : Bool
  evidenceAccepted : Bool
  noViolations : Bool
  notHalted : Bool
  closureMatches : Bool
  allGatesPassed : Bool
  requiredGatesPresent : Bool
  controlsGatePassed : Bool
  deriving Repr

structure ClaimResult where
  claimId : String
  branch : String
  candidateCount : Nat
  decisionCount : Nat
  controlCount : Nat
  decisionArtifact : String
  preservedReceiptLineage : Bool
  gate : ClaimGate
  issues : Array Issue
  deriving Repr

structure SourceBindingProbe where
  claimCount : Nat
  censusFileHash : String
  executionManifestFileHash : String
  passedClaimIds : Std.HashSet String
  issueDetails : Std.HashMap String String
  issueCount : Nat
  preservedCertificateSourceLineageCount : Nat
  deriving Repr

structure ModelResult where
  claimCount : Nat
  censusFileHash : String
  executionManifestFileHash : String
  branchCounts : Std.HashMap String Nat
  candidateCount : Nat
  decisionCount : Nat
  controlCount : Nat
  customDecisionArtifactCount : Nat
  preservedReceiptLineageCount : Nat
  preservedCertificateSourceLineageCount : Nat
  sourceBindingPassedClaimCount : Nat
  sourceBindingIssueCount : Nat
  acceptedClaimCount : Nat
  uncensusedPackageCount : Nat
  issues : Array Issue
  deriving Repr

def runSourceBindingProbe (root : System.FilePath) : IO SourceBindingProbe := do
  let script := root / "generated" / "lean4_validation" / "source_binding_probe.py"
  let output ← IO.Process.output {
    cmd := "python3"
    args := #[script.toString, root.toString]
    cwd := some root
    env := #[("PYTHONDONTWRITEBYTECODE", some "1")]
  }
  let json ← exceptToIO "source-binding probe output" (Json.parse output.stdout)
  let schema ← exceptToIO "source-binding probe schema" (stringField json "schema")
  if schema != "sft-lean4-source-binding-probe/1" then
    throw <| IO.userError s!"unexpected source-binding probe schema: {schema}"
  let claimCount ← exceptToIO "source-binding probe claim_count" (natField json "claim_count")
  let censusFileHash ← exceptToIO "source-binding probe census hash"
    (stringField json "census_file_hash")
  let executionManifestFileHash ← exceptToIO "source-binding probe execution manifest hash"
    (stringField json "execution_manifest_file_hash")
  if !sha256Identity censusFileHash || !sha256Identity executionManifestFileHash then
    throw <| IO.userError "source-binding probe returned a malformed input-file hash"
  let declaredPassed ← exceptToIO "source-binding probe passed_claim_count"
    (natField json "passed_claim_count")
  let declaredIssues ← exceptToIO "source-binding probe issue_count" (natField json "issue_count")
  let preservedLineages ← exceptToIO "source-binding probe preserved lineage count"
    (natField json "preserved_certificate_source_lineage_count")
  let passedIds ← exceptToIO "source-binding probe passed_claim_ids"
    (stringArrayField json "passed_claim_ids")
  let issueRows ← exceptToIO "source-binding probe issues" (arrayField json "issues")
  let mut passedClaimIds : Std.HashSet String := Std.HashSet.emptyWithCapacity passedIds.size
  for claimId in passedIds do
    if passedClaimIds.contains claimId then
      throw <| IO.userError s!"duplicate source-binding pass identity: {claimId}"
    passedClaimIds := passedClaimIds.insert claimId
  let mut issueDetails : Std.HashMap String String := {}
  for issue in issueRows do
    let claimId ← exceptToIO "source-binding issue claim_id" (stringField issue "claim_id")
    let detail ← exceptToIO s!"{claimId} source-binding issue detail"
      (stringField issue "detail")
    if issueDetails.contains claimId then
      throw <| IO.userError s!"duplicate source-binding issue identity: {claimId}"
    issueDetails := issueDetails.insert claimId detail
  if declaredPassed != passedClaimIds.size || declaredIssues != issueDetails.size then
    throw <| IO.userError "source-binding probe declared counts do not match its rows"
  if claimCount != passedClaimIds.size + issueDetails.size then
    throw <| IO.userError "source-binding probe does not partition its declared claims"
  if (output.exitCode == 0) != issueDetails.isEmpty then
    throw <| IO.userError s!"source-binding probe exit code {output.exitCode} contradicts its issue set"
  pure {
    claimCount
    censusFileHash
    executionManifestFileHash
    passedClaimIds
    issueDetails
    issueCount := issueDetails.size
    preservedCertificateSourceLineageCount := preservedLineages
  }

def addIssueUnless (issues : Array Issue) (condition : Bool) (claimId check detail : String) :
    Array Issue :=
  if condition then issues else issues.push { claimId, check, detail }

def parseIndexRow (json : Json) : IO ClaimIndexRow := do
  pure {
    claimId := ← exceptToIO "census claim_id" (stringField json "claim_id")
    branch := ← exceptToIO "census branch" (stringField json "branch")
    closureStatus := ← exceptToIO "census closure_status" (stringField json "closure_status")
    receiptHash := ← exceptToIO "census receipt_hash" (stringField json "receipt_hash")
    receiptPath := ← exceptToIO "census receipt_path" (stringField json "receipt_path")
    modelAdmitted := ← exceptToIO "census model_admitted" (boolField json "model_admitted")
  }

def validRequiredControlSet (kinds : Std.HashSet String) : Bool :=
  kinds.contains "false_premise" &&
  kinds.contains "tampered_source" &&
  kinds.contains "tampered_artifact" &&
  kinds.contains "boundary"

def readRegistration (root : System.FilePath) (row : ClaimIndexRow)
    (seen : Std.HashSet String) : IO RegistrationEvidence := do
  let path := root / "claims" / row.claimId / "registration.json"
  let json ← readJson path
  let artifactId ← exceptToIO s!"{row.claimId} registration claim_id" (stringField json "claim_id")
  let artifactBranch ← exceptToIO s!"{row.claimId} registration branch" (stringField json "branch")
  let dependencies ← exceptToIO s!"{row.claimId} dependencies" (stringArrayField json "dependencies")
  let requiredControls ← exceptToIO s!"{row.claimId} required_controls"
    (stringArrayField json "required_controls")
  let empiricalProtocol ← exceptToIO s!"{row.claimId} empirical_protocol"
    (optionalStringField json "empirical_protocol")
  let grammar ← exceptToIO s!"{row.claimId} candidate_grammar" (field json "candidate_grammar")
  let generator ← exceptToIO s!"{row.claimId} candidate generator" (stringField grammar "generator")
  let boundary ← exceptToIO s!"{row.claimId} candidate boundary" (stringField grammar "boundary")
  let completeness ← exceptToIO s!"{row.claimId} candidate completeness"
    (optionalStringField grammar "completeness_certificate")
  let mut dependencySet : Std.HashSet String := Std.HashSet.emptyWithCapacity dependencies.size
  let mut dependenciesUnique := true
  let mut dependenciesPrior := true
  for dependency in dependencies do
    if dependencySet.contains dependency then dependenciesUnique := false
    dependencySet := dependencySet.insert dependency
    if !seen.contains dependency then dependenciesPrior := false
  let rootShape :=
    if row.claimId == "SFT-ROOT-THERE-IS-NO-NOTHING" then dependencies.isEmpty
    else !dependencies.isEmpty
  let empiricalProtocolExists ←
    match empiricalProtocol with
    | none => pure true
    | some declaration =>
      if declaration.startsWith "experiments/" then
        (root / declaration).pathExists
      else
        pure (nonemptyString declaration)
  pure {
    identityMatches := artifactId == row.claimId
    branchMatches := artifactBranch == row.branch
    dependencies
    dependenciesUnique
    dependenciesPrior
    rootShape
    requiredControls
    empiricalProtocol
    empiricalProtocolExists
    grammarBound := nonemptyString generator && nonemptyString boundary &&
      match completeness with
      | none => true
      | some identity =>
        if identity.startsWith "sha256:" then sha256Identity identity
        else nonemptyString identity
  }

def readEnumeration (root : System.FilePath) (row : ClaimIndexRow) : IO EnumerationEvidence := do
  let path := root / "claims" / row.claimId / "candidate_census.json"
  let json ← readJson path
  let artifactId ← exceptToIO s!"{row.claimId} candidate census claim_id"
    (stringField json "claim_id")
  let expected ← exceptToIO s!"{row.claimId} expected cardinality"
    (natField json "expected_cardinality")
  let boundary ← exceptToIO s!"{row.claimId} grammar boundary"
    (stringField json "grammar_boundary")
  let completeness ← exceptToIO s!"{row.claimId} completeness hash"
    (stringField json "completeness_certificate_hash")
  let candidates ← exceptToIO s!"{row.claimId} candidates" (arrayField json "candidates")
  let mut ids : Std.HashSet String := Std.HashSet.emptyWithCapacity candidates.size
  let mut unique := true
  let mut recordsBound := true
  for candidate in candidates do
    let candidateId ← exceptToIO s!"{row.claimId} candidate_id" (stringField candidate "candidate_id")
    let exactForm ← exceptToIO s!"{row.claimId}/{candidateId} exact_form"
      (stringField candidate "exact_form")
    let traceHash ← exceptToIO s!"{row.claimId}/{candidateId} trace_hash"
      (stringField candidate "trace_hash")
    if ids.contains candidateId then unique := false
    ids := ids.insert candidateId
    recordsBound := recordsBound && nonemptyString candidateId && nonemptyString exactForm &&
      sha256Identity traceHash
  pure {
    identityMatches := artifactId == row.claimId
    expectedCardinality := expected
    actualCardinality := candidates.size
    candidateIds := ids
    candidateIdsUnique := unique
    recordsBound
    grammarBoundary := boundary
    completenessHashBound := sha256Identity completeness
  }

def decisionShape (json : Json) : Bool :=
  match optionalField json "decisions", optionalField json "closure" with
  | some (.arr _), some (.obj _) => true
  | _, _ => false

def readDecisionArtifact (claimDirectory : System.FilePath) : IO (String × Json) := do
  let standard := claimDirectory / "elimination_receipt.json"
  if ← standard.pathExists then
    pure ("elimination_receipt.json", ← readJson standard)
  else
    let entries ← claimDirectory.readDir
    let mut decisionArtifacts : Array (String × Json) := #[]
    for entry in entries do
      if entry.fileName.endsWith ".json" && entry.fileName.contains "receipt" then
        try
          let json ← readJson entry.path
          if decisionShape json then
            decisionArtifacts := decisionArtifacts.push (entry.fileName, json)
        catch _ => pure ()
    if decisionArtifacts.size == 1 then
      pure decisionArtifacts[0]!
    else
      throw <| IO.userError s!"expected one decision artifact in {claimDirectory}, found {decisionArtifacts.size}"

def readDecisions (root : System.FilePath) (row : ClaimIndexRow) : IO DecisionEvidence := do
  let claimDirectory := root / "claims" / row.claimId
  let (artifactName, json) ← readDecisionArtifact claimDirectory
  let artifactId ← exceptToIO s!"{row.claimId} decisions claim_id" (stringField json "claim_id")
  let decisions ← exceptToIO s!"{row.claimId} decisions" (arrayField json "decisions")
  let closure ← exceptToIO s!"{row.claimId} closure" (field json "closure")
  let scope ← exceptToIO s!"{row.claimId} closure scope" (stringField closure "scope")
  let boundary ← exceptToIO s!"{row.claimId} closure boundary"
    (stringField closure "exact_boundary")
  let minimality ← exceptToIO s!"{row.claimId} minimality"
    (boolField closure "minimality_passed")
  let shape ← exceptToIO s!"{row.claimId} named-shape uniqueness"
    (boolField closure "named_shape_uniqueness_passed")
  let closureProof ← exceptToIO s!"{row.claimId} closure proof hash"
    (stringField closure "proof_hash")
  let generality ← exceptToIO s!"{row.claimId} generality certificate hash"
    (optionalStringField closure "generality_certificate_hash")
  let mut ids : Std.HashSet String := Std.HashSet.emptyWithCapacity decisions.size
  let mut unique := true
  let mut recordsBound := true
  let mut survivorCount := 0
  let mut survivorId : Option String := none
  for decision in decisions do
    let candidateId ← exceptToIO s!"{row.claimId} decision candidate_id"
      (stringField decision "candidate_id")
    let survives ← exceptToIO s!"{row.claimId}/{candidateId} survives"
      (boolField decision "survives")
    let reason ← exceptToIO s!"{row.claimId}/{candidateId} reason"
      (stringField decision "reason")
    let proofHash ← exceptToIO s!"{row.claimId}/{candidateId} proof_hash"
      (stringField decision "proof_hash")
    if ids.contains candidateId then unique := false
    ids := ids.insert candidateId
    recordsBound := recordsBound && nonemptyString candidateId && nonemptyString reason &&
      sha256Identity proofHash
    if survives then
      survivorCount := survivorCount + 1
      survivorId := some candidateId
  pure {
    identityMatches := artifactId == row.claimId
    artifactName
    actualCardinality := decisions.size
    decisionIds := ids
    decisionIdsUnique := unique
    recordsBound
    survivorCount
    survivorId
    closureScope := scope
    closureBoundary := boundary
    minimalityPassed := minimality
    namedShapeUniquenessPassed := shape
    closureHashesBound := sha256Identity closureProof &&
      match generality with
      | none => true
      | some identity => sha256Identity identity
  }

def readControls (root : System.FilePath) (row : ClaimIndexRow) : IO ControlEvidence := do
  let path := root / "claims" / row.claimId / "controls.json"
  let json ← readJson path
  let artifactId ← exceptToIO s!"{row.claimId} controls claim_id" (stringField json "claim_id")
  let controls ← exceptToIO s!"{row.claimId} controls" (arrayField json "controls")
  let mut kinds : Std.HashSet String := Std.HashSet.emptyWithCapacity controls.size
  let mut unique := true
  let mut allPassed := true
  let mut recordsBound := true
  for control in controls do
    let kind ← exceptToIO s!"{row.claimId} control kind" (stringField control "kind")
    let passed ← exceptToIO s!"{row.claimId}/{kind} control passed" (boolField control "passed")
    let expected ← exceptToIO s!"{row.claimId}/{kind} expected behavior"
      (stringField control "expected_behavior")
    let observed ← exceptToIO s!"{row.claimId}/{kind} observed behavior"
      (stringField control "observed_behavior")
    let receiptHash ← exceptToIO s!"{row.claimId}/{kind} control receipt hash"
      (stringField control "receipt_hash")
    if kinds.contains kind then unique := false
    kinds := kinds.insert kind
    allPassed := allPassed && passed
    recordsBound := recordsBound && nonemptyString kind && nonemptyString expected &&
      nonemptyString observed && sha256Identity receiptHash
  pure {
    identityMatches := artifactId == row.claimId
    actualCardinality := controls.size
    kinds
    kindsUnique := unique
    allPassed
    recordsBound
    baseControlsPresent := validRequiredControlSet kinds
  }

def optionalExpectedBool (json : Json) (name : String) (expected : Bool) : Bool :=
  match optionalField json name with
  | none => true
  | some (.bool value) => value == expected
  | _ => false

def readEmpirical (root : System.FilePath) (row : ClaimIndexRow) : IO EmpiricalEvidence := do
  let path := root / "claims" / row.claimId / "empirical_validation.json"
  if !(← path.pathExists) then
    pure {
      artifactPresent := false
      identityMatches := true
      passed := true
      custodyPreserved := true
      isolationPreserved := true
      rowsPreserved := true
      hashesBound := true
    }
  else
    let json ← readJson path
    let artifactId ← exceptToIO s!"{row.claimId} empirical claim_id"
      (stringField json "claim_id")
    let passed := optionalExpectedBool json "passed" true
    let rowsPreserved :=
      optionalExpectedBool json "all_rows_preserved" true &&
      optionalExpectedBool json "all_measurement_rows_preserved" true &&
      optionalExpectedBool json "all_external_rows_preserved" true
    let custodyTop :=
      optionalExpectedBool json "target_opened_after_seal" true &&
      optionalExpectedBool json "evaluator_verified_seal" true
    let custodyNested :=
      match optionalField json "target_custody_certificate" with
      | none => true
      | some custody =>
        optionalExpectedBool custody "released_after_prediction_seal" true &&
        optionalExpectedBool custody "target_absent_until_prediction_seal" true
    let isolation :=
      match optionalField json "isolation_certificate" with
      | none => true
      | some certificate =>
        optionalExpectedBool certificate "completed" true &&
        optionalExpectedBool certificate "target_material_present" false &&
        optionalExpectedBool certificate "comparison_code_present" false &&
        jsonArrayEmptyOrMissing certificate "attempted_forbidden_operations"
    let hashes := #["experiment_registration_hash", "measurement_receipt_hash", "validated_seal_hash"]
    let mut hashesBound := true
    for key in hashes do
      match optionalField json key with
      | none => pure ()
      | some (.str value) => hashesBound := hashesBound && sha256Identity value
      | _ => hashesBound := false
    pure {
      artifactPresent := true
      identityMatches := artifactId == row.claimId
      passed
      custodyPreserved := custodyTop && custodyNested
      isolationPreserved := isolation
      rowsPreserved
      hashesBound
    }

def readCertificate (root : System.FilePath) (row : ClaimIndexRow) : IO CertificateEvidence := do
  let path := root / "claims" / row.claimId / "certificate.json"
  let json ← readJson path
  let artifactId ← exceptToIO s!"{row.claimId} certificate claim_id"
    (stringField json "claim_id")
  let closureScope ← exceptToIO s!"{row.claimId} certificate closure scope"
    (stringField json "closure_scope")
  let sourceManifest ← exceptToIO s!"{row.claimId} source manifest hash"
    (stringField json "source_manifest_hash")
  let implementation ← exceptToIO s!"{row.claimId} independent implementation hash"
    (stringField json "independent_implementation_hash")
  let derivationSeal ← exceptToIO s!"{row.claimId} derivation seal hash"
    (stringField json "derivation_seal_hash")
  let externalValidation ← exceptToIO s!"{row.claimId} external validation hash"
    (optionalStringField json "external_validation_hash")
  let lineageHash ← exceptToIO s!"{row.claimId} certificate receipt hash"
    (stringField json "engine_receipt_hash")
  let lineagePath ← exceptToIO s!"{row.claimId} certificate receipt path"
    (stringField json "engine_receipt_path")
  let optionalPassFlags :=
    optionalExpectedBool json "controls_passed" true &&
    optionalExpectedBool json "independently_recomputed" true
  let lineageAbsolute := root / lineagePath
  let lineageReceiptExists ← lineageAbsolute.pathExists
  let mut lineageReceiptMatches := false
  if lineageReceiptExists then
    let lineageReceipt ← readJson lineageAbsolute
    let recordedHash ← exceptToIO s!"{row.claimId} lineage receipt hash"
      (stringField lineageReceipt "receipt_hash")
    let recordedId ← exceptToIO s!"{row.claimId} lineage receipt claim_id"
      (stringField lineageReceipt "claim_id")
    lineageReceiptMatches := recordedHash == lineageHash && recordedId == row.claimId
  pure {
    identityMatches := artifactId == row.claimId
    closureMatches := closureScope == row.closureStatus
    hashesBound := sha256Identity sourceManifest && sha256Identity implementation &&
      sha256Identity derivationSeal && sha256Identity lineageHash &&
      match externalValidation with
      | none => true
      | some identity => sha256Identity identity
    optionalPassFlags
    lineageReceiptExists
    lineageReceiptMatches
    lineageDiffersFromCurrent := lineageHash != row.receiptHash
  }

def requiredReceiptGates : Array String := #[
  "registration", "enumeration", "forcing", "form_closure", "controls", "seal",
  "independent_validation", "model_admission"
]

def readReceipt (root : System.FilePath) (row : ClaimIndexRow) : IO ReceiptEvidence := do
  let path := root / row.receiptPath
  let json ← readJson path
  let artifactId ← exceptToIO s!"{row.claimId} receipt claim_id" (stringField json "claim_id")
  let receiptHash ← exceptToIO s!"{row.claimId} receipt hash" (stringField json "receipt_hash")
  let admitted ← exceptToIO s!"{row.claimId} receipt model_admitted"
    (boolField json "model_admitted")
  let evidence ← exceptToIO s!"{row.claimId} receipt accepted_evidence"
    (boolField json "accepted_evidence")
  let closure ← exceptToIO s!"{row.claimId} receipt closure status"
    (stringField json "closure_status")
  let gates ← exceptToIO s!"{row.claimId} gate results" (arrayField json "gate_results")
  let mut gateNames : Std.HashSet String := Std.HashSet.emptyWithCapacity gates.size
  let mut allGatesPassed := true
  let mut controlsGatePassed := false
  for gate in gates do
    let name ← exceptToIO s!"{row.claimId} gate name" (stringField gate "gate")
    let passed ← exceptToIO s!"{row.claimId}/{name} gate passed" (boolField gate "passed")
    gateNames := gateNames.insert name
    allGatesPassed := allGatesPassed && passed
    if name == "controls" then controlsGatePassed := passed
  let requiredGatesPresent := requiredReceiptGates.all fun name => gateNames.contains name
  let noViolations := jsonArrayEmptyOrMissing json "violations"
  let notHalted := (json.getObjValD "halted_stage").isNull
  pure {
    identityMatches := artifactId == row.claimId
    hashMatches := receiptHash == row.receiptHash && sha256Identity receiptHash
    admitted
    evidenceAccepted := evidence
    noViolations
    notHalted
    closureMatches := closure == row.closureStatus
    allGatesPassed
    requiredGatesPresent
    controlsGatePassed
  }

def validateClaim (root : System.FilePath) (row : ClaimIndexRow)
    (seen : Std.HashSet String) (sourceArtifactsBound : Bool)
    (sourceBindingDetail : String) : IO ClaimResult := do
  let registration ← readRegistration root row seen
  let enumeration ← readEnumeration root row
  let decisions ← readDecisions root row
  let controls ← readControls root row
  let empirical ← readEmpirical root row
  let certificate ← readCertificate root row
  let receipt ← readReceipt root row

  let identityBound :=
    registration.identityMatches && registration.branchMatches && registration.grammarBound &&
    enumeration.identityMatches && enumeration.recordsBound && enumeration.completenessHashBound &&
    decisions.identityMatches && decisions.recordsBound && decisions.closureHashesBound &&
    controls.identityMatches && controls.recordsBound && empirical.identityMatches &&
    certificate.identityMatches && receipt.identityMatches
  let dependencyClosed :=
    registration.dependenciesUnique && registration.dependenciesPrior && registration.rootShape
  let candidateEnumerationComplete :=
    enumeration.expectedCardinality == enumeration.actualCardinality &&
    enumeration.candidateIdsUnique && enumeration.candidateIds.size == enumeration.actualCardinality
  let decisionCoverageComplete :=
    decisions.actualCardinality == enumeration.actualCardinality &&
    decisions.decisionIdsUnique && sameStringSet enumeration.candidateIds decisions.decisionIds
  let exactlyOneSurvivor :=
    decisions.survivorCount == 1 && decisions.survivorId.isSome
  let minimalityPassed := decisions.minimalityPassed
  let namedShapeUniquenessPassed := decisions.namedShapeUniquenessPassed
  let directRequiredPresent :=
    registration.requiredControls.all fun kind =>
      controls.kinds.contains kind || empirical.artifactPresent
  let structuralControlsPassed :=
    controls.actualCardinality >= 4 && controls.kindsUnique && controls.allPassed &&
    controls.baseControlsPresent && directRequiredPresent && receipt.controlsGatePassed
  let empiricalRequired := registration.empiricalProtocol.isSome ||
    registration.requiredControls.any fun kind => !controls.kinds.contains kind
  let empiricalBoundaryPassed :=
    registration.empiricalProtocolExists &&
    (!empiricalRequired || empirical.artifactPresent) &&
    empirical.identityMatches && empirical.passed && empirical.custodyPreserved &&
    empirical.isolationPreserved && empirical.rowsPreserved && empirical.hashesBound
  let certificateBound :=
    certificate.identityMatches && certificate.closureMatches && certificate.hashesBound &&
    certificate.optionalPassFlags && certificate.lineageReceiptExists &&
    certificate.lineageReceiptMatches
  let receiptAdmitted :=
    row.modelAdmitted && receipt.identityMatches && receipt.hashMatches && receipt.admitted &&
    receipt.evidenceAccepted && receipt.noViolations && receipt.notHalted &&
    receipt.closureMatches && receipt.allGatesPassed && receipt.requiredGatesPresent

  let gate : ClaimGate := {
    identityBound
    sourceArtifactsBound
    dependencyClosed
    candidateEnumerationComplete
    decisionCoverageComplete
    exactlyOneSurvivor
    minimalityPassed
    namedShapeUniquenessPassed
    structuralControlsPassed
    empiricalBoundaryPassed
    certificateBound
    receiptAdmitted
  }

  let mut issues : Array Issue := #[]
  issues := addIssueUnless issues identityBound row.claimId "identity_binding"
    "one or more claim IDs, branches, hashes, records, or grammar identities are not bound"
  issues := addIssueUnless issues sourceArtifactsBound row.claimId "source_artifact_binding"
    sourceBindingDetail
  issues := addIssueUnless issues dependencyClosed row.claimId "dependency_closure"
    "dependencies must be unique, prior in the manifest, and connected to the single root"
  issues := addIssueUnless issues candidateEnumerationComplete row.claimId "candidate_enumeration"
    s!"expected={enumeration.expectedCardinality} actual={enumeration.actualCardinality}"
  issues := addIssueUnless issues decisionCoverageComplete row.claimId "decision_coverage"
    s!"candidates={enumeration.actualCardinality} decisions={decisions.actualCardinality}"
  issues := addIssueUnless issues exactlyOneSurvivor row.claimId "unique_survivor"
    s!"survivor_count={decisions.survivorCount}"
  issues := addIssueUnless issues minimalityPassed row.claimId "minimality" "minimality flag is not true"
  issues := addIssueUnless issues namedShapeUniquenessPassed row.claimId "named_shape_uniqueness"
    "named-shape uniqueness flag is not true"
  issues := addIssueUnless issues structuralControlsPassed row.claimId "controls"
    "base controls, registered extension controls, or the admitted controls gate did not pass"
  issues := addIssueUnless issues empiricalBoundaryPassed row.claimId "empirical_boundary"
    "empirical protocol, custody, isolation, row retention, or validation did not pass"
  issues := addIssueUnless issues certificateBound row.claimId "certificate_binding"
    "certificate or its preserved receipt lineage is not completely bound"
  issues := addIssueUnless issues receiptAdmitted row.claimId "receipt_admission"
    "the authoritative census receipt is not a clean, fully gated model admission"
  issues := addIssueUnless issues (decisions.closureScope == row.closureStatus) row.claimId
    "closure_scope" "decision closure does not match the census"
  issues := addIssueUnless issues (decisions.closureBoundary == enumeration.grammarBoundary) row.claimId
    "closure_boundary" "decision closure boundary does not match the candidate grammar"

  pure {
    claimId := row.claimId
    branch := row.branch
    candidateCount := enumeration.actualCardinality
    decisionCount := decisions.actualCardinality
    controlCount := controls.actualCardinality
    decisionArtifact := decisions.artifactName
    preservedReceiptLineage := certificate.lineageDiffersFromCurrent
    gate
    issues
  }

def expectedBranches : Array String := #[
  "foundation", "mathematics", "information_science", "computation",
  "quantum_computation", "physics", "chemistry", "materials", "biology",
  "medicine", "consciousness_cognitive_science", "earth_environment",
  "astronomy_cosmology", "social_collective", "social_collective_systems",
  "engineering_translation", "cross_branch_synthesis"
]

def countUncensusedPackages (root : System.FilePath) (censusIds : Std.HashSet String) : IO Nat := do
  let entries ← (root / "claims").readDir
  let mut count := 0
  for entry in entries do
    if (← entry.path.isDir) && entry.fileName != "TEMPLATE" && !censusIds.contains entry.fileName then
      count := count + 1
  pure count

def validateExecutionManifest (root : System.FilePath) (rows : Array Json) : IO (Array Issue) := do
  let manifest ← readJson (root / "census" / "execution_manifest.json")
  let entries ← exceptToIO "execution manifest claims" (arrayField manifest "claims")
  let mut issues : Array Issue := #[]
  if entries.size != rows.size then
    issues := issues.push {
      claimId := "<model>"
      check := "execution_manifest_count"
      detail := s!"census={rows.size} execution_manifest={entries.size}"
    }
  let common := min entries.size rows.size
  for index in [0:common] do
    let censusId ← exceptToIO s!"census row {index} claim_id" (stringField rows[index]! "claim_id")
    let manifestId ← exceptToIO s!"manifest row {index} claim_id"
      (stringField entries[index]! "claim_id")
    let executionFile ← exceptToIO s!"manifest row {index} execution_file"
      (stringField entries[index]! "execution_file")
    issues := addIssueUnless issues (censusId == manifestId) censusId "execution_manifest_order"
      s!"manifest claim at position {index} is {manifestId}"
    let filePresent ← (root / executionFile).pathExists
    issues := addIssueUnless issues filePresent censusId "execution_file"
      s!"missing {executionFile}"
  pure issues

def validateModel (root : System.FilePath) : IO ModelResult := do
  let census ← readJson (root / "census" / "claims.json")
  let rowsJson ← exceptToIO "census claims" (arrayField census "claims")
  let manifestIssues ← validateExecutionManifest root rowsJson
  IO.println "LEAN SFT SOURCE BINDING: start"
  let sourceBindings ← runSourceBindingProbe root
  IO.println s!"LEAN SFT SOURCE BINDING: {sourceBindings.passedClaimIds.size}/{sourceBindings.claimCount} claims; issues={sourceBindings.issueCount}"
  let mut globalIssues := manifestIssues
  globalIssues := addIssueUnless globalIssues (sourceBindings.claimCount == rowsJson.size)
    "<model>" "source_binding_count"
    s!"census={rowsJson.size} source_probe={sourceBindings.claimCount}"
  let mut seen : Std.HashSet String := Std.HashSet.emptyWithCapacity rowsJson.size
  let mut censusIds : Std.HashSet String := Std.HashSet.emptyWithCapacity rowsJson.size
  let mut branchCounts : Std.HashMap String Nat := {}
  let mut candidates := 0
  let mut decisions := 0
  let mut controls := 0
  let mut customDecisionArtifacts := 0
  let mut preservedReceiptLineages := 0
  let mut acceptedClaims := 0

  for index in [0:rowsJson.size] do
    let row ← parseIndexRow rowsJson[index]!
    if censusIds.contains row.claimId then
      globalIssues := globalIssues.push {
        claimId := row.claimId
        check := "duplicate_census_identity"
        detail := "claim ID occurs more than once in the census"
      }
    censusIds := censusIds.insert row.claimId
    branchCounts := branchCounts.insert row.branch (branchCounts.getD row.branch 0 + 1)
    try
      let sourcePassed := sourceBindings.passedClaimIds.contains row.claimId
      let sourceDetail := sourceBindings.issueDetails.getD row.claimId
        "claim is absent from the complete source-binding probe"
      let result ← validateClaim root row seen sourcePassed sourceDetail
      candidates := candidates + result.candidateCount
      decisions := decisions + result.decisionCount
      controls := controls + result.controlCount
      if result.decisionArtifact != "elimination_receipt.json" then
        customDecisionArtifacts := customDecisionArtifacts + 1
      if result.preservedReceiptLineage then
        preservedReceiptLineages := preservedReceiptLineages + 1
      if result.gate.accepted then acceptedClaims := acceptedClaims + 1
      globalIssues := globalIssues ++ result.issues
    catch error =>
      globalIssues := globalIssues.push {
        claimId := row.claimId
        check := "lean_runtime_exception"
        detail := toString error
      }
    seen := seen.insert row.claimId
    if (index + 1) % 25 == 0 || index + 1 == rowsJson.size then
      IO.println s!"LEAN SFT PROGRESS: {index + 1}/{rowsJson.size} claims; candidates={candidates}; issues={globalIssues.size}"

  let rootCount := if seen.contains "SFT-ROOT-THERE-IS-NO-NOTHING" then 1 else 0
  globalIssues := addIssueUnless globalIssues (rootCount == 1) "<model>" "root_identity"
    "the unique operational root is absent"
  for branch in expectedBranches do
    globalIssues := addIssueUnless globalIssues (branchCounts.contains branch) "<model>"
      "branch_coverage" s!"missing branch {branch}"
  let uncensused ← countUncensusedPackages root censusIds
  pure {
    claimCount := rowsJson.size
    censusFileHash := sourceBindings.censusFileHash
    executionManifestFileHash := sourceBindings.executionManifestFileHash
    branchCounts
    candidateCount := candidates
    decisionCount := decisions
    controlCount := controls
    customDecisionArtifactCount := customDecisionArtifacts
    preservedReceiptLineageCount := preservedReceiptLineages
    preservedCertificateSourceLineageCount :=
      sourceBindings.preservedCertificateSourceLineageCount
    sourceBindingPassedClaimCount := sourceBindings.passedClaimIds.size
    sourceBindingIssueCount := sourceBindings.issueCount
    acceptedClaimCount := acceptedClaims
    uncensusedPackageCount := uncensused
    issues := globalIssues
  }

def issueToJson (issue : Issue) : Json :=
  Json.mkObj [
    ("claim_id", issue.claimId),
    ("check", issue.check),
    ("detail", issue.detail)
  ]

def branchCountsToJson (counts : Std.HashMap String Nat) : Json :=
  Json.mkObj <| counts.toArray.toList.map fun (branch, count) => (branch, count)

def modelResultToJson (result : ModelResult) : Json :=
  Json.mkObj [
    ("schema", "sft-lean4-whole-model-validation/1"),
    ("lean_toolchain", "leanprover/lean4:v4.32.0"),
    ("status", if result.issues.isEmpty then "PASS" else "FAIL"),
    ("claim_count", result.claimCount),
    ("census_file_hash", result.censusFileHash),
    ("execution_manifest_file_hash", result.executionManifestFileHash),
    ("accepted_claim_count", result.acceptedClaimCount),
    ("branch_count", result.branchCounts.size),
    ("branches", branchCountsToJson result.branchCounts),
    ("candidate_count", result.candidateCount),
    ("decision_count", result.decisionCount),
    ("control_count", result.controlCount),
    ("custom_decision_artifact_count", result.customDecisionArtifactCount),
    ("preserved_receipt_lineage_count", result.preservedReceiptLineageCount),
    ("preserved_certificate_source_lineage_count",
      result.preservedCertificateSourceLineageCount),
    ("source_binding_passed_claim_count", result.sourceBindingPassedClaimCount),
    ("source_binding_issue_count", result.sourceBindingIssueCount),
    ("uncensused_nonmodel_package_count", result.uncensusedPackageCount),
    ("issue_count", result.issues.size),
    ("issues", Json.arr <| result.issues.map issueToJson)
  ]

def runWholeModelVerification (root reportPath : System.FilePath) : IO Bool := do
  IO.println s!"LEAN SFT WHOLE-MODEL VERIFICATION: root={root}"
  let result ← validateModel root
  let report := modelResultToJson result
  IO.FS.writeFile reportPath (report.pretty 120 ++ "\n")
  if result.issues.isEmpty then
    IO.println s!"LEAN SFT WHOLE-MODEL VERIFICATION: PASS ({result.acceptedClaimCount}/{result.claimCount} claims)"
    IO.println s!"LEAN SFT TOTALS: candidates={result.candidateCount}; decisions={result.decisionCount}; controls={result.controlCount}; branches={result.branchCounts.size}"
    pure true
  else
    IO.eprintln s!"LEAN SFT WHOLE-MODEL VERIFICATION: FAIL ({result.issues.size} issues)"
    for issue in result.issues do
      IO.eprintln s!"{issue.claimId}: {issue.check}: {issue.detail}"
    pure false

end SFTValidation
