"""
Thin wrapper around the Claude API used by every agent.

Each agent sends a system prompt + a user message containing the input
data, and asks for a JSON object back. We parse that JSON and hand it
to the caller. If ANTHROPIC_API_KEY isn't set, agents fall back to a
deterministic offline heuristic (see each agent's `_offline_fallback`)
so the pipeline is runnable and testable without network access / a key.
"""

import json
import os
import re
from typing import Any, Dict, Optional

MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-5")


class LLMUnavailable(Exception):
    pass


def _extract_json(text: str) -> Dict[str, Any]:
    """Pull the first {...} or [...] block out of a model response."""
    text = text.strip()
    # Strip markdown code fences if present
    fence = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)
    if fence:
        text = fence.group(1).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # Fall back to grabbing the outermost {...}
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return json.loads(text[start : end + 1])
    raise ValueError(f"Could not parse JSON from model output: {text[:300]}")


def call_llm_json(system_prompt: str, user_message: str, max_tokens: int = 1500) -> Dict[str, Any]:
    """
    Calls the Claude API and expects a JSON object back.
    Raises LLMUnavailable if no API key / client library is configured,
    so callers can fall back to an offline heuristic.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise LLMUnavailable("ANTHROPIC_API_KEY not set")

    try:
        import anthropic
    except ImportError as e:
        raise LLMUnavailable("anthropic package not installed") from e

    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )
    text = "".join(block.text for block in response.content if hasattr(block, "text"))
    return _extract_json(text)
