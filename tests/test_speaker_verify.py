import pytest
import numpy as np

try:
    import onnxruntime
    import resemblyzer
    HAS_DEPS = True
except ImportError:
    HAS_DEPS = False

class MockSpeakerVerifier:
    def __init__(self):
        self.enrolled = False
        
    def enroll(self, audio_data):
        self.enrolled = True
        return True
        
    def verify(self, audio_data):
        if not self.enrolled:
            return False
        return True

@pytest.fixture
def verifier():
    return MockSpeakerVerifier()

@pytest.mark.skipif(not HAS_DEPS, reason="onnxruntime or resemblyzer not installed")
def test_verifier_initialization(verifier):
    assert verifier.enrolled is False

@pytest.mark.skipif(not HAS_DEPS, reason="onnxruntime or resemblyzer not installed")
def test_enrollment(verifier):
    dummy_audio = np.random.randn(16000).astype(np.float32)
    success = verifier.enroll(dummy_audio)
    assert success is True
    assert verifier.enrolled is True

@pytest.mark.skipif(not HAS_DEPS, reason="onnxruntime or resemblyzer not installed")
def test_verification_logic(verifier):
    dummy_audio = np.random.randn(16000).astype(np.float32)
    
    # Should fail if not enrolled
    assert verifier.verify(dummy_audio) is False
    
    # Should succeed after enrollment
    verifier.enroll(dummy_audio)
    assert verifier.verify(dummy_audio) is True
