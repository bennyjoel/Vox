import logging
import ctypes
import ctypes.wintypes

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    logging.warning("psutil not found. Context detector will have limited functionality.")
    PSUTIL_AVAILABLE = False

logger = logging.getLogger(__name__)

class ContextDetector:
    """Detects active window context to customize dictation."""
    
    def __init__(self):
        self.user32 = ctypes.windll.user32

    def get_active_context(self) -> dict:
        """Returns info about the active window and determined category."""
        context = {
            'window_title': 'Unknown',
            'app_name': 'Unknown',
            'context_category': 'general'
        }
        
        try:
            hwnd = self.user32.GetForegroundWindow()
            if not hwnd:
                return context

            # Get window title
            length = self.user32.GetWindowTextLengthW(hwnd)
            buff = ctypes.create_unicode_buffer(length + 1)
            self.user32.GetWindowTextW(hwnd, buff, length + 1)
            context['window_title'] = buff.value
            
            # Get process name
            pid = ctypes.wintypes.DWORD()
            self.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            
            if PSUTIL_AVAILABLE:
                try:
                    process = psutil.Process(pid.value)
                    context['app_name'] = process.name()
                except psutil.Error:
                    pass

            context['context_category'] = self._categorize(context['window_title'], context['app_name'])

        except Exception as e:
            logger.error(f"Error detecting context: {e}")
            
        return context

    def _categorize(self, title: str, app_name: str) -> str:
        title = title.lower()
        app_name = app_name.lower()
        
        combined = f"{title} {app_name}"
        
        chat_apps = ['slack', 'discord', 'whatsapp', 'telegram', 'teams', 'messenger']
        if any(app in combined for app in chat_apps):
            return 'chat'
            
        email_apps = ['gmail', 'outlook', 'thunderbird', 'mail']
        if any(app in combined for app in email_apps):
            return 'email'
            
        code_apps = ['visual studio', 'code', 'pycharm', 'intellij', 'sublime', 'vim', 'terminal', 'powershell', 'cmd']
        if any(app in combined for app in code_apps):
            return 'code'
            
        doc_apps = ['word', 'docs', 'notion', 'obsidian', 'notepad']
        if any(app in combined for app in doc_apps):
            return 'document'
            
        browser_apps = ['chrome', 'firefox', 'edge', 'safari', 'brave']
        if any(app in combined for app in browser_apps):
            return 'browser'
            
        return 'general'
