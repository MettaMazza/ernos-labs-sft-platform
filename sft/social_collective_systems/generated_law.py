"""Pre-source candidate grammar for Social and Collective Sciences."""
from __future__ import annotations
from dataclasses import dataclass
from itertools import product
from sft.social_collective_systems.obligations import SOCIAL_OBLIGATIONS,FAMILY_ORDER,SocialObligation
from sft.social_collective_systems.structural_model import structural_witnesses

BASE_DEPENDENCIES=("SFT-FOUNDATION-ONE-001","SFT-FOUNDATION-FOLD-001","SFT-FOUNDATION-FOLD-DYNAMICS-001","SFT-MATH-EXACT-ARITHMETIC-001","SFT-MATH-GRAPH-NETWORK-001","SFT-MATH-ORDER-LATTICE-001","SFT-MATH-PROBABILITY-STATISTICS-001","SFT-MATH-OPTIMIZATION-001","SFT-MATH-DYNAMICAL-SYSTEMS-001","SFT-MATH-LOGIC-PROOF-001","SFT-INFO-QUANTITY-001","SFT-INFO-MUTUAL-CONDITIONAL-001","SFT-INFO-CHANNEL-CAPACITY-001","SFT-COMP-FORM-STATE-TRANSITION-001","SFT-COMP-DIST-CAUSALITY-001","SFT-COMP-DIST-COMMUNICATION-001","SFT-COMP-DIST-CONSENSUS-001","SFT-COMP-DIST-DISTRIBUTED-KNOWLEDGE-001","SFT-BIO-BIO-CAUSALITY-001","SFT-BIO-BIO-HANDOFF-001","SFT-CONSC-SUBJECT-CARRIER-001","SFT-CONSC-RED-EMPIRICAL-BOUNDARY-001","SFT-MED-CLINICAL-EVIDENCE-HANDOFF-001","SFT-EARTH-HAZARD-RISK-HANDOFF-001","SFT-ASTRO-ASTRO-HANDOFF-001")
@dataclass(frozen=True)
class Choice: name:str; properties:frozenset[str]; explanation:str
@dataclass(frozen=True)
class Dimension:
    key:str; required_property:str; choices:tuple[Choice,Choice]
    def validate(self):
        if len(self.choices)!=2 or len({x.name for x in self.choices})!=2 or sum(self.required_property in x.properties for x in self.choices)!=1: raise ValueError("invalid Social dimension")
def dimension(key,rejected,rejection,preserving,preservation):
    prop="preserves-"+key; return Dimension(key,prop,(Choice(rejected,frozenset(),rejection),Choice(preserving,frozenset((prop,)),preservation)))
@dataclass(frozen=True)
class SocialBlueprint:
    claim_id:str; title:str; family:str; statement:str; dependencies:tuple[str,...]; generation_rule:str; grammar_boundary:str; dimensions:tuple[Dimension,...]; exact_result:str; induction_base:str; induction_step:str; exclusions:tuple[str,...]; operational_witnesses:tuple[tuple[str,str,bool],...]; experiment_id:str; predicted_observation_label:str; falsification_condition:str
    def validate(self):
        if not self.claim_id.startswith("SFT-SOCIAL-") or len(self.dimensions)!=8: raise ValueError("invalid Social blueprint")
        for x in self.dimensions:x.validate()
        if not all(ok for _,_,ok in self.operational_witnesses): raise ValueError("Social witness failed")
        if self.exact_result!="__".join(x.name for x in unique_survivor(self)): raise ValueError("Social survivor changed")
def dimensions(x:SocialObligation): return (
 dimension("carrier","answer-only-or-decontextualized-carrier","The agents or collective carrier is erased.",x.carrier,"The claim-specific social carrier is retained."),
 dimension("boundary","population-time-or-context-erased","An unbounded social statement universalizes a context.",x.evidence_boundary,"Population, time, context and evidence boundary remain explicit."),
 dimension("relation","imported-fitted-or-status-selected-relation","A model, target, credential or consensus selects the relation.",x.relation,"Only generated relations and admitted dependencies act."),
 dimension("record","aggregate-or-favourable-output-only","An aggregate or favorable result erases agents, minorities and failures.",x.retained_record,"The complete reconstructible record is retained."),
 dimension("evidence","observation-report-model-value-conflated","Evidence, interpretation and value judgment substitute for one another.","evidence-and-normative-class-explicit","Observation, report, archive, inference, model, forecast, missing and normative judgment remain distinct."),
 dimension("provenance","prestige-prior-answer-or-target-selected","Institutional status or an earlier answer selects the law.","root-bound-forward-forcing","The result traces through admitted dependencies to There Is No Nothing."),
 dimension("generality","one-group-one-period-universalized","A favorable case erases context and cross-group differences.","positive-finite-extension-retains-all-contexts","Every finite extension retains favorable, adverse, absent and unresolved contexts."),
 dimension("extension","free-weight-exception-or-opaque-oracle","A fitted weight or opaque classifier manufactures the conclusion.","no-extra-rule","No rule beyond registered structure is introduced."))
