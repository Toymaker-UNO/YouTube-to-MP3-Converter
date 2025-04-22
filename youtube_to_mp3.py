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
import traceback
import psutil
import threading
from model.Log import Log
from model.Configuration import Configuration

CONFIG_FILE = 'youtube_to_mp3.config.json'

# 전역 변수
config = None
log = None

def initialize():
    """애플리케이션의 초기화를 수행합니다.
    - Configuration 인스턴스 생성 및 초기화
    - Log 인스턴스 생성
    - 로깅 설정 초기화
    """
    global config, log
    
    # Configuration 인스턴스 생성 및 초기화
    config = Configuration()
    config.initialize(CONFIG_FILE)
    
    # Log 인스턴스 생성
    log = Log()
    
    # 로깅 설정 초기화
    logging_config = config.get('logging')
    log.initialize(
        enable_logging=logging_config.get('enable_logging', True),
        log_file=logging_config.get('log_file', 'youtube_to_mp3.log.txt'),
        max_size_mb=logging_config.get('max_log_size_mb', 10),
        backup_count=logging_config.get('max_backup_count', 2),
        encoding=logging_config.get('encoding', 'utf-8'),
        log_level=logging_config.get('log_level', 'DEBUG')
    )
    
    # 성능 모니터링 활성화 여부 확인
    if logging_config.get('enable_performance_logging', True):
        start_performance_monitoring()

def log_exception(e):
    """예외 정보를 상세히 로깅"""
    log.error(f"예외 발생: {str(e)}")
    log.error(f"예외 유형: {type(e).__name__}")
    log.error(f"스택 트레이스:\n{traceback.format_exc()}")
    
def log_performance():
    """시스템 성능 정보 로깅"""
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    cpu_percent = process.cpu_percent()
    thread_count = threading.active_count()
    
    log.debug(f"""
성능 정보:
- 메모리 사용량: {memory_info.rss / 1024 / 1024:.2f} MB
- CPU 사용률: {cpu_percent}%
- 활성 스레드 수: {thread_count}
    """)

def start_performance_monitoring():
    """성능 모니터링 스레드 시작"""
    def monitor():
        while True:
            log_performance()
            time.sleep(60)  # 1분마다 로깅
            
    monitor_thread = threading.Thread(target=monitor, daemon=True)
    monitor_thread.start()
    log.info("성능 모니터링 스레드 시작")

