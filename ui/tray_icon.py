import threading
import logging

try:
    from pystray import Icon, Menu, MenuItem
    from PIL import Image, ImageDraw
    HAS_TRAY = True
except ImportError:
    HAS_TRAY = False

class TrayIcon:
    def __init__(self, app=None):
        self.app = app
        self.logger = logging.getLogger(__name__)
        self.state = "IDLE" # IDLE, RECORDING, PROCESSING
        self.icon = None
        self.thread = None

    def _create_image(self, state):
        width = 64
        height = 64
        color1 = "#1a1d26" # bg
        
        if state == "RECORDING":
            color2 = "#EF4444" # red
        elif state == "PROCESSING":
            color2 = "#10B981" # green
        else:
            color2 = "#6366F1" # accent

        if not HAS_TRAY:
            return None

        image = Image.new('RGB', (width, height), color1)
        dc = ImageDraw.Draw(image)
        # Draw circle
        dc.ellipse([8, 8, 56, 56], fill=color1, outline=color2, width=4)
        # Draw mic center
        dc.rounded_rectangle([24, 16, 40, 40], radius=8, fill=color2)
        dc.arc([16, 24, 48, 48], start=0, end=180, fill=color2, width=4)
        dc.line([32, 48, 32, 56], fill=color2, width=4)
        return image

    def _on_show(self, icon, item):
        if self.app:
            pass # trigger window show

    def _on_quit(self, icon, item):
        if self.icon:
            self.icon.stop()
        if self.app:
            self.app.quit()

    def set_state(self, state: str):
        self.state = state
        if self.icon and HAS_TRAY:
            self.icon.icon = self._create_image(state)
            self.icon.title = f"VoxType - {state}"

    def start(self):
        if not HAS_TRAY:
            self.logger.warning("pystray/Pillow not installed. Tray icon disabled.")
            return

        image = self._create_image(self.state)
        menu = Menu(
            MenuItem("Show Window", self._on_show, default=True),
            MenuItem("Settings", lambda: None),
            MenuItem("History", lambda: None),
            Menu.SEPARATOR,
            MenuItem("Quit", self._on_quit)
        )
        self.icon = Icon("VoxType", image, f"VoxType - {self.state}", menu)
        
        self.thread = threading.Thread(target=self.icon.run, daemon=True)
        self.thread.start()

    def stop(self):
        if self.icon:
            self.icon.stop()
