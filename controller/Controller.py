from PyQt5.QtWidgets import QMainWindow, QPushButton, QLineEdit, QApplication, QPlainTextEdit, QComboBox
from PyQt5.QtGui import QClipboard
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from controller.Converter import Converter


# 전역 상수 정의
URL_CHECK_DELAY_MS = 1000  # URL 검사 타이머 지연 시간 (밀리초)


class URLCheckThread(QThread):
    """URL 검사와 제목 가져오기를 처리하는 스레드"""
    result_ready = pyqtSignal(str, bool)  # (제목 또는 메시지, 성공 여부)
    
    def __init__(self, url, converter):
        super().__init__()
        self.url = url
        self.converter = converter
        
    def run(self):
        try:
            if not self.url.strip():
                self.result_ready.emit("URL입력을 기다리고 있습니다.", False)
                return
                
            if not self.converter.is_valid_youtube_url(self.url.strip()):
                self.result_ready.emit("올바르지 않은 URL입니다.", False)
                return
                
            title = self.converter.get_video_title(self.url.strip())
            if title:
                self.result_ready.emit(f"제목: {title}", True)
            else:
                self.result_ready.emit("동영상 정보를 가져올 수 없습니다.", False)
                
        except Exception as e:
            self.result_ready.emit(f"오류 발생: {str(e)}", False)


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
            self._url_check_thread = None
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
            # 타이머 설정
            self._url_check_timer = QTimer()
            self._url_check_timer.setSingleShot(True)
            self._url_check_timer.timeout.connect(lambda: self._check_url(url_input.text()))
            
            # 타이핑 이벤트 연결
            url_input.textChanged.connect(self._handle_url_typing)
            # 엔터키 이벤트 연결
            url_input.returnPressed.connect(lambda: self._check_url(url_input.text()))
        else:
            print("Warning: url_input not found")

    def _handle_url_typing(self, text):
        """URL 입력 중 타이핑 이벤트 핸들러"""
        # 타이머 재시작
        self._url_check_timer.stop()
        self._url_check_timer.start(URL_CHECK_DELAY_MS)  # 설정된 지연 시간 후에 검사

    def _handle_paste_button_click(self):
        """클립보드의 내용을 URL 입력창에 붙여넣고 검사합니다."""
        url_input = self._window.findChild(QLineEdit, "url_input")
        if url_input:
            clipboard_text = self._clipboard.text()
            url_input.setText(clipboard_text)
            # 붙여넣기 후 즉시 검사
            self._check_url(clipboard_text)
        else:
            print("Warning: url_input not found")

    def _check_url(self, text):
        """URL을 검사하고 결과에 따라 UI를 업데이트합니다."""
        # 이전 스레드가 실행 중이면 중지
        if self._url_check_thread and self._url_check_thread.isRunning():
            self._url_check_thread.terminate()
            self._url_check_thread.wait()
            
        # 새 스레드 생성 및 시작
        self._url_check_thread = URLCheckThread(text, self._converter)
        self._url_check_thread.result_ready.connect(self._handle_url_check_result)
        self._url_check_thread.start()
        
        # 로그 디스플레이에 검사 중 메시지 표시
        log_display = self._window.findChild(QPlainTextEdit, "log_display")
        if log_display:
            log_display.setPlainText("URL을 검사하는 중...")

    def _handle_url_check_result(self, message, success):
        """URL 검사 결과를 처리합니다."""
        log_display = self._window.findChild(QPlainTextEdit, "log_display")
        quality_combo = self._window.findChild(QComboBox, "quality_combo")
        download_button = self._window.findChild(QPushButton, "download_button")
        
        if log_display:
            log_display.setPlainText(message)
            
        if quality_combo:
            quality_combo.setEnabled(success)
            
        if download_button:
            download_button.setEnabled(success)


# 싱글톤 인스턴스 생성
controller_instance = Controller() 