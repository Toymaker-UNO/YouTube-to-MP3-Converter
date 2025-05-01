from PyQt5.QtWidgets import QPushButton, QMainWindow
from PyQt5.QtCore import QObject, pyqtSignal
import threading
from model.Log import log
from controller.gui.LineEdit_URLInput import line_edit_url_input_instance
from controller.gui.ComboBox_AudioQuality import combo_box_audio_quality_instance
from controller.gui.PlainTextEdit_LogDisplay import plain_text_edit_log_display_instance
from controller.logic.DownloadYoutubeAudio import download_youtube_audio_instance
from controller.logic.DirectoryManager import directory_manager_instance

class PushButton_Download:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(PushButton_Download, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        self._window = None
        self._url_input = None
        self._current_url = ""

    def setup(self, window: QMainWindow):
        """PushButton_Download를 초기화합니다.
        
        Args:
            window (QMainWindow): 메인 윈도우 객체
        """
        with self._lock:
            self._window = window
            self._download = self._window.findChild(QPushButton, "download")
            if self._download:
                self._download.clicked.connect(self._handle_button_click_event)
                self.disable()
            else:
                log.critical("PushButton_Download 초기화 실패")

    def enable(self):
        self._download.setEnabled(True)
    
    def disable(self):
        self._download.setEnabled(False)

    def _handle_button_click_event(self):
        """다운로드 버튼 클릭 이벤트 핸들러"""
        log.debug("버튼 클릭 [Download]")
        self._download_youtube_audio()
        
    def _download_youtube_audio(self):
        """YouTube 오디오를 다운로드합니다."""
        try:
            # URL과 품질 설정을 가져옵니다
            url = line_edit_url_input_instance.get_url()
            quality = combo_box_audio_quality_instance.get_selected_quality()
                
            # 다운로드 시작 메시지
            plain_text_edit_log_display_instance.print_next_line("다운로드 중...")
            
            # 다운로드 디렉토리 설정
            save_path = directory_manager_instance.make_download_directory()
            
            # 다운로드 실행
            success = download_youtube_audio_instance.download_audio(url, quality, save_path)
            
            if success:
                plain_text_edit_log_display_instance.print_next_line("다운로드 완료!")
            else:
                plain_text_edit_log_display_instance.print_next_line("다운로드 실패. 다시 시도해주세요.")
                
        except Exception as e:
            log.error(f"다운로드 중 오류 발생: {str(e)}")
            plain_text_edit_log_display_instance.print_next_line(f"오류 발생: {str(e)}")

# 싱글톤 인스턴스 생성
push_button_download_instance = PushButton_Download()