def candidate_forms(bp): return tuple(tuple(x) for x in product(*(d.choices for d in bp.dimensions)))
def candidate_preserves(bp,form): return len(form)==8 and all(d.required_property in c.properties for d,c in zip(bp.dimensions,form))
def unique_survivor(bp):
    x=tuple(r for r in candidate_forms(bp) if candidate_preserves(bp,r))
    if len(x)!=1: raise ValueError("Social grammar did not yield one survivor")
    return x[0]
def family_witness(f):
    w=structural_witnesses(); m={FAMILY_ORDER[0]:w["agents_distinct"] and w["directed_relation_retained"],FAMILY_ORDER[1]:w["evidence_classes_distinct"],FAMILY_ORDER[2]:w["period_two_reciprocity"],FAMILY_ORDER[3]:w["ordered_history"],FAMILY_ORDER[4]:w["aggregation_loses_unheld_predecessor"],FAMILY_ORDER[5]:w["allocation_closes"],FAMILY_ORDER[6]:w["directed_relation_retained"],FAMILY_ORDER[7]:w["period_three_collective_recurrence"],FAMILY_ORDER[8]:w["three_member_partition"],FAMILY_ORDER[9]:w["joint_group_product"] and w["aggregation_loses_unheld_predecessor"],FAMILY_ORDER[10]:w["ordered_history"],FAMILY_ORDER[11]:w["evidence_classes_distinct"]}; return m[f]
def build():
    out=[]; family_terminal=None
    for f in FAMILY_ORDER:
        rows=[x for x in SOCIAL_OBLIGATIONS if x.family==f]; local=None
        for x in rows:
            deps=tuple(dict.fromkeys(BASE_DEPENDENCIES+(() if family_terminal is None else (family_terminal,))+(() if local is None else (local,))))
            bp=SocialBlueprint(x.claim_id,x.title,x.family,x.statement,deps,"Generate the literal Cartesian product of eight preregistered binary carrier, boundary, relation, record, evidence, provenance, generality and extension dimensions before external source identities or outcomes are opened; filter only by registered preservation properties.","Exactly eight binary dimensions: 256 forms. Structural closure is depth-independent for positive finite contextual extension; empirical correspondence remains population, place, period, method and protocol bounded.",dimensions(x),"","The least social carrier retains identified agents, typed relation, context, record, evidence class and root provenance.","Adding one lawful finite agent, relation, group, context, period or record preserves earlier identities, minority states, adverse rows and boundaries and appends its trace.",( "semantic numerical zero","negative proof quantity","irrational or imaginary proof value","completed infinity","ungenerated continuum","free or fitted parameter","target-selected survivor","prior answer as premise","credential or prestige as evidence","consensus vote as proof","normative judgment relabelled observation","aggregate relabelled individual state","erased minority adverse missing or unresolved row"),(("carrier","carrier nonempty",bool(x.carrier)),("relation","carrier and relation differ",x.carrier!=x.relation),("boundary","boundary and carrier differ",x.evidence_boundary!=x.carrier),("fold","family witness reproduces",family_witness(x.family))),"SFT-EXP-"+x.claim_id.removeprefix("SFT-")+"-E1","social:"+"__".join((x.carrier,x.relation,x.retained_record,x.evidence_boundary)),x.falsification_condition)
            bp=SocialBlueprint(**{**bp.__dict__,"exact_result":"__".join(c.name for c in unique_survivor(bp))}); bp.validate(); out.append(bp); local=x.claim_id
        family_terminal=rows[-1].claim_id
    return tuple(out)
SOCIAL_BLUEPRINTS=build(); BLUEPRINT_BY_CLAIM={x.claim_id:x for x in SOCIAL_BLUEPRINTS}
if len(SOCIAL_BLUEPRINTS)!=72 or len(BLUEPRINT_BY_CLAIM)!=72 or any(len(candidate_forms(x))!=256 for x in SOCIAL_BLUEPRINTS): raise ValueError("Social candidate census failed")
