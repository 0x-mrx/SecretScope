from app.services.risk_engine import RiskEngine

def test_risk_calculation_website_aws():
    res = RiskEngine.calculate_risk("WEBSITE", "AWS_ACCESS_KEY", "CRITICAL")
    assert res["exposure_risk"] == "CRITICAL"
    assert res["compliance_risk"] == "CRITICAL"
    assert res["operational_risk"] == "CRITICAL"
    assert res["risk_score"] == 100.0

def test_risk_calculation_file_low():
    res = RiskEngine.calculate_risk("FILE_PATH", "OTHER", "LOW")
    assert res["exposure_risk"] == "MEDIUM"
    assert res["compliance_risk"] == "MEDIUM"
    assert res["operational_risk"] == "LOW"
    # Base = 25.0 * 0.8 = 20.0
    assert res["risk_score"] == 20.0
