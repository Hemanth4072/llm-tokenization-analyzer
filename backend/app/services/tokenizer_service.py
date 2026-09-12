"""
Tokenizer Service
------------------
Responsible for loading Hugging Face tokenizer instances and running real
tokenization. This is the only part of the app that talks to the
`transformers` library, so every other module deals with plain Python
data instead of tokenizer-library objects.

Design notes:
- Tokenizers are loaded lazily (on first use) and then cached in-memory,
  so we never reload the same tokenizer from disk/hub on every request.
- Loading is protected by a lock so concurrent requests during a cold
  start don't trigger duplicate loads of the same tokenizer.
- Adding a new tokenizer only requires adding an entry to SUPPORTED_MODELS
  in config.py - no changes needed here as long as it's a standard
  AutoTokenizer-compatible checkpoint.
"""
import threading
from functools import lru_cache
from typing import Dict, List, NamedTuple

from transformers import AutoTokenizer, PreTrainedTokenizerBase

from app.config import MODEL_LOOKUP, ModelInfo


class TokenizeResultData(NamedTuple):
    model_id: str
    display_name: str
    token_texts: List[str]
    token_ids: List[int]
    special_tokens_used: List[str]


class UnsupportedModelError(ValueError):
    pass


class TokenizerService:
    """Loads and caches Hugging Face tokenizers, and exposes a simple
    tokenize() API that returns plain Python data structures."""

    def __init__(self) -> None:
        self._cache: Dict[str, PreTrainedTokenizerBase] = {}
        self._lock = threading.Lock()

    def _get_model_info(self, model_id: str) -> ModelInfo:
        info = MODEL_LOOKUP.get(model_id)
        if info is None:
            raise UnsupportedModelError(f"Unsupported model id: {model_id}")
        return info

    def get_tokenizer(self, model_id: str) -> PreTrainedTokenizerBase:
        """Return a cached tokenizer instance, loading it on first use."""
        if model_id in self._cache:
            return self._cache[model_id]

        with self._lock:
            # Re-check in case another thread loaded it while we waited.
            if model_id in self._cache:
                return self._cache[model_id]

            info = self._get_model_info(model_id)
            tokenizer = AutoTokenizer.from_pretrained(info.hf_checkpoint)
            self._cache[model_id] = tokenizer
            return tokenizer

    def tokenize(self, text: str, model_id: str) -> TokenizeResultData:
        """
        Tokenize `text` with the tokenizer for `model_id`, using the
        tokenizer's own `tokenize()` + `convert_tokens_to_ids()` so the
        token texts and IDs come straight from the real model vocabulary.
        No special tokens (like BERT's [CLS]/[SEP]) are injected here -
        this call reflects the raw tokenization of the given text.
        """
        info = self._get_model_info(model_id)
        tokenizer = self.get_tokenizer(model_id)

        token_texts = tokenizer.tokenize(text)
        token_ids = tokenizer.convert_tokens_to_ids(token_texts)

        return TokenizeResultData(
            model_id=info.model_id,
            display_name=info.display_name,
            token_texts=token_texts,
            token_ids=token_ids,
            special_tokens_used=[],
        )

    def count_tokens(self, text: str, model_id: str) -> int:
        """Fast path when only the count is needed (e.g. context analysis)."""
        tokenizer = self.get_tokenizer(model_id)
        return len(tokenizer.tokenize(text))

    def display_name_for(self, model_id: str) -> str:
        return self._get_model_info(model_id).display_name

    def default_context_window_for(self, model_id: str) -> int:
        return self._get_model_info(model_id).default_context_window


@lru_cache
def get_tokenizer_service() -> TokenizerService:
    """Singleton accessor so FastAPI dependency injection reuses the same
    service (and therefore the same tokenizer cache) across requests."""
    return TokenizerService()
