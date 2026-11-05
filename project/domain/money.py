from dataclasses import dataclass


@dataclass(frozen=True)
class Money:
    """Money value object. Stored in cents to avoid floating-point errors."""
    cents: int

    @classmethod
    def from_dollars(cls, dollars) -> "Money":
        return cls(int(round(float(dollars) * 100)))

    @property
    def dollars(self) -> float:
        return self.cents / 100

    def __add__(self, other: "Money") -> "Money":
        return Money(self.cents + other.cents)

    def __sub__(self, other: "Money") -> "Money":
        return Money(self.cents - other.cents)

    def __mul__(self, n: int) -> "Money":
        return Money(self.cents * int(n))

    def __lt__(self, other: "Money") -> bool:
        return self.cents < other.cents

    def __le__(self, other: "Money") -> bool:
        return self.cents <= other.cents

    def __ge__(self, other: "Money") -> bool:
        return self.cents >= other.cents

    def __str__(self) -> str:
        return f"${self.cents / 100:.2f}"