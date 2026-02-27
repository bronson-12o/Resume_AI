"""
AI Service abstraction layer.
Supports OpenAI and Anthropic. Designed to be swappable.
Includes timeouts, retries, and safe JSON parsing.
"""
import json
import logging
import os
import re
import time
from typing import Optional

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
RETRY_BASE_DELAY = 1  # seconds
REQUEST_TIMEOUT = 30  # seconds


class AIServiceError(Exception):
    """Raised when the AI service fails after all retries."""
    pass


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
        """Send a prompt and get a structured response with retry logic."""
        last_error = None

        for attempt in range(MAX_RETRIES):
            try:
                start = time.time()
                if self.provider == "openai":
                    result = self._generate_openai(system_prompt, user_prompt, response_format, temperature)
                elif self.provider == "anthropic":
                    result = self._generate_anthropic(system_prompt, user_prompt, response_format, temperature)
                else:
                    raise ValueError(f"Unsupported AI provider: {self.provider}")

                duration = time.time() - start
                logger.info(f"AI call succeeded: provider={self.provider}, duration={duration:.2f}s")
                return result

            except (ValueError, AIServiceError):
                raise
            except Exception as e:
                last_error = e
                duration = time.time() - start
                logger.warning(
                    f"AI call failed (attempt {attempt + 1}/{MAX_RETRIES}): "
                    f"provider={self.provider}, duration={duration:.2f}s, error={type(e).__name__}: {e}"
                )
                if attempt < MAX_RETRIES - 1:
                    delay = RETRY_BASE_DELAY * (2 ** attempt)
                    time.sleep(delay)

        raise AIServiceError(f"AI service failed after {MAX_RETRIES} attempts: {last_error}")

    def _generate_openai(
        self, system_prompt: str, user_prompt: str, response_format: str, temperature: float
    ) -> dict:
        from openai import OpenAI

        client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            timeout=REQUEST_TIMEOUT,
        )

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
            return _safe_parse_json(content)
        return {"text": content}

    def _generate_anthropic(
        self, system_prompt: str, user_prompt: str, response_format: str, temperature: float
    ) -> dict:
        from anthropic import Anthropic

        client = Anthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            timeout=REQUEST_TIMEOUT,
        )

        response = client.messages.create(
            model=os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514"),
            max_tokens=4096,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
            temperature=temperature,
        )
        content = response.content[0].text

        if response_format == "json":
            return _safe_parse_json(content)
        return {"text": content}


def _safe_parse_json(text: str) -> dict:
    """Parse JSON from AI response, handling markdown code blocks and malformed output."""
    text = text.strip()

    # Strip markdown code fences (```json ... ``` or ``` ... ```)
    if text.startswith("```"):
        match = re.search(r"```(?:json)?\s*\n?(.*?)```", text, re.DOTALL)
        if match:
            text = match.group(1).strip()

    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Fallback: extract first JSON object from text
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    raise AIServiceError(f"Failed to parse JSON from AI response: {text[:200]}")


# Singleton instance
ai_service = AIService()
