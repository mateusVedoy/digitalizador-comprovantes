import pytest

from src.domain.receipt_data import ReceiptData


class TestReceiptData:
    def test_creation_with_valid_data(self):
        receipt = ReceiptData(
            datetime="2026-03-15T14:30:00", amount=187.50, type="expense"
        )
        assert receipt.datetime == "2026-03-15T14:30:00"
        assert receipt.amount == 187.50
        assert receipt.type == "expense"

    def test_immutability(self):
        receipt = ReceiptData(
            datetime="2026-03-15T14:30:00", amount=100.0, type="income"
        )
        with pytest.raises(AttributeError):
            receipt.amount = 200.0


# Esse arquivo possui código gerado com IA
