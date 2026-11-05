from dataclasses import dataclass, field
from datetime import datetime
from .money import Money


@dataclass
class Payment:
    """Cash payment value object."""
    amount_due: Money          # amount to be paid
    tendered: Money            # amount handed over by the customer
    method: str = "CASH"
    paid_at: datetime = field(default_factory=datetime.now)

    @property
    def change(self) -> Money:
        return self.tendered - self.amount_due