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
                self._file_formatter = None
                self._console_formatter = None
                self._logger = None
                
    def setup(self, 
              enable_logging: bool = True,
              log_file: str = 'log.txt',
              max_size_mb: int = 10,
              backup_count: int = 2,
              encoding: str = 'utf-8',
              log_level: str = 'DEBUG') -> None:
        """
        로깅 시스템을 초기화합니다.
        
        Args:
            enable_logging (bool): 로깅 활성화 여부
            log_file (str): 로그 파일 경로
            max_size_mb (int): 최대 파일 크기 (MB)
            backup_count (int): 백업 파일 최대 개수
            encoding (str): 파일 인코딩
            log_level (str): 로그 레벨 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        with self._lock:
            self._enable_logging = enable_logging
            self._log_file = log_file
            self._max_size_mb = max_size_mb
            self._backup_count = backup_count
            self._encoding = encoding
            self._log_level = self._convert_log_level(log_level)

            if False == enable_logging:
                return
            
            # 로거 초기화
            self._initialize_logger()
            
            # 기존 핸들러 제거
            self._remove_existing_handlers()
            
            # 파일 핸들러 설정
            self._open_file_handler()
            self._set_file_formatter()
            
            # 콘솔 핸들러 설정
            self._open_console_handler()
            self._set_console_formatter()

    def _convert_log_level(self, log_level: str) -> int:
        """
        로그 레벨 문자열을 숫자로 변환합니다.
        
        Args:
            log_level (str): 로그 레벨 (DEBUG, INFO, WARNING, ERROR, CRITICAL)  
        """
        level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        return level_map.get(log_level.upper(), logging.DEBUG)

    def _initialize_logger(self) -> None:
        """
        로거를 초기화합니다.
        """
        self._logger = logging.getLogger('default_logger')
        self._logger.setLevel(self._log_level)

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

    def _set_file_formatter(self) -> None:
        """
        파일 핸들러의 포메터를 설정합니다.
        상세한 로그 정보를 포함합니다.
        """
        if hasattr(self, '_file_handler'):
            self._file_formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S.%f'
            )
            self._file_handler.setFormatter(self._file_formatter)

    def _open_console_handler(self) -> None:
        """
        콘솔 핸들러를 생성하고 로거에 추가합니다.
        """
        self._console_handler = logging.StreamHandler()
        self._console_handler.setLevel(self._log_level)
        self._logger.addHandler(self._console_handler)

    def _set_console_formatter(self) -> None:
        """
        콘솔 핸들러의 포메터를 설정합니다.
        간단하고 가독성 있는 형식을 사용합니다.
        """
        if hasattr(self, '_console_handler'):
            self._console_formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S.%f'
            )
            self._console_handler.setFormatter(self._console_formatter)

    def _close_file_handler(self) -> None:
        """
        파일 핸들러를 닫고 로거에서 제거합니다.
        """
        if hasattr(self, '_file_handler'):
            self._logger.removeHandler(self._file_handler)
            self._file_handler.close()
            del self._file_handler
            self._file_handler = None

    def _close_console_handler(self) -> None:
        """
        콘솔 핸들러를 닫고 로거에서 제거합니다.
        """
        if hasattr(self, '_console_handler'):
            self._logger.removeHandler(self._console_handler)
            self._console_handler.close()
            del self._console_handler
            self._console_handler = None

    def debug(self, msg: str) -> None:
        """디버그 메시지를 로깅합니다."""
        with self._lock:
            if self._logger and self._enable_logging:
                self._logger.debug(msg)

    def info(self, msg: str) -> None:
        """정보 메시지를 로깅합니다."""
        with self._lock:
            if self._logger and self._enable_logging:
                self._logger.info(msg)

    def warning(self, msg: str) -> None:
        """경고 메시지를 로깅합니다."""
        with self._lock:
            if self._logger and self._enable_logging:
                self._logger.warning(msg)

    def error(self, msg: str) -> None:
        """오류 메시지를 로깅합니다."""
        with self._lock:
            if self._logger and self._enable_logging:
                self._logger.error(msg)

    def critical(self, msg: str) -> None:
        """심각한 오류 메시지를 로깅합니다."""
        with self._lock:
            if self._logger and self._enable_logging:
                self._logger.critical(msg)

    def exception(self, msg: str) -> None:
        """예외 정보를 로깅합니다."""
        with self._lock:
            if self._logger and self._enable_logging:
                self._logger.exception(msg)
                
# 싱글톤 인스턴스 생성
log = NewLog()