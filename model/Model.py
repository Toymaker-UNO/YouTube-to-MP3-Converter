import json
import os
from model.Configuration import configuration_instance
from model.Log import log_instance

class Model:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Model, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        pass
    
    def initialize(self, config_path):
        configuration_instance.initialize(config_path)
        
        # 로깅 설정 가져오기
        enable_logging = configuration_instance.get("logging", "enable_logging")
        log_file = configuration_instance.get("logging", "log_file")
        max_size_mb = configuration_instance.get("logging", "max_log_size_mb")
        backup_count = configuration_instance.get("logging", "max_backup_count")
        encoding = configuration_instance.get("logging", "encoding")
        log_level = configuration_instance.get("logging", "log_level")
        
        # Log 초기화
        log_instance.initialize(
            enable_logging=enable_logging,
            log_file=log_file,
            max_size_mb=max_size_mb,
            backup_count=backup_count,
            encoding=encoding,
            log_level=log_level
        )

# 싱글톤 인스턴스 생성
model_instance = Model() 