from PyQt5.QtWidgets import QPushButton
from view.AbstractGUIItem import AbstractGUIItem

class ButtonItem(AbstractGUIItem, QPushButton):
    """QPushButton을 상속받는 콘크리트 클래스"""
    
    def __init__(self, text: str = "", parent=None):
        """ButtonItem 초기화
        
        Args:
            text (str): 버튼에 표시할 텍스트
            parent (QWidget, optional): 부모 위젯
        """
        super().__init__(parent)
        self.setText(text)
        
    def set_text(self, text: str) -> None:
        """버튼 텍스트 설정
        
        Args:
            text (str): 설정할 텍스트
        """
        self.setText(text)
        
    def get_text(self) -> str:
        """버튼 텍스트 반환
        
        Returns:
            str: 현재 버튼 텍스트
        """
        return self.text()
        
    def set_icon(self, icon) -> None:
        """버튼 아이콘 설정
        
        Args:
            icon: 설정할 아이콘
        """
        self.setIcon(icon)
        
    def set_flat(self, flat: bool) -> None:
        """버튼 평면 스타일 설정
        
        Args:
            flat (bool): True면 평면 스타일 활성화
        """
        self.setFlat(flat)
        
    def set_checkable(self, checkable: bool) -> None:
        """버튼 체크 가능 여부 설정
        
        Args:
            checkable (bool): True면 체크 가능한 버튼으로 설정
        """
        self.setCheckable(checkable)
        
    def is_checked(self) -> bool:
        """버튼 체크 상태 반환
        
        Returns:
            bool: 체크 상태
        """
        return self.isChecked() 