from PyQt5.QtWidgets import QMainWindow, QPushButton, QLineEdit, QApplication, QPlainTextEdit
from PyQt5.QtGui import QClipboard
from PyQt5.QtCore import Qt


class Controller:
    """컨트롤러 클래스의 싱글톤 구현"""
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(Controller, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def initialize(self, window: QMainWindow):
        """
        컨트롤러를 초기화하고 이벤트 핸들러를 설정합니다.
        
        Args:
            window (QMainWindow): View에서 생성된 메인 윈도우 인스턴스
        """
        if not self._initialized:
            self._window = window
            self._clipboard = QApplication.clipboard()
            self._setup_event_handlers()
            self._initialized = True
            
            # 로그 디스플레이 초기화
            self._initialize_log_display()

    def _initialize_log_display(self):
        """로그 디스플레이를 초기화하고 초기 메시지를 출력합니다."""
        log_display = self._window.findChild(QPlainTextEdit, "log_display")
        if log_display:
            log_display.setPlainText("URL입력을 기다리고 있습니다.")
        else:
            print("Warning: log_display not found")

    def _setup_event_handlers(self):
        """이벤트 핸들러를 설정합니다."""
        # Paste 버튼 클릭 이벤트 연결
        paste_button = self._window.findChild(QPushButton, "paste_button")
        if paste_button:
            paste_button.clicked.connect(self._handle_paste_button_click)
        else:
            print("Warning: paste_button not found")

    def _handle_paste_button_click(self):
        """클립보드의 내용을 URL 입력창에 붙여넣습니다."""
        url_input = self._window.findChild(QLineEdit, "url_input")
        if url_input:
            clipboard_text = self._clipboard.text()
            url_input.setText(clipboard_text)
        else:
            print("Warning: url_input not found")


# 싱글톤 인스턴스 생성
controller_instance = Controller() 