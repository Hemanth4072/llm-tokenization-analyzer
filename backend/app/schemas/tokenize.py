"""
Request/response schemas for tokenization endpoints.
"""
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator

from app.config import MODEL_LOOKUP, settings


class TokenizeRequest(BaseModel):
    text: str = Field(..., description="The text to tokenize.")
    models: List[str] = Field(..., min_length=1, description="Model IDs to tokenize with.")

    @field_validator("text")
    @classmethod
    def text_must_not_be_blank_or_too_long(cls, value: str) -> str:
        if value.strip() == "":
            raise ValueError("text must not be empty.")
        if len(value) > settings.max_input_characters:
            raise ValueError(
                f"text exceeds the maximum allowed length of {settings.max_input_characters} characters."
            )
        return value

    @field_validator("models")
    @classmethod
    def models_must_be_supported(cls, value: List[str]) -> List[str]:
        unknown = [m for m in value if m not in MODEL_LOOKUP]
        if unknown:
            supported = ", ".join(MODEL_LOOKUP.keys())
            raise ValueError(f"Unsupported model id(s): {unknown}. Supported models: {supported}.")
        return value


class TokenDetail(BaseModel):
    text: str
    token_id: int
    position: int


class TokenizeResult(BaseModel):
    model: str
    display_name: str
    tokens: List[TokenDetail]
    token_count: int
    special_tokens_used: List[str] = Field(default_factory=list)


class TokenizeResponse(BaseModel):
    results: List[TokenizeResult]


class ModelSummary(BaseModel):
    id: str
    name: str
    default_context_window: int


class ModelsResponse(BaseModel):
    models: List[ModelSummary]


class HealthResponse(BaseModel):
    status: str
