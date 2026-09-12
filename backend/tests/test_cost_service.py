import pytest
from app.services import cost_service


def test_zero_tokens():
    assert cost_service.estimate_cost(0, 1.0) == 0.0


def test_normal_values():
    # 1000 tokens at $2 per 1000 tokens = $2
    assert cost_service.estimate_cost(1000, 2.0) == 2.0


def test_decimal_prices():
    assert cost_service.estimate_cost(1500, 0.0015) == pytest.approx(0.00225)


def test_zero_price():
    assert cost_service.estimate_cost(5000, 0.0) == 0.0


def test_negative_token_count_rejected():
    with pytest.raises(ValueError):
        cost_service.estimate_cost(-1, 1.0)


def test_negative_price_rejected():
    with pytest.raises(ValueError):
        cost_service.estimate_cost(100, -0.5)
