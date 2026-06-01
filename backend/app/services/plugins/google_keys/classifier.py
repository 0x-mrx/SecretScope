from typing import Dict, Any

def classify_match(match: str, context: str) -> Dict[str, Any]:
    # Check if there are Firebase markers or Google maps markers in context
    context_lower = context.lower()
    confidence = 0.8
    severity = "HIGH"
    extra = {}

    if "firebase" in context_lower:
        extra["sub_type"] = "Firebase API Key"
        confidence = 0.95
    elif "maps" in context_lower or "google" in context_lower:
        extra["sub_type"] = "Google API Key"
        confidence = 0.9

    # Masking
    masked = f"AIzaSy{'' * 4}{'*' * 28}{match[-4:]}"

    return {
        "secret_type": "GOOGLE_API_KEY",
        "confidence": confidence,
        "severity": severity,
        "masked_value": masked,
        "extra_metadata": extra
    }
