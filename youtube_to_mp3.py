import sys
import os
import json
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLineEdit, QPushButton, QLabel, 
                           QComboBox, QFileDialog, QMessageBox, QProgressBar,
                           QTextEdit, QCheckBox, QStyle, QStyleFactory)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPalette, QColor, QClipboard
import re
import time
import yt_dlp
from datetime import datetime

CONFIG_FILE = 'youtube_to_mp3.config.json'

def load_config():
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
    return {'ffmpeg_path': '', 'save_path': os.path.expanduser('~/Downloads')}

def save_config(config):
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving config: {e}")

def is_valid_youtube_url(url):
    youtube_regex = r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?([^"&?/s]{11})'
    return bool(re.match(youtube_regex, url))

def get_video_info(url):
    """비디오 정보를 가져오는 함수"""
    try:
        # URL 정규화
        if 'youtu.be' in url:
            video_id = url.split('youtu.be/')[-1].split('?')[0]
            url = f'https://www.youtube.com/watch?v={video_id}'
        elif '&' in url:
            url = url.split('&')[0]
            
        print(f"처리 중인 URL: {url}")
        
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'noplaylist': True,
            'ignoreerrors': False,
            'verbose': False,
            'force_generic_extractor': False
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            if info is None:
                print("비디오 정보를 추출할 수 없습니다.")
                return None
                
            if 'entries' in info:  # 플레이리스트인 경우
                print("플레이리스트 URL은 지원하지 않습니다.")
                return None
                    
            if 'title' not in info:
                print("제목 정보가 없습니다.")
                return None
                
            return info['title']
            
    except Exception as e:
        print(f"비디오 정보를 가져오는 중 오류 발생: {str(e)}")
        return None

class DownloadThread(QThread):
    progress = pyqtSignal(int)
    speed = pyqtSignal(str)
    finished = pyqtSignal(str, str)  # (메시지, 파일경로)
    error = pyqtSignal(str)
    conversion_started = pyqtSignal()
    stopped = pyqtSignal()
    
    def __init__(self, url, quality, save_path, ffmpeg_path):
        super().__init__()
        self.url = url
        self.quality = quality
        self.save_path = save_path
        self.ffmpeg_path = ffmpeg_path
        self._is_running = True
        self.output_file = None
        
    def stop(self):
        self._is_running = False
        self.stopped.emit()
        
    def run(self):
        try:
            if not os.path.exists(self.ffmpeg_path):
                raise FileNotFoundError("FFmpeg 경로가 올바르지 않습니다.")
                
            quality_map = {
                '320K': '320',
                '256K': '256',
                '192K': '192',
                '160K': '160',
                '128K': '128',
                '96K': '96',
                '64K': '64',
                '48K': '48'
            }
            
            # 임시 파일명 생성
            temp_filename = f"temp_{int(time.time())}"
            
            ydl_opts = {
                'format': f'bestaudio[abr<={quality_map[self.quality]}]',
                'outtmpl': os.path.join(self.save_path, f'{temp_filename}.%(ext)s'),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': quality_map[self.quality],
                }],
                'progress_hooks': [self.progress_hook],
                'ffmpeg_location': self.ffmpeg_path,
                'noplaylist': True,
                'extract_flat': False,
                'quiet': True,
                'no_warnings': True
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=True)
                if not self._is_running:
                    return
                    
                # 변환 시작 신호 전송
                self.conversion_started.emit()
                
                # 출력 파일 경로 확인
                output_file = os.path.join(self.save_path, f"{temp_filename}.mp3")
                if not os.path.exists(output_file):
                    raise FileNotFoundError("변환된 파일을 찾을 수 없습니다.")
                    
                # 파일 크기 확인
                file_size = os.path.getsize(output_file)
                if file_size == 0:
                    raise ValueError("변환된 파일이 비어 있습니다.")
                    
                # 최종 파일명으로 변경
                final_filename = f"{info['title']}.mp3"
                final_path = os.path.join(self.save_path, final_filename)
                
                # 파일명 중복 처리
                counter = 1
                while os.path.exists(final_path):
                    final_filename = f"{info['title']}_{counter}.mp3"
                    final_path = os.path.join(self.save_path, final_filename)
                    counter += 1
                    
                os.rename(output_file, final_path)
                self.output_file = final_path
                
                if not self._is_running:
                    return
                    
                self.finished.emit('다운로드 완료', final_path)
                
        except Exception as e:
            if self._is_running:
                self.error.emit(str(e))
                
    def get_output_file(self):
        return self.output_file

    def progress_hook(self, d):
        if not self._is_running:
            return
            
        if d['status'] == 'downloading':
            try:
                total = d.get('total_bytes', 0)
                downloaded = d.get('downloaded_bytes', 0)
                speed = d.get('speed', 0)
                
                if total > 0:
                    percentage = int((downloaded / total) * 100)
                    self.progress.emit(percentage)
                    
                if speed:
                    speed_str = f"{speed/1024/1024:.1f} MB/s"
                    self.speed.emit(speed_str)
            except:
                pass

