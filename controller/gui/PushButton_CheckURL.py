from PyQt5.QtWidgets import QPushButton, QMainWindow, QLineEdit
from PyQt5.QtCore import QObject, pyqtSignal, QThread
from controller.gui.LineEdit_URLInput import line_edit_url_input_instance
from controller.gui.ComboBox_AudioQuality import combo_box_audio_quality_instance
from controller.gui.PushButton_Download import push_button_download_instance
from controller.gui.PlainTextEdit_LogDisplay import plain_text_edit_log_display_instance
from controller.logic.CheckURL import check_url_instance
import threading
from model.Log import log
from controller.logic.YoutubeTitle import youtube_title_instance

class TitleFetchThread(QThread):
    get_title_success = pyqtSignal(str)
    get_title_failed = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, url):
        super().__init__()
        self.url = url
        
    def run(self):
        try:
            title = youtube_title_instance.get(self.url)
            if title:
                self.get_title_success.emit(title)
            else:
                self.get_title_failed.emit("제목을 가져올 수 없습니다.")
        except Exception as e:
            log.error(f"제목 가져오기 중 오류 발생: {str(e)}")
            self.error_occurred.emit(f"오류 발생: {str(e)}")

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
        self._current_url = ""
        self._title_fetch_thread = None

    def setup(self, window: QMainWindow):
        """PushButton_CheckURL를 초기화합니다.
        
        Args:
            window (QMainWindow): 메인 윈도우 객체
        """
        with self._lock:
            self._window = window
            self._check_url = self._window.findChild(QPushButton, "check_url")
            if self._check_url:
                self._check_url.clicked.connect(self._handle_button_click_event)
                self.enable()
            else:
                log.critical("PushButton_CheckURL 초기화 실패")

    def enable(self):
        self._check_url.setEnabled(True)
    
    def disable(self):
        self._check_url.setEnabled(False)

    def _handle_button_click_event(self):
        """URL 검사 버튼 클릭 이벤트 핸들러"""
        name = self._check_url.text()
        log.debug("버튼 클릭: [" + name + "]")

        if name == "Check URL":
            self._check_url_button_clicked()
        else:
            self._change_url_button_clicked()

    def _check_url_button_clicked(self):
        """URL 검사 수행"""
        url = line_edit_url_input_instance.get_url()
        
        if not check_url_instance.is_valid_youtube_url(url):
            log.debug("유효하지 않은 URL입니다.")
            plain_text_edit_log_display_instance.print_next_line("유효하지 않은 URL입니다.")
            return
            
        # 이전 스레드가 실행 중이면 종료
        if self._title_fetch_thread and self._title_fetch_thread.isRunning():
            self._title_fetch_thread.terminate()
            self._title_fetch_thread.wait()
            
        # 새 스레드 생성 및 시작
        self._title_fetch_thread = TitleFetchThread(url)
        self._title_fetch_thread.get_title_success.connect(self._thread_get_title_success)
        self._title_fetch_thread.get_title_failed.connect(self._thread_get_title_failed)
        self._title_fetch_thread.error_occurred.connect(self._thread_error_occurred)
        self._title_fetch_thread.start()
        
        # UI 상태 업데이트
        self.disable()
        line_edit_url_input_instance.disable()
        plain_text_edit_log_display_instance.print_next_line("제목을 가져오는 중...")

    def _change_url_button_clicked(self):
        self._button_mode_change_check_url()

    def _thread_get_title_success(self, title):
        """제목 가져오기 성공 핸들러"""
        plain_text_edit_log_display_instance.print_next_line("제목: " + title)
        self._button_mode_change_change_url()

    def _thread_get_title_failed(self, message):
        """제목 가져오기 실패 핸들러"""
        plain_text_edit_log_display_instance.print_next_line(message)
        self._button_mode_change_check_url()

    def _thread_error_occurred(self, message):
        """오류 발생 핸들러"""
        plain_text_edit_log_display_instance.print_next_line(message)
        self._button_mode_change_check_url()
        
    def _button_mode_change_check_url(self):
        line_edit_url_input_instance.enable()
        combo_box_audio_quality_instance.disable()
        push_button_download_instance.disable()
        self._check_url.setText("Check URL")
        self.enable()

    def _button_mode_change_change_url(self):
        line_edit_url_input_instance.disable()
        combo_box_audio_quality_instance.enable()
        push_button_download_instance.enable()
        self._check_url.setText("Change URL")
        self.enable()

# 싱글톤 인스턴스 생성
push_button_check_url_instance = PushButton_CheckURL()