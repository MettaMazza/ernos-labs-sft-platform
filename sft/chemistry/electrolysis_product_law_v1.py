"""Fold-native electrolysis and product-amount law (ECHEM-006)."""
from __future__ import annotations

from dataclasses import dataclass

from sft.claim_evidence import EMPTY_ONE, EmptyOne, PositiveRatio
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import LawDimension, dimension


@dataclass(frozen=True)
class ElectrolysisAccount:
    process_identity: HeldLabel
    electrode_path: HeldLabel
    product_identity: HeldLabel
    condition: HeldLabel
    transferred_carriers: PositiveCount
    carriers_per_product: PositiveCount

    def __post_init__(self) -> None:
        required = (
            (self.process_identity, "electrolysis-process"), (self.electrode_path, "electrode-path"),
            (self.product_identity, "chemical-product"), (self.condition, "electrochemical-condition"),
        )
        if any(row.family != family for row, family in required):
            raise InadmissibleExactValue("electrolysis account lost process, path, product or condition custody")
        if not isinstance(self.transferred_carriers, PositiveCount) or not isinstance(self.carriers_per_product, PositiveCount):
            raise InadmissibleExactValue("electrolysis carrier accounts must be positive exact counts")


@dataclass(frozen=True)
class ProductAmountResult:
    complete_products: PositiveCount | EmptyOne
    retained_carrier_remainder: PositiveCount | EmptyOne
    exact_product_amount: PositiveRatio
    product_identity: HeldLabel
    electrode_path: HeldLabel


def electrolysis_product_amount(account: ElectrolysisAccount) -> ProductAmountResult:
    complete, remainder = divmod(account.transferred_carriers.value, account.carriers_per_product.value)
    return ProductAmountResult(
        PositiveCount(complete) if complete else EMPTY_ONE,
        PositiveCount(remainder) if remainder else EMPTY_ONE,
        PositiveRatio(account.transferred_carriers, account.carriers_per_product),
        account.product_identity,
        account.electrode_path,
    )


def compose_carrier_batches(first: ElectrolysisAccount, second: ElectrolysisAccount) -> ElectrolysisAccount:
    if (first.process_identity, first.electrode_path, first.product_identity, first.condition, first.carriers_per_product) != (second.process_identity, second.electrode_path, second.product_identity, second.condition, second.carriers_per_product):
        raise InadmissibleExactValue("only like electrolysis carrier batches compose")
    return ElectrolysisAccount(first.process_identity, first.electrode_path, first.product_identity, first.condition, PositiveCount(first.transferred_carriers.value + second.transferred_carriers.value), first.carriers_per_product)


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001", "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
    "SFT-MATH-EXACT-ARITHMETIC-001", "SFT-MATH-COMBINATORICS-001",
    "SFT-INFO-CONSERVATION-LOSS-001", "SFT-PHYS-PLASMA-COLLECTIVE-001",
    "SFT-CHEM-STOICH-COMPOSITION-001", "SFT-CHEM-STOICH-CONSERVATION-001",
    "SFT-CHEM-HALF-REACTION-IDENTITY-ORIENTATION-001", "SFT-CHEM-ELECTROCHEMICAL-WORK-REACTION-DIRECTION-005",
)

DIMENSIONS: tuple[LawDimension, ...] = (
    dimension("custody", "mass-answer-only", "A mass answer loses electrolysis identity and path.", "complete-process-electrode-product-custody", "Process, electrode path, product and condition remain held."),
    dimension("charge", "continuous-charge-premise", "A continuum charge does not expose transferred distinctions.", "positive-counted-transfer-occurrences", "Transferred carriers are exact positive occurrences."),
    dimension("stoichiometry", "empirical-equivalent-factor", "A fitted equivalent factor does not retain carrier demand.", "positive-carriers-per-product-occurrence", "Product demand is a positive stoichiometric carrier count."),
    dimension("amount", "rounded-product-count", "Rounding destroys exact carrier custody.", "exact-carrier-to-product-ratio", "Product amount is the exact positive ratio of transferred carriers to required carriers."),
    dimension("remainder", "discarded-incomplete-product", "Discarding a remainder loses transferred distinctions.", "complete-products-plus-held-remainder", "Complete products and any remaining carriers are separately retained."),
    dimension("absence", "numerical-zero-product", "Numerical zero is not a native product magnitude.", "structural-EmptyOne-no-complete-product", "Insufficient carriers close the complete-product field to EmptyOne."),
    dimension("record", "selected-coulometer-result", "A selected mass-per-charge value can hide experimental corrections.", "complete-charge-product-amount-vector", "Every registered run, correction, uncertainty and adverse row remains downstream."),
    dimension("composition", "batch-specific-conversion", "A batch-specific rule adds an unforced parameter.", "like-batches-compose-by-counted-addition", "Like carrier batches compose without changing the product rule."),
)

EXACT_RESULT = "complete-process-electrode-product-custody__positive-counted-transfer-occurrences__positive-carriers-per-product-occurrence__exact-carrier-to-product-ratio__complete-products-plus-held-remainder__structural-EmptyOne-no-complete-product__complete-charge-product-amount-vector__like-batches-compose-by-counted-addition"


def _account(transferred: int, required: int = 2) -> ElectrolysisAccount:
    return ElectrolysisAccount(HeldLabel("electrolysis-process", "test"), HeldLabel("electrode-path", "cathode"), HeldLabel("chemical-product", "product"), HeldLabel("electrochemical-condition", "held"), PositiveCount(transferred), PositiveCount(required))


def _witnesses() -> tuple[tuple[str, str, bool], ...]:
    exact = electrolysis_product_amount(_account(4))
    remainder = electrolysis_product_amount(_account(5))
    insufficient = electrolysis_product_amount(_account(1))
    composed = electrolysis_product_amount(compose_carrier_batches(_account(2), _account(2)))
    mismatch = False
    try:
        compose_carrier_batches(_account(2), _account(2, 3))
    except InadmissibleExactValue:
        mismatch = True
    return (
        ("exact-ratio", "Five transferred carriers for two per product retain five-halves.", remainder.exact_product_amount.fraction.numerator == 5 and remainder.exact_product_amount.fraction.denominator == 2),
        ("complete-products", "Four carriers yield two complete products.", exact.complete_products.value == 2),
        ("remainder", "One incomplete carrier remains held.", remainder.retained_carrier_remainder.value == 1),
        ("absence", "Insufficient carriers close complete products to EmptyOne.", insufficient.complete_products == EMPTY_ONE),
        ("no-remainder", "Exact division closes remainder to EmptyOne.", exact.retained_carrier_remainder == EMPTY_ONE),
        ("identity", "Product identity remains held.", exact.product_identity.family == "chemical-product"),
        ("batch-composition", "Like batches compose exactly.", composed.complete_products.value == 2),
        ("mismatch-control", "Unlike stoichiometric batches halt.", mismatch),
    )


OPERATIONAL_WITNESSES = _witnesses()

__all__ = ("DEPENDENCIES", "DIMENSIONS", "EXACT_RESULT", "ElectrolysisAccount", "OPERATIONAL_WITNESSES", "ProductAmountResult", "compose_carrier_batches", "electrolysis_product_amount")
