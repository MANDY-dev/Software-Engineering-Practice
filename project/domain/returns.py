from dataclasses import dataclass, field
from datetime import datetime
from .money import Money


@dataclass
class ReturnLineItem:
    product_id: str
    name: str
    unit_price: Money
    quantity: int

    @property
    def subtotal(self) -> Money:
        return self.unit_price * self.quantity


@dataclass
class ReturnRecord:
    return_id: str
    original_sale_id: str
    items: list = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

    def add_item(self, item: ReturnLineItem) -> None:
        for existing in self.items:
            if existing.product_id == item.product_id:
                existing.quantity += item.quantity
                return
        self.items.append(item)

    @property
    def total_refund(self) -> Money:
        result = Money(0)
        for item in self.items:
            result = result + item.subtotal
        return result