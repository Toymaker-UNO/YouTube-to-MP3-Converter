import re
from PyQt5.QtWidgets import QPlainTextEdit, QApplication, QLineEdit, QPushButton, QMainWindow
from PyQt5.QtCore import QObject, pyqtSignal, QThread
import yt_dlp
from view.GUIBuilder import GUIBuilder
from model.Log import Log

log = Log()

class TitleExtractorThread(QThread):
    """YouTube 동영상 제목을 추출하는 스레드"""
    
    title_extracted = pyqtSignal(str)  # 제목 추출 성공 시
    error_occurred = pyqtSignal(str)   # 에러 발생 시
    
    def __init__(self, url: str):
        super().__init__()
        self.url = url
        self._stop = False
        log.info(f"TitleExtractorThread 초기화: URL={url}")
        
    def stop(self):
        """스레드를 안전하게 중지합니다."""
        self._stop = True
        self.terminate()
        self.wait()
        
    def run(self):
        try:
            log.info("제목 추출 시작")
            if not self.url:
                log.warning("URL이 비어있음")
                self.error_occurred.emit("URL을 입력해주세요.")
                return
                
            if not self.is_valid_url(self.url):
                log.warning(f"유효하지 않은 URL: {self.url}")
                self.error_occurred.emit("올바르지 않은 URL입니다.")
                return
                
            log.info(f"URL 검증 완료: {self.url}")
            
            # yt-dlp 옵션 설정
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
                'noplaylist': True,
                'ignoreerrors': False,
                'verbose': False,
                'force_generic_extractor': False,
                'socket_timeout': 10,  # 10초 타임아웃
                'extractor_retries': 3  # 3번 재시도
            }
            
            log.info("yt-dlp 옵션 설정 완료")
            
            # 제목 추출
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                log.info("동영상 정보 추출 시작")
                info = ydl.extract_info(self.url, download=False)
                
                if self._stop:
                    log.info("스레드 중지 요청됨")
                    return
                    
                if info is None:
                    log.error("동영상 정보 추출 실패")
                    self.error_occurred.emit("동영상 정보를 가져올 수 없습니다.")
                    return
                    
                log.info(f"동영상 정보 추출 완료: {info.keys()}")
                
                if 'entries' in info:  # 플레이리스트인 경우
                    log.warning("플레이리스트 URL 감지")
                    self.error_occurred.emit("플레이리스트 URL은 지원하지 않습니다.")
                    return
                    
                if 'title' not in info:
                    log.error("제목 정보 없음")
                    self.error_occurred.emit("제목 정보가 없습니다.")
                    return
                    
                title = info['title']
                log.info(f"제목 추출 성공: {title}")
                self.title_extracted.emit(f"제목: {title}")
            
        except Exception as e:
            log.error(f"제목 추출 중 오류 발생: {str(e)}")
            log.error(f"예외 유형: {type(e).__name__}")
            self.error_occurred.emit(f"제목 추출 중 오류 발생: {str(e)}")
            
    def is_valid_url(self, url: str) -> bool:
        """YouTube URL이 유효한지 검증합니다."""
        youtube_pattern = r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
        is_valid = bool(re.match(youtube_pattern, url))
        log.info(f"URL 검증 결과: {url} -> {'유효함' if is_valid else '유효하지 않음'}")
        if is_valid:
            self.title_extracted.emit("올바른 URL 입니다")
        return is_valid

class YouTubeController(QObject):
    """YouTube URL 처리와 제목 추출을 담당하는 컨트롤러"""
    
    def __init__(self):
        """YouTubeController 초기화"""
        super().__init__()
        self.window = None
        self.log_display = None
        self.url_input = None
        self.paste_button = None
        self.title_extractor_thread = None
        
    def initialize(self, window: QMainWindow):
        """GUI를 초기화하고 윈도우를 표시합니다.
        
        Args:
            window (QMainWindow): 메인 윈도우
        """
        self.window = window
        
        # 중앙 위젯 가져오기
        central_widget = window.centralWidget()
        
        # 위젯 찾기
        self.log_display = central_widget.findChild(QPlainTextEdit, "log_display")
        self.url_input = central_widget.findChild(QLineEdit, "url_input")
        self.paste_button = central_widget.findChild(QPushButton, "paste_button")
        
        # 이벤트 연결
        self.url_input.textChanged.connect(self.on_url_changed)
        self.url_input.returnPressed.connect(self.on_url_entered)  # Enter 키 이벤트
        self.url_input.editingFinished.connect(self.on_url_editing_finished)  # 포커스 잃을 때
        self.paste_button.clicked.connect(self.paste_from_clipboard)
        
        # 초기 안내 메시지 표시
        if self.log_display:
            self.log_display.appendPlainText("Please enter a YouTube URL or click 'Paste from Clipboard' button.")
        
        # 윈도우 표시
        self.window.show()
        
    def on_url_changed(self, text: str):
        """URL 입력이 변경되었을 때 호출됩니다."""
        # 입력 중에는 아무것도 하지 않음
        pass
        
    def on_url_entered(self):
        """Enter 키가 눌렸을 때 호출됩니다."""
        self.validate_and_extract_title()
        
    def on_url_editing_finished(self):
        """URL 입력 필드에서 포커스를 잃을 때 호출됩니다."""
        self.validate_and_extract_title()
        
    def validate_and_extract_title(self):
        """URL을 검증하고 제목을 추출합니다."""
        url = self.url_input.text().strip()
        
        # 이전 스레드가 실행 중이면 중지
        if self.title_extractor_thread and self.title_extractor_thread.isRunning():
            self.title_extractor_thread.terminate()
            self.title_extractor_thread.wait()
            
        # 새로운 스레드 생성 및 시작
        self.title_extractor_thread = TitleExtractorThread(url)
        self.title_extractor_thread.title_extracted.connect(self.on_title_extracted)
        self.title_extractor_thread.error_occurred.connect(self.on_error)
        self.title_extractor_thread.start()
        
    def on_title_extracted(self, title: str):
        """제목이 추출되었을 때 호출됩니다."""
        if self.log_display:
            self.log_display.appendPlainText(title)
            
    def on_error(self, error_message: str):
        """오류가 발생했을 때 호출됩니다."""
        if self.log_display:
            self.log_display.appendPlainText(error_message)
            
    def paste_from_clipboard(self):
        """클립보드에서 URL을 붙여넣고 처리합니다."""
        try:
            clipboard = QApplication.clipboard()
            url = clipboard.text().strip()
            
            if url:
                self.url_input.setText(url)
                # 붙여넣기 후 바로 검증
                self.validate_and_extract_title()
            elif self.log_display:
                self.log_display.appendPlainText("클립보드에 URL이 없습니다.")
        except Exception as e:
            error_msg = f"클립보드 접근 중 오류 발생: {str(e)}"
            if self.log_display:
                self.log_display.appendPlainText(error_msg)

    def cleanup(self):
        """프로그램 종료 시 리소스를 정리합니다."""
        if self.title_extractor_thread and self.title_extractor_thread.isRunning():
            log.info("TitleExtractorThread 종료 중...")
            self.title_extractor_thread.stop()
            log.info("TitleExtractorThread 종료됨") 