from PyQt5.QtWidgets import QProgressBar
from view.AbstractGUIItem import AbstractGUIItem

class ProgressBarItem(AbstractGUIItem, QProgressBar):
    """QProgressBar를 상속받는 콘크리트 클래스"""
    
    def __init__(self, parent=None):
        """ProgressBarItem 초기화
        
        Args:
            parent (QWidget, optional): 부모 위젯
        """
        super().__init__(parent)
        
    def set_value(self, value: int) -> None:
        """진행률 값 설정
        
        Args:
            value (int): 설정할 값 (0-100)
        """
        self.setValue(value)
        
    def get_value(self) -> int:
        """현재 진행률 값 반환
        
        Returns:
            int: 현재 진행률 값
        """
        return self.value()
        
    def set_minimum(self, minimum: int) -> None:
        """최소값 설정
        
        Args:
            minimum (int): 최소값
        """
        self.setMinimum(minimum)
        
    def set_maximum(self, maximum: int) -> None:
        """최대값 설정
        
        Args:
            maximum (int): 최대값
        """
        self.setMaximum(maximum)
        
    def set_range(self, minimum: int, maximum: int) -> None:
        """값 범위 설정
        
        Args:
            minimum (int): 최소값
            maximum (int): 최대값
        """
        self.setRange(minimum, maximum)
        
    def set_format(self, format_str: str) -> None:
        """진행률 표시 형식 설정
        
        Args:
            format_str (str): 형식 문자열
        """
        self.setFormat(format_str)
        
    def reset(self) -> None:
        """진행률 초기화"""
        self.reset()
        
    def set_text_visible(self, visible: bool) -> None:
        """텍스트 표시 여부 설정
        
        Args:
            visible (bool): True면 텍스트 표시
        """
        self.setTextVisible(visible) 