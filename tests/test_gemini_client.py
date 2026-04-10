import pytest

from src.infra.gemini_client import GeminiClient
from src.domain.receipt_data import ReceiptData
from src.shared.errors import ExtractionError


class FakeFunctionCall:
    def __init__(self, name, args):
        self.name = name
        self.args = args


class FakePart:
    def __init__(self, function_call=None):
        self.function_call = function_call


class FakeContent:
    def __init__(self, parts):
        self.parts = parts


class FakeCandidate:
    def __init__(self, content):
        self.content = content


class FakeResponse:
    def __init__(self, candidates):
        self.candidates = candidates


class TestGeminiClientParseToolCall:
    def test_parse_tool_call_success(self):
        fc = FakeFunctionCall(
            name="send_receipt_data",
            args={"datetime": "2026-01-01T10:00:00", "amount": 50.0, "type": "income"},
        )
        response = FakeResponse(
            candidates=[FakeCandidate(content=FakeContent(parts=[FakePart(function_call=fc)]))]
        )
        result = GeminiClient._parse_tool_call(response)
        assert isinstance(result, ReceiptData)
        assert result.amount == 50.0
        assert result.type == "income"

    def test_parse_tool_call_no_candidates(self):
        response = FakeResponse(candidates=[])
        with pytest.raises(ExtractionError):
            GeminiClient._parse_tool_call(response)

    def test_parse_tool_call_no_function_call(self):
        response = FakeResponse(
            candidates=[FakeCandidate(content=FakeContent(parts=[FakePart()]))]
        )
        with pytest.raises(ExtractionError):
            GeminiClient._parse_tool_call(response)

    def test_parse_tool_call_wrong_tool(self):
        fc = FakeFunctionCall(name="wrong_tool", args={})
        response = FakeResponse(
            candidates=[FakeCandidate(content=FakeContent(parts=[FakePart(function_call=fc)]))]
        )
        with pytest.raises(ExtractionError):
            GeminiClient._parse_tool_call(response)


# Esse arquivo possui código gerado com IA
