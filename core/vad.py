import logging
import numpy as np
import collections

try:
    import torch
    import torchaudio
    SILERO_AVAILABLE = True
except ImportError:
    logging.warning("torch not found, falling back to energy-based VAD")
    SILERO_AVAILABLE = False

from config import SAMPLE_RATE, SILENCE_DURATION_MS, MAX_SEGMENT_SECONDS

logger = logging.getLogger(__name__)

class VoiceActivityDetector:
    """Detects voice activity in audio streams."""
    
    def __init__(self, threshold: float = 0.5):
        self.threshold = threshold
        self.silero_model = None
        
        if SILERO_AVAILABLE:
            try:
                model, utils = torch.hub.load(
                    repo_or_dir='snakers4/silero-vad',
                    model='silero_vad',
                    force_reload=False,
                    trust_repo=True
                )
                self.silero_model = model
                self.get_speech_timestamps = utils[0]
                logger.info("Loaded Silero VAD model.")
            except Exception as e:
                logger.error(f"Failed to load Silero VAD: {e}")
                self.silero_model = None

    def process_audio(self, audio: np.ndarray) -> list[np.ndarray]:
        """Processes raw audio and returns a list of speech segments."""
        if len(audio) == 0:
            return []

        # Convert to 1D array if needed
        if len(audio.shape) > 1:
            audio_1d = audio.flatten()
        else:
            audio_1d = audio

        segments = []
        
        if self.silero_model is not None:
            try:
                # Silero expects torch tensor
                tensor = torch.from_numpy(audio_1d)
                
                # Get timestamps
                speech_timestamps = self.get_speech_timestamps(
                    tensor, 
                    self.silero_model, 
                    sampling_rate=SAMPLE_RATE,
                    threshold=self.threshold,
                    min_silence_duration_ms=SILENCE_DURATION_MS
                )
                
                for ts in speech_timestamps:
                    start = ts['start']
                    end = ts['end']
                    # Apply MAX_SEGMENT_SECONDS limitation roughly
                    max_samples = int(MAX_SEGMENT_SECONDS * SAMPLE_RATE)
                    if end - start > max_samples:
                        end = start + max_samples
                        
                    segments.append(audio_1d[start:end])
                    
            except Exception as e:
                logger.error(f"Silero VAD processing failed: {e}")
                # Fallback to energy based
                segments = self._energy_vad(audio_1d)
        else:
            segments = self._energy_vad(audio_1d)
            
        return segments
        
    def _energy_vad(self, audio: np.ndarray) -> list[np.ndarray]:
        """Fallback energy-based VAD."""
        frame_size = int(SAMPLE_RATE * 0.03) # 30ms frames
        segments = []
        
        rms_threshold = 0.01 # Arbitrary energy threshold
        
        in_speech = False
        current_segment = []
        silence_frames = 0
        max_silence_frames = int((SILENCE_DURATION_MS / 1000.0) * SAMPLE_RATE / frame_size)
        
        for i in range(0, len(audio), frame_size):
            frame = audio[i:i+frame_size]
            if len(frame) < frame_size:
                break
                
            rms = np.sqrt(np.mean(frame**2))
            
            if rms > rms_threshold:
                if not in_speech:
                    in_speech = True
                current_segment.append(frame)
                silence_frames = 0
            else:
                if in_speech:
                    current_segment.append(frame)
                    silence_frames += 1
                    if silence_frames >= max_silence_frames:
                        in_speech = False
                        segments.append(np.concatenate(current_segment))
                        current_segment = []
                        
        if in_speech and current_segment:
            segments.append(np.concatenate(current_segment))
            
        return segments
