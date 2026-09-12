"""
Request/response schemas for analysis, comparison, context-window, and
cost-estimation endpoints.
"""
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, model_validator

from app.config import MODEL_LOOKUP, settings


# ---------- /api/analyze ----------

class AnalyzeRequest(BaseModel):
    text: str
    models: List[str] = Field(..., min_length=1)

    @field_validator("text")
    @classmethod
    def text_not_blank(cls, value: str) -> str:
        if value.strip() == "":
            raise ValueError("text must not be empty.")
        if len(value) > settings.max_input_characters:
            raise ValueError(f"text exceeds the maximum allowed length of {settings.max_input_characters} characters.")
        return value

    @field_validator("models")
    @classmethod
    def models_supported(cls, value: List[str]) -> List[str]:
        unknown = [m for m in value if m not in MODEL_LOOKUP]
        if unknown:
            raise ValueError(f"Unsupported model id(s): {unknown}.")
        return value


class ModelAnalysis(BaseModel):
    model: str
    display_name: str
    character_count: int
    word_count: int
    token_count: int
    unique_token_count: int
    characters_per_token: float
    tokens_per_word: float


class AnalyzeResponse(BaseModel):
    results: List[ModelAnalysis]


# ---------- /api/compare ----------

class CompareRequest(AnalyzeRequest):
    """Compare uses the same input shape as analyze; kept as a distinct
    type so the two endpoints can diverge later without breaking clients."""
    pass


class CompareResponse(BaseModel):
    character_count: int
    word_count: int
    results: List[ModelAnalysis]


# ---------- /api/context-analysis ----------

class ContextAnalysisRequest(BaseModel):
    model: str
    text: Optional[str] = None
    token_count: Optional[int] = None
    max_tokens: int = Field(..., gt=0, description="Configured maximum context size. Must be positive.")

    @field_validator("model")
    @classmethod
    def model_supported(cls, value: str) -> str:
        if value not in MODEL_LOOKUP:
            raise ValueError(f"Unsupported model id: {value}.")
        return value

    @model_validator(mode="after")
    def require_text_or_token_count(self) -> "ContextAnalysisRequest":
        if self.text is None and self.token_count is None:
            raise ValueError("Either 'text' or 'token_count' must be provided.")
        if self.token_count is not None and self.token_count < 0:
            raise ValueError("token_count must be non-negative.")
        return self


class ContextAnalysisResponse(BaseModel):
    current_tokens: int
    max_tokens: int
    remaining_tokens: int
    percentage_used: float
    severity: str  # "ok" | "warning" | "critical" | "over_limit"


# ---------- /api/cost-estimate ----------

class CostEstimateRequest(BaseModel):
    token_count: int = Field(..., ge=0)
    price_per_1000_tokens: float = Field(..., ge=0)


class CostEstimateResponse(BaseModel):
    token_count: int
    price_per_1000_tokens: float
    estimated_cost: float
