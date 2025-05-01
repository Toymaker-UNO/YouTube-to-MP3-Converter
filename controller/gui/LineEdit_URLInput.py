from PyQt5.QtWidgets import QLineEdit, QMainWindow
from PyQt5.QtCore import QObject, pyqtSignal
import threading

class LineEdit_URLInput:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(LineEdit_URLInput, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        self._window = None
        self._url_input = None

    def setup(self, window: QMainWindow):
        """LineEdit_URLInput를 초기화합니다.
        
        Args:
            window (QMainWindow): 메인 윈도우 객체
        """
        with self._lock:
            self._window = window
            self._url_input = self._window.findChild(QLineEdit, "url_input")
            if self._url_input:
                self._url_input.setPlaceholderText("Enter YouTube URL here.")
            else:
                print("LineEdit_URLInput 초기화 실패")

    def enable(self):
        self._url_input.setEnabled(True)
    
    def disable(self):
        self._url_input.setEnabled(False)

# 싱글톤 인스턴스 생성
line_edit_url_input_instance = LineEdit_URLInput()