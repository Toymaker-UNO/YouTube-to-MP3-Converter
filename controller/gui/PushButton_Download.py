from PyQt5.QtWidgets import QPushButton, QMainWindow
from PyQt5.QtCore import QObject, pyqtSignal
import threading
from model.Log import log_instance

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
                self._download.clicked.connect(self._handle_download_click)
                self.disable()
            else:
                log_instance.critical("PushButton_Download 초기화 실패")

    def enable(self):
        self._download.setEnabled(True)
    
    def disable(self):
        self._download.setEnabled(False)

    def _handle_download_click(self):
        """다운로드 버튼 클릭 이벤트 핸들러"""
        pass

# 싱글톤 인스턴스 생성
push_button_download_instance = PushButton_Download()