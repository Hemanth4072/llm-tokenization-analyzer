import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_models_endpoint():
    response = client.get("/api/models")
    assert response.status_code == 200
    body = response.json()
    ids = [m["id"] for m in body["models"]]
    assert "gpt2" in ids
    assert "bert-base-cased" in ids


def test_valid_tokenize_request():
    response = client.post("/api/tokenize", json={"text": "I love AI.", "models": ["gpt2"]})
    assert response.status_code == 200
    body = response.json()
    assert body["results"][0]["model"] == "gpt2"
    assert body["results"][0]["token_count"] == len(body["results"][0]["tokens"])
    assert body["results"][0]["token_count"] > 0


def test_tokenize_with_both_models():
    response = client.post("/api/tokenize", json={"text": "Compare tokenizers.", "models": ["gpt2", "bert-base-cased"]})
    assert response.status_code == 200
    body = response.json()
    assert len(body["results"]) == 2


def test_invalid_model_rejected():
    response = client.post("/api/tokenize", json={"text": "Hello", "models": ["made-up-model"]})
    assert response.status_code == 422  # Pydantic validation error


def test_empty_text_rejected():
    response = client.post("/api/tokenize", json={"text": "", "models": ["gpt2"]})
    assert response.status_code == 422


def test_malformed_request_missing_models():
    response = client.post("/api/tokenize", json={"text": "Hello"})
    assert response.status_code == 422


def test_analyze_endpoint():
    response = client.post("/api/analyze", json={"text": "Hello world!", "models": ["gpt2"]})
    assert response.status_code == 200
    body = response.json()
    result = body["results"][0]
    assert result["character_count"] == len("Hello world!")
    assert result["word_count"] == 2


def test_compare_endpoint():
    response = client.post("/api/compare", json={"text": "Compare this text.", "models": ["gpt2", "bert-base-cased"]})
    assert response.status_code == 200
    body = response.json()
    assert len(body["results"]) == 2
    assert body["character_count"] == len("Compare this text.")


def test_context_analysis_with_text():
    response = client.post(
        "/api/context-analysis",
        json={"model": "gpt2", "text": "short text", "max_tokens": 1024},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["max_tokens"] == 1024
    assert body["severity"] in ("ok", "warning", "critical", "over_limit")


def test_context_analysis_with_token_count():
    response = client.post(
        "/api/context-analysis",
        json={"model": "gpt2", "token_count": 900, "max_tokens": 1000},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["current_tokens"] == 900
    assert body["severity"] == "critical"


def test_context_analysis_invalid_max_tokens():
    response = client.post(
        "/api/context-analysis",
        json={"model": "gpt2", "token_count": 10, "max_tokens": 0},
    )
    assert response.status_code == 422  # gt=0 constraint on schema


def test_context_analysis_missing_text_and_token_count():
    response = client.post(
        "/api/context-analysis",
        json={"model": "gpt2", "max_tokens": 1000},
    )
    assert response.status_code == 422


def test_cost_estimate_endpoint():
    response = client.post(
        "/api/cost-estimate",
        json={"token_count": 2000, "price_per_1000_tokens": 0.002},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["estimated_cost"] == pytest.approx(0.004)


def test_cost_estimate_rejects_negative_price():
    response = client.post(
        "/api/cost-estimate",
        json={"token_count": 100, "price_per_1000_tokens": -1},
    )
    assert response.status_code == 422
