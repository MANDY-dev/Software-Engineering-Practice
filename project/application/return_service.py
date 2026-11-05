import uuid
from domain.returns import ReturnRecord, ReturnLineItem


class ReturnService:
    """Handle Returns use case."""

    def __init__(self, product_repo, sale_repo, return_repo):
        self.product_repo = product_repo
        self.sale_repo = sale_repo
        self.return_repo = return_repo
        self._current: ReturnRecord | None = None
        self._original_sale = None

    @property
    def current_return(self) -> ReturnRecord | None:
        return self._current

    def start_return(self, sale_id: str) -> ReturnRecord:
        sale = self.sale_repo.find_by_id(sale_id)
        if not sale or not sale.completed:
            raise ValueError(f"No completed sale found for ID: {sale_id}")
        self._original_sale = sale
        self._current = ReturnRecord(return_id=self._new_id(),
                                     original_sale_id=sale_id)
        return self._current

    def add_item(self, product_id: str, quantity: int = 1) -> ReturnRecord:
        if not self._current or not self._original_sale:
            raise RuntimeError("No active return - please start a return first")
        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero")

        sold_qty = sum(i.quantity for i in self._original_sale.items
                       if i.product_id == product_id)
        if sold_qty == 0:
            raise ValueError(f"Product not found in the original sale: {product_id}")

        returned_before = self._returned_qty(product_id)
        already = sum(i.quantity for i in self._current.items
                      if i.product_id == product_id)
        if returned_before + already + quantity > sold_qty:
            raise ValueError(
                f"Return quantity exceeds the eligible amount "
                f"(already returned: {returned_before}, "
                f"pending this return: {already}, originally sold: {sold_qty})")

        product = self.product_repo.find_by_id(product_id)
        unit_price = next(i.unit_price for i in self._original_sale.items
                          if i.product_id == product_id)
        self._current.add_item(ReturnLineItem(
            product_id=product_id,
            name=product.name if product else product_id,
            unit_price=unit_price,
            quantity=quantity,
        ))
        return self._current

    def confirm(self) -> ReturnRecord:
        if not self._current or not self._original_sale:
            raise RuntimeError("No active return - please start a return first")
        if not self._current.items:
            raise ValueError("No items selected for return")

        for item in self._current.items:
            product = self.product_repo.find_by_id(item.product_id)
            if product:
                product.increase_stock(item.quantity)

        record = self._current
        self.return_repo.save(record)
        self._current = None
        self._original_sale = None
        return record

    def cancel_return(self) -> None:
        self._current = None
        self._original_sale = None

    def _returned_qty(self, product_id: str) -> int:
        total = 0
        for r in self.return_repo.find_by_sale(self._current.original_sale_id):
            for item in r.items:
                if item.product_id == product_id:
                    total += item.quantity
        return total

    def _new_id(self) -> str:
        return "R" + uuid.uuid4().hex[:8].upper()