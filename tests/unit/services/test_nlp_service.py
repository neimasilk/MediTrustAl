import pytest
from src.app.services.nlp_service import extract_entities_placeholder

def test_extract_entities_placeholder_returns_dummy_data():
    """
    Tests that extract_entities_placeholder returns the expected dummy data
    regardless of the input.
    """
    expected_output = {
        "entities": [
            {"text": "Blood Pressure", "type": "VitalSign"},
            {"text": "120/80 mmHg", "type": "Measurement"}
        ]
    }

    # Test with some sample text
    result1 = extract_entities_placeholder("test input")
    assert result1 == expected_output

    # Test with different sample text
    result2 = extract_entities_placeholder("another test input with more text")
    assert result2 == expected_output

    # Test with empty string
    result3 = extract_entities_placeholder("")
    assert result3 == expected_output

    # Test with None (though type hint expects str, good to be robust)
    # Depending on how strict we want to be, this could also be a TypeError test
    # For a placeholder, consistent dummy output is the key.
    result4 = extract_entities_placeholder(None)
    assert result4 == expected_output
