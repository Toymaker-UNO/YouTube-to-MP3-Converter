import logging
import os
import time
from logging.handlers import RotatingFileHandler
from typing import Optional

class Log:
    _instance: Optional['Log'] = None
    _initialized: bool = False

    # 로그 설정 상수
    LOG_FILE = 'youtube_to_mp3.log.txt'
    MAX_SIZE = 10 * 1024 * 1024  # 10MB
    BACKUP_COUNT = 2
    ENCODING = 'utf-8'
    
    # 로그 레벨 매핑
    LEVEL_MAP = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Log, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._initialized = True
            self.logger = logging.getLogger('YouTubeToMP3')
            self.logger.setLevel(logging.DEBUG)
            self._setup_handlers()

    def _setup_handlers(self):
        """로그 핸들러 설정"""
        # 파일 핸들러 설정
        file_handler = RotatingFileHandler(
            self.LOG_FILE,
            maxBytes=self.MAX_SIZE,
            backupCount=self.BACKUP_COUNT,
            encoding=self.ENCODING
        )
        file_handler.setLevel(logging.DEBUG)
        
        # 콘솔 핸들러 설정
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # 밀리초 포맷터 설정
        formatter = logging.Formatter(
            '%(asctime)s.%(msecs)03d - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # 핸들러 추가
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def debug(self, message: str):
        """디버그 레벨 로그"""
        self.logger.debug(message)

    def info(self, message: str):
        """정보 레벨 로그"""
        self.logger.info(message)

    def warning(self, message: str):
        """경고 레벨 로그"""
        self.logger.warning(message)

    def error(self, message: str):
        """에러 레벨 로그"""
        self.logger.error(message)

    def critical(self, message: str):
        """치명적 레벨 로그"""
        self.logger.critical(message)

    def log_exception(self, exception: Exception):
        """예외 로깅"""
        self.error(f"예외 발생: {str(exception)}")
        self.debug(f"예외 상세: {exception.__class__.__name__}")

    def log_performance(self, message: str):
        """성능 로깅"""
        self.info(f"성능 정보: {message}")

    def set_level(self, level: str):
        """로그 레벨 설정"""
        self.logger.setLevel(self.LEVEL_MAP.get(level, logging.INFO))

    def get_log_file_path(self) -> str:
        """로그 파일 경로 반환"""
        return self.LOG_FILE

    def set_max_log_size_mb(self, size_mb: int):
        """로그 파일의 최대 크기를 MB 단위로 설정"""
        if size_mb < 1:
            self.warning(f"로그 파일 크기가 너무 작습니다: {size_mb}MB. 최소 1MB로 설정됩니다.")
            size_mb = 1
            
        max_bytes = size_mb * 1024 * 1024  # MB를 바이트로 변환
        
        # 모든 핸들러를 순회하면서 RotatingFileHandler 찾기
        for handler in self.logger.handlers:
            if isinstance(handler, RotatingFileHandler):
                handler.maxBytes = max_bytes
                self.info(f"로그 파일 최대 크기가 {size_mb}MB로 설정되었습니다.")
                return
                
        self.warning("RotatingFileHandler를 찾을 수 없습니다.")

    def set_max_backup_count(self, count: int):
        """로그 파일의 최대 백업 개수 설정"""
        if count < 0:
            self.warning(f"백업 개수가 음수입니다: {count}. 0으로 설정됩니다.")
            count = 0
            
        # 모든 핸들러를 순회하면서 RotatingFileHandler 찾기
        for handler in self.logger.handlers:
            if isinstance(handler, RotatingFileHandler):
                handler.backupCount = count
                self.info(f"로그 파일 백업 개수가 {count}개로 설정되었습니다.")
                return
                
        self.warning("RotatingFileHandler를 찾을 수 없습니다.")

    def set_encoding(self, encoding: str):
        """로그 파일의 인코딩 설정"""
        if not encoding:
            self.warning("인코딩이 지정되지 않았습니다. 기본값 'utf-8'을 사용합니다.")
            encoding = 'utf-8'
            
        # 모든 핸들러를 순회하면서 RotatingFileHandler 찾기
        for handler in self.logger.handlers:
            if isinstance(handler, RotatingFileHandler):
                # 현재 파일을 닫고
                handler.close()
                # 새로운 인코딩으로 다시 열기
                handler.encoding = encoding
                self.info(f"로그 파일 인코딩이 {encoding}로 설정되었습니다.")
                return
                
        self.warning("RotatingFileHandler를 찾을 수 없습니다.")

    def set_log_file_path(self, file_path: str):
        """로그 파일의 경로 설정"""
        if not file_path:
            self.warning("로그 파일 경로가 지정되지 않았습니다.")
            return
            
        # 모든 핸들러를 순회하면서 RotatingFileHandler 찾기
        for handler in self.logger.handlers:
            if isinstance(handler, RotatingFileHandler):
                # 현재 파일을 닫고
                handler.close()
                # 새로운 경로로 핸들러 다시 생성
                new_handler = RotatingFileHandler(
                    file_path,
                    maxBytes=handler.maxBytes,
                    backupCount=handler.backupCount,
                    encoding=handler.encoding
                )
                new_handler.setLevel(handler.level)
                new_handler.setFormatter(handler.formatter)
                
                # 기존 핸들러 제거
                self.logger.removeHandler(handler)
                # 새로운 핸들러 추가
                self.logger.addHandler(new_handler)
                
                # 클래스 변수 업데이트
                self.LOG_FILE = file_path
                self.info(f"로그 파일 경로가 {file_path}로 설정되었습니다.")
                return
                
        self.warning("RotatingFileHandler를 찾을 수 없습니다.")

    def enable_logging(self, enabled: bool):
        """로깅 활성화/비활성화 설정"""
        if enabled:
            # 로깅 활성화
            self.logger.disabled = False
            self.info("로깅이 활성화되었습니다.")
        else:
            # 비활성화 전에 마지막 로그 메시지
            self.info("로깅이 비활성화됩니다.")
            # 로깅 비활성화
            self.logger.disabled = True

    def is_logging_enabled(self) -> bool:
        """현재 로깅 활성화 상태 반환"""
        return not self.logger.disabled

# 사용 예시:
# logger = Log()
# logger.info("정보 메시지")
# logger.error("에러 메시지") 