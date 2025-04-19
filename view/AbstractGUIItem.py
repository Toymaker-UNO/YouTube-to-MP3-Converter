from abc import ABC, abstractmethod
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QPoint
from PyQt5.QtGui import QColor, QPalette, QCursor, QDrag, QPixmap

class AbstractGUIItem(ABC):
    """GUI 아이템의 추상 기본 클래스입니다.
    모든 GUI 컴포넌트는 이 클래스를 상속받아 구현해야 합니다.
    """
    
    def __init__(self, parent: QWidget = None):
        """GUI 아이템을 초기화합니다.
        
        Args:
            parent (QWidget, optional): 부모 위젯. 기본값은 None.
        """
        self._widget = None
        self._parent = parent
        self._style_sheet = ""
        self._visibility = True
        self._enabled = True
        self._x = 0
        self._y = 0
        self._background_color = None
        self._foreground_color = None
        self._border_color = None
        self._margin_top = 0
        self._margin_right = 0
        self._margin_bottom = 0
        self._margin_left = 0
        self._padding_top = 0
        self._padding_right = 0
        self._padding_bottom = 0
        self._padding_left = 0
        self._tooltip = ""
        self._tooltip_style = ""
        self._cursor = Qt.ArrowCursor
        self._hover_style = ""
        self._focus_style = ""
        self._drag_enabled = False
        self._drop_enabled = False
        self._animation_duration = 300
        self._animation_easing = QEasingCurve.OutCubic
        self._custom_styles = {}
        
    @property
    def widget(self) -> QWidget:
        """위젯 인스턴스를 반환합니다."""
        return self._widget
        
    @property
    def parent(self) -> QWidget:
        """부모 위젯을 반환합니다."""
        return self._parent
        
    @property
    def style_sheet(self) -> str:
        """스타일시트를 반환합니다."""
        return self._style_sheet
        
    @style_sheet.setter
    def style_sheet(self, value: str):
        """스타일시트를 설정합니다."""
        self._style_sheet = value
        if self._widget:
            self._widget.setStyleSheet(value)
            
    @property
    def visibility(self) -> bool:
        """위젯의 표시 여부를 반환합니다."""
        return self._visibility
        
    @visibility.setter
    def visibility(self, visible: bool):
        """위젯의 표시 여부를 설정합니다."""
        self._visibility = visible
        if self._widget:
            self._widget.setVisible(visible)
            
    @property
    def enabled(self) -> bool:
        """위젯의 활성화 상태를 반환합니다."""
        return self._enabled
        
    @enabled.setter
    def enabled(self, value: bool):
        """위젯의 활성화 상태를 설정합니다."""
        self._enabled = value
        if self._widget:
            self._widget.setEnabled(value)
            
    @property
    def x(self) -> int:
        """위젯의 x 좌표를 반환합니다."""
        return self._x
        
    @x.setter
    def x(self, value: int):
        """위젯의 x 좌표를 설정합니다."""
        self._x = value
        if self._widget:
            self._widget.move(value, self._y)
            
    @property
    def y(self) -> int:
        """위젯의 y 좌표를 반환합니다."""
        return self._y
        
    @y.setter
    def y(self, value: int):
        """위젯의 y 좌표를 설정합니다."""
        self._y = value
        if self._widget:
            self._widget.move(self._x, value)
            
    @property
    def background_color(self) -> QColor:
        """배경색을 반환합니다."""
        return self._background_color
        
    @background_color.setter
    def background_color(self, color: QColor):
        """배경색을 설정합니다."""
        self._background_color = color
        self._update_colors()
        
    @property
    def foreground_color(self) -> QColor:
        """전경색을 반환합니다."""
        return self._foreground_color
        
    @foreground_color.setter
    def foreground_color(self, color: QColor):
        """전경색을 설정합니다."""
        self._foreground_color = color
        self._update_colors()
        
    @property
    def border_color(self) -> QColor:
        """테두리 색상을 반환합니다."""
        return self._border_color
        
    @border_color.setter
    def border_color(self, color: QColor):
        """테두리 색상을 설정합니다."""
        self._border_color = color
        self._update_colors()
            
    @property
    def margin_top(self) -> int:
        """상단 마진을 반환합니다."""
        return self._margin_top
        
    @margin_top.setter
    def margin_top(self, value: int):
        """상단 마진을 설정합니다."""
        self._margin_top = value
        self._update_margin_padding()
        
    @property
    def margin_right(self) -> int:
        """우측 마진을 반환합니다."""
        return self._margin_right
        
    @margin_right.setter
    def margin_right(self, value: int):
        """우측 마진을 설정합니다."""
        self._margin_right = value
        self._update_margin_padding()
        
    @property
    def margin_bottom(self) -> int:
        """하단 마진을 반환합니다."""
        return self._margin_bottom
        
    @margin_bottom.setter
    def margin_bottom(self, value: int):
        """하단 마진을 설정합니다."""
        self._margin_bottom = value
        self._update_margin_padding()
        
    @property
    def margin_left(self) -> int:
        """좌측 마진을 반환합니다."""
        return self._margin_left
        
    @margin_left.setter
    def margin_left(self, value: int):
        """좌측 마진을 설정합니다."""
        self._margin_left = value
        self._update_margin_padding()
        
    @property
    def padding_top(self) -> int:
        """상단 패딩을 반환합니다."""
        return self._padding_top
        
    @padding_top.setter
    def padding_top(self, value: int):
        """상단 패딩을 설정합니다."""
        self._padding_top = value
        self._update_margin_padding()
        
    @property
    def padding_right(self) -> int:
        """우측 패딩을 반환합니다."""
        return self._padding_right
        
    @padding_right.setter
    def padding_right(self, value: int):
        """우측 패딩을 설정합니다."""
        self._padding_right = value
        self._update_margin_padding()
        
    @property
    def padding_bottom(self) -> int:
        """하단 패딩을 반환합니다."""
        return self._padding_bottom
        
    @padding_bottom.setter
    def padding_bottom(self, value: int):
        """하단 패딩을 설정합니다."""
        self._padding_bottom = value
        self._update_margin_padding()
        
    @property
    def padding_left(self) -> int:
        """좌측 패딩을 반환합니다."""
        return self._padding_left
        
    @padding_left.setter
    def padding_left(self, value: int):
        """좌측 패딩을 설정합니다."""
        self._padding_left = value
        self._update_margin_padding()
        
    @property
    def tooltip(self) -> str:
        """툴팁을 반환합니다."""
        return self._tooltip
        
    @tooltip.setter
    def tooltip(self, value: str):
        """툴팁을 설정합니다."""
        self._tooltip = value
        if self._widget:
            self._widget.setToolTip(value)
            
    @property
    def tooltip_style(self) -> str:
        """툴팁 스타일을 반환합니다."""
        return self._tooltip_style
        
    @tooltip_style.setter
    def tooltip_style(self, value: str):
        """툴팁 스타일을 설정합니다."""
        self._tooltip_style = value
        if self._widget:
            self._widget.setStyleSheet(f"QToolTip {{ {value} }}")
            
    @property
    def cursor(self) -> Qt.CursorShape:
        """마우스 포인터가 위젯 위에 올라갔을 때 표시될 커서 모양을 반환합니다.
        
        Returns:
            Qt.CursorShape: 현재 설정된 커서 모양
                - Qt.ArrowCursor: 기본 화살표 커서
                - Qt.CrossCursor: 십자 커서
                - Qt.WaitCursor: 대기 커서 (모래시계)
                - Qt.IBeamCursor: 텍스트 입력 커서 (I 모양)
                - Qt.SizeVerCursor: 수직 크기 조절 커서
                - Qt.SizeHorCursor: 수평 크기 조절 커서
                - Qt.SizeBDiagCursor: 대각선 크기 조절 커서
                - Qt.SizeFDiagCursor: 반대 대각선 크기 조절 커서
                - Qt.SizeAllCursor: 모든 방향 크기 조절 커서
                - Qt.BlankCursor: 빈 커서 (커서 숨김)
                - Qt.SplitVCursor: 수직 분할 커서
                - Qt.SplitHCursor: 수평 분할 커서
                - Qt.PointingHandCursor: 손가락 포인팅 커서
                - Qt.ForbiddenCursor: 금지 커서
                - Qt.WhatsThisCursor: 도움말 커서
                - Qt.BusyCursor: 작업 중 커서
        """
        return self._cursor
        
    @cursor.setter
    def cursor(self, value: Qt.CursorShape):
        """마우스 포인터가 위젯 위에 올라갔을 때 표시될 커서 모양을 설정합니다.
        
        Args:
            value (Qt.CursorShape): 설정할 커서 모양
                - 마우스가 위젯 위에 올라가면 설정된 커서 모양으로 변경됩니다.
                - 마우스가 위젯을 벗어나면 자동으로 기본 화살표 커서로 복귀합니다.
                - 각 위젯마다 독립적으로 커서 모양을 설정할 수 있습니다.
        """
        self._cursor = value
        if self._widget:
            self._widget.setCursor(QCursor(value))
            
    @property
    def hover_style(self) -> str:
        """호버 스타일을 반환합니다."""
        return self._hover_style
        
    @hover_style.setter
    def hover_style(self, value: str):
        """호버 스타일을 설정합니다."""
        self._hover_style = value
        self._update_styles()
        
    @property
    def focus_style(self) -> str:
        """포커스 스타일을 반환합니다."""
        return self._focus_style
        
    @focus_style.setter
    def focus_style(self, value: str):
        """포커스 스타일을 설정합니다."""
        self._focus_style = value
        self._update_styles()
            
    @property
    def drag_enabled(self) -> bool:
        """위젯의 드래그 기능 활성화 여부를 반환합니다.
        
        Returns:
            bool: 드래그 기능이 활성화되어 있으면 True, 비활성화되어 있으면 False
                - True: 위젯을 마우스로 드래그할 수 있음
                - False: 위젯을 마우스로 드래그할 수 없음
        """
        return self._drag_enabled
        
    @drag_enabled.setter
    def drag_enabled(self, value: bool):
        """위젯의 드래그 기능을 활성화 또는 비활성화합니다.
        
        Args:
            value (bool): 드래그 기능 활성화 여부
                - True: 위젯의 드래그 기능을 활성화
                    - 마우스로 위젯을 드래그할 수 있게 됨
                    - 드래그 시작 시 start_drag() 메서드가 호출됨
                - False: 위젯의 드래그 기능을 비활성화
                    - 마우스로 위젯을 드래그할 수 없게 됨
                    
        Note:
            - 드래그 기능이 활성화되어 있어도 실제 드래그 동작은 start_drag() 메서드를 통해 시작됨
            - 드래그 중인 위젯의 시각적 피드백은 커스텀 스타일을 통해 구현 가능
        """
        self._drag_enabled = value
        if self._widget:
            self._widget.setAcceptDrops(value)
            
    @property
    def drop_enabled(self) -> bool:
        """위젯의 드롭 기능 활성화 여부를 반환합니다.
        
        Returns:
            bool: 드롭 기능이 활성화되어 있으면 True, 비활성화되어 있으면 False
                - True: 위젯이 다른 위젯으로부터 드롭된 항목을 받아들일 수 있음
                - False: 위젯이 드롭된 항목을 받아들일 수 없음
        """
        return self._drop_enabled
        
    @drop_enabled.setter
    def drop_enabled(self, value: bool):
        """위젯의 드롭 기능을 활성화 또는 비활성화합니다.
        
        Args:
            value (bool): 드롭 기능 활성화 여부
                - True: 위젯의 드롭 기능을 활성화
                    - 다른 위젯으로부터 드롭된 항목을 받아들일 수 있게 됨
                    - 드롭 이벤트를 처리할 수 있게 됨
                - False: 위젯의 드롭 기능을 비활성화
                    - 드롭된 항목을 받아들일 수 없게 됨
                    
        Note:
            - 드롭 기능이 활성화되어 있어도 실제 드롭 동작은 dropEvent() 메서드를 통해 처리됨
            - 드롭 가능한 영역에 대한 시각적 피드백은 커스텀 스타일을 통해 구현 가능
            - drag_enabled와 함께 사용하여 드래그 앤 드롭 기능을 완성할 수 있음
        """
        self._drop_enabled = value
        if self._widget:
            self._widget.setAcceptDrops(value)
            
    @property
    def animation_duration(self) -> int:
        """애니메이션 지속 시간을 반환합니다."""
        return self._animation_duration
        
    @animation_duration.setter
    def animation_duration(self, value: int):
        """애니메이션 지속 시간을 설정합니다."""
        self._animation_duration = value
        
    @property
    def animation_easing(self) -> QEasingCurve.Type:
        """애니메이션 이징을 반환합니다."""
        return self._animation_easing
        
    @animation_easing.setter
    def animation_easing(self, value: QEasingCurve.Type):
        """애니메이션 이징을 설정합니다."""
        self._animation_easing = value
            
    def set_margin(self, top: int = None, right: int = None, bottom: int = None, left: int = None):
        """마진을 한 번에 설정합니다.
        
        Args:
            top (int, optional): 상단 마진
            right (int, optional): 우측 마진
            bottom (int, optional): 하단 마진
            left (int, optional): 좌측 마진
        """
        if top is not None:
            self._margin_top = top
        if right is not None:
            self._margin_right = right
        if bottom is not None:
            self._margin_bottom = bottom
        if left is not None:
            self._margin_left = left
        self._update_margin_padding()
            
    def set_padding(self, top: int = None, right: int = None, bottom: int = None, left: int = None):
        """패딩을 한 번에 설정합니다.
        
        Args:
            top (int, optional): 상단 패딩
            right (int, optional): 우측 패딩
            bottom (int, optional): 하단 패딩
            left (int, optional): 좌측 패딩
        """
        if top is not None:
            self._padding_top = top
        if right is not None:
            self._padding_right = right
        if bottom is not None:
            self._padding_bottom = bottom
        if left is not None:
            self._padding_left = left
        self._update_margin_padding()
            
    def set_styles(self, hover: str = None, focus: str = None):
        """상태별 스타일을 설정합니다.
        
        Args:
            hover (str, optional): 호버 스타일
            focus (str, optional): 포커스 스타일
        """
        if hover is not None:
            self._hover_style = hover
        if focus is not None:
            self._focus_style = focus
        self._update_styles()
            
    def set_custom_style(self, selector: str, style: str):
        """커스텀 스타일을 설정합니다.
        
        Args:
            selector (str): CSS 선택자
            style (str): CSS 스타일
        """
        self._custom_styles[selector] = style
        self._update_styles()
        
    def remove_custom_style(self, selector: str):
        """커스텀 스타일을 제거합니다.
        
        Args:
            selector (str): 제거할 CSS 선택자
        """
        if selector in self._custom_styles:
            del self._custom_styles[selector]
            self._update_styles()
            
    def animate_position(self, x: int, y: int):
        """위치를 애니메이션과 함께 변경합니다.
        
        Args:
            x (int): 목표 x 좌표
            y (int): 목표 y 좌표
        """
        if not self._widget:
            return
            
        animation = QPropertyAnimation(self._widget, b"pos")
        animation.setDuration(self._animation_duration)
        animation.setEasingCurve(self._animation_easing)
        animation.setStartValue(self._widget.pos())
        animation.setEndValue(QPoint(x, y))
        animation.start()
        
        self._x = x
        self._y = y
        
    def animate_size(self, width: int, height: int):
        """크기를 애니메이션과 함께 변경합니다.
        
        Args:
            width (int): 목표 너비
            height (int): 목표 높이
        """
        if not self._widget:
            return
            
        animation = QPropertyAnimation(self._widget, b"size")
        animation.setDuration(self._animation_duration)
        animation.setEasingCurve(self._animation_easing)
        animation.setStartValue(self._widget.size())
        animation.setEndValue(QSize(width, height))
        animation.start()
        
    def start_drag(self, data):
        """드래그를 시작합니다.
        
        Args:
            data: 드래그할 데이터
        """
        if not self._widget or not self.drag_enabled:
            return
            
        drag = QDrag(self._widget)
        mime_data = QMimeData()
        mime_data.setText(str(data))
        drag.setMimeData(mime_data)
        
        pixmap = QPixmap(self._widget.size())
        self._widget.render(pixmap)
        drag.setPixmap(pixmap)
        
        drag.exec_(Qt.CopyAction)
        
    @abstractmethod
    def create_widget(self) -> QWidget:
        """위젯을 생성하고 반환합니다.
        
        Returns:
            QWidget: 생성된 위젯
        """
        pass
        
    def initialize(self):
        """위젯을 초기화합니다."""
        self._widget = self.create_widget()
        if self._parent:
            self._widget.setParent(self._parent)
        self._widget.setStyleSheet(self._style_sheet)
        self._widget.setVisible(self._visibility)
        self._widget.setEnabled(self._enabled)
        self._widget.move(self._x, self._y)
        self._widget.setToolTip(self._tooltip)
        self._widget.setCursor(QCursor(self._cursor))
        self._widget.setAcceptDrops(self._drop_enabled)
        self._update_colors()
        self._update_margin_padding()
        self._update_styles()
        
    def set_size(self, width: int, height: int):
        """위젯의 크기를 설정합니다.
        
        Args:
            width (int): 너비
            height (int): 높이
        """
        if self._widget:
            self._widget.setFixedSize(width, height)
            
    def set_minimum_size(self, width: int, height: int):
        """위젯의 최소 크기를 설정합니다.
        
        Args:
            width (int): 최소 너비
            height (int): 최소 높이
        """
        if self._widget:
            self._widget.setMinimumSize(width, height)
            
    def set_maximum_size(self, width: int, height: int):
        """위젯의 최대 크기를 설정합니다.
        
        Args:
            width (int): 최대 너비
            height (int): 최대 높이
        """
        if self._widget:
            self._widget.setMaximumSize(width, height)
            
    def set_alignment(self, alignment: Qt.Alignment):
        """위젯의 정렬 방식을 설정합니다.
        
        Args:
            alignment (Qt.Alignment): 정렬 방식
        """
        if self._widget:
            self._widget.setAlignment(alignment)
            
    def set_position(self, x: int, y: int):
        """위젯의 위치를 설정합니다.
        
        Args:
            x (int): x 좌표
            y (int): y 좌표
        """
        self._x = x
        self._y = y
        if self._widget:
            self._widget.move(x, y)
            
    def move(self, dx: int, dy: int):
        """위젯을 상대적으로 이동합니다.
        
        Args:
            dx (int): x 방향 이동 거리
            dy (int): y 방향 이동 거리
        """
        self._x += dx
        self._y += dy
        if self._widget:
            self._widget.move(self._x, self._y)
            
    def set_colors(self, background: QColor = None, foreground: QColor = None, border: QColor = None):
        """위젯의 색상을 한 번에 설정합니다.
        
        Args:
            background (QColor, optional): 배경색
            foreground (QColor, optional): 전경색
            border (QColor, optional): 테두리 색상
        """
        if background is not None:
            self._background_color = background
        if foreground is not None:
            self._foreground_color = foreground
        if border is not None:
            self._border_color = border
        self._update_colors()
            
    def _update_colors(self):
        """위젯의 색상을 업데이트합니다."""
        if not self._widget:
            return
            
        style = []
        
        if self._background_color:
            style.append(f"background-color: {self._background_color.name()};")
            
        if self._foreground_color:
            style.append(f"color: {self._foreground_color.name()};")
            
        if self._border_color:
            style.append(f"border: 1px solid {self._border_color.name()};")
            
        if style:
            self._widget.setStyleSheet(" ".join(style))
            
    def _update_margin_padding(self):
        """마진과 패딩을 업데이트합니다."""
        if not self._widget:
            return
            
        style = []
        
        if self._margin_top or self._margin_right or self._margin_bottom or self._margin_left:
            style.append(f"margin: {self._margin_top}px {self._margin_right}px {self._margin_bottom}px {self._margin_left}px;")
            
        if self._padding_top or self._padding_right or self._padding_bottom or self._padding_left:
            style.append(f"padding: {self._padding_top}px {self._padding_right}px {self._padding_bottom}px {self._padding_left}px;")
            
        if style:
            self._widget.setStyleSheet(" ".join(style))
            
    def _update_styles(self):
        """모든 스타일을 업데이트합니다."""
        if not self._widget:
            return
            
        styles = []
        
        # 기본 스타일
        if self._style_sheet:
            styles.append(self._style_sheet)
            
        # 호버 스타일
        if self._hover_style:
            styles.append(f"QWidget:hover {{ {self._hover_style} }}")
            
        # 포커스 스타일
        if self._focus_style:
            styles.append(f"QWidget:focus {{ {self._focus_style} }}")
            
        # 커스텀 스타일
        for selector, style in self._custom_styles.items():
            styles.append(f"{selector} {{ {style} }}")
            
        if styles:
            self._widget.setStyleSheet(" ".join(styles))
            
    def show(self):
        """위젯을 표시합니다."""
        self.visibility = True
        
    def hide(self):
        """위젯을 숨깁니다."""
        self.visibility = False
        
    def toggle_visibility(self):
        """위젯의 표시 여부를 토글합니다."""
        self.visibility = not self.visibility
        
    def update(self):
        """위젯을 업데이트합니다."""
        if self._widget:
            self._widget.update()
        
    def enable(self):
        """위젯을 활성화합니다."""
        self.enabled = True
        
    def disable(self):
        """위젯을 비활성화합니다."""
        self.enabled = False
        
    def toggle_enabled(self):
        """위젯의 활성화 상태를 토글합니다."""
        self.enabled = not self.enabled 