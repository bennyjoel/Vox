import pytest
import re

# Mock GibberishFilter since core isn't provided
class GibberishFilter:
    def is_gibberish(self, text):
        if not text:
            return True
        text = text.strip()
        
        # Test empty or too short
        if len(text) < 2:
            return True
            
        # Test numbers only
        if re.match(r'^[0-9\s]+$', text):
            return True
            
        # Common whisper hallucinations
        hallucinations = ["thanks for watching", "subscribe", "thank you"]
        if text.lower() in hallucinations:
            return True
            
        return False

@pytest.fixture
def filter():
    return GibberishFilter()

def test_empty_text(filter):
    assert filter.is_gibberish("") is True
    assert filter.is_gibberish("   ") is True

def test_single_word(filter):
    assert filter.is_gibberish("a") is True
    # Real single words might not be gibberish depending on logic, but single char is
    assert filter.is_gibberish("I") is True

def test_numbers_only(filter):
    assert filter.is_gibberish("123") is True
    assert filter.is_gibberish("1 2 3 4") is True

def test_known_gibberish(filter):
    assert filter.is_gibberish("Thanks for watching") is True
    assert filter.is_gibberish("subscribe") is True

def test_real_english(filter):
    assert filter.is_gibberish("Hello, this is a real sentence.") is False
    assert filter.is_gibberish("Testing the microphone now.") is False
