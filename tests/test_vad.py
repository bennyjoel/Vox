import pytest
import numpy as np

class MockVAD:
    def __init__(self):
        self.is_initialized = True
        
    def has_speech(self, audio_data):
        # Dummy logic: if max amplitude > 0.1, it's speech
        if np.max(np.abs(audio_data)) > 0.1:
            return True
        return False

@pytest.fixture
def vad():
    return MockVAD()

def test_vad_initialization(vad):
    assert vad.is_initialized is True

def test_silent_audio(vad):
    # Pure silence
    audio = np.zeros(16000, dtype=np.float32)
    assert vad.has_speech(audio) is False

def test_tone_noise_audio(vad):
    # High amplitude "noise"
    audio = np.ones(16000, dtype=np.float32) * 0.5
    assert vad.has_speech(audio) is True
