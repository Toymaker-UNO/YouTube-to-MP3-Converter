from PyQt5.QtWidgets import QMainWindow, QLabel, QWidget
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
        width = self._parse_pixel_value(size['width'])
        height = self._parse_pixel_value(size['height'])
        window.resize(width, height)
        
        # 윈도우 크기 고정 설정
        if size.get('fixed', False):
            window.setFixedSize(width, height)
        
        # 위치 설정
        position = window_config['position']
        x = self._parse_pixel_value(position['x'])
        y = self._parse_pixel_value(position['y'])
        window.move(x, y)
        
        # 중앙 위젯 생성
        central_widget = QWidget()
        window.setCentralWidget(central_widget)
        
        # 라벨 생성 및 배치
        labels = self.config.get('gui', 'labels')
        for label_config in labels:
            label = self._create_label(label_config)
            position = label_config['position']
            x = self._parse_pixel_value(position['x'])
            y = self._parse_pixel_value(position['y'])
            label.move(x, y)
            label.setParent(central_widget)  # 라벨을 central_widget의 자식으로 설정
        
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
        
    def _parse_pixel_value(self, value: str) -> int:
        """픽셀 값을 파싱합니다.
        
        Args:
            value (str): 픽셀 값 (예: "800px")
            
        Returns:
            int: 파싱된 픽셀 값
            
        Raises:
            ValueError: 픽셀 값이 유효하지 않은 경우
        """
        if isinstance(value, int):
            return value
            
        if not isinstance(value, str):
            raise ValueError(f"유효하지 않은 픽셀 값: {value}")
            
        if value.endswith('px'):
            return int(value[:-2])
        else:
            raise ValueError(f"유효하지 않은 픽셀 값: {value}")
        
    def _create_label(self, config: dict) -> QLabel:
        """라벨 위젯을 생성합니다.
        
        Args:
            config (dict): 라벨 설정
            
        Returns:
            QLabel: 생성된 라벨 위젯
        """
        label = QLabel(config['text'])
        
        # 스타일 설정
        style = config['style']
        label.setStyleSheet(self._create_label_style_sheet(style))
        
        return label
        
    def _create_label_style_sheet(self, style: dict) -> str:
        """라벨 스타일시트를 생성합니다.
        
        Args:
            style (dict): 스타일 설정
            
        Returns:
            str: 생성된 스타일시트
        """
        return f"""
            QLabel {{
                color: {style['color']};
                font-size: {style['font_size']};
                font-family: {style['font_family']};
                font-weight: {style['font_weight']};
                background-color: {style['background_color']};
                border: {style['border']['width']} solid {style['border']['color']};
                border-radius: {style['border']['radius']};
                padding-top: {style['padding']['top']};
                padding-right: {style['padding']['right']};
                padding-bottom: {style['padding']['bottom']};
                padding-left: {style['padding']['left']};
            }}
        """
        
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