from PyQt5.QtWidgets import QComboBox, QMainWindow
from PyQt5.QtCore import QObject, pyqtSignal
import threading
from model.Log import log

class ComboBox_AudioQuality:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(ComboBox_AudioQuality, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        self._window = None
        self._audio_quality = None

    def setup(self, window: QMainWindow):
        """ComboBox_AudioQuality를 초기화합니다.
        
        Args:
            window (QMainWindow): 메인 윈도우 객체
        """
        with self._lock:
            self._window = window
            self._audio_quality = self._window.findChild(QComboBox, "audio_quality")
            self.disable()
            if not self._audio_quality:
                log.critical("ComboBox_AudioQuality 초기화 실패")

    def enable(self):
        self._audio_quality.setEnabled(True)
    
    def disable(self):
        self._audio_quality.setEnabled(False)
        
    def get_selected_quality(self) -> str:
        """선택된 오디오 품질을 반환합니다."""
        return self._audio_quality.currentText()

# 싱글톤 인스턴스 생성
combo_box_audio_quality_instance = ComboBox_AudioQuality()