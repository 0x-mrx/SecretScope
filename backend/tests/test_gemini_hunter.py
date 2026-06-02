from unittest.mock import patch, MagicMock
from app.services.gemini_exploit import GeminiExploiter
from app.services.gemini_hunter import GeminiHunter

@patch("httpx.get")
def test_test_models_endpoint_success(mock_get):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "models": [{"name": "models/gemini-pro"}, {"name": "models/gemini-1.5-flash"}]
    }
    mock_get.return_value = mock_resp

    res = GeminiExploiter.test_models_endpoint("AIzaSyFakeKey")
    assert res["status"] == "SUCCESS"
    assert "models/gemini-pro" in res["models"]

@patch("httpx.post")
def test_test_text_generation_success(mock_post):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "candidates": [{"content": {"parts": [{"text": "Hello world output."}]}}]
    }
    mock_post.return_value = mock_resp

    res = GeminiExploiter.test_text_generation("AIzaSyFakeKey")
    assert res["status"] == "SUCCESS"
    assert res["result"] == "Hello world output."

def test_extract_keys_from_text():
    hunter = GeminiHunter()
    sample = "Some text with AIzaSyA1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s and another string."
    keys = hunter.extract_keys_from_text(sample)
    assert len(keys) == 1
    assert keys[0] == "AIzaSyA1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s"
