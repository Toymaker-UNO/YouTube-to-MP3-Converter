import json
from typing import Dict, Any

class Configuration:
    _instance = None
    _config: Dict[str, Any] = {}
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Configuration, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        pass
    
    def initialize(self, config_file: str) -> None:
        """JSON 형식의 설정 파일을 파싱하여 초기화합니다.
        
        Args:
            config_file (str): 파싱할 JSON 파일의 경로
        """
        if self._initialized:
            print("이미 초기화가 완료되었습니다.")
            return
        
        self._initialized = True
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                self._config = json.load(f)
        except Exception as e:
            print(f"설정 파일 파싱 중 오류 발생: {str(e)}")
            self._config = {} 
    
    def get(self, *keys: str) -> Any:
        """설정 값을 가져옵니다.
        
        Args:
            *keys: 가져올 설정의 키 값들 (여러 단계의 중첩된 키)
            
        Returns:
            Any: 설정 값. 키가 없는 경우 None을 반환
            
        Examples:
            # 단일 키
            ffmpeg_path = config.get("ffmpeg_path")
            
            # 중첩된 키
            log_file = config.get("logging", "log_file")
            
            # 더 깊은 중첩 구조
            value = config.get("level1", "level2", "level3", "level4")
        """
        result = self._config
        for key in keys:
            if isinstance(result, dict):
                result = result.get(key)
            else:
                return None
        return result 