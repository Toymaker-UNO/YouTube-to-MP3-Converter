from PyQt5.QtWidgets import QPushButton, QMainWindow
from PyQt5.QtCore import QObject, pyqtSignal, QThread
import threading
from model.Log import log
from controller.gui.LineEdit_URLInput import line_edit_url_input_instance
from controller.gui.ComboBox_AudioQuality import combo_box_audio_quality_instance
from controller.gui.PlainTextEdit_LogDisplay import plain_text_edit_log_display_instance
from controller.logic.DownloadYoutubeAudio import download_youtube_audio_instance
from controller.logic.DirectoryManager import directory_manager_instance
from controller.logic.ConverterToMP3 import converter_to_mp3_instance

class DownloadThread(QThread):
    """다운로드 작업을 처리하는 스레드"""
    progress_updated = pyqtSignal(str)  # 진행 상황 메시지
    download_completed = pyqtSignal(str, str)  # 완료 메시지
    error_occurred = pyqtSignal(str)    # 오류 메시지

    def __init__(self, url, quality, save_path):
        super().__init__()
        self.url = url
        self.quality = quality
        self.save_path = save_path
        self.current_speed = "0.0 MB/s"
        
    def run(self):
        try:
            # 진행 상황 콜백 함수
            def on_progress(percentage):
                progress_text = "다운로드: " + plain_text_edit_log_display_instance.create_progress_bar(percentage)
                if 100 != percentage:
                    progress_text += f" ({self.current_speed:>12})"
                self.progress_updated.emit(progress_text)
                
            def on_speed(speed):
                self.current_speed = speed
            
            # 다운로드
            downloaded_file, title = download_youtube_audio_instance.download_audio(
                url=self.url,
                quality=self.quality,
                progress_callback=on_progress,
                speed_callback=on_speed
            )

            # 다운로드 완료 메시지
            self.download_completed.emit(downloaded_file, title)
            
        except Exception as e:
            self.error_occurred.emit(f"오류가 발생했습니다: {str(e)}")

class ConvertThread(QThread):
    """MP3 변환 작업을 처리하는 스레드"""
    progress_updated = pyqtSignal(str)  # 진행 상황 메시지
    convert_completed = pyqtSignal(str)  # 완료 메시지
    error_occurred = pyqtSignal(str)    # 오류 메시지

    def __init__(self, input_file, title, quality, save_path):
        super().__init__()
        self.input_file = input_file
        self.title = title
        self.quality = quality
        self.save_path = save_path

    def run(self):
        try:
            # 진행 상황 콜백 함수
            def on_progress(percentage):
                progress_text = "MP3변환: " + plain_text_edit_log_display_instance.create_progress_bar(round(percentage, 2))
                self.progress_updated.emit(progress_text)

            # MP3 변환
            self._final_path = converter_to_mp3_instance.convert(
                input_file=self.input_file,
                title=self.title,
                quality=self.quality,
                save_path=self.save_path,
                progress_callback=on_progress
            )   

            # 변환 완료 메시지
            self.convert_completed.emit(self._final_path)

        except Exception as e:
            self.error_occurred.emit(f"오류가 발생했습니다: {str(e)}")

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
        self._download_button = None
        self._download_thread = None
        self._convert_thread = None

    def setup(self, window: QMainWindow):
        """PushButton_Download를 초기화합니다.
        
        Args:
            window (QMainWindow): 메인 윈도우 객체
        """
        with self._lock:
            self._window = window
            self._download_button = self._window.findChild(QPushButton, "download")
            if self._download_button:
                self._download_button.clicked.connect(self._handle_button_click_event)
                self.disable()
            else:
                log.critical("PushButton_Download 초기화 실패")

    def enable(self):
        self._download_button.setEnabled(True)
    
    def disable(self):
        self._download_button.setEnabled(False)

    def _handle_button_click_event(self):
        """다운로드 버튼 클릭 이벤트 핸들러"""
        log.debug("버튼 클릭 [Download]")
        self._all_buttons_disable()

        try:
            self._url = line_edit_url_input_instance.get_url()
            self._quality = combo_box_audio_quality_instance.get_selected_quality()
            self._save_path = directory_manager_instance.make_download_directory()
                
            plain_text_edit_log_display_instance.print_next_line("다운로드를 시작합니다.")
            plain_text_edit_log_display_instance.print_next_line("다운로드 준비 중...")

            # 이전 스레드가 실행 중이면 종료
            if self._download_thread and self._download_thread.isRunning():
                self._download_thread.terminate()
                self._download_thread.wait()

            self._download_thread = DownloadThread(self._url, self._quality, self._save_path)
            self._download_thread.progress_updated.connect(self._progress_updated)
            self._download_thread.download_completed.connect(self._download_completed)
            self._download_thread.error_occurred.connect(self._error_occurred)
            self._download_thread.start()
                
        except Exception as e:
            log.error(f"다운로드 중 오류 발생: {str(e)}")
            plain_text_edit_log_display_instance.print_next_line(f"오류 발생: {str(e)}")
            self._all_buttons_enable()
   
    def _download_completed(self, downloaded_file, title):
        """다운로드 완료 핸들러"""
        plain_text_edit_log_display_instance.print_next_line("다운로드 완료!")
        plain_text_edit_log_display_instance.print_next_line("MP3 변환을 시작합니다.")
        plain_text_edit_log_display_instance.print_next_line("MP3 변환 준비 중...")

        # 이전 스레드가 실행 중이면 종료            # 이전 스레드가 실행 중이면 종료
        if self._convert_thread and self._convert_thread.isRunning():
            self._convert_thread.terminate()
            self._convert_thread.wait()

        self._convert_thread = ConvertThread(downloaded_file, title, self._quality, self._save_path)
        self._convert_thread.progress_updated.connect(self._progress_updated)
        self._convert_thread.convert_completed.connect(self._convert_completed)
        self._convert_thread.error_occurred.connect(self._error_occurred)
        self._convert_thread.start()

    def _convert_completed(self, final_path):
        """MP3 변환 완료 핸들러"""
        plain_text_edit_log_display_instance.print_next_line("MP3 변환 완료!")
        plain_text_edit_log_display_instance.print_next_line("저장 경로: " + final_path)

    def _progress_updated(self, message):
        plain_text_edit_log_display_instance.print_current_line(message)

    def _error_occurred(self, message):
        log.error(f"오류 발생: {message}")
        plain_text_edit_log_display_instance.print_next_line(f"오류 발생: {message}")
        self._all_buttons_enable()

    def _all_buttons_disable(self):
        """모든 버튼을 비활성화합니다."""
        self.disable()
        combo_box_audio_quality_instance.disable()
        # 순환 참조를 피하기 위해 동적으로 import
        from controller.gui.PushButton_CheckURL import push_button_check_url_instance
        push_button_check_url_instance.disable()

    def _all_buttons_enable(self):
        """모든 버튼을 활성화합니다."""
        self.enable()
        combo_box_audio_quality_instance.enable()
        # 순환 참조를 피하기 위해 동적으로 import
        from controller.gui.PushButton_CheckURL import push_button_check_url_instance
        push_button_check_url_instance.enable()

# 싱글톤 인스턴스 생성
push_button_download_instance = PushButton_Download()