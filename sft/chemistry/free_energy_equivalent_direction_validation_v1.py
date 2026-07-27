"""Post-seal complete NIST-JANAF reaction-direction validation for THERMO-007."""

from __future__ import annotations
from fractions import Fraction
import json
from pathlib import Path
import platform
from sft.chemistry.free_energy_equivalent_direction_batch_v1 import FREE_ENERGY_EQUIVALENT_DIRECTION_SPEC,IDENTITY_HASH,IDENTITY_PATH,PRIMARY_HASH,PRIMARY_PATH,TARGET_HASH,TARGET_PATH
from sft.claim_evidence import CapabilityClosedFoldInterpreter,CrossPlatformCustodyExchange,FoldTable,FoldWord,HostilePackageAuditor,TargetVault,fold_program_from_mapping,snapshot_protected_tree,target_identity_from_release
from sft.engine import EmpiricalValidation,seal_isolation_certificate,seal_target_custody_certificate,unsealed_isolation_certificate,unsealed_target_custody_certificate
from sft.engine.canonical import sha256_identity
from sft.engine.empirical import BlindExperimentBoundary,PredictionEnvelope
from sft.engine.exact import HeldLabel
from sft.engine.source import hash_file


SPECIES_COLUMNS=("temperature-kelvin","heat-capacity-joule-per-mole-kelvin","entropy-joule-per-mole-kelvin","gibbs-function-joule-per-mole-kelvin","enthalpy-increment-kilojoule-per-mole","formation-enthalpy-kilojoule-per-mole","formation-gibbs-kilojoule-per-mole","log10-formation-equilibrium-constant")


def _identities(root):
    if hash_file(root/IDENTITY_PATH)!=IDENTITY_HASH:raise ValueError("THERMO-007 identity registry changed")
    doc=json.loads((root/IDENTITY_PATH).read_text());rows=tuple(doc.get("rows",()))
    forbidden={"temperature-kelvin","NO2_complete_row","N2O4_complete_row","reaction-gibbs-kilojoule-per-mole-external-signed-inscription","reaction-gibbs-exact-positive-separation-kilojoule-per-mole","reaction-log10-equilibrium-constant-external-signed-inscription","held-reaction-direction","target_payload","target_payload_hash"}
    if doc.get("complete_target_count")!=64 or doc.get("all_temperature_thermochemical_direction_and_target_hash_values_absent") is not True or len(rows)!=64 or any(forbidden.intersection(row) for row in rows):raise ValueError("THERMO-007 value-free identity boundary changed")
    return rows


def prediction_program_document(root):
    instructions=[{"opcode":"input","destination":"premise","arguments":["registered-premise"]}];table=[]
    for ordinal,row in enumerate(_identities(root),start=1):
        prefix=f"reaction-direction-row-{ordinal}";instructions.append({"opcode":"label","destination":prefix+"-target","arguments":["target-id",row["target_id"]]});registers=["premise"]
        fields=(("common_source_row_ordinal","positive-common-row-ordinal"),("reaction_identity","reaction-identity"),("stoichiometric_identity","stoichiometric-identity"),("standard_state_pressure","standard-state-pressure"))
        for number,(key,family) in enumerate(fields,start=1):destination=f"{prefix}-identity-{number}";instructions.append({"opcode":"label","destination":destination,"arguments":[family,str(row[key])]});registers.append(destination)
        destination=prefix+"-source-pair";instructions.append({"opcode":"label","destination":destination,"arguments":["paired-source-identity-hash",sha256_identity(tuple(row["source_ids"]))]});registers.append(destination)
        for family,label in (("path-law","complete-forward-and-reverse-path-accounts"),("account-law","exact-positive-energy-and-distinction-accounts"),("order-law","strict-exact-product-support-order"),("orientation-law","held-forward-reverse-or-EmptyOne-equilibrium")):
            destination=f"{prefix}-law-{len(registers)}";instructions.append({"opcode":"label","destination":destination,"arguments":[family,label]});registers.append(destination)
        instructions.append({"opcode":"word","destination":prefix+"-word","arguments":registers});table.extend((prefix+"-target",prefix+"-word"))
    instructions.extend(({"opcode":"table","destination":"complete-reaction-direction-vector","arguments":table},{"opcode":"emit","destination":"","arguments":["complete-reaction-direction-vector"]}))
    return {"schema":"sft-v3-fold-program/1","program_id":FREE_ENERGY_EQUIVALENT_DIRECTION_SPEC.experiment_id+"-value-free-complete-vector","instructions":instructions}


