import threading
from typing import Optional
import logging
from logging.handlers import RotatingFileHandler

class NewLog:
    _instance: Optional['NewLog'] = None
    _lock = threading.Lock()
    
    def __new__(cls) -> 'NewLog':
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(NewLog, cls).__new__(cls)
                cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        with self._lock:
            if not self._initialized:
                self._initialized = True 
                self._enable_logging = False
                self._log_file = 'log.txt'
                self._max_size_mb = 10
                self._backup_count = 2
                self._encoding = 'utf-8'
                self._log_level = logging.DEBUG
                self._file_handler = None
                self._console_handler = None
                self._formatter = None
                self._logger = None

    def _remove_existing_handlers(self) -> None:
        """
        기존에 등록된 모든 핸들러를 제거하고 닫습니다.
        이는 로깅 설정을 재설정하기 전에 호출되어야 합니다.
        """
        if hasattr(self, '_logger'):
            for handler in self._logger.handlers[:]:
                self._logger.removeHandler(handler)
                handler.close()

    def _open_file_handler(self) -> None:
        """
        파일 핸들러를 생성하고 로거에 추가합니다.
        """
        self._file_handler = RotatingFileHandler(
            filename=self._log_file,
            maxBytes=self._max_size_mb * 1024 * 1024    ,
            backupCount=self._backup_count,
            encoding=self._encoding
        )
        self._file_handler.setLevel(self._log_level)
        self._logger.addHandler(self._file_handler)
        
    def _close_file_handler(self) -> None:
        """
        파일 핸들러를 닫고 로거에서 제거합니다.
        """
        if hasattr(self, '_file_handler'):
            self._logger.removeHandler(self._file_handler)
            self._file_handler.close()
            del self._file_handler
            self._file_handler = None

    def _open_console_handler(self) -> None:
        """
        콘솔 핸들러를 생성하고 로거에 추가합니다.
        """
        self._console_handler = logging.StreamHandler()
        self._console_handler.setLevel(self._log_level)
        self._logger.addHandler(self._console_handler)
        
    def _close_console_handler(self) -> None:
        """
        콘솔 핸들러를 닫고 로거에서 제거합니다.
        """
        if hasattr(self, '_console_handler'):
            self._logger.removeHandler(self._console_handler)
            self._console_handler.close()
            del self._console_handler
            self._console_handler = None

    def _set_file_formatter(self) -> None:
        """
        파일 핸들러의 포메터를 설정합니다.
        상세한 로그 정보를 포함합니다.
        """
        if hasattr(self, '_file_handler'):
            formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S.%f'
            )
            self._file_handler.setFormatter(formatter)
            
    def _set_console_formatter(self) -> None:
        """
        콘솔 핸들러의 포메터를 설정합니다.
        간단하고 가독성 있는 형식을 사용합니다.
        """
        if hasattr(self, '_console_handler'):
            formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S.%f'
            )
            self._console_handler.setFormatter(formatter)


                

