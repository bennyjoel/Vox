import logging
import queue
import collections
import numpy as np
try:
    import sounddevice as sd
except ImportError:
    logging.error("sounddevice package not found. Please install it using 'pip install sounddevice'")
    sd = None

from config import SAMPLE_RATE, CHANNELS, BLOCKSIZE, PRE_ROLL_MS

logger = logging.getLogger(__name__)

class AudioRecorder:
    """Records audio using sounddevice WASAPI shared mode."""
    
    def __init__(self, gain_boost: float = 1.0):
        self.gain_boost = gain_boost
        self.stream = None
        self.audio_queue = queue.Queue()
        self.is_recording = False
        
        # Calculate pre-roll buffer size
        pre_roll_samples = int(SAMPLE_RATE * (PRE_ROLL_MS / 1000.0))
        self.pre_roll_blocks = max(1, pre_roll_samples // BLOCKSIZE)
        self.pre_roll_buffer = collections.deque(maxlen=self.pre_roll_blocks)
        
    def _audio_callback(self, indata: np.ndarray, frames: int, time, status):
        if status:
            logger.warning(f"Audio stream status: {status}")
            
        data = indata.copy()
        if self.gain_boost != 1.0:
            data = np.clip(data * self.gain_boost, -1.0, 1.0)
            
        if self.is_recording:
            self.audio_queue.put(data)
        else:
            self.pre_roll_buffer.append(data)
            
    def start(self):
        """Starts recording audio."""
        if self.is_recording:
            return
            
        if sd is None:
            logger.error("Cannot start recording: sounddevice is not available.")
            return

        self.audio_queue = queue.Queue()
        # Add pre-roll buffer to queue
        for block in self.pre_roll_buffer:
            self.audio_queue.put(block)
            
        self.is_recording = True
        try:
            kwargs = {
                'samplerate': SAMPLE_RATE,
                'channels': CHANNELS,
                'dtype': 'float32',
                'blocksize': BLOCKSIZE,
                'callback': self._audio_callback
            }
                
            self.stream = sd.InputStream(**kwargs)
            self.stream.start()
            logger.info("Started audio recording.")
        except Exception as e:
            logger.error(f"Failed to start audio stream: {e}")
            self.is_recording = False

    def stop(self):
        """Stops recording and returns the stream."""
        if not self.is_recording:
            return
            
        self.is_recording = False
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
            logger.info("Stopped audio recording.")

    def get_audio(self) -> np.ndarray:
        """Retrieves all recorded audio as a single numpy array."""
        chunks = []
        while True:
            try:
                chunks.append(self.audio_queue.get_nowait())
            except queue.Empty:
                break
            
        if not chunks:
            return np.zeros((0, 1), dtype=np.float32)
            
        return np.concatenate(chunks, axis=0)
        
    def __del__(self):
        self.stop()