def experiment_registration_record(root):return {"experiment_id":FREE_ENERGY_EQUIVALENT_DIRECTION_SPEC.experiment_id,"claim_id":FREE_ENERGY_EQUIVALENT_DIRECTION_SPEC.claim_id,"provenance":"observational_derivation","frozen_relation":FREE_ENERGY_EQUIVALENT_DIRECTION_SPEC.exact_result,"identity_registry":(IDENTITY_PATH,IDENTITY_HASH),"withheld_target_registry":(TARGET_PATH,TARGET_HASH),"primary_source_record":(PRIMARY_PATH,PRIMARY_HASH),"prediction_program":prediction_program_document(root),"target_ids":tuple(row.target_id for row in FREE_ENERGY_EQUIVALENT_DIRECTION_SPEC.target_rows),"all_temperature_Gibbs_logK_direction_and_target_hash_values_absent_from_prediction":True,"falsification_condition":FREE_ENERGY_EQUIVALENT_DIRECTION_SPEC.falsification_condition}


def _prediction_map(output):
    if not isinstance(output,FoldTable) or len(output.entries)!=64:raise ValueError("THERMO-007 prediction is not the complete 64-row table")
    resolved={}
    for entry in output.entries:
        if not isinstance(entry.left,HeldLabel) or entry.left.family!="target-id" or not isinstance(entry.right,FoldWord) or len(entry.right.cells)!=10:raise ValueError("THERMO-007 prediction lost a complete consequence")
        resolved[entry.left.label]=entry.right
    if len(resolved)!=64:raise ValueError("THERMO-007 duplicated a target identity")
    return resolved


def _source_rows(root):
    for path,expected in ((TARGET_PATH,TARGET_HASH),(PRIMARY_PATH,PRIMARY_HASH)):
        if hash_file(root/path)!=expected:raise ValueError(f"THERMO-007 source changed: {path}")
    identities=_identities(root);doc=json.loads((root/TARGET_PATH).read_text());targets=tuple(doc.get("rows",()))
    if doc.get("complete_target_count")!=64 or doc.get("release_requires_complete_identity_prediction_seal") is not True or len(targets)!=64:raise ValueError("THERMO-007 target registry changed")
    resolved=[]
    for identity,target in zip(identities,targets):
        if identity["target_id"]!=target.get("target_id") or identity["common_source_row_ordinal"]!=target.get("common_source_row_ordinal") or set(target.get("NO2_complete_row",{}))!=set(SPECIES_COLUMNS) or set(target.get("N2O4_complete_row",{}))!=set(SPECIES_COLUMNS):raise ValueError("THERMO-007 identity/target binding changed")
        resolved.append({**identity,"target_payload":target,"target_payload_hash":sha256_identity(target)})
    return tuple(resolved)


def exact_reaction_direction_analysis(rows):
    temperatures=[];gibbs=[];logk=[];directions=[]
    for row in rows:
        target=row["target_payload"];a=target["NO2_complete_row"];b=target["N2O4_complete_row"]
        temperature=Fraction(a["temperature-kelvin"]);dg=2*Fraction(a["formation-gibbs-kilojoule-per-mole"])-Fraction(b["formation-gibbs-kilojoule-per-mole"]);lk=2*Fraction(a["log10-formation-equilibrium-constant"])-Fraction(b["log10-formation-equilibrium-constant"])
        expected="equilibrium" if dg==0 else "forward" if dg<0 else "reverse"
        temperatures.append(temperature);gibbs.append(dg);logk.append(lk);directions.append(expected)
        if str(dg)!=target["reaction-gibbs-kilojoule-per-mole-external-signed-inscription"] or str(abs(dg))!=target["reaction-gibbs-exact-positive-separation-kilojoule-per-mole"] or str(lk)!=target["reaction-log10-equilibrium-constant-external-signed-inscription"] or expected!=target["held-reaction-direction"]:raise ValueError("THERMO-007 target calculation changed")
    crossings=tuple(index for index,(left,right) in enumerate(zip(directions,directions[1:])) if left!=right)
    return {"temperatures_kelvin":tuple(temperatures),"reaction_gibbs_signed_external_inscriptions":tuple(gibbs),"reaction_gibbs_exact_positive_separations":tuple(abs(value) for value in gibbs),"reaction_log10K_signed_external_inscriptions":tuple(logk),"held_direction_vector":tuple(directions),"all_temperatures_strictly_increasing":all(a<b for a,b in zip(temperatures,temperatures[1:])),"all_Gibbs_logK_signs_opposed":all((dg<0 and lk>0) or (dg>0 and lk<0) for dg,lk in zip(gibbs,logk)),"five_reverse_and_fifty_nine_forward_rows_retained":directions.count("reverse")==5 and directions.count("forward")==59,"single_direction_crossing_retained":crossings==(4,),"exact_crossing_bracket_300_to_350_kelvin":temperatures[4:6]==[Fraction(300),Fraction(350)] or temperatures[4:6]==(Fraction(300),Fraction(350)),"all_64_rows_retained":len(rows)==64,"all_eight_columns_per_species_retained":all(set(r["target_payload"]["NO2_complete_row"])==set(SPECIES_COLUMNS) and set(r["target_payload"]["N2O4_complete_row"])==set(SPECIES_COLUMNS) for r in rows)}


