import logging
import threading
import ctypes
import ctypes.wintypes
import time

logger = logging.getLogger(__name__)

# Win32 Constants
MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
MOD_WIN = 0x0008
MOD_NOREPEAT = 0x4000
WM_HOTKEY = 0x0312

VK_CODES = {
    'space': 0x20,
    'shift': 0x10,
    'ctrl': 0x11,
    'alt': 0x12,
    'a': 0x41, 'b': 0x42, 'c': 0x43, 'd': 0x44, 'e': 0x45, 'f': 0x46,
    'g': 0x47, 'h': 0x48, 'i': 0x49, 'j': 0x4A, 'k': 0x4B, 'l': 0x4C,
    'm': 0x4D, 'n': 0x4E, 'o': 0x4F, 'p': 0x50, 'q': 0x51, 'r': 0x52,
    's': 0x53, 't': 0x54, 'u': 0x55, 'v': 0x56, 'w': 0x57, 'x': 0x58,
    'y': 0x59, 'z': 0x5A,
    'f1': 0x70, 'f2': 0x71, 'f3': 0x72, 'f4': 0x73, 'f5': 0x74, 'f6': 0x75,
    'f7': 0x76, 'f8': 0x77, 'f9': 0x78, 'f10': 0x79, 'f11': 0x7A, 'f12': 0x7B
}

class HotkeyManager:
    """Manages global hotkeys using Win32 API."""
    
    def __init__(self, on_press: callable, on_release: callable = None, mode: str = 'toggle'):
        self.on_press = on_press
        self.on_release = on_release
        self.mode = mode # 'toggle' or 'push_to_talk'
        self.thread = None
        self.stop_event = threading.Event()
        self.hotkey_id = 1
        self.is_active = False # For toggle mode tracking
        
        self.user32 = ctypes.windll.user32

    def register(self, modifiers: list[str], key: str):
        """Prepares hotkey configuration."""
        self.fsModifiers = 0
        for mod in modifiers:
            mod = mod.lower()
            if mod == 'ctrl': self.fsModifiers |= MOD_CONTROL
            if mod == 'shift': self.fsModifiers |= MOD_SHIFT
            if mod == 'alt': self.fsModifiers |= MOD_ALT
            if mod == 'win': self.fsModifiers |= MOD_WIN
            
        self.fsModifiers |= MOD_NOREPEAT
        
        self.vk = VK_CODES.get(key.lower())
        if self.vk is None:
            raise ValueError(f"Unsupported key: {key}")

    def _message_loop(self):
        """Runs in a separate thread to handle Windows messages."""
        if not self.user32.RegisterHotKey(None, self.hotkey_id, self.fsModifiers, self.vk):
            logger.error("Failed to register hotkey")
            return
            
        logger.info("Hotkey registered successfully.")
        
        msg = ctypes.wintypes.MSG()
        while not self.stop_event.is_set():
            # Use PeekMessage with PM_REMOVE to not block indefinitely
            if self.user32.PeekMessageW(ctypes.byref(msg), None, 0, 0, 1): # 1 is PM_REMOVE
                if msg.message == WM_HOTKEY and msg.wParam == self.hotkey_id:
                    self._handle_hotkey()
                self.user32.TranslateMessage(ctypes.byref(msg))
                self.user32.DispatchMessageW(ctypes.byref(msg))
            else:
                time.sleep(0.01) # Prevent CPU hogging
                
        self.user32.UnregisterHotKey(None, self.hotkey_id)
        logger.info("Hotkey unregistered.")

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
            # Push-to-talk requires key release detection, which RegisterHotKey doesn't do easily.
            # We would need SetWindowsHookEx for true PTT, which can trigger anti-virus.
            # Fallback for now: just trigger on_press, maybe a timer triggers on_release, or we rely on VAD.
            # Better to just use toggle as default, but call on_press here anyway.
            if self.on_press:
                self.on_press()

    def start(self):
        """Starts the hotkey listener thread."""
        if self.thread and self.thread.is_alive():
            return
            
        self.stop_event.clear()
        self.thread = threading.Thread(target=self._message_loop, daemon=True)
        self.thread.start()

    def stop(self):
        """Stops the hotkey listener."""
        self.stop_event.set()
        if self.thread:
            self.thread.join(timeout=1.0)
            self.thread = None
