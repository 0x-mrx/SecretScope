from unittest.mock import patch, MagicMock
from app.services.key_validator import KeyValidator

@patch("httpx.get")
def test_validate_google_key_success(mock_get):
    # Mocking response for a valid key
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"results": []}  # No error_message
    mock_get.return_value = mock_resp

    res = KeyValidator.validate_secret("GOOGLE_API_KEY", "AIzaSyFakeKey1234567890123456789012345")
    assert res["status"] == "VALID"
    assert "succeeded" in res["details"]

@patch("httpx.get")
def test_validate_google_key_invalid(mock_get):
    # Mocking response for an invalid key
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"error_message": "API key not authorized"}
    mock_get.return_value = mock_resp

    res = KeyValidator.validate_secret("GOOGLE_API_KEY", "AIzaSyFakeKey1234567890123456789012345")
    assert res["status"] == "INVALID"
    assert "rejected" in res["details"]

@patch("httpx.get")
def test_validate_github_token_success(mock_get):
    # Mocking response for a valid token
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"login": "bughunter"}
    mock_resp.headers = {"X-OAuth-Scopes": "repo, read:org"}
    mock_get.return_value = mock_resp

    res = KeyValidator.validate_secret("GITHUB_TOKEN", "ghp_fakeToken1234567890123456789012345")
    assert res["status"] == "VALID"
    assert "User: bughunter" in res["details"]
    assert "repo, read:org" in res["details"]

@patch("httpx.get")
def test_validate_github_token_unauthorized(mock_get):
    # Mocking response for an invalid token
    mock_resp = MagicMock()
    mock_resp.status_code = 401
    mock_get.return_value = mock_resp

    res = KeyValidator.validate_secret("GITHUB_TOKEN", "ghp_fakeToken1234567890123456789012345")
    assert res["status"] == "INVALID"
    assert "revoked or invalid" in res["details"]

def test_validate_unsupported_type():
    res = KeyValidator.validate_secret("AWS_ACCESS_KEY", "AKIAFAKEACCESSKEYID")
    assert res["status"] == "UNSUPPORTED"
