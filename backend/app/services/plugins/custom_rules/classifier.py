from typing import Dict, Any

def classify_match(match: str, context: str, rule_name: str, default_severity: str = "MEDIUM") -> Dict[str, Any]:
    confidence = 0.8
    # Crude severity derivation from description
    severity = "MEDIUM"
    if default_severity in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]:
        severity = default_severity

    if len(match) <= 8:
        masked = "*" * len(match)
    else:
        masked = f"{match[:2]}{'*' * (len(match) - 4)}{match[-2:]}"

    return {
        "secret_type": rule_name,
        "confidence": confidence,
        "severity": severity,
        "masked_value": masked,
        "extra_metadata": {"is_custom": True}
    }
