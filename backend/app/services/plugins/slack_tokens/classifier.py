from typing import Dict, Any

def classify_match(match: str, context: str) -> Dict[str, Any]:
    confidence = 0.9
    severity = "HIGH"
    extra = {}

    if "hooks.slack.com" in match:
        extra["token_type"] = "Slack Incoming Webhook URL"
        severity = "MEDIUM"
    elif match.startswith("xoxb-"):
        extra["token_type"] = "Slack Bot Token"
    elif match.startswith("xoxp-"):
        extra["token_type"] = "Slack User Token"

    # Masking
    if "services" in match:
        parts = match.split("/")
        # mask third part
        masked = f"https://hooks.slack.com/services/{parts[-3]}/{parts[-2]}/" + "*" * len(parts[-1])
    else:
        masked = f"{match[:5]}{'*' * 15}{match[-4:]}"

    return {
        "secret_type": "SLACK_TOKEN",
        "confidence": confidence,
        "severity": severity,
        "masked_value": masked,
        "extra_metadata": extra
    }
