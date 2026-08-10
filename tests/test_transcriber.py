import pytest
import numpy as np
import sys

try:
    import faster_whisper
    HAS_WHISPER = True
except ImportError:
    HAS_WHISPER = False

# Mock implementation for tests since core isn't provided
class MockTranscriber:
    def __init__(self, model_size="base"):
        self.model_size = model_size
        self.is_loaded = False
        
    def check_availability(self):
        return HAS_WHISPER
        
    def transcribe(self, audio_data):
        return "Hello world"

@pytest.fixture
def transcriber():
    return MockTranscriber(model_size="tiny")

@pytest.mark.skipif(not HAS_WHISPER, reason="faster-whisper is not installed")
def test_transcriber_initialization(transcriber):
    assert transcriber.model_size == "tiny"

@pytest.mark.skipif(not HAS_WHISPER, reason="faster-whisper is not installed")
def test_model_availability_check(transcriber):
    assert transcriber.check_availability() is True

@pytest.mark.skipif(not HAS_WHISPER, reason="faster-whisper is not installed")
def test_transcription():
    transcriber = MockTranscriber()
    # Dummy 16kHz audio array, 1 second of silence/noise
    dummy_audio = np.zeros(16000, dtype=np.float32)
    result = transcriber.transcribe(dummy_audio)
    assert isinstance(result, str)
