import os
import sys
import urllib.request
from PyQt5.QtCore import QThread, pyqtSignal
import yt_dlp

class InfoFetchWorker(QThread):
    # Signals to communicate fetched video info to the main thread
    fetched = pyqtSignal(bool, dict) # Emits (success, data_dict)

    def __init__(self, url):
        super().__init__()
        self.url = url

    def run(self):
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'skip_download': True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=False)
                
                title = info.get('title', 'Unknown Title')
                channel = info.get('uploader', info.get('channel', 'Unknown Channel'))
                duration_sec = info.get('duration')
                duration_str = self.format_duration(duration_sec)
                
                thumbnail_url = info.get('thumbnail')
                thumbnail_bytes = b''
                if thumbnail_url:
                    try:
                        req = urllib.request.Request(
                            thumbnail_url, 
                            headers={'User-Agent': 'Mozilla/5.0'}
                        )
                        with urllib.request.urlopen(req, timeout=5) as response:
                            thumbnail_bytes = response.read()
                    except Exception:
                        pass # Continue even if thumbnail image fetch fails
                
                data = {
                    'title': title,
                    'channel': channel,
                    'duration': duration_str,
                    'thumbnail_data': thumbnail_bytes
                }
                self.fetched.emit(True, data)
        except Exception as e:
            self.fetched.emit(False, {'error': str(e).split('\n')[0]})

    def format_duration(self, seconds):
        if not seconds:
            return "Unknown"
        seconds = int(seconds)
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        if h > 0:
            return f"{h}:{m:02d}:{s:02d}"
        else:
            return f"{m}:{s:02d}"

class DownloadWorker(QThread):
    # Signals to communicate progress back to the UI
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    finished = pyqtSignal(bool, str) # Emits (success, message)

    def __init__(self, url, download_path, mode, quality):
        super().__init__()
        self.url = url
        self.download_path = download_path
        self.mode = mode
        self.quality = quality
        self.is_running = True
        self._title = "Video"

    def run(self):
        self.status.emit("Fetching info...")
        
        ydl_opts = {
            'outtmpl': os.path.join(self.download_path, '%(title)s.%(ext)s'),
            'progress_hooks': [self.progress_hook],
            'quiet': True,
            'no_warnings': True,
        }

        # Select optimized format options for maximum quality
        if self.mode == "video":
            ydl_opts['merge_output_format'] = 'mp4'
            if "best" in self.quality.lower():
                ydl_opts['format'] = 'bestvideo+bestaudio/best'
            else:
                height = self.quality.split("p")[0].strip()
                # Optimized format selection: Best separate video <= target details combined with best audio,
                # with progressive fallbacks to avoid failure on older or single-format videos.
                ydl_opts['format'] = f'bestvideo[height<={height}]+bestaudio/best[height<={height}]/best'
        else:  # "audio"
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                self.status.emit("Connecting to YouTube...")
                info = ydl.extract_info(self.url, download=False)
                self._title = info.get('title', 'Video')
                
                if not self.is_running:
                    self.finished.emit(False, "Download cancelled.")
                    return
                
                self.status.emit(f"Preparing download: {self._title}...")
                ydl.download([self.url])
                
            if self.is_running:
                self.progress.emit(100)
                self.finished.emit(True, f"Successfully downloaded: {self._title}")
            else:
                self.finished.emit(False, "Download cancelled.")
        except Exception as e:
            error_msg = str(e)
            if "cancelled" in error_msg.lower():
                self.finished.emit(False, "Download cancelled.")
                return
            
            # Catch/format ffmpeg missing or private/unavailable stream issues
            if "ffmpeg" in error_msg.lower():
                error_msg = "FFmpeg not found! Please install FFmpeg (required for merging audio/video or MP3 extraction)."
            else:
                error_msg = error_msg.split('\n')[0]
                if error_msg.startswith("ERROR: "):
                    error_msg = error_msg[7:]
            self.finished.emit(False, error_msg)

    def progress_hook(self, d):
        if not self.is_running:
            raise Exception("Download cancelled by user.")
            
        if d['status'] == 'downloading':
            downloaded = d.get('downloaded_bytes', 0)
            total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            
            # Format speed metrics
            speed = d.get('speed')
            speed_str = ""
            if speed:
                if speed > 1024 * 1024:
                    speed_str = f" @ {speed / (1024 * 1024):.1f} MB/s"
                elif speed > 1024:
                    speed_str = f" @ {speed / 1024:.1f} KB/s"
            
            if total > 0:
                percent = int(downloaded / total * 100)
                percent = min(max(percent, 0), 100)
                self.progress.emit(percent)
                self.status.emit(f"Downloading... {percent}%{speed_str}")
            else:
                self.status.emit(f"Downloading...{speed_str}")
        elif d['status'] == 'finished':
            self.status.emit("Finalizing files (converting/merging/extracting audio)...")

    def stop(self):
        self.is_running = False
