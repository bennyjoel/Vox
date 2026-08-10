import os
import logging
import numpy as np
from dataclasses import dataclass
from typing import Optional, List

try:
    from faster_whisper import WhisperModel
    FASTER_WHISPER_AVAILABLE = True
except ImportError:
    logging.error("faster-whisper not found. Please install: pip install faster-whisper")
    FASTER_WHISPER_AVAILABLE = False

from config import MODELS_DIR

logger = logging.getLogger(__name__)

@dataclass
class TranscriptionResult:
    text: str
    language: str
    avg_logprob: float
    compression_ratio: float
    segments: list
    duration: float

class Transcriber:
    """Wrapper around faster-whisper for transcription."""
    
    def __init__(self, model_name: str = 'small', device: str = 'auto', compute_type: str = 'auto'):
        self.model_name = model_name
        self.model = None
        
        if not FASTER_WHISPER_AVAILABLE:
            return
            
        try:
            # Auto-detect compute type based on device if 'auto'
            import torch
            if device == 'auto':
                device = 'cuda' if torch.cuda.is_available() else 'cpu'
            if compute_type == 'auto':
                compute_type = 'float16' if device == 'cuda' else 'int8'
                
            logger.info(f"Loading Whisper model {model_name} on {device} with {compute_type}...")
            
            # This will download the model if not present, caching in MODELS_DIR
            self.model = WhisperModel(
                model_name, 
                device=device, 
                compute_type=compute_type,
                download_root=MODELS_DIR
            )
            logger.info("Whisper model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            raise RuntimeError(f"Could not load model {model_name}. {e}")

    def transcribe(self, audio: np.ndarray, language: Optional[str] = None, 
                  initial_prompt: Optional[str] = None, hotwords: Optional[str] = None) -> TranscriptionResult:
        """Transcribes audio using the loaded model."""
        if self.model is None:
            raise RuntimeError("Transcriber model is not loaded.")
            
        if len(audio) == 0:
            return TranscriptionResult("", "en", 0.0, 1.0, [], 0.0)
            
        try:
            # faster_whisper accepts 1D float32 numpy arrays directly at 16kHz
            if len(audio.shape) > 1:
                audio = audio.flatten()
                
            segments_gen, info = self.model.transcribe(
                audio, 
                language=language,
                initial_prompt=initial_prompt,
                hotwords=hotwords,
                vad_filter=True # Use built-in VAD as secondary filter
            )
            
            segments = list(segments_gen)
            
            text = " ".join([seg.text.strip() for seg in segments])
            
            # Calculate averages
            avg_logprob = sum(seg.avg_logprob for seg in segments) / len(segments) if segments else 0.0
            avg_compression = sum(seg.compression_ratio for seg in segments) / len(segments) if segments else 1.0
            
            return TranscriptionResult(
                text=text,
                language=info.language,
                avg_logprob=avg_logprob,
                compression_ratio=avg_compression,
                segments=segments,
                duration=info.duration
            )
            
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return TranscriptionResult("", "en", 0.0, 1.0, [], 0.0)

    @staticmethod
    def get_available_models() -> List[str]:
        return ['tiny', 'base', 'small', 'medium', 'large-v3-turbo']
        
    @staticmethod
    def is_model_available(model_name: str) -> bool:
        # Simplistic check - faster-whisper usually puts them in models--guillaumekln--faster-whisper-model_name
        # Proper way is to try initializing or use huggingface_hub
        # For simplicity we just return True and let initialization handle it
        return True
