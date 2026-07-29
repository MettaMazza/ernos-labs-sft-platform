"""Fold-native nuclide chemical carrier law (NUCHEM-001)."""
from dataclasses import dataclass
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import dimension

@dataclass(frozen=True)
class NuclideChemicalCarrier:
    element: HeldLabel; nucleon_count: PositiveCount; nuclear_state: HeldLabel; species: HeldLabel; phase: HeldLabel; occurrence: PositiveCount
    def __post_init__(self):
        if (self.element.family,self.nuclear_state.family,self.species.family,self.phase.family)!=("element","nuclear-state","chemical-species","chemical-phase"):raise InadmissibleExactValue("complete nuclide chemical carrier required")

DEPENDENCIES=("SFT-FOUNDATION-FORM-ENFORCEMENT-001","SFT-MATH-EXACT-ARITHMETIC-001","SFT-CHEM-MEAS-CHEMICAL-SPECIES-001","SFT-CHEM-ELEM-ISOTOPE-001","SFT-PHYS-NUCLEAR-RADIOACTIVITY-001")
DIMENSIONS=(dimension("element","anonymous-radiation","Radiation alone loses element.","held-element-identity","Element remains held."),dimension("nuclide","element-only-identity","Element alone collapses isotopes.","positive-nucleon-count","Nucleon count distinguishes nuclide."),dimension("state","ground-state-assumption","Nuclear state cannot be assumed.","held-nuclear-state","Nuclear state remains held."),dimension("species","bare-nuclide-answer","Chemistry requires species identity.","held-chemical-species","Chemical carrier remains held."),dimension("phase","phase-free-species","Phase affects the chemical record.","held-chemical-phase","Phase remains held."),dimension("occurrence","continuum-amount-premise","Continuum amount hides occurrences.","positive-counted-occurrence","Each occurrence is counted."),dimension("record","selected-nuclide-row","One row hides carrier diversity.","complete-nuclide-species-vector","Every registered carrier remains."),dimension("extension","lookup-table-exception","A lookup cannot define identity.","fresh-occurrence-preserves-identity","Successors preserve every coordinate."))
EXACT_RESULT="held-element-identity__positive-nucleon-count__held-nuclear-state__held-chemical-species__held-chemical-phase__positive-counted-occurrence__complete-nuclide-species-vector__fresh-occurrence-preserves-identity"
def _w():
 r=NuclideChemicalCarrier(HeldLabel("element","strontium"),PositiveCount(90),HeldLabel("nuclear-state","held"),HeldLabel("chemical-species","solution-carrier"),HeldLabel("chemical-phase","aqueous"),PositiveCount(1))
 return (("element","Element held.",r.element.label=="strontium"),("nuclide","Count positive.",r.nucleon_count.value==90),("state","State held.",r.nuclear_state.label=="held"),("species","Species held.",r.species.label=="solution-carrier"),("phase","Phase held.",r.phase.label=="aqueous"),("occurrence","Occurrence positive.",r.occurrence.value==1),("distinct","Coordinates distinct.",len({r.element.family,r.species.family,r.phase.family})==3),("successor","Fresh occurrence preserves identity.",r.__class__(r.element,r.nucleon_count,r.nuclear_state,r.species,r.phase,PositiveCount(2)).species==r.species))
OPERATIONAL_WITNESSES=_w()
