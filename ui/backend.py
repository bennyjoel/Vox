import json
import logging

class VoxTypeAPI:
    def __init__(self, app=None):
        self.app = app
        self.logger = logging.getLogger(__name__)
        # Mock initial state
        self._state = {
            "status": "idle", # idle, recording, processing
            "is_voice_locked": False,
            "model_loaded": True
        }

    def get_state(self) -> dict:
        return self._state

    def toggle_recording(self):
        if self.app:
            self.app.toggle_recording()
        return True

    def set_status(self, status: str):
        self._state["status"] = status

    def get_settings(self) -> dict:
        return {
            "general": {"startup": False, "mode": "toggle"},
            "ai": {"prompt": "Clean up this dictation.", "has_key": False},
            "audio": {"microphone": "default", "sensitivity": 50, "whisper_mode": False},
            "voice": {"voice_lock": False, "sensitivity": 75}
        }

    def save_settings(self, settings: dict):
        self.logger.info(f"Saving settings: {settings}")
        return True

    def get_history(self, limit=50, offset=0) -> list:
        return [
            {
                "id": 1,
                "timestamp": "2026-08-10T08:00:00Z",
                "app_context": "Notepad",
                "raw_text": "hello this is a test",
                "cleaned_text": "Hello, this is a test.",
                "word_count": 5
            }
        ]

    def search_history(self, query: str) -> list:
        return self.get_history()

    def delete_history_item(self, id: int):
        return True

    def get_stats(self) -> dict:
        return {
            "total_words": 15024,
            "total_dictations": 342,
            "time_saved_minutes": 120,
            "most_used_language": "English",
            "most_used_app": "VS Code"
        }

    def test_microphone(self) -> dict:
        return {"level": 0.8, "status": "ok"}

    def get_microphones(self) -> list:
        return [{"id": "default", "name": "Default Microphone"}, {"id": "1", "name": "USB Audio Device"}]

    def set_microphone(self, device_id: str):
        return True

    def start_enrollment(self):
        return True

    def submit_enrollment_sample(self, index: int):
        return {"success": True, "quality": 0.9}

    def finish_enrollment(self) -> bool:
        self._state["is_voice_locked"] = True
        return True

    def test_voice_match(self) -> dict:
        return {"match": True, "confidence": 0.95}

    def delete_voiceprint(self):
        self._state["is_voice_locked"] = False
        return True

    def get_enrollment_sentences(self) -> list:
        return [
            "The quick brown fox jumps over the lazy dog.",
            "I am recording my voice to create a unique voiceprint.",
            "This dictation software will only respond to me.",
            "Artificial intelligence helps to transcribe my speech accurately.",
            "My voice is my password, verify me."
        ]

    def is_model_downloaded(self, model_name: str) -> bool:
        return True

    def download_model(self, model_name: str):
        return True

    def get_available_models(self) -> list:
        return [
            {"name": "tiny.en", "size": "39MB", "downloaded": True},
            {"name": "base.en", "size": "74MB", "downloaded": False}
        ]

    def test_gemini_key(self, api_key: str) -> bool:
        return True

    def get_snippets(self) -> list:
        return [{"trigger": "brb", "expansion": "Be right back!"}]

    def add_snippet(self, trigger: str, expansion: str):
        return True

    def delete_snippet(self, trigger: str):
        return True

    def get_dictionary_words(self) -> list:
        return ["VoxType", "pywebview", "glassmorphism"]

    def add_dictionary_word(self, word: str):
        return True

    def remove_dictionary_word(self, word: str):
        return True

    def get_app_profiles(self) -> list:
        return [{"app_pattern": "code.exe", "prompt": "Format as python code."}]

    def save_app_profile(self, profile: dict):
        return True

    def delete_app_profile(self, app_pattern: str):
        return True

    def quit_app(self):
        import sys
        sys.exit(0)
