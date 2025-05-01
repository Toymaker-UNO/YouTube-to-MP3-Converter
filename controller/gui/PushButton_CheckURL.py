from PyQt5.QtWidgets import QPushButton, QMainWindow, QLineEdit
from PyQt5.QtCore import QObject, pyqtSignal
from controller.gui.LineEdit_URLInput import line_edit_url_input_instance
from controller.gui.ComboBox_AudioQuality import combo_box_audio_quality_instance
from controller.gui.PushButton_Download import push_button_download_instance
from controller.gui.PlainTextEdit_LogDisplay import plain_text_edit_log_display_instance
from controller.logic.CheckURL import check_url_instance
import threading
from model.Log import log

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

    def setup(self, window: QMainWindow):
        """PushButton_CheckURL를 초기화합니다.
        
        Args:
            window (QMainWindow): 메인 윈도우 객체
        """
        with self._lock:
            self._window = window
            self._check_url = self._window.findChild(QPushButton, "check_url")
            if self._check_url:
                self._check_url.clicked.connect(self._handle_check_url_click)
                self.enable()
            else:
                log.critical("PushButton_CheckURL 초기화 실패")

    def enable(self):
        self._check_url.setEnabled(True)
    
    def disable(self):
        self._check_url.setEnabled(False)

    def _get_text(self):
        return self._check_url.text()
    
    #버튼의 text 를 변경하는 함수
    def _set_text(self, text):
        self._check_url.setText(text)

    def _handle_check_url_click(self):
        """URL 검사 버튼 클릭 이벤트 핸들러"""
        name = self._get_text()
        log.debug("버튼 클릭: [" + name + "]")

        if name == "Check URL":
            self._do_check_url()
        else:
            self._do_change_url()

    def _do_check_url(self):
        log.debug("버튼 클릭 (Check URL)")
        url = line_edit_url_input_instance.get_url()
        if check_url_instance.is_valid_youtube_url(url):
            log.debug("유효한 URL입니다.")
            plain_text_edit_log_display_instance.print_next_line("유효한 URL입니다.")
            combo_box_audio_quality_instance.enable()
            push_button_download_instance.enable()
            line_edit_url_input_instance.disable()
            self._set_text("Change URL")
        else:
            log.debug("유효하지 않은 URL입니다.")
            plain_text_edit_log_display_instance.print_next_line("유효하지 않은 URL입니다.")
        
    def _do_change_url(self):
        log.debug("버튼 클릭 (ChangeURL)")
        line_edit_url_input_instance.enable()
        self._set_text("Check URL")
        combo_box_audio_quality_instance.disable()
        push_button_download_instance.disable()

# 싱글톤 인스턴스 생성
push_button_check_url_instance = PushButton_CheckURL()