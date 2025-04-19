from PyQt5.QtWidgets import QMainWindow
from view.AbstractGUIItem import AbstractGUIItem

class MainWindowItem(AbstractGUIItem, QMainWindow):
    """QMainWindow를 상속받는 콘크리트 클래스"""
    
    def __init__(self, parent=None):
        """MainWindowItem 초기화
        
        Args:
            parent (QWidget, optional): 부모 위젯
        """
        super().__init__(parent)
        
    def set_central_widget(self, widget) -> None:
        """중앙 위젯 설정
        
        Args:
            widget: 중앙에 배치할 위젯
        """
        self.setCentralWidget(widget)
        
    def set_menu_bar(self, menu_bar) -> None:
        """메뉴바 설정
        
        Args:
            menu_bar: 설정할 메뉴바
        """
        self.setMenuBar(menu_bar)
        
    def set_status_bar(self, status_bar) -> None:
        """상태바 설정
        
        Args:
            status_bar: 설정할 상태바
        """
        self.setStatusBar(status_bar)
        
    def set_window_title(self, title: str) -> None:
        """창 제목 설정
        
        Args:
            title (str): 설정할 제목
        """
        self.setWindowTitle(title)
        
    def set_window_icon(self, icon) -> None:
        """창 아이콘 설정
        
        Args:
            icon: 설정할 아이콘
        """
        self.setWindowIcon(icon)
        
    def add_tool_bar(self, tool_bar) -> None:
        """툴바 추가
        
        Args:
            tool_bar: 추가할 툴바
        """
        self.addToolBar(tool_bar)
        
    def set_dock_widget(self, area, dock_widget) -> None:
        """도크 위젯 설정
        
        Args:
            area: 도크 영역 (Qt.LeftDockWidgetArea 등)
            dock_widget: 설정할 도크 위젯
        """
        self.addDockWidget(area, dock_widget)
        
    def set_unified_title_and_tool_bar_on_mac(self, set: bool) -> None:
        """맥OS에서 제목과 툴바 통합 설정
        
        Args:
            set (bool): True면 통합 활성화
        """
        self.setUnifiedTitleAndToolBarOnMac(set) 