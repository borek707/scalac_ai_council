"""Structured-output generation with a bounded repair loop.

LLMs frequently return JSON that *almost* matches a schema.  Rather than
failing the whole run, :func:`generate_structured` validates the model
output against a Pydantic schema and, on failure, re-prompts the model with
the concrete validation errors — up to a bounded number of attempts.
"""

from __future__ import annotations

import json
import logging
import re
from typing import TYPE_CHECKING

from pydantic import BaseModel, ValidationError

if TYPE_CHECKING:
    from council.llm.provider import LLMProvider

logger = logging.getLogger(__name__)

_JSON_FENCE_RE = re.compile(r"```(?:json)?\s*(\{.*?\}|\[.*?\])\s*```", re.DOTALL)


class StructuredOutputError(RuntimeError):
    """Raised when structured output cannot be produced within the retry budget."""


def _extract_json(text: str) -> str:
    """Return the most likely JSON payload from a model response.

    Handles fenced code blocks and leading/trailing prose around the object.
    """
    fenced = _JSON_FENCE_RE.search(text)
    if fenced:
        return fenced.group(1)
    # Fall back to the first balanced-looking object/array span.
    start = next((i for i, ch in enumerate(text) if ch in "{["), None)
    if start is None:
        return text.strip()
    end_char = "}" if text[start] == "{" else "]"
    end = text.rfind(end_char)
    if end > start:
        return text[start : end + 1]
    return text.strip()


def parse_model[T: BaseModel](text: str, model_cls: type[T]) -> T:
    """Parse and validate *text* into *model_cls*; raises on failure."""
    payload = _extract_json(text)
    data = json.loads(payload)
    return model_cls.model_validate(data)


async def generate_structured[T: BaseModel](
    provider: LLMProvider,
    prompt: str,
    model_cls: type[T],
    *,
    system: str | None = None,
    max_retries: int = 2,
    temperature: float = 0.3,
    max_tokens: int = 4000,
) -> T:
    """Generate output and validate it against *model_cls* with repair retries.

    Parameters
    ----------
    provider:
        Any :class:`~council.llm.provider.LLMProvider`.
    prompt:
        The base user prompt.  A JSON-schema instruction is appended.
    model_cls:
        Target Pydantic model.
    max_retries:
        Number of *additional* repair attempts after the first try
        (total attempts = ``max_retries + 1``).
    """
    schema_json = json.dumps(model_cls.model_json_schema())
    base_instruction = (
        f"{prompt}\n\n"
        "Respond with ONLY a single JSON object that validates against this "
        f"JSON schema (no prose, no code fences):\n{schema_json}"
    )

    last_error: Exception | None = None
    current_prompt = base_instruction

    for attempt in range(max_retries + 1):
        response = await provider.generate(
            prompt=current_prompt,
            system=system,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        try:
            return parse_model(response.content, model_cls)
        except (json.JSONDecodeError, ValidationError) as exc:
            last_error = exc
            logger.warning(
                "Structured output attempt %d/%d failed: %s",
                attempt + 1,
                max_retries + 1,
                exc,
            )
            current_prompt = (
                f"{base_instruction}\n\n"
                "Your previous response was invalid and could not be parsed.\n"
                f"Error:\n{exc}\n\n"
                "Return corrected JSON only."
            )

    raise StructuredOutputError(
        f"Could not produce valid {model_cls.__name__} after {max_retries + 1} attempts: "
        f"{last_error}"
    )


__all__ = [
    "StructuredOutputError",
    "generate_structured",
    "parse_model",
]
