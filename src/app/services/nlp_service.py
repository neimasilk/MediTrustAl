def extract_entities_placeholder(text_input: str):
    """
    Placeholder function for NLP entity extraction.
    Ignores the input text and returns a dummy list of entities.
    """
    return {
        "entities": [
            {"text": "Blood Pressure", "type": "VitalSign"},
            {"text": "120/80 mmHg", "type": "Measurement"}
        ]
    }
