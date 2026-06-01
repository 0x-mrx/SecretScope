from typing import Dict, Any

def classify_match(match: str, context: str) -> Dict[str, Any]:
    confidence = 0.95
    severity = "CRITICAL"
    extra = {}

    if match.startswith("ghp_"):
        extra["token_type"] = "Personal Access Token (PAT)"  # nosec B105
    elif match.startswith("ghs_"):
        extra["token_type"] = "Server-to-Server Token"  # nosec B105
        severity = "HIGH"

    masked = f"{match[:4]}{'*' * 20}{match[-4:]}"

    return {
        "secret_type": "GITHUB_TOKEN",  # nosec B105
        "confidence": confidence,
        "severity": severity,
        "masked_value": masked,
        "extra_metadata": extra
    }
