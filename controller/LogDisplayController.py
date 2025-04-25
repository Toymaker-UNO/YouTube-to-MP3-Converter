from PyQt5.QtWidgets import QMainWindow, QPlainTextEdit
from PyQt5.QtCore import Qt
from datetime import datetime

class LogDisplayController:
    """로그 디스플레이를 관리하는 컨트롤러 클래스"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LogDisplayController, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """LogDisplayController 초기화"""
        self._window = None
        self._log_display = None
        
    def initialize(self, window: QMainWindow):
        """로그 디스플레이를 초기화합니다.
        
        Args:
            window (QMainWindow): 메인 윈도우 객체
        """
        self._window = window
        self._log_display = self._window.findChild(QPlainTextEdit, "log_display")
        if self._log_display:
            # 가로 스크롤바가 생성되지 않도록 자동 줄바꿈 설정
            self._log_display.setLineWrapMode(QPlainTextEdit.WidgetWidth)
            
    def print(self, message: str):
        """로그 메시지를 출력합니다.
        
        Args:
            message (str): 출력할 메시지
        """
        if self._log_display:
            current_time = self.get_current_time()
            self._log_display.appendPlainText(f"{current_time} {message}")
            self._scroll_to_bottom()
            
    def _scroll_to_bottom(self):
        """로그 디스플레이를 최하단으로 스크롤합니다."""
        if self._log_display:
            v_scrollbar = self._log_display.verticalScrollBar()
            v_scrollbar.setValue(v_scrollbar.maximum()) 

    def get_current_time(self) -> str:
        """현재 시간을 [YY.MM.DD-HH:MM:SS.MSEC] 형식으로 반환합니다.
        
        Returns:
            str: 포맷팅된 현재 시간 문자열
        """
        now = datetime.now()
        return now.strftime("[%y.%m.%d-%H:%M:%S.%f")[:-3] + "]"

# 싱글톤 인스턴스 생성
log_display_controller_instance = LogDisplayController()