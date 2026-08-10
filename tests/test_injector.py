import pytest
import sys

class MockTextInjector:
    def __init__(self):
        self.clipboard_history = []
        
    def inject(self, text):
        self.clipboard_history.append(text)
        return True

@pytest.fixture
def injector():
    return MockTextInjector()

def test_injector_initialization(injector):
    assert injector.clipboard_history == []

@pytest.mark.skipif(sys.platform != "win32", reason="TextInjector is designed for Windows only")
def test_clipboard_operations(injector):
    success = injector.inject("Hello world")
    assert success is True
    assert "Hello world" in injector.clipboard_history
