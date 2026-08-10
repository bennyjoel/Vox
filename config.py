import os

APP_NAME = "VoxType"
LOCALAPPDATA = os.environ.get('LOCALAPPDATA', os.path.expanduser('~'))
APP_DATA_DIR = os.path.join(LOCALAPPDATA, 'VoxType')
MODELS_DIR = os.path.join(APP_DATA_DIR, 'models')
DB_PATH = os.path.join(APP_DATA_DIR, 'voxtype.db')
VOICEPRINT_PATH = os.path.join(APP_DATA_DIR, 'voiceprint.npy')

os.makedirs(APP_DATA_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)

DEFAULT_HOTKEY = {'modifiers': ['shift', 'alt'], 'key': 'space'}
SAMPLE_RATE = 16000
CHANNELS = 1
BLOCKSIZE = 512
VAD_THRESHOLD = 0.5
SILENCE_DURATION_MS = 500
PRE_ROLL_MS = 150
MAX_SEGMENT_SECONDS = 15
SPEAKER_VERIFY_THRESHOLD = 0.68
GIBBERISH_LOGPROB_THRESHOLD = -1.0
GIBBERISH_COMPRESSION_THRESHOLD = 2.4
GIBBERISH_DICT_VALIDITY_THRESHOLD = 0.6
GIBBERISH_REPETITION_THRESHOLD = 0.3
GEMINI_TIMEOUT = 5
GEMINI_MAX_RETRIES = 2
DEFAULT_WHISPER_MODEL = 'small'

ENROLLMENT_SENTENCES = [
    "I am setting up my voice profile for VoxType so it can recognize me.",
    "The quick brown fox jumps over the lazy dog.",
    "Artificial intelligence is transforming how we interact with computers.",
    "My unique voice will be used to unlock dictation features securely.",
    "Please verify this audio sample against my stored voiceprint."
]
