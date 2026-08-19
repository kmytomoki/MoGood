from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from schema import UnitType

PriceBasis = Literal["per_100g", "per_100ml", "per_item"]


@dataclass
class UnitPriceResult:
    unit_price_yen: float
    basis: PriceBasis
    normalized_quantity: float
    normalized_unit: str


def compute_unit_price(price_yen: int, quantity_value: float, quantity_unit: UnitType) -> UnitPriceResult:
    if price_yen < 0:
        raise ValueError("price_yen must be non-negative")
    if quantity_value <= 0:
        raise ValueError("quantity_value must be greater than zero")

    if quantity_unit in ("g", "kg"):
        grams = quantity_value * 1000.0 if quantity_unit == "kg" else quantity_value
        unit_price = (price_yen / grams) * 100.0
        return UnitPriceResult(
            unit_price_yen=round(unit_price, 2),
            basis="per_100g",
            normalized_quantity=grams,
            normalized_unit="g",
        )

    if quantity_unit in ("ml", "L"):
        ml = quantity_value * 1000.0 if quantity_unit == "L" else quantity_value
        unit_price = (price_yen / ml) * 100.0
        return UnitPriceResult(
            unit_price_yen=round(unit_price, 2),
            basis="per_100ml",
            normalized_quantity=ml,
            normalized_unit="ml",
        )

    if quantity_unit in ("個", "枚", "本"):
        unit_price = price_yen / quantity_value
        return UnitPriceResult(
            unit_price_yen=round(unit_price, 2),
            basis="per_item",
            normalized_quantity=quantity_value,
            normalized_unit=quantity_unit,
        )

    raise ValueError(f"Unsupported quantity_unit: {quantity_unit}")
