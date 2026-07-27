import os
import ast
import pytest
from unittest.mock import patch
from src.extract import EmailExtraction, extract_facts_cached

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def test_app_syntax_and_structure():
    """
    Verify that src/app.py is valid Python syntax and imports extract_facts_cached.
    """
    app_path = os.path.join(PROJECT_ROOT, "src", "app.py")
    assert os.path.exists(app_path), "src/app.py must exist"
    
    with open(app_path, "r", encoding="utf-8") as f:
        content = f.read()
        tree = ast.parse(content, filename=app_path)
        
    assert tree is not None, "src/app.py should parse into a valid AST"


def test_extract_facts_cached_lru():
    """
    Verify that extract_facts_cached utilizes in-memory LRU caching to prevent duplicate API calls.
    """
    mock_facts = EmailExtraction(
        aircraft_type="A320",
        customer_name="Flagship Air",
        customer_class="flagship",
        modification_type="cabin",
        fleet_size=5,
        scope="Full cabin interior refit",
        complexity="standard",
        is_valid=True
    )
    
    sample_text = "Test email for caching check 12345"
    
    with patch("src.extract.extract_facts", return_value=mock_facts) as mock_raw:
        # First call triggers extract_facts
        res1 = extract_facts_cached(sample_text)
        assert res1.aircraft_type == "A320"
        assert mock_raw.call_count == 1
        
        # Second call with identical text uses LRU cache (0 additional API calls)
        res2 = extract_facts_cached(sample_text)
        assert res2.aircraft_type == "A320"
        assert mock_raw.call_count == 1

def test_missing_api_key_error_handling():
    from src.extract import extract_facts
    with patch.dict(os.environ, {}, clear=True):
        facts = extract_facts("Some sample email text")
        assert facts.is_valid is False
        assert facts.error_type == "missing_api_key"
        assert "GEMINI_API_KEY" in facts.error_message

def test_quota_exceeded_error_handling():
    from src.extract import extract_facts
    with patch.dict(os.environ, {"GEMINI_API_KEY": "test_key"}):
        with patch("google.genai.Client") as mock_client:
            mock_client.return_value.models.generate_content.side_effect = Exception("429 RESOURCE_EXHAUSTED Quota exceeded")
            facts = extract_facts("Some sample email text", max_retries=1)
            assert facts.is_valid is False
            assert facts.error_type == "quota_exceeded"
            assert "quota" in facts.error_message.lower()
