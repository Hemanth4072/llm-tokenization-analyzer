import pytest
from app.services import analysis_service


def test_count_characters():
    assert analysis_service.count_characters("hello") == 5
    assert analysis_service.count_characters("") == 0


def test_count_words():
    assert analysis_service.count_words("I love AI.") == 3
    assert analysis_service.count_words("") == 0
    assert analysis_service.count_words("single") == 1
    assert analysis_service.count_words("  extra   spaces  ") == 2


def test_count_unique_tokens():
    assert analysis_service.count_unique_tokens(["a", "a", "b"]) == 2
    assert analysis_service.count_unique_tokens([]) == 0


def test_characters_per_token():
    assert analysis_service.characters_per_token(10, 5) == 2.0
    assert analysis_service.characters_per_token(10, 0) == 0.0


def test_tokens_per_word():
    assert analysis_service.tokens_per_word(10, 5) == 2.0
    assert analysis_service.tokens_per_word(10, 0) == 0.0


def test_context_utilization_zero_tokens():
    result = analysis_service.context_utilization(0, 1024)
    assert result["current_tokens"] == 0
    assert result["percentage_used"] == 0.0
    assert result["severity"] == "ok"


def test_context_utilization_normal():
    result = analysis_service.context_utilization(500, 1000)
    assert result["percentage_used"] == 50.0
    assert result["severity"] == "ok"


def test_context_utilization_warning_threshold():
    result = analysis_service.context_utilization(800, 1000)
    assert result["severity"] == "warning"


def test_context_utilization_critical_threshold():
    result = analysis_service.context_utilization(950, 1000)
    assert result["severity"] == "critical"


def test_context_utilization_at_limit():
    result = analysis_service.context_utilization(1000, 1000)
    assert result["percentage_used"] == 100.0
    assert result["remaining_tokens"] == 0
    assert result["severity"] == "critical"


def test_context_utilization_over_limit():
    result = analysis_service.context_utilization(1200, 1000)
    assert result["remaining_tokens"] == -200
    assert result["severity"] == "over_limit"


def test_context_utilization_invalid_max_tokens():
    with pytest.raises(ValueError):
        analysis_service.context_utilization(10, 0)
    with pytest.raises(ValueError):
        analysis_service.context_utilization(10, -5)


def test_context_utilization_negative_current_tokens():
    with pytest.raises(ValueError):
        analysis_service.context_utilization(-1, 1000)
