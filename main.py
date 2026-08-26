import sys
import os
from PyQt5.QtWidgets import QApplication, QFileDialog
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtGui import QDesktopServices, QPixmap
from ui_main_window import MainWindow
from downloader import DownloadWorker, InfoFetchWorker

class YTGrabberApp(MainWindow):
    def __init__(self):
        super().__init__()
        
        # Determine default download folder path
        self.download_folder = self.get_downloads_folder()
        self.folder_input.setText(self.download_folder)
        
        # Connect Action Buttons
        self.folder_btn.clicked.connect(self.choose_folder)
        self.download_btn.clicked.connect(self.start_download)
        self.open_folder_btn.clicked.connect(self.open_folder)
        
        # Connect URL Event Triggers
        self.url_input.editingFinished.connect(self.fetch_info)
        
        # Keep references for worker threads
        self.download_worker = None
        self.fetch_worker = None

    def get_downloads_folder(self):
        """Standard procedure to resolve the user's local downloads directory."""
        if os.name == 'nt':
            import winreg
            try:
                sub_key = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders'
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub_key) as key:
                    path = winreg.QueryValueEx(key, '{374DE290-123F-4565-9164-39C4925E467B}')[0]
                    if os.path.exists(path):
                        return path
            except Exception:
                pass
        
        # Common OS platform-neutral path fallback
        home = os.path.expanduser('~')
        downloads = os.path.join(home, 'Downloads')
        if os.path.exists(downloads):
            return downloads
        
        return os.getcwd()

    def choose_folder(self):
        """Triggers a QFileDialog box to set download location."""
        selected_dir = QFileDialog.getExistingDirectory(
            self,
            "Select Save Directory",
            self.folder_input.text() or self.get_downloads_folder()
        )
        if selected_dir:
            self.download_folder = os.path.abspath(selected_dir)
            self.folder_input.setText(self.download_folder)

    def validate_url(self, url):
        """Simplistic validator to make sure field contains a Youtube address."""
        url = url.strip()
        if not url:
            return False, "URL column cannot be empty!"
        
        # Matches typical expressions
        if "youtube.com" not in url.lower() and "youtu.be" not in url.lower():
            return False, "Invalid URL! Paste a valid YouTube link (e.g. contains youtube.com or youtu.be)."
            
        return True, ""

    def fetch_info(self):
        """Fetches metadata asynchronously in a background thread to update the preview panel."""
        url = self.url_input.text().strip()
        
        # Clean/validation
        is_valid, _ = self.validate_url(url)
        if not is_valid:
            # Restore placeholder defaults
            self.preview_title.setText("Video title will appear here")
            self.preview_details.setText("Channel name · duration")
            self.preview_thumbnail.clear()
            self.preview_thumbnail.setText("▶")
            return

        # Cancel any active info-fetching thread
        if self.fetch_worker and self.fetch_worker.isRunning():
            self.fetch_worker.terminate()
            self.fetch_worker.wait()

        # Update stats
        self.status_label.setText("Fetching video information...")
        self.status_label.setStyleSheet("color: #cbd5e1;")  # Reset to standard slate
        
        # Launch QThread InfoFetchWorker
        self.fetch_worker = InfoFetchWorker(url)
        self.fetch_worker.fetched.connect(self.info_fetch_finished)
        self.fetch_worker.start()

    def info_fetch_finished(self, success, data):
        """Updates the media preview card widget when fetch reaches conclusion."""
        if success:
            # Map parameters
            self.preview_title.setText(data['title'])
            self.preview_details.setText(f"{data['channel']} · {data['duration']}")
            
            # Load thumbnail image
            if data['thumbnail_data']:
                pixmap = QPixmap()
                pixmap.loadFromData(data['thumbnail_data'])
                self.preview_thumbnail.setText("") # Clear placeholder play icon text
                self.preview_thumbnail.setPixmap(pixmap)
            else:
                self.preview_thumbnail.clear()
                self.preview_thumbnail.setText("▶")
            
            self.status_label.setText("Video loaded! Ready to download.")
            self.status_label.setStyleSheet("color: #cbd5e1;")
        else:
            # Fail gracefully, restore placeholder info and show inline error
            self.preview_title.setText("Video title will appear here")
            self.preview_details.setText("Channel name · duration")
            self.preview_thumbnail.clear()
            self.preview_thumbnail.setText("▶")
            
            self.status_label.setText(f"Error fetching video data: {data.get('error', 'Unknown Error')}")
            self.status_label.setStyleSheet("color: #ef4444;") # Highlight error in red

    def start_download(self):
        """Locks UI inputs and initiates DownloadWorker thread."""
        url = self.url_input.text().strip()
        
        is_valid, err_msg = self.validate_url(url)
        if not is_valid:
            self.status_label.setText(err_msg)
            self.status_label.setStyleSheet("color: #ef4444;")
            return

        download_path = self.folder_input.text().strip()
        if not download_path or not os.path.isdir(download_path):
            self.status_label.setText("Error: Selected downloads save folder does not exist.")
            self.status_label.setStyleSheet("color: #ef4444;")
            return

        mode = "video" if self.radio_video.isChecked() else "audio"
        quality = self.quality_combo.currentText()

        # Update UI components status
        self.set_ui_loading_state(True)
        self.status_label.setText("Starting download worker...")
        self.status_label.setStyleSheet("color: #cbd5e1;")
        self.progress_bar.setValue(0)
        self.status_percent_label.setText("0%")
        self.open_folder_btn.setVisible(False)

        # Launch QThread DownloadWorker
        self.download_worker = DownloadWorker(url, download_path, mode, quality)
        self.download_worker.progress.connect(self.update_progress)
        self.download_worker.status.connect(self.update_status)
        self.download_worker.finished.connect(self.download_finished)
        self.download_worker.start()

    def update_progress(self, val):
        """Updates numerical values in visual progress guides."""
        self.progress_bar.setValue(val)
        self.status_percent_label.setText(f"{val}%")

    def update_status(self, text):
        """Updates state descriptions displayed in the status card."""
        self.status_label.setText(text)

    def download_finished(self, success, msg):
        """Restores user input toggles and updates summary of final results."""
        self.set_ui_loading_state(False)
        
        if success:
            self.progress_bar.setValue(100)
            self.status_percent_label.setText("100%")
            self.status_label.setText(f"Done ✅\n{msg}")
            self.status_label.setStyleSheet("color: #10b981;") # Emerald 500
            self.open_folder_btn.setVisible(True)
        else:
            self.status_label.setText(f"Error: {msg}")
            self.status_label.setStyleSheet("color: #ef4444;") # Red 500
            
    def set_ui_loading_state(self, loading):
        """Disables controls while downloads are running to ensure thread safety."""
        self.url_input.setEnabled(not loading)
        self.paste_btn.setEnabled(not loading)
        self.folder_btn.setEnabled(not loading)
        self.radio_video.setEnabled(not loading)
        self.radio_audio.setEnabled(not loading)
        
        if loading:
            self.quality_combo.setEnabled(False)
        else:
            self.quality_combo.setEnabled(self.radio_video.isChecked())
            
        self.download_btn.setEnabled(not loading)
        if loading:
            self.download_btn.setText("☁ Downloading... (Connecting)")
        else:
            self.download_btn.setText("☁   Download")

    def open_folder(self):
        """Trigger explorer to open user's download directory."""
        path = self.folder_input.text()
        if os.path.exists(path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(path))

    def closeEvent(self, event):
        """Explicitly cleans up and safely terminates backend threads on closure request."""
        if self.download_worker and self.download_worker.isRunning():
            self.download_worker.stop()
            self.download_worker.wait()
        if self.fetch_worker and self.fetch_worker.isRunning():
            self.fetch_worker.terminate()
            self.fetch_worker.wait()
        event.accept()

if __name__ == "__main__":
    # Support high DPI displays nicely
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        
    app = QApplication(sys.argv)
    app.setStyle("Fusion") # Absolutely critical on Windows to enable CSS backgrounds on buttons
    window = YTGrabberApp()
    window.show()
    sys.exit(app.exec_())
