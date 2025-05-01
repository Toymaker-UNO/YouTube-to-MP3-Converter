from PyQt5.QtWidgets import QPushButton, QMainWindow
from PyQt5.QtCore import QObject, pyqtSignal
import threading

class PushButton_CheckURL:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(PushButton_CheckURL, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        self._window = None
        self._url_input = None
        self._current_url = ""

    def setup(self, window: QMainWindow):
        """PushButton_CheckURL를 초기화합니다.
        
        Args:
            window (QMainWindow): 메인 윈도우 객체
        """
        with self._lock:
            self._window = window
            self._check_url = self._window.findChild(QPushButton, "check_url")
            if self._check_url:
                self.enable()
            else:
                print("PushButton_CheckURL 초기화 실패")

    def enable(self):
        self._check_url.setEnabled(True)
    
    def disable(self):
        self._check_url.setEnabled(False)

# 싱글톤 인스턴스 생성
push_button_check_url_instance = PushButton_CheckURL()