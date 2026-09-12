"""
Analysis Service
-----------------
Pure, stateless calculations built on top of tokenizer output:
character/word counts, token statistics, and context-window utilization.

Kept free of any HTTP or tokenizer-loading concerns so it's trivial to
unit test in isolation.
"""
import re
from typing import List

WORD_PATTERN = re.compile(r"\S+")


def count_characters(text: str) -> int:
    return len(text)


def count_words(text: str) -> int:
    """Whitespace-delimited word count. Works reasonably across
    space-delimited scripts; languages without whitespace word boundaries
    (e.g. Japanese) will naturally report a lower "word" count, which is
    expected and worth noting in the UI rather than hidden."""
    return len(WORD_PATTERN.findall(text))


def count_unique_tokens(token_texts: List[str]) -> int:
    return len(set(token_texts))


def characters_per_token(character_count: int, token_count: int) -> float:
    if token_count == 0:
        return 0.0
    return round(character_count / token_count, 4)


def tokens_per_word(token_count: int, word_count: int) -> float:
    if word_count == 0:
        return 0.0
    return round(token_count / word_count, 4)


def context_utilization(current_tokens: int, max_tokens: int) -> dict:
    """
    Computes context-window utilization.

    Raises ValueError if max_tokens <= 0, per the documented contract -
    callers (routes) are responsible for translating that into a 4xx
    response.
    """
    if max_tokens <= 0:
        raise ValueError("max_tokens must be greater than 0.")
    if current_tokens < 0:
        raise ValueError("current_tokens must be non-negative.")

    remaining = max_tokens - current_tokens
    percentage = round((current_tokens / max_tokens) * 100, 2)

    if current_tokens > max_tokens:
        severity = "over_limit"
    elif percentage >= 90:
        severity = "critical"
    elif percentage >= 75:
        severity = "warning"
    else:
        severity = "ok"

    return {
        "current_tokens": current_tokens,
        "max_tokens": max_tokens,
        "remaining_tokens": remaining,
        "percentage_used": percentage,
        "severity": severity,
    }
