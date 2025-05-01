import os
import threading
from typing import Optional

class DirectoryManager:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(DirectoryManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        pass

    def make_download_directory(self, save_path: str = None):
        """저장 경로를 설정하고 필요한 경우 생성합니다."""
        if save_path is None:
            save_path = os.path.join(os.getcwd(), 'downloads')
            
        if not os.path.exists(save_path):
            os.makedirs(save_path)
            
        return save_path
    
# 싱글톤 인스턴스 생성
directory_manager_instance = DirectoryManager()