import re
from typing import Dict, Any

SECRET_KEY_PATTERN = re.compile(r'(?i)secret[_-]?key|aws[_-]?secret|key\s*[:=]\s*["\']?([A-Za-z0-9/+=]{40})["\']?')

def classify_match(match: str, context: str) -> Dict[str, Any]:
    confidence = 0.85
    severity = "CRITICAL"
    extra = {}

    # Check if a 40-character secret key is nearby in the context
    secret_match = SECRET_KEY_PATTERN.search(context)
    if secret_match:
        confidence = 0.99
        extra["secret_found"] = "Companion Secret Key detected in context"  # nosec B105

    masked = f"{match[:4]}{'*' * 12}{match[-4:]}"

    return {
        "secret_type": "AWS_ACCESS_KEY",  # nosec B105
        "confidence": confidence,
        "severity": severity,
        "masked_value": masked,
        "extra_metadata": extra
    }
