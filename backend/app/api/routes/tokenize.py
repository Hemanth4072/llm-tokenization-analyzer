from fastapi import APIRouter, Depends, HTTPException

from app.schemas.tokenize import (
    TokenizeRequest,
    TokenizeResponse,
    TokenizeResult,
    TokenDetail,
    ModelsResponse,
    ModelSummary,
    HealthResponse,
)
from app.services.tokenizer_service import TokenizerService, get_tokenizer_service
from app.config import SUPPORTED_MODELS

router = APIRouter(tags=["tokenize"])


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@router.get("/models", response_model=ModelsResponse)
def list_models() -> ModelsResponse:
    return ModelsResponse(
        models=[
            ModelSummary(
                id=m.model_id,
                name=m.display_name,
                default_context_window=m.default_context_window,
            )
            for m in SUPPORTED_MODELS
        ]
    )


@router.post("/tokenize", response_model=TokenizeResponse)
def tokenize(
    request: TokenizeRequest,
    tokenizer_service: TokenizerService = Depends(get_tokenizer_service),
) -> TokenizeResponse:
    try:
        results = []
        for model_id in request.models:
            data = tokenizer_service.tokenize(request.text, model_id)
            tokens = [
                TokenDetail(text=text, token_id=token_id, position=position)
                for position, (text, token_id) in enumerate(zip(data.token_texts, data.token_ids))
            ]
            results.append(
                TokenizeResult(
                    model=data.model_id,
                    display_name=data.display_name,
                    tokens=tokens,
                    token_count=len(tokens),
                    special_tokens_used=data.special_tokens_used,
                )
            )
        return TokenizeResponse(results=results)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
