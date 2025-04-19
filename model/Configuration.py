import json
from typing import Dict, Any

class Configuration:
    _instance = None
    _config: Dict[str, Any] = {}
    _initialized = False
    _config_file: str = ""
    
    # 기본값 정의
    _default_config = {
        "gui": {
            "main_window": {
                "title": "YouTube to MP3 Converter",
                "icon_path": "resources/icon.png",
                "size": {
                    "width": 800,
                    "height": 600
                },
                "position": {
                    "x": 100,
                    "y": 100
                },
                "style": {
                    "theme": "dark",
                    "background_color": "#2b2b2b",
                    "text_color": "#ffffff",
                    "border_color": "#3c3f41",
                    "border_width": "1px",
                    "border_radius": "5px",
                    "padding": "10px",
                    "margin": "5px"
                },
                "animation": {
                    "enabled": True,
                    "duration": 300,
                    "easing": "OutCubic"
                }
            }
        }
    }
    
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
        self._config_file = config_file
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                self._config = json.load(f)
        except Exception as e:
            print(f"설정 파일 파싱 중 오류 발생: {str(e)}")
            self._config = {}
            
        # 기본값과 설정 파일의 값을 병합
        self._merge_defaults()
    
    def _merge_defaults(self) -> None:
        """기본값과 설정 파일의 값을 병합합니다."""
        def merge_dicts(d1: dict, d2: dict) -> dict:
            result = d1.copy()
            for key, value in d2.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = merge_dicts(result[key], value)
                else:
                    result[key] = value
            return result
        
        self._config = merge_dicts(self._default_config, self._config)
    
    def get(self, *keys: str) -> Any:
        """설정 값을 가져옵니다.
        
        Args:
            *keys: 가져올 설정의 키 값들 (여러 단계의 중첩된 키)
            
        Returns:
            Any: 설정 값. 키가 없는 경우 기본값을 반환
            
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

    def set(self, value: Any, *keys: str) -> None:
        """설정 값을 업데이트합니다.
        
        Args:
            value: 설정할 값
            *keys: 업데이트할 설정의 키 값들 (여러 단계의 중첩된 키)
            
        Examples:
            # 단일 키
            config.set("C:/ffmpeg/bin", "ffmpeg_path")
            
            # 중첩된 키
            config.set("app.log", "logging", "log_file")
            
            # 더 깊은 중첩 구조
            config.set("new_value", "level1", "level2", "level3", "level4")
        """
        if not keys:
            return
            
        current = self._config
        for i, key in enumerate(keys[:-1]):
            if key not in current:
                current[key] = {}
            current = current[key]
            
        current[keys[-1]] = value

    def save(self, config_file: str = None) -> None:
        """현재 설정을 JSON 파일로 저장합니다.
        
        Args:
            config_file (str, optional): 저장할 JSON 파일의 경로. 
                                      지정하지 않으면 initialize에서 사용한 파일 경로를 사용합니다.
            
        Examples:
            config.save()  # initialize에서 사용한 파일 경로로 저장
            config.save("new_config.json")  # 새로운 파일 경로로 저장
        """
        if config_file is None:
            config_file = self._config_file
            
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"설정 파일 저장 중 오류 발생: {str(e)}") 