import pytest
import re

class OfflineFormatter:
    def format(self, text):
        if not text:
            return ""
        
        # Remove filler words
        fillers = [r'\bum\b', r'\buh\b', r'\blike\b']
        for f in fillers:
            text = re.sub(f, '', text, flags=re.IGNORECASE)
            
        # Capitalize and clean spaces
        text = " ".join(text.split())
        if text:
            text = text[0].upper() + text[1:]
            
        return text

class GeminiFormatter:
    def __init__(self, api_key=None):
        self.api_key = api_key
        
    def format(self, text):
        return text  # mock

@pytest.fixture
def offline_formatter():
    return OfflineFormatter()

def test_offline_formatter_basic(offline_formatter):
    result = offline_formatter.format("hello world")
    assert result == "Hello world"

def test_filler_word_removal(offline_formatter):
    result = offline_formatter.format("um hello uh world like")
    assert result == "Hello world"

def test_capitalization(offline_formatter):
    assert offline_formatter.format("this is a test") == "This is a test"

def test_edge_cases(offline_formatter):
    assert offline_formatter.format("") == ""
    assert offline_formatter.format("   ") == ""
    assert offline_formatter.format("um uh") == ""

def test_gemini_formatter_init():
    formatter = GeminiFormatter(api_key="dummy_key")
    assert formatter.api_key == "dummy_key"
