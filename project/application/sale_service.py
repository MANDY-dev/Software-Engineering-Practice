import uuid
from domain.money import Money
from domain.sale import Sale, SaleLineItem
from domain.payment import Payment


class SaleService:
    """Process Sale use case."""

    def __init__(self, product_repo, sale_repo):
        self.product_repo = product_repo
        self.sale_repo = sale_repo
        self._current: Sale | None = None

    @property
    def current_sale(self) -> Sale | None:
        return self._current

    def start_sale(self) -> Sale:
        self._current = Sale(sale_id=self._new_id())
        return self._current

    def scan_item(self, product_id: str, quantity: int = 1) -> Sale:
        if not self._current:
            raise RuntimeError("No active sale - please start a new sale first")
        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero")

        product = self.product_repo.find_by_id(product_id)
        if not product:
            raise ValueError(f"Product not found: {product_id}")

        already = sum(i.quantity for i in self._current.items
                      if i.product_id == product_id)
        if already + quantity > product.stock:
            raise ValueError(
                f"Insufficient stock for {product.name} "
                f"(in stock: {product.stock}, already scanned: {already})")

        self._current.add_item(SaleLineItem(
            product_id=product.product_id,
            name=product.name,
            unit_price=product.price,
            quantity=quantity,
        ))
        return self._current

    def make_payment(self, tendered_dollars: float) -> Sale:
        if not self._current:
            raise RuntimeError("No active sale - please start a new sale first")

        sale = self._current
        payment = Payment(amount_due=sale.total,
                          tendered=Money.from_dollars(tendered_dollars))
        sale.complete(payment)

        # Transactional stock update
        for item in sale.items:
            product = self.product_repo.find_by_id(item.product_id)
            product.decrease_stock(item.quantity)

        self.sale_repo.save(sale)
        self._current = None
        return sale

    def cancel_sale(self) -> None:
        self._current = None

    def _new_id(self) -> str:
        return "S" + uuid.uuid4().hex[:8].upper()