import logging
import time

try:
    import win32clipboard
    import win32con
    import ctypes
    WIN32_AVAILABLE = True
except ImportError:
    logging.error("pywin32 not found. Clipboard and keystroke injection will not work.")
    WIN32_AVAILABLE = False

logger = logging.getLogger(__name__)

# ctypes structures for SendInput
if WIN32_AVAILABLE:
    PUL = ctypes.POINTER(ctypes.c_ulong)
    class KeyBdInput(ctypes.Structure):
        _fields_ = [("wVk", ctypes.c_ushort),
                    ("wScan", ctypes.c_ushort),
                    ("dwFlags", ctypes.c_ulong),
                    ("time", ctypes.c_ulong),
                    ("dwExtraInfo", PUL)]

    class HardwareInput(ctypes.Structure):
        _fields_ = [("uMsg", ctypes.c_ulong),
                    ("wParamL", ctypes.c_short),
                    ("wParamH", ctypes.c_ushort)]

    class MouseInput(ctypes.Structure):
        _fields_ = [("dx", ctypes.c_long),
                    ("dy", ctypes.c_long),
                    ("mouseData", ctypes.c_ulong),
                    ("dwFlags", ctypes.c_ulong),
                    ("time", ctypes.c_ulong),
                    ("dwExtraInfo", PUL)]

    class Input_I(ctypes.Union):
        _fields_ = [("ki", KeyBdInput),
                    ("mi", MouseInput),
                    ("hi", HardwareInput)]

    class Input(ctypes.Structure):
        _fields_ = [("type", ctypes.c_ulong),
                    ("ii", Input_I)]


class TextInjector:
    """Injects text into the active window."""
    
    def __init__(self):
        if WIN32_AVAILABLE:
            try:
                # Register custom clipboard formats to bypass history and cloud sync
                self.cf_exclude_history = win32clipboard.RegisterClipboardFormat("ExcludeClipboardContentFromMonitorProcessing")
                self.cf_exclude_cloud = win32clipboard.RegisterClipboardFormat("CanUploadToCloudClipboard")
            except Exception as e:
                logger.warning(f"Failed to register custom clipboard formats: {e}")
                self.cf_exclude_history = None
                self.cf_exclude_cloud = None
        else:
            self.cf_exclude_history = None
            self.cf_exclude_cloud = None

    def inject(self, text: str, method: str = 'clipboard'):
        """Injects text. method can be 'clipboard' or 'clipboard_only'."""
        if not text or not WIN32_AVAILABLE:
            return
            
        try:
            # Backup current clipboard
            backup_text = None
            win32clipboard.OpenClipboard()
            try:
                if win32clipboard.IsClipboardFormatAvailable(win32con.CF_UNICODETEXT):
                    backup_text = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
            except Exception:
                pass
            finally:
                win32clipboard.CloseClipboard()

            # Set new clipboard text
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, text)
            
            # Apply exclusion flags if available
            if self.cf_exclude_history:
                win32clipboard.SetClipboardData(self.cf_exclude_history, b'\x00')
            if self.cf_exclude_cloud:
                win32clipboard.SetClipboardData(self.cf_exclude_cloud, b'\x00')
                
            win32clipboard.CloseClipboard()

            if method == 'clipboard':
                # Wait briefly for clipboard to settle
                time.sleep(0.05)
                
                # Send Ctrl+V
                self._send_ctrl_v()
                
                # Wait before restoring
                time.sleep(0.15)
                
                # Restore original text
                if backup_text:
                    try:
                        win32clipboard.OpenClipboard()
                        win32clipboard.EmptyClipboard()
                        win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, backup_text)
                        win32clipboard.CloseClipboard()
                    except Exception as e:
                        logger.warning(f"Failed to restore clipboard backup: {e}")

        except Exception as e:
            logger.error(f"Text injection failed: {e}")
            try:
                win32clipboard.CloseClipboard()
            except:
                pass

    def _send_ctrl_v(self):
        """Simulates Ctrl+V keystroke via ctypes."""
        if not WIN32_AVAILABLE:
            return
            
        VK_CONTROL = 0x11
        VK_V = 0x56
        KEYEVENTF_KEYUP = 0x0002

        inputs = (Input * 4)()
        
        # Ctrl Down
        inputs[0].type = 1
        inputs[0].ii.ki = KeyBdInput(VK_CONTROL, 0, 0, 0, None)
        
        # V Down
        inputs[1].type = 1
        inputs[1].ii.ki = KeyBdInput(VK_V, 0, 0, 0, None)
        
        # V Up
        inputs[2].type = 1
        inputs[2].ii.ki = KeyBdInput(VK_V, 0, KEYEVENTF_KEYUP, 0, None)
        
        # Ctrl Up
        inputs[3].type = 1
        inputs[3].ii.ki = KeyBdInput(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0, None)
        
        ctypes.windll.user32.SendInput(4, ctypes.pointer(inputs), ctypes.sizeof(Input))
