import threading
from PyQt5.QtWidgets import QMainWindow
from controller.gui.LineEdit_URLInput import line_edit_url_input_instance
from controller.gui.PushButton_CheckURL import push_button_check_url_instance
from controller.gui.ComboBox_AudioQuality import combo_box_audio_quality_instance
from controller.gui.PushButton_Download import push_button_download_instance
from controller.gui.PlainTextEdit_LogDisplay import plain_text_edit_log_display_instance

class NewController:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(NewController, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        pass

    def run(self, window: QMainWindow):
        line_edit_url_input_instance.setup(window)
        push_button_check_url_instance.setup(window)
        combo_box_audio_quality_instance.setup(window)
        push_button_download_instance.setup(window)
        plain_text_edit_log_display_instance.setup(window)
        

# 싱글톤 인스턴스 생성
new_controller_instance = NewController() 