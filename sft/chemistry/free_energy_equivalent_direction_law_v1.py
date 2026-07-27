"""Fold-native free-energy-equivalent reaction direction law for THERMO-007."""

from __future__ import annotations

from dataclasses import dataclass

from sft.claim_evidence import EmptyOne, PositiveRatio
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import LawDimension, dimension


def _ratio(value) -> PositiveRatio:return PositiveRatio.from_pair(value.numerator,value.denominator)


@dataclass(frozen=True)
class ReactionPathAccount:
    path_identity: HeldLabel
    reaction_boundary: HeldLabel
    condition_identity: HeldLabel
    retained_energy_requirement: PositiveRatio
    closed_distinction_count: PositiveCount

    def __post_init__(self):
        required=((self.path_identity,"reaction-path"),(self.reaction_boundary,"reaction-boundary"),(self.condition_identity,"reaction-condition"))
        if any(not isinstance(value,HeldLabel) or value.family!=family for value,family in required):raise InadmissibleExactValue("reaction path account lost a held identity")
        if self.path_identity.label not in {"forward-path","reverse-path"}:raise InadmissibleExactValue("reaction account requires forward or reverse path")
        if not isinstance(self.retained_energy_requirement,PositiveRatio) or not isinstance(self.closed_distinction_count,PositiveCount):raise InadmissibleExactValue("reaction account requires exact positive energy and distinction support")


@dataclass(frozen=True)
class ReactionDirectionResult:
    orientation: HeldLabel
    energy_separation: PositiveRatio|EmptyOne
    distinction_separation: PositiveCount|EmptyOne


def free_energy_equivalent_direction(forward:ReactionPathAccount,reverse:ReactionPathAccount)->ReactionDirectionResult:
    """Compare complete retained energy and closed-distinction accounts by exact product order."""
    if not isinstance(forward,ReactionPathAccount) or not isinstance(reverse,ReactionPathAccount):raise InadmissibleExactValue("direction requires complete forward/reverse accounts")
    if forward.path_identity.label!="forward-path" or reverse.path_identity.label!="reverse-path":raise InadmissibleExactValue("direction accounts are not ordered forward then reverse")
    if forward.reaction_boundary!=reverse.reaction_boundary or forward.condition_identity!=reverse.condition_identity:raise InadmissibleExactValue("direction comparison changed reaction boundary or conditions")
    fe,fd=forward.retained_energy_requirement.fraction,forward.closed_distinction_count.value
    re,rd=reverse.retained_energy_requirement.fraction,reverse.closed_distinction_count.value
    if fe==re and fd==rd:return ReactionDirectionResult(HeldLabel("reaction-direction","equilibrium"),EmptyOne(),EmptyOne())
    forward_no_greater=fe<=re and fd<=rd;reverse_no_greater=re<=fe and rd<=fd
    if forward_no_greater and (fe<re or fd<rd):orientation="forward-favoured"
    elif reverse_no_greater and (re<fe or rd<fd):orientation="reverse-favoured"
    else:raise InadmissibleExactValue("incomparable path accounts do not force a reaction direction")
    energy=EmptyOne() if fe==re else _ratio(re-fe if re>fe else fe-re)
    distinction=EmptyOne() if fd==rd else PositiveCount(rd-fd if rd>fd else fd-rd)
    return ReactionDirectionResult(HeldLabel("reaction-direction",orientation),energy,distinction)


def common_successor_preserves_direction(forward:ReactionPathAccount,reverse:ReactionPathAccount,energy_extension:PositiveRatio,distinction_extension:PositiveCount)->bool:
    if not isinstance(energy_extension,PositiveRatio) or not isinstance(distinction_extension,PositiveCount):raise InadmissibleExactValue("common successor requires exact positive additions")
    prior=free_energy_equivalent_direction(forward,reverse)
    def extend(account):
        return ReactionPathAccount(account.path_identity,account.reaction_boundary,account.condition_identity,_ratio(account.retained_energy_requirement.fraction+energy_extension.fraction),PositiveCount(account.closed_distinction_count.value+distinction_extension.value))
    return free_energy_equivalent_direction(extend(forward),extend(reverse)).orientation==prior.orientation


DEPENDENCIES=(
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001","SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001","SFT-MATH-EXACT-ARITHMETIC-001","SFT-MATH-ORDER-LATTICE-001","SFT-INFO-CONSERVATION-LOSS-001","SFT-INFO-ENTROPY-UNCERTAINTY-001","SFT-PHYS-THERMO-SECOND-LAW-001","SFT-PHYS-THERMO-STATE-RELATION-001","SFT-CHEM-RXN-IDENTITY-001","SFT-CHEM-EQ-CHEMICAL-001","SFT-CHEM-THERMO-DIRECTION-001","SFT-CHEM-INTERNAL-ENERGY-COMPOSITION-003","SFT-CHEM-HEAT-WORK-TRANSFER-PARTITION-004","SFT-CHEM-ENTROPY-MULTIPLICITY-CORRESPONDENCE-005","SFT-CHEM-ENTHALPY-EQUIVALENT-STATE-006",
)