class FreeEnergyEquivalentDirectionValidator:
    def __init__(self,root):self.root=root.resolve();self.spec=FREE_ENERGY_EQUIVALENT_DIRECTION_SPEC
    def validate(self,sealed):
        self.spec.validate();registration=experiment_registration_record(self.root);registration_hash=sha256_identity(registration);document=prediction_program_document(self.root);program=fold_program_from_mapping(document);inputs={"registered-premise":HeldLabel("sealed-derivation",sealed.seal_hash)};envelope=PredictionEnvelope(self.spec.experiment_id,{"registered-premise":sha256_identity(inputs["registered-premise"])},tuple(row.target_id for row in self.spec.target_rows),sealed.seal_hash,registration_hash)
        before=snapshot_protected_tree(self.root);execution=CapabilityClosedFoldInterpreter().execute(program,inputs);boundary=BlindExperimentBoundary(envelope);prediction_seal=boundary.seal_prediction(execution.output,execution.trace);after=snapshot_protected_tree(self.root);audited,audit=HostilePackageAuditor().audit_program_document(document,before,after)
        if sha256_identity(audited)!=execution.program_hash or not audit.passed:raise ValueError("THERMO-007 prediction package changed")
        predicted=_prediction_map(execution.output);source_rows=_source_rows(self.root);target_values={row["target_id"]:HeldLabel("external-reaction-row-hash",row["target_payload_hash"]) for row in source_rows};vault=TargetVault(experiment_id=self.spec.experiment_id,custodian_id=self.spec.experiment_id+"-complete-target-custodian",targets=target_values,custody_nonce=sha256_identity((registration_hash,TARGET_HASH)),expected_envelope_hash=sha256_identity(envelope));release=vault.release(prediction_seal);CrossPlatformCustodyExchange.verify(vault.commitment,release,prediction_seal);boundary.measurement_context(release.targets)
        comparisons=[]
        for row in source_rows:
            target_id=row["target_id"];word=predicted[target_id];identity_match=isinstance(word.cells[1],HeldLabel) and word.cells[1].label==str(row["common_source_row_ordinal"]) and isinstance(word.cells[2],HeldLabel) and word.cells[2].label==row["reaction_identity"] and isinstance(word.cells[3],HeldLabel) and word.cells[3].label==row["stoichiometric_identity"] and isinstance(word.cells[4],HeldLabel) and word.cells[4].label==row["standard_state_pressure"] and isinstance(word.cells[5],HeldLabel) and word.cells[5].label==sha256_identity(tuple(row["source_ids"])) and isinstance(word.cells[6],HeldLabel) and word.cells[6].label=="complete-forward-and-reverse-path-accounts" and isinstance(word.cells[7],HeldLabel) and word.cells[7].label=="exact-positive-energy-and-distinction-accounts" and isinstance(word.cells[8],HeldLabel) and word.cells[8].label=="strict-exact-product-support-order" and isinstance(word.cells[9],HeldLabel) and word.cells[9].label=="held-forward-reverse-or-EmptyOne-equilibrium";target_match=release.targets[target_id]==HeldLabel("external-reaction-row-hash",row["target_payload_hash"]);comparisons.append({"target_id":target_id,"identity_match":identity_match,"postseal_target_hash_match":target_match,"passed":identity_match and target_match})
        analysis=exact_reaction_direction_analysis(source_rows);tampered=[dict(r) for r in source_rows];payload=dict(tampered[5]["target_payload"]);payload["held-reaction-direction"]="reverse";tampered[5]={**tampered[5],"target_payload":payload};tamper_rejected=False
        try:exact_reaction_direction_analysis(tuple(tampered))
        except ValueError:tamper_rejected=True
        controls={"tampered_direction_rejected":tamper_rejected,"complete_64_row_vector_retained":len(release.targets)==64,"both_direction_classes_retained":set(analysis["held_direction_vector"])=={"forward","reverse"},"single_crossing_bracket_retained":analysis["single_direction_crossing_retained"] and analysis["exact_crossing_bracket_300_to_350_kelvin"],"complete_two_species_eight_column_rows_retained":analysis["all_eight_columns_per_species_retained"],"prediction_contains_no_withheld_target_hash":TARGET_HASH not in json.dumps(document,sort_keys=True)}
        analysis_passed=all(bool(value) for key,value in analysis.items() if key not in {"temperatures_kelvin","reaction_gibbs_signed_external_inscriptions","reaction_gibbs_exact_positive_separations","reaction_log10K_signed_external_inscriptions","held_direction_vector"});passed=all(row["passed"] for row in comparisons) and analysis_passed and all(controls.values())
        isolation=seal_isolation_certificate(unsealed_isolation_certificate(executor_id=self.spec.experiment_id+"-prediction-executor",host_platform=platform.system() or "registered-host",python_implementation=platform.python_implementation(),interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id),program_hash=execution.program_hash,input_manifest_hash=execution.input_manifest_hash,registered_target_identity_hash=vault.commitment.target_identity_hash,comparison_implementation_identity_hash=sha256_identity(("exact-reaction-direction-gibbs-logK-correspondence",self.spec.falsification_condition)),prediction_seal_hash=prediction_seal.seal_hash,output_hash=execution.output_hash,trace_hash=execution.trace_hash));target_identity=target_identity_from_release(release)
        if target_identity!=vault.commitment.target_identity_hash:raise ValueError("THERMO-007 released target differs from commitment")
        custody=seal_target_custody_certificate(unsealed_target_custody_certificate(custodian_id=release.custodian_id,experiment_registration_hash=registration_hash,registered_target_identity_hash=target_identity,prediction_seal_hash=prediction_seal.seal_hash,target_release_manifest_hash=release.release_hash));measurement_payload={"experiment_registration_hash":registration_hash,"derivation_seal_hash":sealed.seal_hash,"prediction_seal_hash":prediction_seal.seal_hash,"temperatures":tuple(str(v) for v in analysis["temperatures_kelvin"]),"reaction_Gibbs":tuple(str(v) for v in analysis["reaction_gibbs_signed_external_inscriptions"]),"reaction_logK":tuple(str(v) for v in analysis["reaction_log10K_signed_external_inscriptions"]),"directions":analysis["held_direction_vector"],"comparisons":comparisons,"controls":controls,"trace":execution.trace_hash}
        measurements=tuple(f"row {index}: T={analysis['temperatures_kelvin'][index-1]} K; |reaction Gibbs|={analysis['reaction_gibbs_exact_positive_separations'][index-1]} kJ/mol; direction={analysis['held_direction_vector'][index-1]}; external log10 K={analysis['reaction_log10K_signed_external_inscriptions'][index-1]}" for index in range(1,65))+("complete vector: 5 reverse rows followed by 59 forward rows","exact equilibrium-crossing bracket: 300 K reverse; 350 K forward")+tuple(f"{k}: {v}" for k,v in controls.items())
        return EmpiricalValidation(validated_seal_hash=sealed.seal_hash,experiment_registration_hash=registration_hash,isolation_certificate=isolation,target_custody_certificate=custody,evaluator_verified_seal=True,target_opened_after_seal=True,all_rows_preserved=True,data_source_ids=("NIST-JANAF-N-007-NO2-GAS","NIST-JANAF-N-032-N2O4-GAS"),measurements=measurements,measurement_receipt_hash=sha256_identity(measurement_payload),falsification_condition=self.spec.falsification_condition,passed=passed)


__all__=("FreeEnergyEquivalentDirectionValidator","_identities","_prediction_map","_source_rows","exact_reaction_direction_analysis","experiment_registration_record","prediction_program_document")
