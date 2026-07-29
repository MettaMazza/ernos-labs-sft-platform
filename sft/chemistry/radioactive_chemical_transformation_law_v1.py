"""Fold-native radioactive chemical transformation network (NUCHEM-002)."""
from dataclasses import dataclass
from sft.claim_evidence import EMPTY_ONE
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import dimension

@dataclass(frozen=True)
class ChemicalDecayEdge:
    parent: HeldLabel; daughter: HeldLabel; parent_species: HeldLabel; daughter_species: HeldLabel; channel: HeldLabel; events: PositiveCount
    def __post_init__(self):
        if (self.parent.family,self.daughter.family,self.parent_species.family,self.daughter_species.family,self.channel.family)!=("parent-nuclide","daughter-nuclide","parent-species","daughter-species","decay-channel"):raise InadmissibleExactValue("complete parent/daughter chemical edge required")

def network(edges):
 if not edges:return EMPTY_ONE
 if len({(e.parent,e.daughter,e.channel) for e in edges})!=len(edges):raise InadmissibleExactValue("duplicate decay edge")
 return tuple(edges)
DEPENDENCIES=("SFT-FOUNDATION-FORM-ENFORCEMENT-001","SFT-MATH-GRAPH-NETWORK-001","SFT-PHYS-NUCLEAR-RADIOACTIVE-DECAY-TERMINAL-005","SFT-CHEM-NET-REACTION-001","SFT-CHEM-ELEM-ISOTOPE-001","SFT-CHEM-NUCLEAR-CHEMICAL-CARRIER-001")
DIMENSIONS=(dimension("parent","parent-number-only","Parent number loses identity.","held-parent-nuclide","Parent nuclide held."),dimension("daughter","anonymous-product","Product loses daughter identity.","held-daughter-nuclide","Daughter nuclide held."),dimension("chemistry","nuclear-edge-only","Chemical states would be lost.","held-parent-daughter-species","Both chemical species remain."),dimension("channel","unlabelled-transition","Channel identity is required.","held-decay-channel","Channel remains held."),dimension("events","continuum-decay-flow","Flow hides events.","positive-counted-transformations","Events are counted."),dimension("network","selected-decay-edge","One edge hides branching.","complete-directed-transformation-network","Every edge remains."),dimension("absence","numerical-zero-daughter","Numerical zero is not native absence.","structural-EmptyOne-no-edge","No edge is structural absence."),dimension("extension","daughter-overwrites-parent","Overwriting destroys reconstruction.","successor-retains-prior-network","Every successor preserves prior edges."))
EXACT_RESULT="held-parent-nuclide__held-daughter-nuclide__held-parent-daughter-species__held-decay-channel__positive-counted-transformations__complete-directed-transformation-network__structural-EmptyOne-no-edge__successor-retains-prior-network"
def _e(n=1):return ChemicalDecayEdge(HeldLabel("parent-nuclide","p"),HeldLabel("daughter-nuclide","d"),HeldLabel("parent-species","ps"),HeldLabel("daughter-species","ds"),HeldLabel("decay-channel",str(n)),PositiveCount(n))
OPERATIONAL_WITNESSES=(("parent","Parent held.",_e().parent.label=="p"),("daughter","Daughter held.",_e().daughter.label=="d"),("species","Both species held.",_e().parent_species.label!="" and _e().daughter_species.label!=""),("channel","Channel held.",_e().channel.label=="1"),("events","Events positive.",_e().events.value==1),("network","Edge retained.",len(network((_e(),)))==1),("absence","No edge is EmptyOne.",network(())==EMPTY_ONE),("successor","Two distinct edges retained.",len(network((_e(1),_e(2))))==2))
