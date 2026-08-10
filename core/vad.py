import logging
import numpy as np
import webrtcvad

from config import SAMPLE_RATE, SILENCE_DURATION_MS, MAX_SEGMENT_SECONDS

logger = logging.getLogger(__name__)

class VoiceActivityDetector:
    """Detects voice activity using WebRTC VAD."""
    
    def __init__(self, mode: int = 3):
        # mode 0-3 (3 is most aggressive in filtering out non-speech)
        self.vad = webrtcvad.Vad(mode)
        
    def process_audio(self, audio: np.ndarray) -> list[np.ndarray]:
        """Processes raw float32 audio and returns a list of speech segments."""
        if len(audio) == 0:
            return []

        if len(audio.shape) > 1:
            audio_1d = audio.flatten()
        else:
            audio_1d = audio

        # WebRTC VAD requires 16-bit PCM mono audio
        # Convert float32 [-1.0, 1.0] to int16
        audio_int16 = (audio_1d * 32767).astype(np.int16)
        
        # WebRTC VAD accepts 10, 20, or 30 ms frames
        frame_duration_ms = 30
        frame_size = int(SAMPLE_RATE * (frame_duration_ms / 1000.0))
        
        segments = []
        current_segment = []
        in_speech = False
        silence_frames = 0
        max_silence_frames = int((SILENCE_DURATION_MS / 1000.0) * SAMPLE_RATE / frame_size)
        
        for i in range(0, len(audio_int16) - frame_size + 1, frame_size):
            frame = audio_int16[i:i+frame_size]
            frame_bytes = frame.tobytes()
            
            try:
                is_speech = self.vad.is_speech(frame_bytes, SAMPLE_RATE)
            except Exception as e:
                logger.error(f"VAD error: {e}")
                is_speech = False
                
            if is_speech:
                if not in_speech:
                    in_speech = True
                current_segment.append(audio_1d[i:i+frame_size])
                silence_frames = 0
            else:
                if in_speech:
                    current_segment.append(audio_1d[i:i+frame_size])
                    silence_frames += 1
                    if silence_frames >= max_silence_frames:
                        in_speech = False
                        segments.append(np.concatenate(current_segment))
                        current_segment = []
                        
        if in_speech and current_segment:
            segments.append(np.concatenate(current_segment))
            
        return segments
