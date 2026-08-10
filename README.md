<h1 align="center">
  <br>
  VoxType
  <br>
</h1>

<p align="center">
  <a href="https://github.com/yourusername/VoxType/releases/latest">
    <img src="https://img.shields.io/github/v/release/yourusername/VoxType?style=flat-square" alt="Latest Release">
  </a>
  <a href="https://www.python.org/downloads/release/python-3110/">
    <img src="https://img.shields.io/badge/python-3.11-blue.svg?style=flat-square" alt="Python 3.11">
  </a>
  <a href="https://github.com/yourusername/VoxType/blob/main/LICENSE">
    <img src="https://img.shields.io/github/license/yourusername/VoxType?style=flat-square" alt="License">
  </a>
</p>

<p align="center">
  <strong>Local-First AI Dictation App for Windows</strong>
</p>

## 🎙️ What is VoxType?
VoxType is a powerful, privacy-focused dictation tool built exclusively for Windows. Leveraging state-of-the-art AI models, it offers rapid and accurate voice-to-text functionality right on your local machine. No subscriptions, no cloud latency, and complete peace of mind knowing your voice data never leaves your computer.

## ⚖️ Why VoxType?

| Feature | VoxType | Wispr Flow |
|---------|---------|------------|
| **Cost** | 100% Free | Subscription-based |
| **Privacy** | Local-First (Offline by default) | Cloud processing |
| **Speaker Verification** | Yes (Voice Owner Lock) | No |
| **App-Specific Profiles** | Yes | Limited |
| **Extensibility** | High (Python-based) | Closed Ecosystem |

## ✨ Features
* 🔒 **Local Processing:** Powered by Faster-Whisper, no internet required for core transcription.
* 🛡️ **Voice Owner Lock:** Speaker verification ensures it only dictates when *you* speak.
* 🤖 **Smart Formatting (Optional):** Integration with Google Gemini for advanced formatting and grammar correction.
* 🎯 **Context-Aware Profiles:** Automatically adapts tone and formatting based on your active window (e.g., Slack vs VS Code).
* 📝 **Personal Dictionary:** Add custom hotwords to boost transcription accuracy for niche terminology.
* ⚡ **Gibberish Filter:** Built-in safeguards prevent random noises from being typed out as hallucinatory text.

## 🖼️ Screenshots
*Placeholder: UI Dashboard*
*Placeholder: System Tray Menu*
*Placeholder: Settings Window*

## 🚀 Quick Start (One-Click Install)
The easiest way to install VoxType on Windows is using our one-line PowerShell installer. It will automatically download the app, set up the virtual environment, install dependencies, and create a desktop shortcut.

Open **PowerShell** and run:
```powershell
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/bennyjoel/Vox/main/install.ps1" -OutFile "install.ps1"; .\install.ps1
```

*Alternatively, you can download the latest release from the [Releases page](https://github.com/bennyjoel/Vox/releases) and extract it manually.*

## 🛠️ Build from Source
To build VoxType yourself, you need Python 3.11+.

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/VoxType.git
   cd VoxType
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the app:
   ```bash
   python main.py
   ```

## 🏗️ How It Works
VoxType listens to your microphone when the global hotkey is pressed. The audio is captured in chunks and passed through a local Voice Activity Detector (VAD) to ignore silence. If speech is detected, the audio is analyzed by the Voice Owner Lock mechanism. Verified audio is then transcribed by the Faster-Whisper engine, formatted (either locally or via an LLM), and injected directly into your active text field via simulated keystrokes or clipboard pasting.

## 🔐 Voice Owner Lock
Voice Owner Lock uses AI speaker verification (via ONNX runtime) to create an acoustic fingerprint of your voice during setup. When dictating in a noisy environment, VoxType compares incoming audio against your voice profile. If someone else talks, their speech is ignored, preventing unwanted text from entering your documents.

## ⚙️ Configuration
All configurations are stored locally in a SQLite database (`settings.db`) located in your AppData folder. You can tweak everything from the default transcription hotkey to app-specific profiles via the intuitive GUI dashboard.

## ❓ FAQ
* **Does it work on Mac/Linux?**
  Currently, VoxType is optimized and built for Windows, utilizing `pywin32` for window tracking and clipboard injection.

* **Is an internet connection required?**
  No! The core Whisper transcription works entirely offline. Internet is only required if you enable the Gemini API for advanced AI formatting.

## 🤝 Contributing
Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change. 

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Credits & Acknowledgments
* [Faster-Whisper](https://github.com/SYSTRAN/faster-whisper)
* [Silero VAD](https://github.com/snakers4/silero-vad)
* [Resemblyzer](https://github.com/resemble-ai/Resemblyzer)
