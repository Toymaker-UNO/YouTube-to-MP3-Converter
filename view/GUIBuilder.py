from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve, QTimer
from model.Configuration import Configuration

class GUIBuilder:
    """설정 파일을 읽어 메인 윈도우를 생성하는 클래스"""
    
    def __init__(self):
        """GUIBuilder 초기화"""
        self.config = Configuration()
        
    def create_main_window(self) -> QMainWindow:
        """메인 윈도우 생성
        
        Returns:
            QMainWindow: 생성된 메인 윈도우
            
        Raises:
            KeyError: 필수 설정이 누락된 경우
            ValueError: 설정 값의 타입이 맞지 않는 경우
        """
        window = QMainWindow()
        window_config = self.config.get('gui', 'main_window')
        
        # 기본 설정 적용
        window.setWindowTitle(window_config['title'])
        
        # 아이콘 설정
        icon_path = window_config['icon_path']
        if icon_path:
            window.setWindowIcon(QIcon(icon_path))
        
        # 크기 설정
        size = window_config['size']
        window.resize(size['width'], size['height'])
        
        # 위치 설정
        position = window_config['position']
        window.move(position['x'], position['y'])
        
        # 스타일 설정
        style = window_config['style']
        window.setStyleSheet(self._create_style_sheet('QMainWindow', style))
        
        # 애니메이션 설정
        animation = window_config['animation']
        if animation['enabled']:
            # 초기 투명도 설정
            window.setWindowOpacity(animation['initial_opacity'])
            # 윈도우가 표시된 후 애니메이션 시작
            QTimer.singleShot(animation['start_delay'], lambda: self._setup_animations(window, animation))
        
        return window
        
    def _setup_animations(self, window: QMainWindow, animation_config: dict) -> None:
        """윈도우 애니메이션 설정
        
        Args:
            window (QMainWindow): 애니메이션을 적용할 윈도우
            animation_config (dict): 애니메이션 설정
        """
        # 페이드 인 애니메이션
        fade_animation = QPropertyAnimation(window, b"windowOpacity")
        fade_animation.setDuration(animation_config['duration'])
        fade_animation.setStartValue(animation_config['initial_opacity'])
        fade_animation.setEndValue(1.0)
        
        # 이징 커브 설정
        easing_type = getattr(QEasingCurve, animation_config['easing'], QEasingCurve.OutCubic)
        fade_animation.setEasingCurve(easing_type)
        
        # 애니메이션 시작
        fade_animation.start()
        
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
                background-color: {style['background_color']};
                color: {style['text_color']};
                border: {style['border_width']} solid {style['border_color']};
                border-radius: {style['border_radius']};
                padding: {style['padding']};
                margin: {style['margin']};
            }}
        """ 