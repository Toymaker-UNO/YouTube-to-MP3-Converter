from PyQt5.QtWidgets import QLabel
from view.AbstractGUIItem import AbstractGUIItem

class LabelItem(AbstractGUIItem, QLabel):
    """QLabel을 상속받는 콘크리트 클래스"""
    
    def __init__(self, text: str = "", parent=None):
        """LabelItem 초기화
        
        Args:
            text (str): 라벨에 표시할 텍스트
            parent (QWidget, optional): 부모 위젯
        """
        super().__init__(parent)
        self.setText(text)
        
    def set_text(self, text: str) -> None:
        """라벨 텍스트 설정
        
        Args:
            text (str): 설정할 텍스트
        """
        self.setText(text)
        
    def get_text(self) -> str:
        """라벨 텍스트 반환
        
        Returns:
            str: 현재 라벨 텍스트
        """
        return self.text()
        
    def set_alignment(self, alignment: int) -> None:
        """텍스트 정렬 설정
        
        Args:
            alignment (int): 정렬 방식 (Qt.AlignLeft, Qt.AlignCenter 등)
        """
        self.setAlignment(alignment)
        
    def set_word_wrap(self, wrap: bool) -> None:
        """단어 줄바꿈 설정
        
        Args:
            wrap (bool): True면 단어 줄바꿈 활성화
        """
        self.setWordWrap(wrap) 