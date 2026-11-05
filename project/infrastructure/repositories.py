from typing import Dict, List, Optional
from domain.product import Product
from domain.money import Money
from domain.sale import Sale
from domain.returns import ReturnRecord


class InMemoryProductRepository:
    def __init__(self):
        self._products: Dict[str, Product] = {}
        self._seed()

    def _seed(self):
        """Pre-loaded catalogue of 18 international products."""
        catalogue = [
            # ---- Soft drinks & water ----
            Product("P001", "Coca-Cola 330ml",            Money.from_dollars(1.50), 120),
            Product("P002", "Pepsi Cola 330ml",           Money.from_dollars(1.50), 100),
            Product("P003", "Evian Mineral Water 500ml",  Money.from_dollars(2.20), 150),
            Product("P004", "Sprite 330ml",               Money.from_dollars(1.40), 110),
            # ---- Snacks ----
            Product("P005", "Lay's Classic Chips 50g",    Money.from_dollars(2.99),  90),
            Product("P006", "Doritos Nacho Cheese 48g",   Money.from_dollars(3.49),  80),
            Product("P007", "Pringles Original 107g",     Money.from_dollars(4.49),  65),
            Product("P008", "Oreo Cookies 154g",          Money.from_dollars(4.29),  70),
            # ---- Chocolate & candy ----
            Product("P009", "Snickers Bar 50g",           Money.from_dollars(1.99), 110),
            Product("P010", "KitKat 4-Finger 41g",        Money.from_dollars(2.49),  95),
            Product("P011", "Ferrero Rocher 3pcs",        Money.from_dollars(3.99),  45),
            Product("P012", "M&M's Milk Chocolate 45g",   Money.from_dollars(2.79),  85),
            # ---- Coffee & tea ----
            Product("P013", "Nescafe Instant Coffee 100g", Money.from_dollars(6.99), 60),
            Product("P014", "Lipton Black Tea 25 bags",   Money.from_dollars(4.99),  55),
            Product("P015", "Starbucks Frappuccino 281ml", Money.from_dollars(3.29), 50),
            # ---- Energy drinks ----
            Product("P016", "Red Bull Energy Drink 250ml", Money.from_dollars(2.99), 85),
            # ---- Personal care ----
            Product("P017", "Colgate Toothpaste 100ml",   Money.from_dollars(3.79),  75),
            Product("P018", "Dove Soap Bar 100g",         Money.from_dollars(2.29), 100),
        ]
        for p in catalogue:
            self.add(p)

    def add(self, product: Product) -> None:
        self._products[product.product_id] = product

    def find_by_id(self, product_id: str) -> Optional[Product]:
        return self._products.get(product_id)

    def all(self) -> List[Product]:
        return list(self._products.values())


class InMemorySaleRepository:
    def __init__(self):
        self._sales: Dict[str, Sale] = {}

    def save(self, sale: Sale) -> None:
        self._sales[sale.sale_id] = sale

    def find_by_id(self, sale_id: str) -> Optional[Sale]:
        return self._sales.get(sale_id)

    def all(self) -> List[Sale]:
        return list(self._sales.values())


class InMemoryReturnRepository:
    def __init__(self):
        self._returns: List[ReturnRecord] = []

    def save(self, record: ReturnRecord) -> None:
        self._returns.append(record)

    def find_by_sale(self, sale_id: str) -> List[ReturnRecord]:
        return [r for r in self._returns if r.original_sale_id == sale_id]