class TitleCheckThread(QThread):
    title_checked = pyqtSignal(str, bool)
    
    def __init__(self, url):
        super().__init__()
        self.url = url
        self._is_running = True
        
    def stop(self):
        self._is_running = False
        
    def run(self):
        try:
            if not self._is_running:
                return
                
            if not self.url:
                self.title_checked.emit('', False)
                return
                
            if not is_valid_youtube_url(self.url):
                self.title_checked.emit('올바르지 않은 YouTube URL입니다.', False)
                return
                
            title = get_video_info(self.url)
            if not self._is_running:
                return
                
            if title:
                self.title_checked.emit(f'제목: {title}', True)
            else:
                self.title_checked.emit('동영상 정보를 가져올 수 없습니다.', False)
                
        except Exception as e:
            if self._is_running:
                self.title_checked.emit(f'오류: {str(e)}', False)

class YouTubeToMP3(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = load_config()
        self.ffmpeg_path = self.config.get('ffmpeg_path', '')
        self.download_thread = None
        self.title_check_thread = None
        self.initUI()
        self.dark_mode_checkbox.setChecked(True)
        self.set_dark_mode()
        
    def closeEvent(self, event):
        if self.download_thread and self.download_thread.isRunning():
            self.download_thread.stop()
            self.download_thread.wait()
            
        if self.title_check_thread and self.title_check_thread.isRunning():
            self.title_check_thread.stop()
            self.title_check_thread.wait()
            
        event.accept()
        
    def initUI(self):
        # GUI 크기 및 위치 설정
        self.setWindowTitle('YouTube to MP3 Converter')
        self.setGeometry(100, 100, 1000, 500)
        self.setMinimumSize(1000, 500)
        self.setMaximumSize(1200, 800)
        
        # 메인 위젯 및 레이아웃 설정
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setSpacing(20)  # 위젯 간 간격 증가
        main_layout.setContentsMargins(30, 30, 30, 30)  # 여백 증가
        
        # 상단 컨트롤 영역
        top_layout = QVBoxLayout()
        top_layout.setSpacing(20)
        
        # URL 입력 영역
        url_layout = QHBoxLayout()
        url_label = QLabel('YouTube URL:')
        url_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        url_label.setFixedWidth(100)
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText('YouTube URL을 입력하세요')
        self.url_input.setMinimumHeight(35)
        self.url_input.textChanged.connect(self.on_url_changed)
        
        # 클립보드 붙여넣기 버튼 추가
        self.paste_button = QPushButton('클립보드 붙여넣기')
        self.paste_button.setObjectName('paste_button')
        self.paste_button.setFixedHeight(35)
        self.paste_button.clicked.connect(self.paste_from_clipboard)
        
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_input)
        url_layout.addWidget(self.paste_button)
        top_layout.addLayout(url_layout)
        
        # 음질 선택 영역
        quality_layout = QHBoxLayout()
        quality_label = QLabel('음질:')
        quality_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        quality_label.setFixedWidth(100)
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(['320K', '256K', '192K', '160K', '128K', '96K', '64K', '48K'])
        self.quality_combo.setMinimumHeight(35)
        quality_layout.addWidget(quality_label)
        quality_layout.addWidget(self.quality_combo)
        top_layout.addLayout(quality_layout)
        
        # 저장 경로 선택 영역
        path_layout = QHBoxLayout()
        path_label = QLabel('저장 경로:')
        path_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        path_label.setFixedWidth(100)
        self.path_input = QLineEdit()
        self.path_input.setReadOnly(True)
        self.path_input.setText(self.config.get('save_path', os.path.expanduser('~/Downloads')))
        self.path_input.setMinimumHeight(35)
        self.path_button = QPushButton('찾아보기')
        self.path_button.setObjectName('path_button')  # 객체 이름 설정
        self.path_button.setFixedHeight(35)  # 고정 높이 설정
        self.path_button.clicked.connect(self.select_path)
        path_layout.addWidget(path_label)
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(self.path_button)
        top_layout.addLayout(path_layout)
        
        # 다크 모드 체크박스
        self.dark_mode_checkbox = QCheckBox('다크 모드')
        self.dark_mode_checkbox.setStyleSheet("""
            QCheckBox {
                color: white;
                font-size: 14px;
                font-weight: bold;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
            }
            QCheckBox::indicator:unchecked {
                background-color: #2b2b2b;
                border: 2px solid #3b3b3b;
                border-radius: 4px;
            }
            QCheckBox::indicator:checked {
                background-color: #4a90e2;
                border: 2px solid #4a90e2;
                border-radius: 4px;
            }
        """)
        self.dark_mode_checkbox.setChecked(True)
        self.dark_mode_checkbox.stateChanged.connect(self.toggle_dark_mode)
        top_layout.addWidget(self.dark_mode_checkbox)
        
        # 제목 표시 영역
        self.title_label = QLabel('')
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("color: #4a90e2; font-size: 14px; font-weight: bold;")
        self.title_label.setMinimumHeight(35)
        top_layout.addWidget(self.title_label)
        
        main_layout.addLayout(top_layout)
        
        # 진행 상태 영역
        status_layout = QHBoxLayout()
        status_layout.setSpacing(5)  # 위젯 간 간격을 5px로 설정
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMinimumHeight(35)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #2b2b2b;
                border-radius: 5px;
                text-align: center;
                background-color: #2b2b2b;
                font-size: 12px;
            }
            QProgressBar::chunk {
                background-color: #4a90e2;
                border-radius: 3px;
            }
        """)
        self.speed_label = QLabel('')
        self.speed_label.setAlignment(Qt.AlignVCenter | Qt.AlignRight)
        self.speed_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                padding: 8px;
                min-width: 80px;
            }
        """)
        self.speed_label.setMinimumHeight(35)
        status_layout.addWidget(self.progress_bar, 1)
        status_layout.addWidget(self.speed_label)
        main_layout.addLayout(status_layout)
        
        # 상태 메시지 영역
        self.status_label = QLabel('')
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #4a90e2; font-size: 14px; font-weight: bold;")
        self.status_label.setMinimumHeight(35)
        main_layout.addWidget(self.status_label)
        
        # 버튼 영역
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)
        self.convert_button = QPushButton('MP3 변환')
        self.convert_button.setObjectName('convert_button')  # 객체 이름 설정
        self.convert_button.setFixedHeight(45)  # 고정 높이 설정
        self.convert_button.clicked.connect(self.convert_to_mp3)
        self.convert_button.setEnabled(False)
        
        button_layout.addWidget(self.convert_button)
        main_layout.addLayout(button_layout)
        
    def toggle_dark_mode(self, state):
        if state == Qt.Checked:
            self.set_dark_mode()
            self.dark_mode_checkbox.setStyleSheet("""
                QCheckBox {
                    color: white;
                    font-size: 14px;
                    font-weight: bold;
                    spacing: 8px;
                }
                QCheckBox::indicator {
                    width: 20px;
                    height: 20px;
                }
                QCheckBox::indicator:unchecked {
                    background-color: #2b2b2b;
                    border: 2px solid #3b3b3b;
                    border-radius: 4px;
                }
                QCheckBox::indicator:checked {
                    background-color: #4a90e2;
                    border: 2px solid #4a90e2;
                    border-radius: 4px;
                }
            """)
        else:
            self.set_light_mode()
            self.dark_mode_checkbox.setStyleSheet("""
                QCheckBox {
                    color: black;
                    font-size: 14px;
                    font-weight: bold;
                    spacing: 8px;
                }
                QCheckBox::indicator {
                    width: 20px;
                    height: 20px;
                }
                QCheckBox::indicator:unchecked {
                    background-color: #ffffff;
                    border: 2px solid #cccccc;
                    border-radius: 4px;
                }
                QCheckBox::indicator:checked {
                    background-color: #4a90e2;
                    border: 2px solid #4a90e2;
                    border-radius: 4px;
                }
            """)
            
    def set_dark_mode(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1a1a1a;
            }
            QMainWindow::title {
                background-color: #1a1a1a;
                color: #ffffff;
                padding: 5px;
            }
            QLabel {
                color: #ffffff;
                font-size: 12px;
            }
            QLineEdit {
                background-color: #2b2b2b;
                color: white;
                border: 1px solid #3b3b3b;
                border-radius: 4px;
                padding: 5px;
                font-size: 12px;
            }
            QComboBox {
                background-color: #2b2b2b;
                color: white;
                border: 1px solid #3b3b3b;
                border-radius: 4px;
                padding: 5px;
                font-size: 12px;
                min-height: 25px;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: url(down_arrow.png);
                width: 12px;
                height: 12px;
            }
            QComboBox QAbstractItemView {
                background-color: #2b2b2b;
                color: white;
                border: 1px solid #3b3b3b;
                selection-background-color: #4a90e2;
                selection-color: white;
            }
            QComboBox:hover {
                border: 1px solid #4a90e2;
            }
            QComboBox:on {
                border: 1px solid #4a90e2;
            }
            QPushButton {
                background-color: #2b2b2b;
                color: white;
                border: 2px solid #3b3b3b;
                border-radius: 5px;
                padding: 10px 20px;
                min-width: 120px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3b3b3b;
            }
            QPushButton:disabled {
                background-color: #1b1b1b;
                color: #666666;
            }
            QPushButton#path_button {
                background-color: #2b2b2b;
                color: white;
                border: 2px solid #3b3b3b;
                font-size: 12px;
            }
            QPushButton#path_button:hover {
                background-color: #3b3b3b;
            }
            QPushButton#path_button:disabled {
                background-color: #1b1b1b;
                color: #666666;
            }
            QPushButton#paste_button {
                background-color: #2b2b2b;
                color: white;
                border: 2px solid #3b3b3b;
                font-size: 12px;
            }
            QPushButton#paste_button:hover {
                background-color: #3b3b3b;
            }
            QPushButton#paste_button:disabled {
                background-color: #1b1b1b;
                color: #666666;
            }
            QPushButton#convert_button {
                background-color: #2b2b2b;
                color: white;
                border: 2px solid #3b3b3b;
            }
            QPushButton#convert_button:hover {
                background-color: #3b3b3b;
            }
            QPushButton#convert_button:disabled {
                background-color: #1b1b1b;
                color: #666666;
            }
            QCheckBox {
                color: white;
                font-size: 14px;
                font-weight: bold;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
            }
            QCheckBox::indicator:unchecked {
                background-color: #2b2b2b;
                border: 2px solid #3b3b3b;
                border-radius: 4px;
            }
            QCheckBox::indicator:checked {
                background-color: #4a90e2;
                border: 2px solid #4a90e2;
                border-radius: 4px;
            }
            QProgressBar {
                border: 2px solid #2b2b2b;
                border-radius: 5px;
                text-align: center;
                background-color: #2b2b2b;
                height: 25px;
                font-size: 12px;
            }
            QProgressBar::chunk {
                background-color: #4a90e2;
                border-radius: 3px;
            }
        """)
        
    def set_light_mode(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QMainWindow::title {
                background-color: #f0f0f0;
                color: #000000;
                padding: 5px;
            }
            QLabel {
                color: #000000;
                font-size: 12px;
            }
            QLineEdit {
                background-color: #ffffff;
                color: black;
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 5px;
                font-size: 12px;
            }
            QComboBox {
                background-color: #ffffff;
                color: black;
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 5px;
                font-size: 12px;
                min-height: 25px;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: url(down_arrow.png);
                width: 12px;
                height: 12px;
            }
            QComboBox QAbstractItemView {
                background-color: #ffffff;
                color: black;
                border: 1px solid #cccccc;
                selection-background-color: #4a90e2;
                selection-color: white;
            }
            QComboBox:hover {
                border: 1px solid #4a90e2;
            }
            QComboBox:on {
                border: 1px solid #4a90e2;
            }
            QPushButton {
                background-color: #f0f0f0;
                color: black;
                border: 2px solid #cccccc;
                border-radius: 5px;
                padding: 10px 20px;
                min-width: 120px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:disabled {
                background-color: #f5f5f5;
                color: #999999;
            }
            QPushButton#path_button {
                background-color: #f0f0f0;
                color: black;
                border: 2px solid #cccccc;
                font-size: 12px;
            }
            QPushButton#path_button:hover {
                background-color: #e0e0e0;
            }
            QPushButton#path_button:disabled {
                background-color: #f5f5f5;
                color: #999999;
            }
            QPushButton#paste_button {
                background-color: #f0f0f0;
                color: black;
                border: 2px solid #cccccc;
                font-size: 12px;
            }
            QPushButton#paste_button:hover {
                background-color: #e0e0e0;
            }
            QPushButton#paste_button:disabled {
                background-color: #f5f5f5;
                color: #999999;
            }
            QPushButton#convert_button {
                background-color: #f0f0f0;
                color: black;
                border: 2px solid #cccccc;
            }
            QPushButton#convert_button:hover {
                background-color: #e0e0e0;
            }
            QPushButton#convert_button:disabled {
                background-color: #f5f5f5;
                color: #999999;
            }
            QCheckBox {
                color: black;
                font-size: 14px;
                font-weight: bold;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
            }
            QCheckBox::indicator:unchecked {
                background-color: #ffffff;
                border: 2px solid #cccccc;
                border-radius: 4px;
            }
            QCheckBox::indicator:checked {
                background-color: #4a90e2;
                border: 2px solid #4a90e2;
                border-radius: 4px;
            }
            QProgressBar {
                border: 2px solid #cccccc;
                border-radius: 5px;
                text-align: center;
                background-color: #ffffff;
                height: 25px;
                font-size: 12px;
            }
            QProgressBar::chunk {
                background-color: #4a90e2;
                border-radius: 3px;
            }
        """)
        
    def select_path(self):
        folder = QFileDialog.getExistingDirectory(self, '저장 경로 선택')
        if folder:
            self.path_input.setText(folder)
            self.config['save_path'] = folder
            save_config(self.config)
            
    def on_url_changed(self, text):
        if self.title_check_thread and self.title_check_thread.isRunning():
            self.title_check_thread.stop()
            self.title_check_thread.wait()
            self.title_check_thread = None
            
        self.title_label.setText('')
        self.convert_button.setEnabled(False)
        self.status_label.setText('')
        
        if not text.strip():
            return
            
        if not is_valid_youtube_url(text.strip()):
            self.status_label.setText('유효하지 않은 YouTube URL입니다.')
            return
            
        self.status_label.setText('제목을 가져오는 중...')
        self.title_check_thread = TitleCheckThread(text.strip())
        self.title_check_thread.title_checked.connect(self.handle_title_check)
        self.title_check_thread.start()
        
    def handle_title_check(self, title, success):
        self.title_label.setText(title)
        self.convert_button.setEnabled(success)
        self.status_label.setText('')
        
    def convert_to_mp3(self):
        try:
            url = self.url_input.text().strip()
            if not url:
                QMessageBox.warning(self, '경고', 'URL을 입력해주세요.')
                return
                
            if not is_valid_youtube_url(url):
                QMessageBox.warning(self, '경고', '유효하지 않은 YouTube URL입니다.')
                return
                
            if not self.convert_button.isEnabled():
                QMessageBox.warning(self, '경고', '유효한 동영상 URL을 입력해주세요.')
                return
                
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            self.status_label.setText('다운로드 중...')
            self.convert_button.setEnabled(False)
            
            if self.download_thread and self.download_thread.isRunning():
                self.download_thread.stop()
                self.download_thread.wait()
                
            self.download_thread = DownloadThread(
                url,
                self.quality_combo.currentText(),
                self.path_input.text(),
                self.ffmpeg_path
            )
            self.download_thread.progress.connect(self.update_progress)
            self.download_thread.speed.connect(self.update_speed)
            self.download_thread.finished.connect(self.download_finished)
            self.download_thread.error.connect(self.download_error)
            self.download_thread.conversion_started.connect(self.on_conversion_started)
            self.download_thread.stopped.connect(self.download_stopped)
            self.download_thread.start()
            
        except Exception as e:
            QMessageBox.critical(self, '오류', f'변환 중 오류가 발생했습니다: {str(e)}')
            self.reset_ui()
            
    def update_progress(self, percentage):
        self.progress_bar.setValue(percentage)
        if percentage == 100:
            self.status_label.setText('다운로드 완료, MP3 변환 중...')
            
    def update_speed(self, speed):
        self.speed_label.setText(speed)
            
    def on_conversion_started(self):
        self.status_label.setText('MP3 변환 중...')
        
    def download_finished(self, message, file_path):
        self.status_label.setText('변환이 완료되었습니다!')
        self.progress_bar.setValue(100)
        
        # 파일 정보 표시
        file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB 단위로 변환
        quality = self.quality_combo.currentText()
        
        msg = QMessageBox()
        msg.setWindowTitle('성공')
        msg.setText(f'변환이 완료되었습니다!\n\n'
                   f'파일: {os.path.basename(file_path)}\n'
                   f'크기: {file_size:.2f} MB\n'
                   f'음질: {quality}')
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #f0f0f0;
            }
            QMessageBox QLabel {
                color: black;
                font-size: 14px;
            }
            QMessageBox QPushButton {
                background-color: #f0f0f0;
                color: black;
                border: 2px solid #cccccc;
                border-radius: 5px;
                padding: 10px 20px;
                min-width: 120px;
                font-size: 14px;
                font-weight: bold;
            }
            QMessageBox QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        msg.exec_()
        self.reset_ui()
        self.url_input.clear()
        self.title_label.clear()
        self.status_label.clear()
        self.speed_label.clear()
        self.progress_bar.setVisible(False)
        self.convert_button.setEnabled(False)
        
    def download_error(self, error_message):
        self.status_label.setText('오류가 발생했습니다.')
        QMessageBox.critical(self, '오류', f'변환 중 오류가 발생했습니다: {error_message}')
        self.reset_ui()
        
    def download_stopped(self):
        self.status_label.setText('다운로드가 중지되었습니다.')
        self.progress_bar.setValue(0)
        self.reset_ui()
        
    def reset_ui(self):
        self.convert_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.speed_label.setText('')
        self.status_label.setText('')

    def paste_from_clipboard(self):
        clipboard = QApplication.clipboard()
        clipboard_text = clipboard.text()
        if clipboard_text:
            self.url_input.setText(clipboard_text)
            

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = YouTubeToMP3()
    ex.show()
    sys.exit(app.exec_()) 