DIMENSIONS:tuple[LawDimension,...]=(
    dimension("paths","single-path-or-answer-only-direction","One path or an answer label cannot establish comparative direction.","complete-forward-and-reverse-path-accounts","Both paths retain boundary, conditions, energy and distinction support."),
    dimension("energy","signed-or-fitted-free-energy-scalar","A signed or fitted scalar imports an equation and erases energy provenance.","exact-positive-retained-energy-requirements","Each path retains its complete exact positive energy requirement."),
    dimension("distinctions","entropy-logarithm-or-omitted-distinction-cost","A logarithm or omitted cost imports a convention and loses closed distinctions.","exact-positive-closed-distinction-counts","Each path retains the exact positive count of distinctions observation closes."),
    dimension("order","weighted-sum-or-target-selected-comparison","A weighted scalar requires a free trade-off and may select the target.","strict-exact-product-support-order","Direction is forced only when one complete account is no greater on both axes and strict on at least one."),
    dimension("orientation","negative-direction-value-or-forced-tie-break","A sign or tie-break invents content not present in the accounts.","held-forward-reverse-or-EmptyOne-equilibrium","Orientation is held; exact equality yields structural EmptyOne separations and equilibrium."),
    dimension("prediction","Gibbs-logK-or-direction-target-readable-before-seal","Target values could select the ordering rule.","complete-value-free-reaction-state-identity-seal","All reaction-row identities seal before temperature, Gibbs, log-K or direction values open."),
    dimension("record","selected-temperature-or-single-direction-showcase","A selected row can hide a direction reversal or adverse record.","complete-64-row-two-direction-crossing-vector","Every common finite JANAF row and the complete crossing are retained."),
    dimension("extension","refit-order-after-shared-successor","Refitting destroys invariance under a common retained addition.","depth-independent-common-account-successor","Adding the same positive account to both paths preserves their exact order."),
)


EXACT_RESULT=("complete-forward-and-reverse-path-accounts__exact-positive-retained-energy-requirements__exact-positive-closed-distinction-counts__strict-exact-product-support-order__held-forward-reverse-or-EmptyOne-equilibrium__complete-value-free-reaction-state-identity-seal__complete-64-row-two-direction-crossing-vector__depth-independent-common-account-successor")


def _account(path,energy,distinctions):return ReactionPathAccount(HeldLabel("reaction-path",path),HeldLabel("reaction-boundary","held-reaction"),HeldLabel("reaction-condition","held-condition"),PositiveRatio.from_pair(energy,3),PositiveCount(distinctions))
def _witnesses():
    forward=_account("forward-path",5,2);reverse=_account("reverse-path",8,3);equal_forward=_account("forward-path",5,2);equal_reverse=_account("reverse-path",5,2)
    result=free_energy_equivalent_direction(forward,reverse);equilibrium=free_energy_equivalent_direction(equal_forward,equal_reverse);incomparable=False
    try:free_energy_equivalent_direction(_account("forward-path",5,4),_account("reverse-path",8,2))
    except InadmissibleExactValue:incomparable=True
    return (("forward-order","Lower energy and distinction account forces forward orientation.",result.orientation.label=="forward-favoured"),("positive-separations","Direction retains exact positive separations.",result.energy_separation==PositiveRatio.from_pair(1,1) and result.distinction_separation==PositiveCount(1)),("equilibrium-EmptyOne","Equal complete accounts force equilibrium with structural EmptyOne separations.",equilibrium.orientation.label=="equilibrium" and isinstance(equilibrium.energy_separation,EmptyOne) and isinstance(equilibrium.distinction_separation,EmptyOne)),("incomparable-halts","Crossed accounts do not receive an arbitrary weighted direction.",incomparable),("common-successor","A common positive addition preserves exact direction.",common_successor_preserves_direction(forward,reverse,PositiveRatio.from_pair(7,5),PositiveCount(2))))


OPERATIONAL_WITNESSES=_witnesses()
__all__=("DEPENDENCIES","DIMENSIONS","EXACT_RESULT","OPERATIONAL_WITNESSES","ReactionDirectionResult","ReactionPathAccount","common_successor_preserves_direction","free_energy_equivalent_direction")
