"""
AI Service abstraction layer.
Supports OpenAI and Anthropic. Designed to be swappable.
"""
import json
import os
from typing import Optional


class AIService:
    """
    Abstraction layer for AI providers.
    Currently supports OpenAI and Anthropic. Designed to be swappable.
    """

    def __init__(self, provider: Optional[str] = None):
        self.provider = provider or os.getenv("AI_PROVIDER", "openai")

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        response_format: str = "json",
        temperature: float = 0.3,
    ) -> dict:
        """Send a prompt and get a structured response."""
        if self.provider == "openai":
            return self._generate_openai(system_prompt, user_prompt, response_format, temperature)
        elif self.provider == "anthropic":
            return self._generate_anthropic(system_prompt, user_prompt, response_format, temperature)
        else:
            raise ValueError(f"Unsupported AI provider: {self.provider}")

    def _generate_openai(
        self, system_prompt: str, user_prompt: str, response_format: str, temperature: float
    ) -> dict:
        from openai import OpenAI

        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        kwargs = {
            "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
        }
        if response_format == "json":
            kwargs["response_format"] = {"type": "json_object"}

        response = client.chat.completions.create(**kwargs)
        content = response.choices[0].message.content

        if response_format == "json":
            return json.loads(content)
        return {"text": content}

    def _generate_anthropic(
        self, system_prompt: str, user_prompt: str, response_format: str, temperature: float
    ) -> dict:
        from anthropic import Anthropic

        client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

        response = client.messages.create(
            model=os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514"),
            max_tokens=4096,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
            temperature=temperature,
        )
        content = response.content[0].text

        if response_format == "json":
            # Extract JSON from response - Anthropic may wrap it in markdown
            text = content.strip()
            if text.startswith("```"):
                lines = text.split("\n")
                text = "\n".join(lines[1:-1])
            return json.loads(text)
        return {"text": content}


# Singleton instance
ai_service = AIService()
