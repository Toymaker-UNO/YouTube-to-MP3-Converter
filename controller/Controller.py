from PyQt5.QtWidgets import QMainWindow, QPushButton, QLineEdit, QApplication, QPlainTextEdit, QComboBox
from PyQt5.QtGui import QClipboard
from PyQt5.QtCore import Qt
from controller.Converter import Converter


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
            self._converter = Converter()
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

        # URL 입력 변경 이벤트 연결
        url_input = self._window.findChild(QLineEdit, "url_input")
        if url_input:
            url_input.textChanged.connect(self._handle_url_changed)
        else:
            print("Warning: url_input not found")

    def _handle_paste_button_click(self):
        """클립보드의 내용을 URL 입력창에 붙여넣습니다."""
        url_input = self._window.findChild(QLineEdit, "url_input")
        if url_input:
            clipboard_text = self._clipboard.text()
            url_input.setText(clipboard_text)
        else:
            print("Warning: url_input not found")

    def _handle_url_changed(self, text):
        """URL 입력이 변경될 때 호출되는 핸들러"""
        log_display = self._window.findChild(QPlainTextEdit, "log_display")
        quality_combo = self._window.findChild(QComboBox, "quality_combo")
        download_button = self._window.findChild(QPushButton, "download_button")

        if not text.strip():
            if log_display:
                log_display.setPlainText("URL입력을 기다리고 있습니다.")
            if quality_combo:
                quality_combo.setEnabled(False)
            if download_button:
                download_button.setEnabled(False)
            return

        if not self._converter.is_valid_youtube_url(text.strip()):
            if log_display:
                log_display.setPlainText("올바르지 않은 URL입니다.")
            if quality_combo:
                quality_combo.setEnabled(False)
            if download_button:
                download_button.setEnabled(False)
            return

        # URL이 유효한 경우 제목을 가져옴
        title = self._converter.get_video_title(text.strip())
        if title:
            if log_display:
                log_display.setPlainText(f"제목: {title}")
            if quality_combo:
                quality_combo.setEnabled(True)
            if download_button:
                download_button.setEnabled(True)
        else:
            if log_display:
                log_display.setPlainText("동영상 정보를 가져올 수 없습니다.")
            if quality_combo:
                quality_combo.setEnabled(False)
            if download_button:
                download_button.setEnabled(False)


# 싱글톤 인스턴스 생성
controller_instance = Controller() 