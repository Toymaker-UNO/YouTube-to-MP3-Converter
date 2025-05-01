from PyQt5.QtWidgets import QMainWindow, QPlainTextEdit
from PyQt5.QtCore import Qt
from datetime import datetime
import threading

TIME_STRING_LENGTH = 24
LOG_DISPLAY_WINDOW_WIDTH = 88

class UICLogDisplay:
    """로그 디스플레이를 관리하는 컨트롤러 클래스"""
    
    _instance = None
    _lock = threading.Lock()  # 클래스 레벨의 Lock
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:  # Double-checked locking
                    cls._instance = super(UICLogDisplay, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """UICLogDisplay 초기화"""
        self._window = None
        self._log_display = None
        self._contents = []  # 문자열을 저장하는 리스트
        
    def initialize(self, window: QMainWindow):
        """UICLogDisplay를 초기화합니다.
        
        Args:
            window (QMainWindow): 메인 윈도우 객체
        """
        with self._lock:
            self._window = window
            self._log_display = self._window.findChild(QPlainTextEdit, "log_display")
            if self._log_display:
                # 가로 스크롤바가 생성되지 않도록 자동 줄바꿈 설정
                self._log_display.setLineWrapMode(QPlainTextEdit.WidgetWidth)

    def print_next_line(self, message: str):
        """다음 라인에 로그 메시지를 출력합니다.
        
        Args:
            message (str): 출력할 메시지
        """
        with self._lock:
            if self._log_display:
                log_message = self._get_current_time() + " " + message
                self._contents.append(log_message)
                self._print(log_message)

    def create_progress_bar(self, percentage, progress_length=20):
        """
        텍스트 기반 프로그레스 바를 생성합니다.
        
        Args:
            percentage (int): 진행률 (0-100)
            progress_length (int): 프로그레스 바의 전체 길이 (기본값: 20)
            current_speed (str): 현재 다운로드 속도 (기본값: "0.0 MB/s")
        
        Returns:
            str: 포맷된 프로그레스 바 문자열
        """
        filled = int((percentage * (progress_length - 1)) / 100)  # 최대 progress_length-1칸
        progress_bar = '=' * filled + '>' + ' ' * (progress_length - filled - 1)
        return f"[{progress_bar}] {percentage:3}%"

    def print_current_line(self, message: str):
        """현재 라인에 로그 메시지를 출력합니다.
        
        Args:
            message (str): 출력할 메시지
        """
        with self._lock:
            if self._log_display:
                log_message = self._get_current_time() + " " + message
                self._contents.pop()
                self._contents.append(log_message)
                for i in range(len(self._contents)):
                    if i == 0 :
                        self._print(self._contents[i],True)
                    else:
                        self._print(self._contents[i])

    def _print(self, log_message: str, set_flag: bool = False):
        log_message_list = self._string_devider(log_message, LOG_DISPLAY_WINDOW_WIDTH, LOG_DISPLAY_WINDOW_WIDTH - TIME_STRING_LENGTH, TIME_STRING_LENGTH)
        i = 0
        for log_message in log_message_list:
            if i == 0 and set_flag == True:
                self._log_display.setPlainText(log_message)
            else:
                self._log_display.appendPlainText(log_message)
            i += 1
            self._scroll_to_bottom()
            
    def _scroll_to_bottom(self):
        """로그 디스플레이를 최하단으로 스크롤합니다."""
        if self._log_display:
            v_scrollbar = self._log_display.verticalScrollBar()
            v_scrollbar.setValue(v_scrollbar.maximum()) 

    def _get_current_time(self) -> str:
        """현재 시간을 [YY.MM.DD-HH:MM:SS.MSEC] 형식으로 반환합니다.
        
        Returns:
            str: 포맷팅된 현재 시간 문자열
        """
        now = datetime.now()
        return now.strftime("[%y.%m.%d-%H:%M:%S.%f")[:-3] + "]"

    def _string_devider(self, message: str, first_length: int, second_length: int, empty_length: int) -> list[str]:
        """긴 문자열을 여러 부분으로 나눕니다. 
           첫번째 문자열은 first_length 만큼, 
           두번째 문자열 부터 마지막 문자열 까지는 second_length 만큼 나눕니다.
    
        Args:
           message (str): 나눌 문자열
           first_length (int): 첫 번째 부분의 길이
           second_length (int): 두 번째 부터 마지막 문자열까지 부분의 길이
        
        Returns:
            list[str]: 나눠진 문자열들의 리스트
        """
        if not message:
            return []
        
        result = []
        # 첫 번째 부분
        if len(message) > first_length:
            result.append(message[:first_length])
            remaining = message[first_length:]
        else:
            result.append(message)
            return result
        
        # 나머지 부분
        while remaining:
            if len(remaining) > second_length:
                result.append(" "*empty_length + remaining[:second_length])
                remaining = remaining[second_length:]
            else:
                result.append(" "*empty_length + remaining)
                break
            
        return result


# 싱글톤 인스턴스 생성
uic_log_display_instance = UICLogDisplay()