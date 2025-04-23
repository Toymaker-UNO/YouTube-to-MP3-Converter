from PyQt5.QtWidgets import QMainWindow, QPushButton, QLineEdit, QApplication, QPlainTextEdit, QComboBox
from PyQt5.QtGui import QClipboard
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from controller.Converter import Converter
import os
from datetime import datetime


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


class DownloadThread(QThread):
    """다운로드와 변환 작업을 처리하는 스레드"""
    progress_updated = pyqtSignal(str)  # 진행 상황 메시지
    speed_updated = pyqtSignal(str)     # 다운로드 속도
    download_completed = pyqtSignal(str)  # 완료 메시지
    error_occurred = pyqtSignal(str)    # 오류 메시지
    
    def __init__(self, url, quality, converter):
        super().__init__()
        self.url = url
        self.quality = quality
        self.converter = converter
        self.current_speed = "0.0 MB/s"
        
    def run(self):
        try:
            # 진행 상황 콜백 함수
            def on_progress(percentage):
                # 프로그레스 바 생성 (20칸)
                progress_length = 20
                filled = int((percentage * (progress_length - 1)) / 100)  # 최대 19칸
                progress_bar = '=' * filled + '>' + ' ' * (progress_length - filled - 1)
                # 퍼센트와 속도 표시 위치 고정 (속도는 최대 12자리까지 허용)
                self.progress_updated.emit(f"[{progress_bar}] {percentage:3}%  ({self.current_speed:>12})")
                
            def on_speed(speed):
                self.current_speed = speed
                
            # 다운로드 시작 메시지
            self.progress_updated.emit("다운로드를 시작합니다...")
            
            # 다운로드
            downloaded_file, title = self.converter.download_video(
                url=self.url,
                quality=self.quality,
                progress_callback=on_progress,
                speed_callback=on_speed
            )
            
            # MP3 변환
            self.progress_updated.emit("MP3 변환을 시작합니다...")
            final_path = self.converter.convert_to_mp3(
                input_file=downloaded_file,
                title=title,
                quality=self.quality
            )
            
            self.download_completed.emit(f"변환이 완료되었습니다!\n저장 경로: {final_path}")
            
        except Exception as e:
            self.error_occurred.emit(f"오류가 발생했습니다: {str(e)}")


