from PyQt5.QtWidgets import QLineEdit
from view.AbstractGUIItem import AbstractGUIItem

class LineEditItem(AbstractGUIItem, QLineEdit):
    """QLineEdit을 상속받는 콘크리트 클래스"""
    
    def __init__(self, text: str = "", parent=None):
        """LineEditItem 초기화
        
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
        return self.text()
        
    def set_placeholder(self, text: str) -> None:
        """플레이스홀더 텍스트 설정
        
        Args:
            text (str): 설정할 플레이스홀더 텍스트
        """
        self.setPlaceholderText(text)
        
    def set_max_length(self, length: int) -> None:
        """최대 입력 길이 설정
        
        Args:
            length (int): 최대 입력 길이
        """
        self.setMaxLength(length)
        
    def set_read_only(self, read_only: bool) -> None:
        """읽기 전용 모드 설정
        
        Args:
            read_only (bool): True면 읽기 전용 모드 활성화
        """
        self.setReadOnly(read_only)
        
    def clear(self) -> None:
        """텍스트 지우기"""
        self.clear() 