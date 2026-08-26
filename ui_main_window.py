import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QRadioButton, QButtonGroup, QComboBox,
    QProgressBar, QFrame, QSizePolicy, QApplication, QBoxLayout,
    QScrollArea
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_styles()

    def init_ui(self):
        self.setWindowTitle("123 - YouTube Downloader")
        self.setObjectName("mainWindow")
        
        # Default window size — resizable and mobile-friendly
        self.resize(900, 560)
        self.setMinimumSize(360, 560)
        
        # Outer wrapping layout for centering against the new background
        self.outer_layout = QVBoxLayout(self)
        # We will control resizing via dynamic margins in resizeEvent
        self.outer_layout.setContentsMargins(0, 0, 0, 0)
        
        # Central container to lock maximum width/height when fullscreen
        self.central_container = QWidget()
        self.central_container.setObjectName("centralContainer")
        
        # Scrolling area for mobile responsive overflowing
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setObjectName("mainScrollArea")
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setStyleSheet("background: transparent;")
        
        self.scroll_content = QWidget()
        self.scroll_content.setObjectName("scrollContent")
        self.scroll_content.setStyleSheet("background: transparent;")
        
        # Root Layout inside the scroll content
        self.root_layout = QBoxLayout(QBoxLayout.LeftToRight, self.scroll_content)
        self.root_layout.setContentsMargins(16, 16, 16, 16)
        self.root_layout.setSpacing(16)
        
        self.scroll_area.setWidget(self.scroll_content)
        
        # Bind scroll area inside central container
        self.central_layout = QVBoxLayout(self.central_container)
        self.central_layout.setContentsMargins(0, 0, 0, 0)
        self.central_layout.addWidget(self.scroll_area)

        # ==========================================
        # LEFT SIDEBAR
        # ==========================================
        self.sidebar_frame = QFrame()
        self.sidebar_frame.setObjectName("sidebarFrame")
        self.sidebar_frame.setFixedWidth(290)
        
        sidebar_layout = QVBoxLayout(self.sidebar_frame)
        sidebar_layout.setContentsMargins(20, 25, 20, 25)
        sidebar_layout.setSpacing(20)

        # Playlist Logo Brand Header
        brand_row = QHBoxLayout()
        brand_row.setSpacing(12)
        
        self.logo_label = QLabel("🦋")
        self.logo_label.setObjectName("logoLabel")
        self.logo_label.setFixedSize(42, 42)
        self.logo_label.setAlignment(Qt.AlignCenter)
        self.logo_label.setAttribute(Qt.WA_StyledBackground, True)
        
        brand_text_layout = QVBoxLayout()
        brand_text_layout.setSpacing(1)
        
        title_label = QLabel("Butterfly")
        title_label.setObjectName("sidebarTitle")
        
        subtitle_label = QLabel("YouTube media downloader")
        subtitle_label.setObjectName("sidebarSub")
        
        brand_text_layout.addWidget(title_label)
        brand_text_layout.addWidget(subtitle_label)
        
        brand_row.addWidget(self.logo_label)
        brand_row.addLayout(brand_text_layout)
        sidebar_layout.addLayout(brand_row)

        # Save Folder Section (Grouped)
        folder_card = QFrame()
        folder_card.setObjectName("sidebarCard")
        folder_card_layout = QVBoxLayout(folder_card)
        folder_card_layout.setContentsMargins(12, 12, 12, 12)
        folder_card_layout.setSpacing(8)
        
        lbl_save_folder = QLabel("Save folder")
        lbl_save_folder.setObjectName("sectionLabel1")
        folder_card_layout.addWidget(lbl_save_folder)
        
        self.folder_input = QLineEdit()
        self.folder_input.setReadOnly(True)
        self.folder_input.setPlaceholderText("Select folder...")
        folder_card_layout.addWidget(self.folder_input)
        
        self.folder_btn = QPushButton("📁  Choose folder")
        self.folder_btn.setObjectName("folderBtn")
        self.folder_btn.setCursor(Qt.PointingHandCursor)
        folder_card_layout.addWidget(self.folder_btn)
        
        sidebar_layout.addWidget(folder_card)

        # Download Format Section (Grouped)
        format_card = QFrame()
        format_card.setObjectName("sidebarCard")
        format_card_layout = QVBoxLayout(format_card)
        format_card_layout.setContentsMargins(12, 12, 12, 12)
        format_card_layout.setSpacing(8)
        
        lbl_download_format = QLabel("Download Format & Quality")
        lbl_download_format.setObjectName("sectionLabel2")
        format_card_layout.addWidget(lbl_download_format)
        
        self.radio_video = QRadioButton("🎥   Video (MP4)")
        self.radio_video.setObjectName("radioVideo")
        self.radio_video.setChecked(True)
        self.radio_video.setCursor(Qt.PointingHandCursor)
        
        self.radio_audio = QRadioButton("🎵   Audio only (MP3)")
        self.radio_audio.setObjectName("radioAudio")
        self.radio_audio.setCursor(Qt.PointingHandCursor)
        
        self.mode_group = QButtonGroup()
        self.mode_group.addButton(self.radio_video)
        self.mode_group.addButton(self.radio_audio)
        
        format_card_layout.addWidget(self.radio_video)
        format_card_layout.addWidget(self.radio_audio)
        
        lbl_resolution = QLabel("Video resolution")
        lbl_resolution.setObjectName("sectionLabel3")
        format_card_layout.addWidget(lbl_resolution)
        
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["Best Available", "2160p (4K)", "1440p (2K)", "1080p", "720p", "480p"])
        self.quality_combo.setCursor(Qt.PointingHandCursor)
        format_card_layout.addWidget(self.quality_combo)
        
        sidebar_layout.addWidget(format_card)

        # Push items to the top
        sidebar_layout.addStretch()
        
        self.root_layout.addWidget(self.sidebar_frame)

        # ==========================================
        # RIGHT WORKSPACE
        # ==========================================
        self.main_panel = QWidget()
        self.main_panel.setObjectName("mainPanel")
        self.main_panel_layout = QVBoxLayout(self.main_panel)
        self.main_panel_layout.setContentsMargins(0, 0, 0, 0)
        self.main_panel_layout.setSpacing(16)

        # 1. URL Card Row
        self.url_card = QFrame()
        self.url_card.setObjectName("urlCard")
        url_card_layout = QVBoxLayout(self.url_card)
        url_card_layout.setContentsMargins(16, 16, 16, 16)
        url_card_layout.setSpacing(8)
        
        url_lbl = QLabel("URL & Preview")
        url_lbl.setObjectName("urlLabel")
        url_card_layout.addWidget(url_lbl)
        
        url_input_row = QHBoxLayout()
        url_input_row.setSpacing(12)
        
        self.url_input = QLineEdit()
        self.url_input.setObjectName("urlInput")
        self.url_input.setPlaceholderText("Paste a YouTube link here")
        
        self.paste_btn = QPushButton("📋 Paste")
        self.paste_btn.setObjectName("pasteBtn")
        self.paste_btn.setCursor(Qt.PointingHandCursor)
        
        url_input_row.addWidget(self.url_input, 4)
        url_input_row.addWidget(self.paste_btn, 1)
        url_card_layout.addLayout(url_input_row)
        
        self.main_panel_layout.addWidget(self.url_card)

        # 2. Preview Card Frame (Contains startup placeholders matching screenshot)
        self.preview_card = QFrame()
        self.preview_card.setObjectName("previewCard")
        
        preview_card_layout = QVBoxLayout(self.preview_card)
        preview_card_layout.setContentsMargins(16, 16, 16, 16)
        preview_card_layout.setSpacing(8)
        
        preview_body = QHBoxLayout()
        preview_body.setSpacing(16)
        
        # Video Thumbnail Label (Default text is red play button placeholder)
        self.preview_thumbnail = QLabel("▶")
        self.preview_thumbnail.setObjectName("previewThumbnail")
        self.preview_thumbnail.setFixedSize(140, 80)
        self.preview_thumbnail.setAlignment(Qt.AlignCenter)
        self.preview_thumbnail.setStyleSheet("""
            QLabel {
                color: #ef4444; 
                font-size: 26px; 
                font-weight: bold;
                background-color: #251c1c; 
                border-radius: 8px;
            }
        """)
        
        # Details Stack
        details_layout = QVBoxLayout()
        details_layout.setSpacing(6)
        
        self.preview_title = QLabel("Video title will appear here")
        self.preview_title.setObjectName("previewTitle")
        self.preview_title.setWordWrap(True)
        
        self.preview_details = QLabel("Channel name · duration")
        self.preview_details.setObjectName("previewDetails")
        
        details_layout.addWidget(self.preview_title)
        details_layout.addWidget(self.preview_details)
        details_layout.addStretch()
        
        preview_body.addWidget(self.preview_thumbnail)
        preview_body.addLayout(details_layout, 1)
        preview_card_layout.addLayout(preview_body)
        
        self.main_panel_layout.addWidget(self.preview_card)

        # 3. Status Card
        self.status_card = QFrame()
        self.status_card.setObjectName("statusCard")
        
        status_card_layout = QVBoxLayout(self.status_card)
        status_card_layout.setContentsMargins(18, 18, 18, 18)
        status_card_layout.setSpacing(12)
        
        # Header Row (Status text [left], percentage [right])
        status_header_layout = QHBoxLayout()
        
        lbl_status_hdr = QLabel("Connection Status")
        lbl_status_hdr.setObjectName("statusHeader")
        
        self.status_percent_label = QLabel("0%")
        self.status_percent_label.setObjectName("statusPercentage")
        
        status_header_layout.addWidget(lbl_status_hdr)
        status_header_layout.addWidget(self.status_percent_label)
        status_card_layout.addLayout(status_header_layout)
        
        # Status Message
        self.status_label = QLabel("Ready to grab video")
        self.status_label.setObjectName("statusLabel")
        self.status_label.setWordWrap(True)
        status_card_layout.addWidget(self.status_label)
        
        # Micro thin Progress Bar (setFixedHeight is 4px)
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(6)
        self.progress_bar.setTextVisible(False)
        status_card_layout.addWidget(self.progress_bar)
        
        status_card_layout.addSpacing(6)
        
        # 4. Action Button Placement
        self.download_btn = QPushButton("☁   Download")
        self.download_btn.setObjectName("downloadBtn")
        self.download_btn.setCursor(Qt.PointingHandCursor)
        
        self.open_folder_btn = QPushButton("📂   Open Folder")
        self.open_folder_btn.setObjectName("openFolderBtn")
        self.open_folder_btn.setCursor(Qt.PointingHandCursor)
        self.open_folder_btn.setVisible(False)
        
        status_card_layout.addWidget(self.open_folder_btn)
        status_card_layout.addWidget(self.download_btn)
        
        self.main_panel_layout.addWidget(self.status_card)

        # Set main workspace
        self.root_layout.addWidget(self.main_panel, 1)
        self.outer_layout.addWidget(self.central_container)

        # Connections
        self.radio_video.toggled.connect(self.toggle_quality_combobox)
        self.paste_btn.clicked.connect(self.paste_from_clipboard)

    def load_styles(self):
        import sys
        # When running as a PyInstaller .exe, files are extracted to sys._MEIPASS
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        qss_path = os.path.join(base_path, "styles.qss")
        if os.path.exists(qss_path):
            with open(qss_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())

    def toggle_quality_combobox(self):
        self.quality_combo.setEnabled(self.radio_video.isChecked())

    def paste_from_clipboard(self):
        clipboard = QApplication.clipboard()
        self.url_input.setText(clipboard.text().strip())
        self.url_input.editingFinished.emit()

    def create_sidebar_divider(self):
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Plain)
        line.setStyleSheet("background-color: #202336; max-height: 1px; border: none;")
        return line

    def resizeEvent(self, event):
        """Responsive layout: automatically calculating dynamic margins for flawless centering."""
        super().resizeEvent(event)
        
        w = self.width()
        h = self.height()
        
        # Calculate dynamic margins to max out width at 940px
        max_w = 940
        margin_x = max((w - max_w) // 2, 0)
        content_w = w - (margin_x * 2)
        
        if content_w < 700:
            # Stacked vertical mode (Mobile) - Free heights
            self.root_layout.setDirection(QBoxLayout.TopToBottom)
            self.sidebar_frame.setMinimumWidth(0)
            self.sidebar_frame.setMaximumWidth(16777215) # Removes fixed width
            margin_y = 0 # Give maximum vertical space for the stacked widgets
        else:
            # Side-by-side mode (Desktop) - Boxed heights
            self.root_layout.setDirection(QBoxLayout.LeftToRight)
            self.sidebar_frame.setFixedWidth(290)
            
            max_h = 600
            margin_y = max((h - max_h) // 2, 0)
            
        # Apply the margins to naturally center everything without forcing minimum clipping limits
        self.outer_layout.setContentsMargins(margin_x, margin_y, margin_x, margin_y)
