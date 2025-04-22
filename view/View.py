import sys
from PyQt5.QtWidgets import QApplication
from view.GUIBuilder import GUIBuilder
from view.GUIScaler import GUIScaler
from model.Configuration import Configuration


class View:
    """View 클래스의 싱글톤 구현."""
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(View, cls).__new__(cls, *args, **kwargs)
            cls._instance._initialized = False
        return cls._instance

    def initialize(self):
        """DPI 인식 설정을 초기화합니다."""
        if not self._initialized:
            GUIScaler.initialize_dpi_scaling_and_awareness()
            self._initialized = True

    def run(self, app):
        """GUI를 실행하고 메인 윈도우를 반환합니다."""
        # GUI 스케일링 적용
        gui_scaler = GUIScaler()
        scale_factor = gui_scaler.apply_scaling(app)

        # GUI 빌더 생성
        gui_builder = GUIBuilder()

        # 메인 윈도우 생성
        window = gui_builder.build()

        # 윈도우 표시
        window.show()

        return window


# 싱글톤 인스턴스 생성
view_instance = View()