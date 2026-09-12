import pytest
from app.services.tokenizer_service import TokenizerService, UnsupportedModelError


@pytest.fixture(scope="module")
def service():
    return TokenizerService()


def test_gpt2_tokenizes_text(service):
    result = service.tokenize("I love learning AI.", "gpt2")
    assert result.model_id == "gpt2"
    assert len(result.token_texts) > 0
    assert len(result.token_texts) == len(result.token_ids)


def test_bert_tokenizes_text(service):
    result = service.tokenize("I love learning AI.", "bert-base-cased")
    assert result.model_id == "bert-base-cased"
    assert len(result.token_texts) > 0
    assert len(result.token_texts) == len(result.token_ids)


def test_token_ids_come_from_real_tokenizer(service):
    # Cross-check against calling the tokenizer directly - guards against
    # ever hard-coding/faking token IDs in the service.
    tokenizer = service.get_tokenizer("gpt2")
    text = "Tokenization is fun."
    expected_tokens = tokenizer.tokenize(text)
    expected_ids = tokenizer.convert_tokens_to_ids(expected_tokens)

    result = service.tokenize(text, "gpt2")
    assert result.token_texts == expected_tokens
    assert result.token_ids == expected_ids


def test_different_models_can_be_compared(service):
    text = "Tokenizers split text differently."
    gpt2_result = service.tokenize(text, "gpt2")
    bert_result = service.tokenize(text, "bert-base-cased")

    # They need not match, but both must return valid data.
    assert gpt2_result.model_id != bert_result.model_id
    assert len(gpt2_result.token_ids) > 0
    assert len(bert_result.token_ids) > 0


def test_tokenizer_instances_are_cached(service):
    first = service.get_tokenizer("gpt2")
    second = service.get_tokenizer("gpt2")
    assert first is second


def test_unsupported_model_raises(service):
    with pytest.raises(UnsupportedModelError):
        service.tokenize("hello", "not-a-real-model")


def test_unicode_and_multilingual_input(service):
    text = "こんにちは世界"  # Japanese: "Hello world"
    result = service.tokenize(text, "gpt2")
    assert len(result.token_texts) > 0


def test_empty_text_returns_no_tokens(service):
    result = service.tokenize("", "gpt2")
    assert result.token_texts == []
    assert result.token_ids == []