def is_valid_youtube_url(url):
    """YouTube URL의 유효성을 검사합니다."""
    youtube_regex = r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?([^"&?/s]{11})'
    return bool(re.match(youtube_regex, url))

def get_video_info(url):
    log.info(f"비디오 정보를 가져옵니다: {url}")
    try:
        # URL 정규화
        if 'youtu.be' in url:
            video_id = url.split('youtu.be/')[-1].split('?')[0]
            url = f'https://www.youtube.com/watch?v={video_id}'
        elif '&' in url:
            url = url.split('&')[0]
            
        log.info(f"처리 중인 URL: {url}")
        
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
                log.error("비디오 정보를 추출할 수 없습니다.")
                return None
                
            if 'entries' in info:  # 플레이리스트인 경우
                log.error("플레이리스트 URL은 지원하지 않습니다.")
                return None
                    
            if 'title' not in info:
                log.error("제목 정보가 없습니다.")
                return None
                
            log.info(f"비디오 제목: {info['title']}")
            return info['title']
            
    except Exception as e:
        log.error(f"비디오 정보를 가져오는 중 오류 발생: {str(e)}")
        return None

class DownloadThread(QThread):
    progress = pyqtSignal(int)
    speed = pyqtSignal(str)
    finished = pyqtSignal(str, str)  # (메시지, 파일경로)
    error = pyqtSignal(str)
    conversion_progress = pyqtSignal(int)
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
        self.download_start_time = None
        self.conversion_start_time = None
        self.conversion_end_time = None
        self.temp_filename = None
        self.download_completed = False
        self.download_started = False
        log.debug(f"다운로드 스레드 초기화: URL={url}, 품질={quality}, 저장경로={save_path}")
        
    def stop(self):
        log.info("다운로드 스레드 중지 요청")
        self._is_running = False
        self.stopped.emit()
        
    def run(self):
        log.debug("다운로드 스레드 시작")
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
            self.temp_filename = f"temp_{int(time.time())}"
            log.info(f"임시 파일명 생성: {self.temp_filename}")
            
            ydl_opts = {
                'format': f'bestaudio[abr<={quality_map[self.quality]}]',
                'outtmpl': os.path.join(self.save_path, f'{self.temp_filename}.%(ext)s'),
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
            
            self.download_start_time = time.time()
            log.info("다운로드 시작")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=True)
                if not self._is_running:
                    log.info("다운로드 중단됨")
                    return
                    
                # 출력 파일 경로 확인
                output_file = os.path.join(self.save_path, f"{self.temp_filename}.mp3")
                log.info(f"출력 파일 경로: {output_file}")
                
                # 변환 완료를 기다림
                while not os.path.exists(output_file):
                    if not self._is_running:
                        log.info("변환 중단됨")
                        return
                    time.sleep(0.1)
                
                # 변환 완료 시간 기록
                self.conversion_end_time = time.time()
                log.info("변환 완료")
                
                # 파일 크기 확인
                file_size = os.path.getsize(output_file)
                if file_size == 0:
                    raise ValueError("변환된 파일이 비어 있습니다.")
                    
                # 최종 파일명으로 변경
                final_filename = f"{info['title']}.mp3"
                final_path = os.path.join(self.save_path, final_filename)
                log.info(f"최종 파일명: {final_filename}")
                
                # 파일명 중복 처리
                counter = 1
                while os.path.exists(final_path):
                    final_filename = f"{info['title']}_{counter}.mp3"
                    final_path = os.path.join(self.save_path, final_filename)
                    counter += 1
                    log.info(f"파일명 중복으로 새 이름 생성: {final_filename}")
                    
                os.rename(output_file, final_path)
                self.output_file = final_path
                
                # 로그 기록
                download_time = self.conversion_start_time - self.download_start_time
                conversion_time = self.conversion_end_time - self.conversion_start_time
                total_time = self.conversion_end_time - self.download_start_time
                
                log.critical(f"""
파일 정보:
- URL: {self.url}
- 제목: {info['title']}
- 원본 크기: {file_size / (1024*1024):.2f} MB
- 다운로드 시간: {download_time:.2f} 초
- 변환 시간: {conversion_time:.2f} 초
- 총 소요 시간: {total_time:.2f} 초
- 선택된 음질: {self.quality}
                """)
                
                if not self._is_running:
                    log.info("작업 중단됨")
                    return
                    
                self.finished.emit('다운로드 완료', final_path)
                
        except Exception as e:
            log_exception(e)
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
                    
                    # 다운로드 시작 시점 기록 (0%일 때)
                    if percentage == 0 and not self.download_started:
                        self.download_started = True
                        self.download_start_time = time.time()
                        log.info("다운로드 시작 (0%)")
                    
                    # 다운로드가 100% 완료되면 변환 시작 시간 기록
                    if percentage == 100 and not self.download_completed:
                        self.download_completed = True
                        self.conversion_start_time = time.time()
                        self.conversion_started.emit()
                        log.info("다운로드 완료 (100%), 변환 시작")
                        return  # 100% 도달 시 속도 업데이트 중지
                    
                if speed and not self.download_completed:  # 다운로드가 완료되지 않았을 때만 속도 업데이트
                    speed_str = f"{speed/1024/1024:.1f} MB/s"
                    self.speed.emit(speed_str)
                log.debug(f"다운로드 진행률: {percentage}%, 속도: {speed_str}")
            except Exception as e:
                log_exception(e)

class TitleCheckThread(QThread):
    title_checked = pyqtSignal(str, bool)
    
    def __init__(self, url):
        super().__init__()
        self.url = url
        self._is_running = True
        log.info(f"제목 확인 스레드 초기화: URL={url}")
        
    def stop(self):
        log.info("제목 확인 스레드 중지 요청")
        self._is_running = False
        
    def run(self):
        log.info("제목 확인 스레드 시작")
        try:
            if not self._is_running:
                log.info("제목 확인 중단됨")
                return
                
            if not self.url:
                log.warning("URL이 비어있음")
                self.title_checked.emit('', False)
                return
                
            if not is_valid_youtube_url(self.url):
                log.warning("유효하지 않은 YouTube URL")
                self.title_checked.emit('올바르지 않은 YouTube URL입니다.', False)
                return
                
            title = get_video_info(self.url)
            if not self._is_running:
                log.info("제목 확인 중단됨")
                return
                
            if title:
                log.info(f"제목 확인 완료: {title}")
                self.title_checked.emit(f'제목: {title}', True)
            else:
                log.warning("제목을 가져올 수 없음")
                self.title_checked.emit('동영상 정보를 가져올 수 없습니다.', False)
                
        except Exception as e:
            log_exception(e)
            if self._is_running:
                self.title_checked.emit(f'오류: {str(e)}', False)

class YouTubeToMP3(QMainWindow):
    def __init__(self):
        super().__init__()
        log.debug("YouTubeToMP3 애플리케이션 초기화")
        self.ffmpeg_path = config.get('ffmpeg_path')
        self.save_path = config.get('save_path')
        log.info(f"초기 설정: FFmpeg 경로={self.ffmpeg_path}, 저장 경로={self.save_path}")
        self.download_thread = None
        self.title_check_thread = None
        self.initUI()
        self.dark_mode_checkbox.setChecked(True)
        self.set_dark_mode()
        
    def closeEvent(self, event):
        log.debug("애플리케이션 종료")
        log_performance()  # 종료 시 성능 정보 로깅
        if self.download_thread and self.download_thread.isRunning():
            log.info("다운로드 스레드 종료")
            self.download_thread.stop()
            self.download_thread.wait()
            
        if self.title_check_thread and self.title_check_thread.isRunning():
            log.info("제목 확인 스레드 종료")
            self.title_check_thread.stop()
            self.title_check_thread.wait()
            
        event.accept()
        
    def initUI(self):
        log.info("UI 초기화")
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
        self.path_input.setText(self.save_path)
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
        log.info(f"다크 모드 전환: {'활성화' if state == Qt.Checked else '비활성화'}")
        if state == Qt.Checked:
            self.set_dark_mode()
            log.info("다크 모드 스타일 적용")
        else:
            self.set_light_mode()
            log.info("라이트 모드 스타일 적용")
            
    def set_dark_mode(self):
        log.info("다크 모드 UI 스타일 설정")
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
        log.info("라이트 모드 UI 스타일 설정")
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
        log.info("저장 경로 선택 대화상자 열기")
        folder = QFileDialog.getExistingDirectory(self, '저장 경로 선택')
        if folder:
            log.info(f"새 저장 경로 선택: {folder}")
            self.path_input.setText(folder)
            self.save_path = folder
            config.set('save_path', folder)
            
    def on_url_changed(self, text):
        log.info(f"URL 변경 감지: {text}")
        if self.title_check_thread and self.title_check_thread.isRunning():
            log.info("이전 제목 확인 스레드 중지")
            self.title_check_thread.stop()
            self.title_check_thread.wait()
            self.title_check_thread = None
            
        self.title_label.setText('')
        self.convert_button.setEnabled(False)
        self.status_label.setText('')
        
        if not text.strip():
            log.info("URL이 비어있음")
            return
            
        if not is_valid_youtube_url(text.strip()):
            log.warning("유효하지 않은 YouTube URL")
            self.status_label.setText('유효하지 않은 YouTube URL입니다.')
            return
            
        log.info("제목 확인 시작")
        self.status_label.setText('제목을 가져오는 중...')
        self.title_check_thread = TitleCheckThread(text.strip())
        self.title_check_thread.title_checked.connect(self.handle_title_check)
        self.title_check_thread.start()
        
    def handle_title_check(self, title, success):
        log.info(f"제목 확인 결과: {title}, 성공={success}")
        self.title_label.setText(title)
        self.convert_button.setEnabled(success)
        self.status_label.setText('')
        
    def convert_to_mp3(self):
        log.debug("MP3 변환 시작")
        try:
            url = self.url_input.text().strip()
            if not url:
                log.warning("URL이 비어있음")
                QMessageBox.warning(self, '경고', 'URL을 입력해주세요.')
                return
                
            if not is_valid_youtube_url(url):
                log.warning("유효하지 않은 YouTube URL")
                QMessageBox.warning(self, '경고', '유효하지 않은 YouTube URL입니다.')
                return
                
            if not self.convert_button.isEnabled():
                log.warning("변환 버튼이 비활성화됨")
                QMessageBox.warning(self, '경고', '유효한 동영상 URL을 입력해주세요.')
                return
                
            log.info("다운로드 준비")
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            self.status_label.setText('다운로드 중...')
            self.convert_button.setEnabled(False)
            
            if self.download_thread and self.download_thread.isRunning():
                log.info("이전 다운로드 스레드 중지")
                self.download_thread.stop()
                self.download_thread.wait()
                
            log.info("새 다운로드 스레드 시작")
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
            log_exception(e)
            QMessageBox.critical(self, '오류', f'변환 중 오류가 발생했습니다: {str(e)}')
            self.reset_ui()
            
    def update_progress(self, percentage):
        log.debug(f"다운로드 진행률: {percentage}%")
        self.progress_bar.setValue(percentage)
        if percentage == 100:
            self.status_label.setText('다운로드 완료, MP3 변환 중...')
            self.speed_label.setText('')  # 속도 표시 지우기
            
    def update_speed(self, speed):
        log.debug(f"다운로드 속도: {speed}")
        self.speed_label.setText(speed)
            
    def on_conversion_started(self):
        log.info("MP3 변환 시작")
        self.status_label.setText('MP3 변환 중...')
        self.speed_label.setText('')  # 속도 표시 지우기
        
    def download_finished(self, message, file_path):
        log.info(f"다운로드 완료: {file_path}")
        self.status_label.setText('변환이 완료되었습니다!')
        self.progress_bar.setValue(100)
        
        # 파일 정보 표시
        file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB 단위로 변환
        quality = self.quality_combo.currentText()
        
        log.info(f"""
변환 완료 정보:
- 파일: {os.path.basename(file_path)}
- 크기: {file_size:.2f} MB
- 음질: {quality}
        """)
        
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
        log.error(f"다운로드 오류: {error_message}")
        self.status_label.setText('오류가 발생했습니다.')
        QMessageBox.critical(self, '오류', f'변환 중 오류가 발생했습니다: {error_message}')
        self.reset_ui()
        
    def download_stopped(self):
        log.info("다운로드 중지됨")
        self.status_label.setText('다운로드가 중지되었습니다.')
        self.progress_bar.setValue(0)
        self.reset_ui()
        
    def reset_ui(self):
        log.info("UI 초기화")
        self.convert_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.speed_label.setText('')
        self.status_label.setText('')

    def paste_from_clipboard(self):
        log.info("클립보드에서 붙여넣기")
        clipboard = QApplication.clipboard()
        clipboard_text = clipboard.text()
        if clipboard_text:
            self.url_input.setText(clipboard_text)
            

if __name__ == '__main__':
    # 애플리케이션 초기화
    initialize()
    
    app = QApplication(sys.argv)
    ex = YouTubeToMP3()
    ex.show()
    log.info("메인 윈도우 표시")
    sys.exit(app.exec_()) 