class Controller:
    """컨트롤러 클래스의 싱글톤 구현"""
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(Controller, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def _get_timestamp(self):
        """현재 시간을 [HH:MM:SS] 형식으로 반환합니다."""
        return datetime.now().strftime("[%H:%M:%S]")

    def _update_log(self, message):
        """로그 디스플레이에 시간이 포함된 메시지를 출력합니다."""
        log_display = self._window.findChild(QPlainTextEdit, "log_display")
        if log_display:
            timestamp = self._get_timestamp()
            
            # 프로그레스바 메시지인 경우
            if message.startswith("[") and ">" in message:
                current_text = log_display.toPlainText()
                if current_text:
                    lines = current_text.split('\n')
                    # 마지막 줄이 프로그레스바인 경우 업데이트
                    if lines[-1].startswith("["):
                        # 기존 타임스탬프 유지
                        old_timestamp = lines[-1].split(']')[0] + ']'
                        log_display.setPlainText('\n'.join(lines[:-1]))  # 마지막 줄 제거
                        log_display.appendPlainText(f"{old_timestamp} 다운로드: {message}")
                        return
                    
            # 일반 메시지인 경우 새 줄에 추가
            log_display.appendPlainText(f"{timestamp} {message}")
            
            # 스크롤을 가장 아래로 내림
            scrollbar = log_display.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())

    def run(self, window: QMainWindow):
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
            self._download_thread = None
            self._setup_event_handlers()
            self._initialized = True
            
            # 로그 디스플레이 초기화
            self._initialize_log_display()

    def _initialize_log_display(self):
        """로그 디스플레이를 초기화하고 초기 메시지를 출력합니다."""
        log_display = self._window.findChild(QPlainTextEdit, "log_display")
        if log_display:
            # 가로 스크롤바의 rangeChanged 시그널 연결
            h_scrollbar = log_display.horizontalScrollBar()
            h_scrollbar.rangeChanged.connect(self._handle_horizontal_scroll_range)
        self._update_log("URL입력을 기다리고 있습니다.")

    def _setup_event_handlers(self):
        """이벤트 핸들러를 설정합니다."""
        # Paste 버튼 클릭 이벤트 연결
        paste_button = self._window.findChild(QPushButton, "paste_button")
        if paste_button:
            paste_button.clicked.connect(self._handle_paste_button_click)
        else:
            print("Warning: paste_button not found")

        # Download 버튼 클릭 이벤트 연결
        download_button = self._window.findChild(QPushButton, "download_button")
        if download_button:
            download_button.clicked.connect(self._handle_download_button_click)
        else:
            print("Warning: download_button not found")

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
        # quality_combo와 download_button 비활성화
        quality_combo = self._window.findChild(QComboBox, "quality_combo", Qt.FindChildrenRecursively)
        download_button = self._window.findChild(QPushButton, "download_button")
        
        if quality_combo:
            quality_combo.setEnabled(False)
        if download_button:
            download_button.setEnabled(False)
            
        # 타이머 재시작
        self._url_check_timer.stop()
        self._url_check_timer.start(URL_CHECK_DELAY_MS)  # 설정된 지연 시간 후에 검사

    def _handle_paste_button_click(self):
        """클립보드의 내용을 URL 입력창에 붙여넣고 검사합니다."""
        url_input = self._window.findChild(QLineEdit, "url_input")
        if url_input:
            # textChanged 시그널을 일시적으로 차단
            url_input.blockSignals(True)
            clipboard_text = self._clipboard.text()
            url_input.setText(clipboard_text)
            url_input.blockSignals(False)
            
            # quality_combo와 download_button 비활성화
            quality_combo = self._window.findChild(QComboBox, "quality_combo", Qt.FindChildrenRecursively)
            download_button = self._window.findChild(QPushButton, "download_button")
            
            if quality_combo:
                quality_combo.setEnabled(False)
            if download_button:
                download_button.setEnabled(False)
                
            # 붙여넣기 후 즉시 검사
            self._check_url(clipboard_text)
        else:
            print("Warning: url_input not found")

    def _handle_download_button_click(self):
        """다운로드 버튼 클릭 이벤트 핸들러"""
        try:
            # URL 입력값 가져오기
            url_input = self._window.findChild(QLineEdit, "url_input")
            if not url_input:
                raise Exception("URL 입력창을 찾을 수 없습니다.")
                
            url = url_input.text().strip()
            if not url:
                raise Exception("URL을 입력해주세요.")
                
            # 품질 설정 가져오기
            quality_combo = self._window.findChild(QComboBox, "quality_combo")
            if not quality_combo:
                raise Exception("품질 설정을 찾을 수 없습니다.")
                
            quality = quality_combo.currentText()
            
            # 이전 다운로드 스레드가 실행 중이면 중지
            if self._download_thread and self._download_thread.isRunning():
                self._download_thread.terminate()
                self._download_thread.wait()
                
            # 다운로드 버튼 비활성화
            download_button = self._window.findChild(QPushButton, "download_button")
            if download_button:
                download_button.setEnabled(False)
                
            # 새 다운로드 스레드 생성 및 시작
            self._download_thread = DownloadThread(url, quality, self._converter)
            self._download_thread.progress_updated.connect(self._update_log)
            self._download_thread.speed_updated.connect(self._update_log)
            self._download_thread.download_completed.connect(self._handle_download_completed)
            self._download_thread.error_occurred.connect(self._handle_download_error)
            self._download_thread.start()
                
        except Exception as e:
            self._update_log(f"오류가 발생했습니다: {str(e)}")
            
    def _handle_download_completed(self, message):
        """다운로드 완료 이벤트 핸들러"""
        self._update_log(message)
        # 다운로드 버튼 활성화
        download_button = self._window.findChild(QPushButton, "download_button")
        if download_button:
            download_button.setEnabled(True)
            
    def _handle_download_error(self, message):
        """다운로드 오류 이벤트 핸들러"""
        self._update_log(message)
        # 다운로드 버튼 활성화
        download_button = self._window.findChild(QPushButton, "download_button")
        if download_button:
            download_button.setEnabled(True)

    def _check_url(self, text):
        """URL을 검사하고 결과에 따라 UI를 업데이트합니다."""
        # 이전 스레드가 실행 중이면 중지
        if self._url_check_thread and self._url_check_thread.isRunning():
            self._url_check_thread.terminate()
            self._url_check_thread.wait()
            
        # 로그 디스플레이에 검사 중 메시지 표시
        self._update_log("URL을 검사하는 중...")
            
        # 새 스레드 생성 및 시작
        self._url_check_thread = URLCheckThread(text, self._converter)
        self._url_check_thread.result_ready.connect(self._handle_url_check_result)
        self._url_check_thread.start()

    def _handle_url_check_result(self, message, success):
        """URL 검사 결과를 처리합니다."""
        log_display = self._window.findChild(QPlainTextEdit, "log_display")
        quality_combo = self._window.findChild(QComboBox, "quality_combo")
        download_button = self._window.findChild(QPushButton, "download_button")
        
        if log_display:
            self._update_log(message)
            
        if quality_combo:
            quality_combo.setEnabled(success)
            
        if download_button:
            download_button.setEnabled(success)

    def _handle_horizontal_scroll_range(self, min_val, max_val):
        """가로 스크롤바의 range 변화 이벤트 핸들러"""
        log_display = self._window.findChild(QPlainTextEdit, "log_display")
        if log_display:
            # max_val이 0보다 크면 가로 스크롤바가 필요하다는 의미
            if max_val > 0:
                # 다음 이벤트 루프에서 실행되도록 QTimer 사용
                QTimer.singleShot(0, lambda: self._scroll_to_bottom(log_display))

    def _scroll_to_bottom(self, log_display):
        """세로 스크롤바를 가장 아래로 내림"""
        v_scrollbar = log_display.verticalScrollBar()
        if v_scrollbar.isVisible():
            v_scrollbar.setValue(v_scrollbar.maximum())

    def __del__(self):
        """소멸자"""
        pass


# 싱글톤 인스턴스 생성
controller_instance = Controller() 