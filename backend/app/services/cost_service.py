"""
Cost Service
-------------
Simple, configurable cost estimation. Pricing is always supplied by the
caller (frontend) rather than hard-coded here, since real provider
pricing changes over time and differs per model - this app is not the
source of truth for pricing.
"""


def estimate_cost(token_count: int, price_per_1000_tokens: float) -> float:
    if token_count < 0:
        raise ValueError("token_count must be non-negative.")
    if price_per_1000_tokens < 0:
        raise ValueError("price_per_1000_tokens must be non-negative.")

    cost = (token_count / 1000) * price_per_1000_tokens
    return round(cost, 6)
