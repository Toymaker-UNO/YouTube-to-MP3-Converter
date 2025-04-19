from PyQt5.QtWidgets import QTextEdit
from view.AbstractGUIItem import AbstractGUIItem

class TextEditItem(AbstractGUIItem, QTextEdit):
    """QTextEdit을 상속받는 콘크리트 클래스"""
    
    def __init__(self, text: str = "", parent=None):
        """TextEditItem 초기화
        
        Args:
            text (str): 초기 텍스트
            parent (QWidget, optional): 부모 위젯
        """
        super().__init__(parent)
        self.setText(text)
        
    def set_text(self, text: str) -> None:
        """텍스트 설정
        
        Args:
            text (str): 설정할 텍스트
        """
        self.setText(text)
        
    def get_text(self) -> str:
        """텍스트 반환
        
        Returns:
            str: 현재 텍스트
        """
        return self.toPlainText()
        
    def set_html(self, html: str) -> None:
        """HTML 텍스트 설정
        
        Args:
            html (str): 설정할 HTML 텍스트
        """
        self.setHtml(html)
        
    def get_html(self) -> str:
        """HTML 텍스트 반환
        
        Returns:
            str: 현재 HTML 텍스트
        """
        return self.toHtml()
        
    def set_read_only(self, read_only: bool) -> None:
        """읽기 전용 모드 설정
        
        Args:
            read_only (bool): True면 읽기 전용 모드 활성화
        """
        self.setReadOnly(read_only)
        
    def set_line_wrap_mode(self, mode) -> None:
        """줄바꿈 모드 설정
        
        Args:
            mode: 줄바꿈 모드
        """
        self.setLineWrapMode(mode)
        
    def set_word_wrap_mode(self, mode) -> None:
        """단어 줄바꿈 모드 설정
        
        Args:
            mode: 단어 줄바꿈 모드
        """
        self.setWordWrapMode(mode)
        
    def clear(self) -> None:
        """텍스트 지우기"""
        self.clear()
        
    def append(self, text: str) -> None:
        """텍스트 추가
        
        Args:
            text (str): 추가할 텍스트
        """
        self.append(text)
        
    def insert_plain_text(self, text: str) -> None:
        """일반 텍스트 삽입
        
        Args:
            text (str): 삽입할 텍스트
        """
        self.insertPlainText(text)
        
    def insert_html(self, html: str) -> None:
        """HTML 텍스트 삽입
        
        Args:
            html (str): 삽입할 HTML 텍스트
        """
        self.insertHtml(html) 