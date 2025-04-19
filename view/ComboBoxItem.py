from PyQt5.QtWidgets import QComboBox
from view.AbstractGUIItem import AbstractGUIItem

class ComboBoxItem(AbstractGUIItem, QComboBox):
    """QComboBox를 상속받는 콘크리트 클래스"""
    
    def __init__(self, parent=None):
        """ComboBoxItem 초기화
        
        Args:
            parent (QWidget, optional): 부모 위젯
        """
        super().__init__(parent)
        
    def add_item(self, text: str, user_data=None) -> None:
        """항목 추가
        
        Args:
            text (str): 표시할 텍스트
            user_data: 사용자 데이터
        """
        self.addItem(text, user_data)
        
    def add_items(self, texts: list) -> None:
        """여러 항목 추가
        
        Args:
            texts (list): 추가할 텍스트 리스트
        """
        self.addItems(texts)
        
    def clear(self) -> None:
        """모든 항목 제거"""
        self.clear()
        
    def current_text(self) -> str:
        """현재 선택된 항목의 텍스트 반환
        
        Returns:
            str: 현재 선택된 항목의 텍스트
        """
        return self.currentText()
        
    def current_index(self) -> int:
        """현재 선택된 항목의 인덱스 반환
        
        Returns:
            int: 현재 선택된 항목의 인덱스
        """
        return self.currentIndex()
        
    def set_current_index(self, index: int) -> None:
        """현재 선택된 항목 설정
        
        Args:
            index (int): 선택할 항목의 인덱스
        """
        self.setCurrentIndex(index)
        
    def set_editable(self, editable: bool) -> None:
        """편집 가능 여부 설정
        
        Args:
            editable (bool): True면 편집 가능 모드 활성화
        """
        self.setEditable(editable)
        
    def item_text(self, index: int) -> str:
        """지정된 인덱스의 항목 텍스트 반환
        
        Args:
            index (int): 항목 인덱스
            
        Returns:
            str: 항목 텍스트
        """
        return self.itemText(index)
        
    def item_data(self, index: int):
        """지정된 인덱스의 사용자 데이터 반환
        
        Args:
            index (int): 항목 인덱스
            
        Returns:
            사용자 데이터
        """
        return self.itemData(index) 