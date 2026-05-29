from healthcare_ai_platform.ml.readmission_model import ReadmissionRiskModel

def test_risk_score_between_zero_and_one():
    result=ReadmissionRiskModel().predict({"prior_admission_count":2,"abnormal_lab_count":1,"has_follow_up_gap":True})
    assert 0 <= result["readmission_risk"] <= 1
    assert result["risk_level"] in {"low","medium","high"}
