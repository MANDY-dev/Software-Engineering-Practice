from dataclasses import dataclass
from .money import Money


@dataclass
class Product:
    product_id: str
    name: str
    price: Money
    stock: int

    def has_stock(self, qty: int) -> bool:
        return self.stock >= qty

    def decrease_stock(self, qty: int) -> None:
        if not self.has_stock(qty):
            raise ValueError(f"Insufficient stock for {self.name}")
        self.stock -= qty

    def increase_stock(self, qty: int) -> None:
        self.stock += qty