import pytest
from src.app.services.ai_service import predict_risk_placeholder

def test_predict_risk_placeholder_returns_dummy_data():
    expected_output = {
        "risk_level": "low",
        "score": 0.1,
        "message": "This is a placeholder risk prediction."
    }
    # Test dengan beberapa input dummy berbeda
    result1 = predict_risk_placeholder({"age": 50, "systolic_bp": 120})
    assert result1 == expected_output

    result2 = predict_risk_placeholder({"feature_x": "value_a", "feature_y": 123})
    assert result2 == expected_output

    result3 = predict_risk_placeholder({}) # Input kosong
    assert result3 == expected_output
