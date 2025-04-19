from model.Configuration import Configuration
from view.MainWindowItem import MainWindowItem
from view.LabelItem import LabelItem
from view.ButtonItem import ButtonItem
from view.LineEditItem import LineEditItem
from view.ComboBoxItem import ComboBoxItem
from view.ProgressBarItem import ProgressBarItem
from view.CheckBoxItem import CheckBoxItem
from view.TextEditItem import TextEditItem

class GUIBuilder:
    """GUI Item을 생성하고 설정을 적용하는 클래스"""
    
    def __init__(self):
        """GUIBuilder 초기화"""
        self.config = Configuration()
        
    def create_main_window(self) -> MainWindowItem:
        """메인 윈도우 생성
        
        Returns:
            MainWindowItem: 생성된 메인 윈도우
        """
        window = MainWindowItem()
        window_config = self.config.get('main_window', {})
        
        # 기본 설정 적용
        window.set_window_title(window_config.get('title', 'YouTube to MP3 Converter'))
        
        # 크기 설정
        size = window_config.get('size', {})
        window.resize(size.get('width', 800), size.get('height', 600))
        
        # 위치 설정
        position = window_config.get('position', {})
        window.move(position.get('x', 100), position.get('y', 100))
        
        # 스타일 설정
        style = window_config.get('style', {})
        window.setStyleSheet(self._create_style_sheet('QMainWindow', style))
        
        return window
        
    def _create_style_sheet(self, widget_type: str, style: dict) -> str:
        """스타일시트 생성
        
        Args:
            widget_type (str): 위젯 타입
            style (dict): 스타일 설정
            
        Returns:
            str: 생성된 스타일시트
        """
        return f"""
            {widget_type} {{
                background-color: {style.get('background_color', 'transparent')};
                color: {style.get('text_color', '#000000')};
                border: {style.get('border_width', '1px')} solid {style.get('border_color', '#000000')};
                border-radius: {style.get('border_radius', '0px')};
                padding: {style.get('padding', '0px')};
                margin: {style.get('margin', '0px')};
            }}
            {widget_type}:hover {{
                background-color: {style.get('hover_background_color', 'transparent')};
                color: {style.get('hover_text_color', '#000000')};
                border-color: {style.get('hover_border_color', '#000000')};
            }}
            {widget_type}:focus {{
                background-color: {style.get('focus_background_color', 'transparent')};
                color: {style.get('focus_text_color', '#000000')};
                border-color: {style.get('focus_border_color', '#000000')};
            }}
        """ 