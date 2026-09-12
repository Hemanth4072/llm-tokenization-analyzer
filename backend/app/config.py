"""
Centralized configuration for the backend.

Keeping model metadata here (instead of scattering string literals through
the codebase) means adding a new tokenizer later is a one-line change here
plus a registry entry in tokenizer_service.py - nothing else has to change.
"""
from pydantic_settings import BaseSettings
from typing import List


class ModelInfo:
    """Static metadata about a supported tokenizer/model."""

    def __init__(self, model_id: str, display_name: str, hf_checkpoint: str, default_context_window: int):
        self.model_id = model_id
        self.display_name = display_name
        self.hf_checkpoint = hf_checkpoint
        self.default_context_window = default_context_window


# The single source of truth for which tokenizers this app supports.
# To add a new tokenizer: add an entry here, then register its loader
# in tokenizer_service.SUPPORTED_MODELS.
SUPPORTED_MODELS: List[ModelInfo] = [
    ModelInfo(
        model_id="gpt2",
        display_name="GPT-2",
        hf_checkpoint="gpt2",
        default_context_window=1024,
    ),
    ModelInfo(
        model_id="bert-base-cased",
        display_name="BERT Base Cased",
        hf_checkpoint="bert-base-cased",
        default_context_window=512,
    ),
]

MODEL_LOOKUP = {m.model_id: m for m in SUPPORTED_MODELS}


class Settings(BaseSettings):
    """
    Runtime configuration, overridable via environment variables.
    Nothing secret lives here - this is just app-level tuning.
    """
    app_name: str = "LLM Tokenization Analyzer API"
    cors_origins: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    # Safety limit so a single request can't tokenize an unbounded amount
    # of text and tie up the server.
    max_input_characters: int = 20_000

    # Default price used only as a starting point in the UI; the frontend
    # can override this per request. This is NOT an authoritative price
    # from any provider.
    default_price_per_1000_tokens: float = 0.0015

    class Config:
        env_prefix = "TOKENIZER_APP_"


settings = Settings()
