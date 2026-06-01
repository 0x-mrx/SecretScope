from typing import Dict, Any

def classify_match(match: str, context: str) -> Dict[str, Any]:
    confidence = 0.9
    severity = "HIGH"
    extra = {}

    if "proj-" in match:
        extra["token_type"] = "OpenAI Project Key"  # nosec B105
    else:
        extra["token_type"] = "OpenAI Account Key"  # nosec B105

    masked = f"{match[:7]}{'*' * 18}{match[-4:]}"

    return {
        "secret_type": "OPENAI_KEY",  # nosec B105
        "confidence": confidence,
        "severity": severity,
        "masked_value": masked,
        "extra_metadata": extra
    }
