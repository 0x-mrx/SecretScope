from app.services.plugins.google_keys.detector import GoogleKeysDetector
from app.services.plugins.aws_keys.detector import AWSKeysDetector
from app.services.plugins.github_tokens.detector import GitHubTokensDetector
from app.services.plugins.slack_tokens.detector import SlackTokensDetector
from app.services.plugins.openai_keys.detector import OpenAIKeysDetector

def test_google_keys_detector():
    content = "const KEY = 'AIzaSyA1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6Q';"
    det = GoogleKeysDetector()
    matches = det.detect(content)
    assert len(matches) == 1
    assert matches[0]["match"] == "AIzaSyA1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6Q"

def test_aws_keys_detector():
    content = "aws_access_key_id = AKIA1234567890ABCDEF"
    det = AWSKeysDetector()
    matches = det.detect(content)
    assert len(matches) == 1
    assert matches[0]["match"] == "AKIA1234567890ABCDEF"

def test_github_tokens_detector():
    content = "export GITHUB_TOKEN=ghp_A1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6Q7R8"
    det = GitHubTokensDetector()
    matches = det.detect(content)
    assert len(matches) == 1
    assert matches[0]["match"] == "ghp_A1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6Q7R8"

def test_slack_tokens_detector():
    content = "slack_bot_token: xoxb-1234567890-abcdef123456"
    det = SlackTokensDetector()
    matches = det.detect(content)
    assert len(matches) == 1
    assert matches[0]["match"] == "xoxb-1234567890-abcdef123456"

def test_openai_keys_detector():
    content = "openai.api_key = 'sk-proj-A1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6Q7R8S9T0'"
    det = OpenAIKeysDetector()
    matches = det.detect(content)
    assert len(matches) == 1
    assert matches[0]["match"] == "sk-proj-A1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6Q7R8S9T0"
