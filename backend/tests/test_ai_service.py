import pytest

from backend.services.ai_service import AIService, AIServiceError


def test_missing_openai_key_fails_immediately(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    service = AIService(provider="openai")

    with pytest.raises(AIServiceError, match="OPENAI_API_KEY"):
        service.generate("system", "user")


def test_missing_anthropic_key_fails_immediately(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    service = AIService(provider="anthropic")

    with pytest.raises(AIServiceError, match="ANTHROPIC_API_KEY"):
        service.generate("system", "user")
