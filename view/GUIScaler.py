import ctypes
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QScreen
from typing import Tuple, Dict
import threading

class GUIScaler:
    """GUI 스케일링을 관리하는 클래스"""
    
    _instance = None
    _lock = threading.Lock()
    
    # 해상도별 기준값
    RESOLUTIONS = {
        'HD': (1280, 720),
        'FHD': (1920, 1080),
        'QHD': (2560, 1440),
        'UHD': (3840, 2160),
        '5K': (5120, 2880),
        '8K': (7680, 4320)
    }
    
    # 화면 비율별 기준값
    ASPECT_RATIOS = {
        '16:9': 16/9,
        '16:10': 16/10,
        '21:9': 21/9,
        '32:9': 32/9
    }
    
    BASE_DPI = 96
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(GUIScaler, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            with self._lock:
                if not self._initialized:
                    self._initialized = True
                    self._initialize()
    
    def __call__(self):
        raise TypeError("GUIScaler는 싱글톤 클래스입니다. 인스턴스를 직접 생성할 수 없습니다.")
    
    @staticmethod
    def initialize_dpi_scaling_and_awareness():
        """Qt DPI 스케일링 설정과 Windows DPI 인식 설정을 초기화합니다."""
        try:    
            # Qt DPI 스케일링 설정
            QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
            QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

            # Windows DPI 인식 설정
            user32 = ctypes.windll.user32
            user32.SetProcessDPIAware()
        except:
            pass
    
    def apply_scaling(self, app: QApplication) -> float:
        """DPI와 해상도를 기반으로 스케일링을 적용합니다."""
        if app is None:
            raise ValueError("QApplication 인스턴스가 필요합니다.")
            
        self.app = app
        # 스케일 팩터 계산
        self.scale_factor = self._calculate_scale_factor()
        
        # 스타일시트 적용
        self._apply_stylesheet()
        
        return self.scale_factor
    
    def _initialize(self):
        """초기화 작업을 수행합니다."""
        self.scale_factor = 1.0
    
    def _calculate_scale_factor(self) -> float:
        """최종 스케일 팩터를 계산합니다."""
        # 현재 화면 정보 가져오기
        primary_screen = self.app.primaryScreen()
        screen_size = primary_screen.size()
        current_dpi = self._get_windows_dpi()
        
        # 화면 비율 계산
        aspect_ratio = self._calculate_aspect_ratio(screen_size.width(), screen_size.height())
        
        # 가장 가까운 표준 해상도 찾기
        closest_res_name, closest_res = self._find_closest_resolution(
            screen_size.width(), screen_size.height())
        
        # 해상도 기반 스케일 팩터 계산
        width_scale = screen_size.width() / closest_res[0]
        height_scale = screen_size.height() / closest_res[1]
        
        # 화면 비율에 따른 보정
        if aspect_ratio in ['21:9', '32:9']:  # 울트라와이드
            resolution_scale = min(width_scale, height_scale) * 0.8  # 좌우 여백 고려
        else:
            resolution_scale = min(width_scale, height_scale)
        
        # DPI 기반 스케일 팩터 계산
        dpi_scale = current_dpi / self.BASE_DPI
        
        # 최종 스케일 팩터 계산
        return min(resolution_scale, dpi_scale)
    
    def _apply_stylesheet(self):
        """스타일시트를 적용합니다."""
        self.app.setStyleSheet(f"""
            * {{
                font-size: {int(12 * self.scale_factor)}px;
            }}
            QMainWindow, QWidget {{
                font-size: {int(12 * self.scale_factor)}px;
            }}
            QLabel, QLineEdit, QComboBox, QPushButton {{
                font-size: {int(12 * self.scale_factor)}px;
                padding: {int(2 * self.scale_factor)}px;
                height: {int(18 * self.scale_factor)}px;
                min-height: {int(18 * self.scale_factor)}px;
            }}
            QLineEdit, QComboBox {{
                background-color: #3c3f41;
                color: #ffffff;
                border: 1px solid #4d4d4d;
                border-radius: 3px;
            }}
            QPushButton {{
                background-color: #2b2b2b;
                color: #ffffff;
                border: 1px solid #3b3b3b;
                border-radius: 3px;
            }}
            QPushButton:hover {{
                background-color: #3b3b3b;
            }}
            QPushButton:pressed {{
                background-color: #1b1b1b;
            }}
        """)
    
    def get_scale_factor(self) -> float:
        """현재 스케일 팩터를 반환합니다."""
        return self.scale_factor
    
    def is_qhd_display(self) -> bool:
        """QHD 모니터인지 여부를 반환합니다."""
        primary_screen = self.app.primaryScreen()
        screen_size = primary_screen.size()
        return screen_size.width() >= 2560 and screen_size.height() >= 1440
    
    def _calculate_aspect_ratio(self, width: int, height: int) -> str:
        """화면 비율을 계산합니다."""
        ratio = width / height
        # 가장 가까운 표준 비율 찾기
        closest_ratio = min(self.ASPECT_RATIOS.items(), 
                          key=lambda x: abs(x[1] - ratio))
        return closest_ratio[0]
    
    def _find_closest_resolution(self, width: int, height: int) -> Tuple[str, Tuple[int, int]]:
        """가장 가까운 표준 해상도를 찾습니다."""
        current_pixels = width * height
        closest = min(self.RESOLUTIONS.items(),
                     key=lambda x: abs(x[1][0] * x[1][1] - current_pixels))
        return closest
    
    def _get_windows_dpi(self) -> int:
        """Windows DPI 설정을 가져옵니다."""
        try:
            return self.app.primaryScreen().logicalDotsPerInch()
        except:
            return self.BASE_DPI 


# 싱글톤 인스턴스 생성
#gui_scaler_instance = GUIScaler()