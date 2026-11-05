from dataclasses import dataclass, field
from datetime import datetime
from .money import Money
from .payment import Payment


@dataclass
class SaleLineItem:
    product_id: str
    name: str
    unit_price: Money
    quantity: int

    @property
    def subtotal(self) -> Money:
        return self.unit_price * self.quantity


@dataclass
class Sale:
    sale_id: str
    items: list = field(default_factory=list)
    payment: Payment | None = None
    created_at: datetime = field(default_factory=datetime.now)
    completed: bool = False

    def add_item(self, item: SaleLineItem) -> None:
        # Merge quantities when the same product is scanned twice
        for existing in self.items:
            if existing.product_id == item.product_id:
                existing.quantity += item.quantity
                return
        self.items.append(item)

    @property
    def total(self) -> Money:
        result = Money(0)
        for item in self.items:
            result = result + item.subtotal
        return result

    def complete(self, payment: Payment) -> None:
        if not self.items:
            raise ValueError("Cart is empty - cannot complete the sale")
        if payment.tendered < self.total:
            raise ValueError("Tendered amount is less than the amount due")
        self.payment = payment
        self.completed = True

    @property
    def change(self) -> Money:
        if not self.payment:
            return Money(0)
        return self.payment.tendered - self.total