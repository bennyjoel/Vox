import os
import logging
import numpy as np

try:
    from resemblyzer import VoiceEncoder, preprocess_wav
    RESEMBLYZER_AVAILABLE = True
except ImportError:
    logging.warning("resemblyzer not found. Speaker verification will be disabled unless installed.")
    RESEMBLYZER_AVAILABLE = False

from config import VOICEPRINT_PATH, SPEAKER_VERIFY_THRESHOLD, SAMPLE_RATE

logger = logging.getLogger(__name__)

class SpeakerVerifier:
    """Handles speaker enrollment and verification."""
    
    def __init__(self):
        self.encoder = None
        if RESEMBLYZER_AVAILABLE:
            try:
                # VoiceEncoder downloads its model on first use if not present
                self.encoder = VoiceEncoder()
                logger.info("Speaker verification model loaded.")
            except Exception as e:
                logger.error(f"Failed to initialize VoiceEncoder: {e}")

    def enroll(self, audio_segments: list[np.ndarray]) -> np.ndarray:
        """Extracts embeddings from segments, averages them, and saves the voiceprint."""
        if not self.encoder:
            logger.warning("Speaker verifier not available for enrollment.")
            return np.zeros(256)
            
        try:
            embeddings = []
            for seg in audio_segments:
                if len(seg.shape) > 1:
                    seg = seg.flatten()
                
                # Resemblyzer preprocess expects standard shape
                processed = preprocess_wav(seg, source_sr=SAMPLE_RATE)
                embed = self.encoder.embed_utterance(processed)
                embeddings.append(embed)
                
            if not embeddings:
                raise ValueError("No valid audio segments provided for enrollment.")
                
            # Average and normalize
            mean_embed = np.mean(embeddings, axis=0)
            voiceprint = mean_embed / np.linalg.norm(mean_embed)
            
            # Save
            np.save(VOICEPRINT_PATH, voiceprint)
            logger.info(f"Voiceprint saved to {VOICEPRINT_PATH}")
            return voiceprint
            
        except Exception as e:
            logger.error(f"Enrollment failed: {e}")
            return np.zeros(256)

    def verify(self, audio: np.ndarray) -> tuple[bool, float]:
        """Verifies if the audio matches the enrolled voiceprint."""
        if not self.encoder:
            logger.warning("Speaker verifier not available, skipping verification.")
            return True, 1.0 # Allow if not available
            
        if not self.is_enrolled():
            logger.warning("No voiceprint enrolled, skipping verification.")
            return True, 1.0
            
        try:
            voiceprint = np.load(VOICEPRINT_PATH)
            
            if len(audio.shape) > 1:
                audio = audio.flatten()
                
            processed = preprocess_wav(audio, source_sr=SAMPLE_RATE)
            embed = self.encoder.embed_utterance(processed)
            
            # Cosine similarity
            score = np.dot(voiceprint, embed) / (np.linalg.norm(voiceprint) * np.linalg.norm(embed))
            
            is_owner = score >= SPEAKER_VERIFY_THRESHOLD
            return bool(is_owner), float(score)
            
        except Exception as e:
            logger.error(f"Verification failed: {e}")
            return False, 0.0

    def is_enrolled(self) -> bool:
        """Checks if a voiceprint exists."""
        return os.path.exists(VOICEPRINT_PATH)

    def delete_voiceprint(self):
        """Removes the stored voiceprint."""
        if self.is_enrolled():
            try:
                os.remove(VOICEPRINT_PATH)
                logger.info("Voiceprint deleted.")
            except Exception as e:
                logger.error(f"Failed to delete voiceprint: {e}")
