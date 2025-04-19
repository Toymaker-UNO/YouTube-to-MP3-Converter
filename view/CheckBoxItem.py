from PyQt5.QtWidgets import QCheckBox
from view.AbstractGUIItem import AbstractGUIItem

class CheckBoxItem(AbstractGUIItem, QCheckBox):
    """QCheckBox를 상속받는 콘크리트 클래스"""
    
    def __init__(self, text: str = "", parent=None):
        """CheckBoxItem 초기화
        
        Args:
            text (str): 체크박스 텍스트
            parent (QWidget, optional): 부모 위젯
        """
        super().__init__(parent)
        self.setText(text)
        
    def set_text(self, text: str) -> None:
        """체크박스 텍스트 설정
        
        Args:
            text (str): 설정할 텍스트
        """
        self.setText(text)
        
    def get_text(self) -> str:
        """체크박스 텍스트 반환
        
        Returns:
            str: 현재 텍스트
        """
        return self.text()
        
    def is_checked(self) -> bool:
        """체크 상태 반환
        
        Returns:
            bool: 체크 상태
        """
        return self.isChecked()
        
    def set_checked(self, checked: bool) -> None:
        """체크 상태 설정
        
        Args:
            checked (bool): True면 체크 상태로 설정
        """
        self.setChecked(checked)
        
    def set_tristate(self, tristate: bool) -> None:
        """3가지 상태 지원 여부 설정
        
        Args:
            tristate (bool): True면 3가지 상태 지원
        """
        self.setTristate(tristate)
        
    def check_state(self) -> int:
        """체크 상태 반환 (3가지 상태 지원 시)
        
        Returns:
            int: 체크 상태 (Qt.Checked, Qt.Unchecked, Qt.PartiallyChecked)
        """
        return self.checkState()
        
    def set_check_state(self, state: int) -> None:
        """체크 상태 설정 (3가지 상태 지원 시)
        
        Args:
            state (int): 설정할 상태
        """
        self.setCheckState(state) 