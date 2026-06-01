from typing import Dict, Any

class RiskEngine:
    @staticmethod
    def calculate_risk(asset_type: str, secret_type: str, severity: str) -> Dict[str, Any]:
        """
        Computes risk dimensions and maps to a unified numeric risk score (0-100).
        """
        # 1. Exposure Risk
        # Websites are public (Critical), repos are High (by default), files are Medium/Low
        if asset_type == "WEBSITE":
            exposure_risk = "CRITICAL"
        elif asset_type == "REPOSITORY":
            exposure_risk = "HIGH"
        else:
            exposure_risk = "MEDIUM"

        # 2. Compliance Risk
        # Sensitive credentials violate PCI-DSS, SOC2, HIPAA, ISO27001
        if secret_type in ["AWS_ACCESS_KEY", "GITHUB_TOKEN", "SLACK_TOKEN"]:  # nosec B105
            compliance_risk = "CRITICAL"
        elif secret_type in ["GOOGLE_API_KEY", "OPENAI_KEY"]:
            compliance_risk = "HIGH"
        else:
            compliance_risk = "MEDIUM"

        # 3. Operational Risk
        # Operational impact of secret revocation or compromise
        if secret_type == "AWS_ACCESS_KEY":  # nosec B105
            operational_risk = "CRITICAL"
        elif secret_type in ["GITHUB_TOKEN", "OPENAI_KEY"]:  # nosec B105
            operational_risk = "HIGH"
        elif secret_type == "SLACK_TOKEN":  # nosec B105
            operational_risk = "MEDIUM"
        else:
            operational_risk = "LOW"

        # Calculate a risk score (0 to 100)
        # Severity weights: CRITICAL = 100, HIGH = 75, MEDIUM = 50, LOW = 25
        # Asset type weights: WEBSITE = 1.2, REPOSITORY = 1.0, FILE_PATH = 0.8
        sev_weights = {"CRITICAL": 100.0, "HIGH": 75.0, "MEDIUM": 50.0, "LOW": 25.0}
        base_score = sev_weights.get(severity, 50.0)
        
        asset_multipliers = {"WEBSITE": 1.2, "REPOSITORY": 1.0, "FILE_PATH": 0.8}
        multiplier = asset_multipliers.get(asset_type, 1.0)
        
        risk_score = min(100.0, base_score * multiplier)

        return {
            "exposure_risk": exposure_risk,
            "compliance_risk": compliance_risk,
            "operational_risk": operational_risk,
            "risk_score": round(risk_score, 2)
        }
