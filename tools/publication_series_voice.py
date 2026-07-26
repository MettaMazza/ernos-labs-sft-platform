"""Shared editorial constitution for the SFT branch-paper series.

This module changes publication prose only.  It does not import, call or modify
the admission engine, claim implementations, receipts or scientific results.
"""


def open_science_position(branch_consequence: str) -> str:
    """Return the required authorship, access, rights and admission statement."""

    return f"""## Public scientific mission and admission boundary

Ernos Labs is an open-source science movement, verification platform and public
tree of knowledge founded by Maria Smith. Its purpose is not to replace one
authority with another. It is to make scientific authority narrow, inspectable
and revocable: a claim is admitted only through its complete derivation chain,
generated alternatives, eliminations, unique survivor, adverse controls,
measurement custody where applicable and unchanged-engine receipt. Open
criticism is unrestricted and necessary; scientific admission is the separate
machine-checked act of satisfying that public standard.

Maria Smith developed Smithian Fold Theory outside formal academic education,
institutional research employment and conventional grant funding. That fact is
not offered as evidence for a theorem; the derivations and observations carry
the entire scientific burden. It is evidence about access. A credential-first
system loses more than individual opportunity: it loses unknown questions,
methods and discoveries from minds that capital and status never authorize.
This work therefore treats Maria Smith's authorship neither as exceptionalism
nor as a reason for dismissal, but as an indictment of every scientific
contribution lost when financial gatekeeping is presented as rigor.

The institutional argument is empirical, not a claim that every institution or
funded researcher acts in bad faith. Published studies document sponsor-linked
differences in outcomes and conclusions, commercial influence over research
agendas, limits and sensitivities in grant review, underpublication of null
results, and inequalities created by paywalls and article-processing charges.
Those findings establish that funding, prestige, publication and consensus are
selection systems with incentives and failure modes. They cannot substitute for
a public proof and evidence chain. Expertise, measurement and adversarial review
remain indispensable; institutional permission does not select a fundamental
law.

{branch_consequence}

Maria Smith retains copyright and scientific authorship. Papers and
documentation are licensed CC BY 4.0 and code is licensed Apache-2.0, permitting
inspection, copying, criticism, reproduction, modification and redistribution
with attribution. “Ernos Labs” is a separate, revocable standards-conformance
designation. A reuse or fork may use the open work under its licences, but may
describe itself as Ernos Labs only while it preserves the public empirical
constitution, complete adverse evidence, unchanged admission route, critical
review and community standards.

Independent replications, lawful extensions, corrections and attempted
invalidations are invited. Credentials cannot rescue a failed gate and lack of
credentials cannot prevent a reproducible result from being evaluated. Contact
Maria.Smith.Sftoe@gmail.com, submit through https://discord.gg/ucwGryVxGr, or
inspect the public project at https://github.com/MettaMazza.
"""


OPEN_SCIENCE_REFERENCES = """- Lundh A et al. *Conflicts of interest at the European Medicines Agency: a policy analysis*. 2018. https://doi.org/10.1007/s00134-018-5293-7.
- Fabbri A et al. *The influence of industry sponsorship on the research agenda*. 2018. https://pubmed.ncbi.nlm.nih.gov/30252531/.
- Gallo SA et al. *Reliability and fairness in peer review of research funding*. 2023. https://pmc.ncbi.nlm.nih.gov/articles/PMC10553257/.
- Demicheli V and Di Pietrantonj C. *Peer review for improving the quality of grant applications*. Cochrane review and archive. https://pmc.ncbi.nlm.nih.gov/articles/PMC8973940/.
- UNESCO. *Recommendation on Open Science*. 2021. https://www.unesco.org/en/legal-affairs/recommendation-open-science.
- NIST. *Artificial Intelligence Risk Management Framework 1.0*. https://airc.nist.gov/airmf-resources/airmf/3-sec-characteristics/.
"""
