from fastapi import APIRouter, Depends, HTTPException

from app.schemas.analysis import (
    AnalyzeRequest,
    AnalyzeResponse,
    ModelAnalysis,
    ContextAnalysisRequest,
    ContextAnalysisResponse,
    CostEstimateRequest,
    CostEstimateResponse,
)
from app.services.tokenizer_service import TokenizerService, get_tokenizer_service
from app.services import analysis_service, cost_service

router = APIRouter(tags=["analysis"])


def _build_model_analysis(text: str, model_id: str, tokenizer_service: TokenizerService) -> ModelAnalysis:
    data = tokenizer_service.tokenize(text, model_id)
    char_count = analysis_service.count_characters(text)
    word_count = analysis_service.count_words(text)
    token_count = len(data.token_texts)

    return ModelAnalysis(
        model=data.model_id,
        display_name=data.display_name,
        character_count=char_count,
        word_count=word_count,
        token_count=token_count,
        unique_token_count=analysis_service.count_unique_tokens(data.token_texts),
        characters_per_token=analysis_service.characters_per_token(char_count, token_count),
        tokens_per_word=analysis_service.tokens_per_word(token_count, word_count),
    )


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze(
    request: AnalyzeRequest,
    tokenizer_service: TokenizerService = Depends(get_tokenizer_service),
) -> AnalyzeResponse:
    try:
        results = [_build_model_analysis(request.text, model_id, tokenizer_service) for model_id in request.models]
        return AnalyzeResponse(results=results)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/context-analysis", response_model=ContextAnalysisResponse)
def context_analysis(
    request: ContextAnalysisRequest,
    tokenizer_service: TokenizerService = Depends(get_tokenizer_service),
) -> ContextAnalysisResponse:
    try:
        if request.token_count is not None:
            current_tokens = request.token_count
        else:
            current_tokens = tokenizer_service.count_tokens(request.text, request.model)

        result = analysis_service.context_utilization(current_tokens, request.max_tokens)
        return ContextAnalysisResponse(**result)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/cost-estimate", response_model=CostEstimateResponse)
def cost_estimate(request: CostEstimateRequest) -> CostEstimateResponse:
    try:
        cost = cost_service.estimate_cost(request.token_count, request.price_per_1000_tokens)
        return CostEstimateResponse(
            token_count=request.token_count,
            price_per_1000_tokens=request.price_per_1000_tokens,
            estimated_cost=cost,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
