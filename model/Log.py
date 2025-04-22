import logging
import os
import time
from logging.handlers import RotatingFileHandler
from typing import Optional
import traceback

class Log:
    # 클래스 레벨 상수
    DEFAULT_LOG_FILE = 'youtube_to_mp3.log.txt'
    DEFAULT_MAX_SIZE = 10 * 1024 * 1024  # 10MB
    DEFAULT_BACKUP_COUNT = 2
    DEFAULT_ENCODING = 'utf-8'
    DEFAULT_LEVEL = logging.DEBUG
    
    # 싱글톤 인스턴스
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Log, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        pass
        
    def initialize(self, 
                  enable_logging: bool = True,
                  log_file: str = DEFAULT_LOG_FILE,
                  max_size_mb: int = 10,
                  backup_count: int = 2,
                  encoding: str = 'utf-8',
                  log_level: str = 'DEBUG') -> None:
        """
        로깅 시스템을 초기화합니다.
        
        Args:
            enable_logging (bool): 로깅 활성화 여부 (기본값: True)
            log_file (str): 로그 파일 경로 (기본값: 'youtube_to_mp3.log.txt')
            max_size_mb (int): 최대 로그 파일 크기 (MB) (기본값: 10)
            backup_count (int): 백업 파일 최대 개수 (기본값: 2)
            encoding (str): 파일 인코딩 (기본값: 'utf-8')
            log_level (str): 로그 레벨 (기본값: 'DEBUG')
                              가능한 값: 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
        """
        if self._initialized:
            self.error("로깅 시스템이 이미 초기화되어 있습니다. 재초기화는 지원하지 않습니다.")
            return
        self._initialized = True
            
        # 로그 파일 경로 설정
        self.DEFAULT_LOG_FILE = log_file
        self.DEFAULT_MAX_SIZE = max_size_mb * 1024 * 1024
        self.DEFAULT_BACKUP_COUNT = backup_count
        self.DEFAULT_ENCODING = encoding
        
        # 로그 레벨 설정
        level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        self.DEFAULT_LEVEL = level_map.get(log_level.upper(), logging.DEBUG)
        
        # 로거 설정
        self.logger = logging.getLogger('youtube_to_mp3')
        self.logger.setLevel(self.DEFAULT_LEVEL)
        
        # 파일 핸들러 설정
        self.file_handler = None
        self.setup_file_handler()
        
        # 콘솔 핸들러 설정
        self.console_handler = logging.StreamHandler()
        self.console_handler.setLevel(self.DEFAULT_LEVEL)
        self.logger.addHandler(self.console_handler)
        
        # 로그 포맷 설정
        self.setup_formatters()
        
        # 로깅 활성화/비활성화
        self.enable_logging(enable_logging)
        
        self.info(f"""
로깅 시스템 초기화 완료:
- 로깅 활성화: {enable_logging}
- 로그 파일: {log_file}
- 최대 크기: {max_size_mb}MB
- 백업 개수: {backup_count}
- 인코딩: {encoding}
- 로그 레벨: {log_level}
        """)
        
    def setup_file_handler(self):
        """파일 핸들러 설정"""
        if self.file_handler:
            self.logger.removeHandler(self.file_handler)
            
        self.file_handler = RotatingFileHandler(
            self.DEFAULT_LOG_FILE,
            maxBytes=self.DEFAULT_MAX_SIZE,
            backupCount=self.DEFAULT_BACKUP_COUNT,
            encoding=self.DEFAULT_ENCODING
        )
        self.file_handler.setLevel(self.DEFAULT_LEVEL)
        self.logger.addHandler(self.file_handler)
        
    def setup_formatters(self):
        """로그 포맷터 설정"""
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        self.file_handler.setFormatter(formatter)
        self.console_handler.setFormatter(formatter)
        
    def debug(self, message: str):
        """디버그 레벨 로깅"""
        self.logger.debug(message)
        
    def info(self, message: str):
        """정보 레벨 로깅"""
        self.logger.info(message)
        
    def warning(self, message: str):
        """경고 레벨 로깅"""
        self.logger.warning(message)
        
    def error(self, message: str):
        """오류 레벨 로깅"""
        self.logger.error(message)
        
    def critical(self, message: str):
        """치명적 오류 레벨 로깅"""
        self.logger.critical(message)
        
    def set_log_file_path(self, path: str):
        """로그 파일 경로 설정"""
        self.DEFAULT_LOG_FILE = path
        self.setup_file_handler()
        
    def set_max_log_size_mb(self, size_mb: int):
        """최대 로그 파일 크기 설정 (MB)"""
        self.DEFAULT_MAX_SIZE = size_mb * 1024 * 1024
        self.setup_file_handler()
        
    def set_max_backup_count(self, count: int):
        """백업 파일 최대 개수 설정"""
        self.DEFAULT_BACKUP_COUNT = count
        self.setup_file_handler()
        
    def set_encoding(self, encoding: str):
        """인코딩 설정"""
        self.DEFAULT_ENCODING = encoding
        self.setup_file_handler()
        
    def set_level(self, level: str):
        """로그 레벨 설정"""
        level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        self.DEFAULT_LEVEL = level_map.get(level.upper(), logging.DEBUG)
        self.logger.setLevel(self.DEFAULT_LEVEL)
        self.file_handler.setLevel(self.DEFAULT_LEVEL)
        self.console_handler.setLevel(self.DEFAULT_LEVEL)
        
    def enable_logging(self, enable: bool = True):
        """로깅 활성화/비활성화"""
        if enable:
            self.logger.setLevel(self.DEFAULT_LEVEL)
            self.file_handler.setLevel(self.DEFAULT_LEVEL)
            self.console_handler.setLevel(self.DEFAULT_LEVEL)
        else:
            self.logger.setLevel(logging.CRITICAL + 1)  # 모든 로깅 비활성화
            self.file_handler.setLevel(logging.CRITICAL + 1)
            self.console_handler.setLevel(logging.CRITICAL + 1)
            
    def is_enabled(self) -> bool:
        """로깅이 활성화되어 있는지 확인"""
        return self.logger.level != logging.CRITICAL + 1
        
    def log_exception(self, exception: Exception):
        """예외 정보를 상세히 로깅"""
        self.error(f"예외 발생: {str(exception)}")
        self.error(f"예외 유형: {type(exception).__name__}")
        self.error(f"스택 트레이스:\n{traceback.format_exc()}")
        
    def log_performance(self, message: str):
        """성능 정보 로깅"""
        self.info(f"성능 정보: {message}")

    def get_log_file_path(self) -> str:
        """로그 파일 경로 반환"""
        return self.DEFAULT_LOG_FILE

# 사용 예시:
# logger = Log()
# logger.info("정보 메시지")
# logger.error("에러 메시지") 

# 싱글톤 인스턴스 생성
log_instance = Log()