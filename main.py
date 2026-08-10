import os
import sys
import threading
import logging
import time

# Configure logging to file to prevent pythonw.exe silent crashes
log_dir = os.path.join(os.environ.get('LOCALAPPDATA', os.path.expanduser('~')), 'VoxType')
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=os.path.join(log_dir, 'voxtype.log'),
    filemode='a'
)
logger = logging.getLogger("VoxType")

# Import Core Modules
from config import APP_DATA_DIR, MODELS_DIR, DEFAULT_HOTKEY
from core.audio_recorder import AudioRecorder
from core.vad import VoiceActivityDetector
from core.transcriber import Transcriber
from core.speaker_verify import SpeakerVerifier
from core.gibberish_filter import GibberishFilter
from core.gemini_formatter import GeminiFormatter
from core.offline_formatter import OfflineFormatter
from core.text_injector import TextInjector
from core.hotkey_manager import HotkeyManager
from core.context_detector import ContextDetector
from core.snippet_engine import SnippetEngine

class DummyDBManager:
    """A dummy database manager for SnippetEngine."""
    def __init__(self):
        self.snippets = {}
    def get_snippets(self): return self.snippets
    def add_snippet(self, t, e): self.snippets[t] = e
    def remove_snippet(self, t): 
        if t in self.snippets: del self.snippets[t]

class VoxTypeApp:
    def __init__(self):
        self.is_recording = False
        self.components_ready = False
        
        # Initialize Core Components
        self.db = DummyDBManager()
        self.audio = AudioRecorder()
        self.vad = VoiceActivityDetector()
        self.transcriber = None # Load async
        self.speaker_verifier = SpeakerVerifier()
        self.gemini = GeminiFormatter()
        self.offline_formatter = OfflineFormatter()
        self.injector = TextInjector()
        self.context_detector = ContextDetector()
        self.snippet_engine = SnippetEngine(self.db)
        self.hotkey_manager = HotkeyManager(on_press=self.toggle_recording, mode='toggle')
        self.api = None
        
    def start(self):
        # Async load of whisper model
        threading.Thread(target=self._load_transcriber, daemon=True).start()
        
        try:
            self.hotkey_manager.register(DEFAULT_HOTKEY['modifiers'], DEFAULT_HOTKEY['key'])
            self.hotkey_manager.start()
            logger.info("VoxType core initialized. Press Ctrl+Shift+Space to toggle recording.")
        except Exception as e:
            logger.error(f"Failed to register hotkey: {e}")
            
    def _load_transcriber(self):
        try:
            self.transcriber = Transcriber()
            self.components_ready = True
            logger.info("Transcriber ready.")
        except Exception as e:
            logger.error(f"Failed to initialize Transcriber: {e}")

    def toggle_recording(self):
        if not self.components_ready:
            logger.warning("Components not ready yet. Please wait.")
            return
            
        if self.is_recording:
            self.stop_recording()
        else:
            self.start_recording()

    def start_recording(self):
        logger.info("Started recording...")
        self.is_recording = True
        if self.api:
            self.api.set_status("recording")
        self.audio.start()

    def stop_recording(self):
        logger.info("Stopped recording. Processing...")
        self.is_recording = False
        if self.api:
            self.api.set_status("processing")
        self.audio.stop()
        
        audio_data = self.audio.get_audio()
        
        # Process in a background thread so we don't block
        threading.Thread(target=self.process_audio, args=(audio_data,), daemon=True).start()

    def process_audio(self, audio_data):
        if len(audio_data) == 0:
            logger.warning("No audio recorded.")
            return

        segments = self.vad.process_audio(audio_data)
        if not segments:
            logger.warning("No speech detected.")
            return
            
        # Combine segments for transcription (could be done per segment)
        import numpy as np
        combined_audio = np.concatenate(segments)
        
        # Speaker Verify (optional)
        if self.speaker_verifier.is_enrolled():
            is_owner, score = self.speaker_verifier.verify(combined_audio)
            if not is_owner:
                logger.warning(f"Speaker not verified (score: {score:.2f}). Dropping transcription.")
                return
            logger.info(f"Speaker verified (score: {score:.2f}).")
            
        # Transcribe
        result = self.transcriber.transcribe(combined_audio)
        if not result.text:
            return
            
        logger.info(f"Raw Text: {result.text}")
        
        # Gibberish check
        is_gibberish, reason = GibberishFilter.is_gibberish(result.text, result.avg_logprob, result.compression_ratio)
        if is_gibberish:
            logger.warning(f"Detected gibberish ({reason}), discarding.")
            return
            
        # Context Detection
        context = self.context_detector.get_active_context()
        logger.info(f"Context: {context['context_category']} ({context['app_name']})")
        
        # Snippets
        expanded_text = self.snippet_engine.check_and_expand(result.text)
        
        # Format
        if self.gemini.is_configured():
            final_text = self.gemini.format_text(expanded_text, context=context['context_category'])
        else:
            final_text = self.offline_formatter.format_text(expanded_text)
            
        logger.info(f"Final Text: {final_text}")
        
        # Inject
        self.injector.inject(final_text, method='clipboard')
        if self.api:
            self.api.set_status("idle")

    def shutdown(self):
        logger.info("Shutting down...")
        self.hotkey_manager.stop()

if __name__ == '__main__':
    import webview
    from ui.backend import VoxTypeAPI
    import os
    
    app = VoxTypeApp()
    app.start()
    
    api = VoxTypeAPI(app=app)
    app.api = api
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    html_path = os.path.join(base_dir, 'ui', 'frontend', 'index.html')
    icon_path = os.path.join(base_dir, 'assets', 'icon.ico')
    
    window = webview.create_window(
        'VoxType', 
        url=html_path, 
        js_api=api,
        width=360, 
        height=100, 
        frameless=True,
        easy_drag=True,
        transparent=True,
        on_top=True,
        background_color='#000000'
    )
    
    def on_closed():
        app.shutdown()
        import sys
        sys.exit(0)
        
    window.events.closed += on_closed
    
    logger.info("Starting pywebview UI...")
    try:
        webview.start(debug=False, icon=icon_path)
    except Exception as e:
        logger.error(f"Failed to start UI: {e}")
        app.shutdown()
