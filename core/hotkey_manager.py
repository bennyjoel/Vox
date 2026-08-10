import logging
import keyboard

logger = logging.getLogger(__name__)

class HotkeyManager:
    """Manages global hotkeys using the 'keyboard' module."""
    
    def __init__(self, on_press: callable, on_release: callable = None, mode: str = 'toggle'):
        self.on_press = on_press
        self.on_release = on_release
        self.mode = mode # 'toggle' or 'push_to_talk'
        self.hotkey_str = ""
        self.is_active = False

    def register(self, modifiers: list[str], key: str):
        """Prepares hotkey configuration."""
        keys = modifiers.copy()
        if key:
            keys.append(key)
        self.hotkey_str = '+'.join(keys).lower()

    def _handle_hotkey(self):
        if self.mode == 'toggle':
            self.is_active = not self.is_active
            if self.is_active:
                if self.on_press:
                    self.on_press()
            else:
                if self.on_release:
                    self.on_release()
        elif self.mode == 'push_to_talk':
            if self.on_press:
                self.on_press()

    def start(self):
        """Starts the hotkey listener."""
        try:
            keyboard.add_hotkey(self.hotkey_str, self._handle_hotkey, suppress=True)
            logger.info(f"Hotkey '{self.hotkey_str}' registered successfully.")
        except Exception as e:
            logger.error(f"Failed to register hotkey: {e}")

    def stop(self):
        """Stops the hotkey listener."""
        try:
            keyboard.remove_hotkey(self.hotkey_str)
            logger.info("Hotkey unregistered.")
        except Exception:
            pass
