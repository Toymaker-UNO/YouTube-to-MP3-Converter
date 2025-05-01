from PyQt5.QtWidgets import QLineEdit, QMainWindow
from PyQt5.QtCore import QObject, pyqtSignal
import threading

class URLInput:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(URLInput, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        self._window = None
        self._url_input = None
        self._current_url = ""

    def setup(self, window: QMainWindow):
        """URLInput를 초기화합니다.
        
        Args:
            window (QMainWindow): 메인 윈도우 객체
        """
        with self._lock:
            self._window = window
            self._url_input = self._window.findChild(QLineEdit, "url_input")
            if self._url_input:
                self._url_input.setPlaceholderText("Enter YouTube URL here.")
                self._is_enabled = True
                self._is_valid = False
            else:
                print("URLInput 초기화 실패")

    def enable(self):
        self._is_enabled = True
        self._url_input.setEnabled(True)
    
    def disable(self):
        self._is_enabled = False
        self._url_input.setEnabled(False)