# 123 🚀

123 is a premium, modern Python desktop application built with PyQt5 that lets you download YouTube videos or extract MP3 audio using the powerful `yt-dlp` library. It features a sleek glassmorphic dark theme, non-blocking asynchronous downloads, live progress tracking, and robust error handling.

## ✨ Features
- **Video Downloads**: Download MP4 files with quality selection (Best, 1080p, 720p, 480p).
- **Audio Extraction**: Download YouTube audio and convert it to high-quality 192kbps MP3 automatically.
- **Multithreading**: Powered by PyQt `QThread`, keeping the GUI fully responsive while downloading.
- **Real-time Stats**: Live progress bar and status indicator displaying speeds and file processing.
- **Quick Save Location Selection**: Choose your save folder and open it with one click when the download finishes.

---

## 🛠️ Prerequisites & Installation

### 1. Install FFmpeg (Required)
FFmpeg is necessary to merge audio/video content (when downloading videos above 720p) and for converting videos to MP3 audio files.

#### **Windows**
1. Open PowerShell/Command Prompt as Administrator and run:
   ```cmd
   winget install FFmpeg
   ```
2. Alternatively, download the build from [gyan.dev](https://www.gyan.dev/ffmpeg/builds/), extract it, and add the `bin` folder to your system's environment `PATH`.

#### **macOS**
Install using [Homebrew](https://brew.sh/):
```bash
brew install ffmpeg
```

#### **Linux**
- **Ubuntu/Debian**:
  ```bash
  sudo apt update && sudo apt install ffmpeg -y
  ```
- **Fedora/RHEL**:
  ```bash
  sudo dnf install ffmpeg -y
  ```

---

### 2. Set Up the Application

Clone, download or navigate to the project directory:
```bash
cd "youtub video download"
```

Install the required Python packages:
```bash
pip install -r requirements.txt
```

---

## 🚀 Running the App

Start the application by running:
```bash
python main.py
```

---

## 🖥️ Screen Layout
- **URL Paste Box**: Enter any standard YouTube link (videos, playlists, shorts, etc.).
- **Choose Save Folder**: Select where downloaded media is saved (defaults to your OS user Downloads folder).
- **Download Type & Video Quality**: Choose MP4 video format with adjustable resolutions or select MP3 audio extraction.
- **Progress Tracking**: Look at transfer rates and percentage completions in real-time.
- **Done & Open Folder**: Click the "Open Folder" button that appears upon success to navigate directly to your media.
