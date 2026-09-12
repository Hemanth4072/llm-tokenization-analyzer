"""
FastAPI application entrypoint.

Route modules stay thin (HTTP concerns only); all business logic lives in
app/services/.
"""
import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.config import settings
from app.api.routes import tokenize, analysis, compare

logger = logging.getLogger("tokenization_analyzer")

app = FastAPI(
    title=settings.app_name,
    description="Analyze and compare how GPT-2 and BERT tokenize text.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError) -> JSONResponse:
    # Never leak internal validation internals/stack traces to the client.
    return JSONResponse(status_code=400, content={"detail": "Invalid request payload."})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    # Catches anything a route/service didn't already turn into an HTTPException
    # (e.g. a tokenizer failing to load because of a network/hub issue). The
    # full exception is logged server-side; the client only ever sees the
    # documented {"detail": ...} shape, never a stack trace.
    logger.exception("Unhandled exception while processing %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected server error occurred. Please try again."},
    )


app.include_router(tokenize.router, prefix="/api")
app.include_router(analysis.router, prefix="/api")
app.include_router(compare.router, prefix="/api")


@app.get("/")
def root() -> dict:
    return {"message": "LLM Tokenization Analyzer API. See /docs for API documentation."}
