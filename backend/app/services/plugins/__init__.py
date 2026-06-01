from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.services.plugins.google_keys.detector import GoogleKeysDetector
from app.services.plugins.google_keys.classifier import classify_match as classify_google

from app.services.plugins.aws_keys.detector import AWSKeysDetector
from app.services.plugins.aws_keys.classifier import classify_match as classify_aws

from app.services.plugins.github_tokens.detector import GitHubTokensDetector
from app.services.plugins.github_tokens.classifier import classify_match as classify_github

from app.services.plugins.slack_tokens.detector import SlackTokensDetector
from app.services.plugins.slack_tokens.classifier import classify_match as classify_slack

from app.services.plugins.openai_keys.detector import OpenAIKeysDetector
from app.services.plugins.openai_keys.classifier import classify_match as classify_openai

from app.services.plugins.custom_rules.detector import CustomRulesDetector
from app.services.plugins.custom_rules.classifier import classify_match as classify_custom

def scan_and_classify_content(content: str, db: Session) -> List[Dict[str, Any]]:
    """
    Runs all active scanners against text content and classifies findings.
    """
    findings = []
    if not content:
        return findings

    # 1. AWS Keys
    aws_det = AWSKeysDetector()
    for m in aws_det.detect(content):
        classification = classify_aws(m["match"], m["context"])
        findings.append({**m, **classification})

    # 2. Google Keys
    google_det = GoogleKeysDetector()
    for m in google_det.detect(content):
        classification = classify_google(m["match"], m["context"])
        findings.append({**m, **classification})

    # 3. GitHub Tokens
    github_det = GitHubTokensDetector()
    for m in github_det.detect(content):
        classification = classify_github(m["match"], m["context"])
        findings.append({**m, **classification})

    # 4. Slack Tokens
    slack_det = SlackTokensDetector()
    for m in slack_det.detect(content):
        classification = classify_slack(m["match"], m["context"])
        findings.append({**m, **classification})

    # 5. OpenAI Keys
    openai_det = OpenAIKeysDetector()
    for m in openai_det.detect(content):
        classification = classify_openai(m["match"], m["context"])
        findings.append({**m, **classification})

    # 6. Custom DB Rules
    custom_det = CustomRulesDetector()
    for m in custom_det.detect_custom(content, db):
        classification = classify_custom(
            m["match"], 
            m["context"], 
            m["secret_type_name"], 
            m["default_severity"]
        )
        findings.append({
            "match": m["match"],
            "line": m["line"],
            "index": m["index"],
            "context": m["context"],
            "secret_type_id": m["secret_type_id"],
            **classification
        })

    return findings
