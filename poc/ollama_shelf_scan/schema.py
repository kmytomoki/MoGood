from typing import Literal, Optional

from pydantic import BaseModel, Field


UnitType = Literal["g", "kg", "ml", "L", "個", "枚", "本"]


class ShelfTagExtraction(BaseModel):
    product_name: str = Field(description="商品名")
    price_yen: int = Field(description="税込または税抜の価格（円）", ge=0)
    tax_included: Optional[bool] = Field(
        default=None, description="税込表記ならtrue、税抜表記ならfalse、不明ならnull"
    )
    quantity_value: float = Field(description="内容量または数量", gt=0)
    quantity_unit: UnitType = Field(description="単位")
