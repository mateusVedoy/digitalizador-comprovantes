from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class LlmConfig:
    """Value Object com configurações opcionais da LLM."""

    gemini_api_key: Optional[str] = None
    llm_model: Optional[str] = None
    max_tokens: Optional[int] = None


# Esse arquivo possui código gerado com IA
