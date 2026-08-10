import logging
import time

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    logging.warning("google-generativeai not found. Gemini formatting disabled.")
    GENAI_AVAILABLE = False

from config import GEMINI_TIMEOUT, GEMINI_MAX_RETRIES

logger = logging.getLogger(__name__)

class GeminiFormatter:
    """Uses Gemini API to format dictation text."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.model = None
        if self.api_key and GENAI_AVAILABLE:
            self._init_client()

    def _init_client(self):
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash')
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
            self.model = None

    def update_key(self, api_key: str):
        self.api_key = api_key
        if self.api_key and GENAI_AVAILABLE:
            self._init_client()
        else:
            self.model = None

    def is_configured(self) -> bool:
        return self.api_key is not None and self.model is not None and GENAI_AVAILABLE

    def test_connection(self) -> bool:
        if not self.is_configured():
            return False
        try:
            response = self.model.generate_content("Hello")
            return response.text is not None
        except Exception as e:
            logger.error(f"Gemini connection test failed: {e}")
            return False

    def format_text(self, raw_text: str, context: str = 'general', custom_prompt: str = None) -> str:
        if not self.is_configured() or not raw_text.strip():
            return raw_text

        system_prompt = (
            "You are a dictation text formatter. Clean up the following dictated speech into polished written text. Rules:\n"
            "1. Remove all filler words (um, uh, like, you know, basically, actually, so, well, I mean)\n"
            "2. Fix grammar, spelling, and punctuation\n"
            "3. Handle self-corrections (e.g., 'Tuesday no wait Wednesday' -> 'Wednesday')\n"
            "4. Format numbers, dates, and times naturally\n"
            "5. Do NOT add any information that wasn't in the original speech\n"
            "6. Do NOT wrap in quotes or add commentary\n"
            "7. Return ONLY the cleaned text\n"
        )

        context_additions = {
            'chat': 'Keep the tone casual and friendly. Use contractions.',
            'email': 'Keep the tone professional and clear.',
            'code': 'Preserve technical terms, variable names, and code-related vocabulary exactly.',
            'document': 'Use proper paragraph structure and formal tone.'
        }

        if custom_prompt:
            system_prompt += f"\nAdditional instructions: {custom_prompt}\n"
        elif context in context_additions:
            system_prompt += f"\nContext: {context_additions[context]}\n"

        prompt = f"{system_prompt}\n\nRaw speech:\n{raw_text}"

        for attempt in range(GEMINI_MAX_RETRIES):
            try:
                # Setting an explicit timeout is tricky in the current SDK for generate_content
                # we rely on default timeouts, but handle exceptions
                response = self.model.generate_content(prompt)
                
                if response.text:
                    return response.text.strip()
                return raw_text
                
            except Exception as e:
                logger.warning(f"Gemini formatting attempt {attempt + 1} failed: {e}")
                time.sleep(1)
                
        logger.error("All Gemini formatting attempts failed. Returning raw text.")
        return raw_text

    def execute_command(self, command: str, selected_text: str) -> str:
        if not self.is_configured():
            return selected_text
            
        prompt = (
            f"Apply the following command to the selected text.\n"
            f"Command: {command}\n"
            f"Selected text:\n{selected_text}\n"
            f"Return ONLY the modified text, without quotes or explanation."
        )
        
        try:
            response = self.model.generate_content(prompt)
            if response.text:
                return response.text.strip()
        except Exception as e:
            logger.error(f"Gemini command execution failed: {e}")
            
        return selected_text
