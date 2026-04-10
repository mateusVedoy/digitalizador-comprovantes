from dataclasses import dataclass


@dataclass(frozen=True)
class ReceiptData:
    """Value Object with extracted receipt data."""

    datetime: str
    amount: float
    type: str  # "income" or "expense"


# Esse arquivo possui código gerado com IA
