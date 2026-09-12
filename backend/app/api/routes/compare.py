from fastapi import APIRouter, Depends, HTTPException

from app.schemas.analysis import CompareRequest, CompareResponse
from app.services.tokenizer_service import TokenizerService, get_tokenizer_service
from app.services import analysis_service
from app.api.routes.analysis import _build_model_analysis

router = APIRouter(tags=["compare"])


@router.post("/compare", response_model=CompareResponse)
def compare(
    request: CompareRequest,
    tokenizer_service: TokenizerService = Depends(get_tokenizer_service),
) -> CompareResponse:
    try:
        results = [_build_model_analysis(request.text, model_id, tokenizer_service) for model_id in request.models]
        return CompareResponse(
            character_count=analysis_service.count_characters(request.text),
            word_count=analysis_service.count_words(request.text),
            results=results,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
