from PyQt5.QtWidgets import QMainWindow, QLabel, QWidget, QLineEdit, QPushButton, QComboBox, QPlainTextEdit
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve, QTimer, Qt
from model.Configuration import configuration_instance

class GUIBuilder:
    """설정 파일을 읽어 메인 윈도우를 생성하는 클래스"""
    
    def __init__(self):
        """GUIBuilder 초기화"""
        
    def build(self) -> QMainWindow:
        """설정 파일을 읽어 메인 윈도우를 생성합니다.
        
        Returns:
            QMainWindow: 생성된 메인 윈도우
        """
        window = self._build_main_window()
        
        # 중앙 위젯 생성 및 설정
        central_widget = self._build_central_widget(window)
        
        # 라벨 생성 및 배치
        self._build_label(central_widget)
        
        # 라인 에딧 생성 및 배치
        self._build_line_edit(central_widget)
        
        # 푸시 버튼 생성 및 배치
        self._build_push_button(central_widget)
        
        # 콤보박스 생성 및 배치
        self._build_combo_boxes(central_widget)
        
        # QPlainTextEdit 생성 및 배치
        self._build_plain_text_edits(central_widget)
        
        return window
        
    def _build_central_widget(self, window: QMainWindow) -> QWidget:
        """메인 윈도우의 중앙 위젯을 생성하고 설정합니다.
        
        Args:
            window (QMainWindow): 중앙 위젯을 설정할 메인 윈도우
            
        Returns:
            QWidget: 생성된 중앙 위젯
        """
        central_widget = QWidget()
        window.setCentralWidget(central_widget)
        return central_widget
        
    def _build_main_window(self) -> QMainWindow:
        """메인 윈도우를 생성하고 설정합니다.
        
        Returns:
            QMainWindow: 생성된 메인 윈도우
        """
        window = QMainWindow()
        window_config = configuration_instance.get('gui', 'main_window')
        
        # 기본 설정 적용
        if 'customizing' in window_config and 'title' in window_config['customizing']:
            window.setWindowTitle(window_config['customizing']['title'])
        
        # 아이콘 설정
        if 'customizing' in window_config and 'icon_path' in window_config['customizing']:
            icon_path = window_config['customizing']['icon_path']
            if icon_path:
                window.setWindowIcon(QIcon(icon_path))
        
        # 크기 설정
        if 'position' in window_config:
            size = window_config['position']
            if 'width' in size and 'height' in size:
                width = self._parse_pixel_value(size['width'])
                height = self._parse_pixel_value(size['height'])
                window.resize(width, height)
                
                # 윈도우 크기 고정 설정
                if size.get('fixed_size', False):
                    window.setFixedSize(width, height)
        
        # 위치 설정
        if 'position' in window_config:
            position = window_config['position']
            if 'x' in position and 'y' in position:
                x = self._parse_pixel_value(position['x'])
                y = self._parse_pixel_value(position['y'])
                window.move(x, y)
        
        # 스타일 설정
        window.setStyleSheet(self._json_to_css(window_config['stylesheet']))
        
        # 애니메이션 설정
        if 'animation' in window_config:
            animation = window_config['animation']
            # 초기 투명도 설정 (애니메이션 활성화 여부와 관계없이 적용)
            initial_opacity = animation.get('initial_opacity', 1.0)
            window.setWindowOpacity(initial_opacity)
            
            if animation.get('enabled', False):
                # 윈도우가 표시된 후 애니메이션 시작
                QTimer.singleShot(animation.get('start_delay', 100), 
                                lambda: self._setup_animations(window, animation))
        
        return window
        
    def _build_label(self, parent: QWidget) -> None:
        """라벨을 생성하고 배치합니다.
        
        Args:
            parent (QWidget): 라벨의 부모 위젯
        """
        labels = configuration_instance.get('gui', 'labels')
        for label_config in labels:
            label = self._create_label(label_config)
            if 'position' in label_config:
                position = label_config['position']
                if 'x' in position and 'y' in position:
                    x = self._parse_pixel_value(position['x'])
                    y = self._parse_pixel_value(position['y'])
                    label.move(x, y)
            label.setParent(parent)
        
    def _build_line_edit(self, parent: QWidget) -> None:
        """라인 에딧을 생성하고 배치합니다.
        
        Args:
            parent (QWidget): 라인 에딧의 부모 위젯
        """
        line_edits = configuration_instance.get('gui', 'line_edits')
        for line_edit_config in line_edits:
            line_edit = self._create_line_edit(line_edit_config)
            if 'position' in line_edit_config:
                position = line_edit_config['position']
                if 'x' in position and 'y' in position:
                    x = self._parse_pixel_value(position['x'])
                    y = self._parse_pixel_value(position['y'])
                    line_edit.move(x, y)
                    
                # 크기 설정
                if 'width' in position and 'height' in position:
                    width = self._parse_pixel_value(position['width'])
                    height = self._parse_pixel_value(position['height'])
                    line_edit.resize(width, height)
                    
            line_edit.setParent(parent)
        
    def _build_push_button(self, parent: QWidget) -> None:
        """푸시 버튼을 생성하고 배치합니다.
        
        Args:
            parent (QWidget): 푸시 버튼의 부모 위젯
        """
        push_buttons = configuration_instance.get('gui', 'push_buttons')
        for button_config in push_buttons:
            button = self._create_push_button(button_config)
            if 'position' in button_config:
                position = button_config['position']
                if 'x' in position and 'y' in position:
                    x = self._parse_pixel_value(position['x'])
                    y = self._parse_pixel_value(position['y'])
                    button.move(x, y)
                    
                # 크기 설정
                if 'width' in position and 'height' in position:
                    width = self._parse_pixel_value(position['width'])
                    height = self._parse_pixel_value(position['height'])
                    button.resize(width, height)
                    
            button.setParent(parent)
        
    def _create_push_button(self, config: dict) -> QPushButton:
        """푸시 버튼 위젯을 생성합니다.
        
        Args:
            config (dict): 푸시 버튼 설정
            
        Returns:
            QPushButton: 생성된 푸시 버튼 위젯
        """
        button = QPushButton()
        
        # ID 설정
        if 'id' in config:
            button.setObjectName(config['id'])
        
        # 스타일 설정
        button.setStyleSheet(self._json_to_css(config['stylesheet']))
        
        # 커스터마이징 설정
        if 'customizing' in config:
            customizing = config['customizing']
            if 'text' in customizing:
                button.setText(customizing['text'])
            if 'icon_path' in customizing:
                button.setIcon(QIcon(customizing['icon_path']))
            if 'tooltip' in customizing:
                button.setToolTip(customizing['tooltip'])
            if 'enabled' in customizing:
                button.setEnabled(customizing['enabled'])
        
        return button
        
    def _create_line_edit(self, config: dict) -> QLineEdit:
        """라인 에딧 위젯을 생성합니다.
        
        Args:
            config (dict): 라인 에딧 설정
            
        Returns:
            QLineEdit: 생성된 라인 에딧 위젯
        """
        line_edit = QLineEdit()
        
        # ID 설정
        if 'id' in config:
            line_edit.setObjectName(config['id'])
        
        # 스타일 설정
        line_edit.setStyleSheet(self._json_to_css(config['stylesheet']))
        
        # 커스터마이징 설정
        if 'customizing' in config:
            customizing = config['customizing']
            if 'placeholder_text' in customizing:
                line_edit.setPlaceholderText(customizing['placeholder_text'])
            if 'max_length' in customizing:
                line_edit.setMaxLength(customizing['max_length'])
            if 'enabled' in customizing:
                line_edit.setEnabled(customizing['enabled'])
        
        return line_edit
        
    def _create_label(self, config: dict) -> QLabel:
        """라벨 위젯을 생성합니다.
        
        Args:
            config (dict): 라벨 설정
            
        Returns:
            QLabel: 생성된 라벨 위젯
        """
        label = QLabel(config['customizing']['text'])
        
        # 스타일 설정
        label.setStyleSheet(self._json_to_css(config['stylesheet']))
        
        return label
        
    def _json_to_css(self, stylesheet_dict: dict) -> str:
        """JSON 형식의 스타일시트를 CSS 텍스트로 변환합니다.
        
        Args:
            stylesheet_dict (dict): JSON 형식의 스타일시트
            
        Returns:
            str: CSS 형식의 스타일시트 텍스트
        """
        css_rules = []
        for selector, properties in stylesheet_dict.items():
            rule = f"{selector} {{"
            for prop_name, prop_value in properties.items():
                rule += f"\n    {prop_name}: {prop_value};"
            rule += "\n}"
            css_rules.append(rule)
        return "\n".join(css_rules)
        
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

    def _build_combo_boxes(self, parent: QWidget) -> None:
        """콤보박스 위젯들을 생성하고 배치합니다."""
        try:
            combo_boxes = configuration_instance.get('gui', 'combo_boxes')
            for combo_config in combo_boxes:
                combo = self._create_combo_box(combo_config)
                if combo:
                    combo.setParent(parent)
        except KeyError:
            return

    def _create_combo_box(self, combo_config: dict) -> QComboBox:
        """개별 콤보박스 위젯을 생성하고 설정합니다."""
        combo = QComboBox()
        
        # ID 설정
        if 'id' in combo_config:
            combo.setObjectName(combo_config['id'])
        
        # 위치 설정
        if 'position' in combo_config:
            pos = combo_config['position']
            combo.setGeometry(
                int(pos['x'].replace('px', '')),
                int(pos['y'].replace('px', '')),
                int(pos['width'].replace('px', '')),
                int(pos['height'].replace('px', ''))
            )

        # 스타일시트 적용
        if 'stylesheet' in combo_config:
            combo.setStyleSheet(self._json_to_css(combo_config['stylesheet']))

        # 커스터마이징 설정
        if 'customizing' in combo_config:
            custom = combo_config['customizing']
            if 'items' in custom:
                combo.addItems(custom['items'])
            if 'default_index' in custom:
                combo.setCurrentIndex(custom['default_index'])
            if 'enabled' in custom:
                combo.setEnabled(custom['enabled'])

        return combo

    def _build_plain_text_edits(self, parent: QWidget) -> None:
        """QPlainTextEdit 위젯들을 생성하고 배치합니다."""
        try:
            plain_text_edits = configuration_instance.get('gui', 'plain_text_edits')
            for edit_config in plain_text_edits:
                edit = self._create_plain_text_edit(edit_config)
                if edit:
                    edit.setParent(parent)
        except KeyError:
            return

    def _create_plain_text_edit(self, edit_config: dict) -> QPlainTextEdit:
        """개별 QPlainTextEdit 위젯을 생성하고 설정합니다."""
        edit = QPlainTextEdit()
        
        # ID 설정
        if 'id' in edit_config:
            edit.setObjectName(edit_config['id'])
        
        # 위치 설정
        if 'position' in edit_config:
            pos = edit_config['position']
            edit.setGeometry(
                int(pos['x'].replace('px', '')),
                int(pos['y'].replace('px', '')),
                int(pos['width'].replace('px', '')),
                int(pos['height'].replace('px', ''))
            )

        # 스타일시트 적용
        if 'stylesheet' in edit_config:
            edit.setStyleSheet(self._json_to_css(edit_config['stylesheet']))

        # 커스터마이징 설정
        if 'customizing' in edit_config:
            custom = edit_config['customizing']
            
            # 편집 가능 여부 설정
            if 'editable' in custom:
                edit.setReadOnly(not custom['editable'])
            
            # 텍스트 상호작용 설정
            if 'text_interaction' in custom:
                interaction = custom['text_interaction']
                if interaction == 'none':
                    edit.setTextInteractionFlags(Qt.NoTextInteraction)
                elif interaction == 'selectable':
                    edit.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
                elif interaction == 'editable':
                    edit.setTextInteractionFlags(Qt.TextEditorInteraction)
            
            # 줄 바꿈 설정
            if 'line_wrap' in custom:
                edit.setLineWrapMode(QPlainTextEdit.NoWrap if not custom['line_wrap'] else QPlainTextEdit.WidgetWidth)
            
            # 탭 너비 설정
            if 'tab_stop_width' in custom:
                edit.setTabStopDistance(custom['tab_stop_width'] * edit.fontMetrics().horizontalAdvance(' '))
            
            # 스크롤바 설정
            edit.setVerticalScrollBarPolicy(
                Qt.ScrollBarAsNeeded if custom.get('scroll_bar_vertical', True) else Qt.ScrollBarAlwaysOff
            )
            edit.setHorizontalScrollBarPolicy(
                Qt.ScrollBarAsNeeded if custom.get('scroll_bar_horizontal', True) else Qt.ScrollBarAlwaysOff
            )

        return edit 