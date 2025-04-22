import json
from typing import Dict, Any

class Configuration:
    _instance = None
    _config: Dict[str, Any] = {}
    _initialized = False
    _config_file: str = ""
    
    # 필수 설정 키 목록
    _required_keys = {
        "gui": {
            "main_window": {
                "position": {
                    "x": str,
                    "y": str,
                    "width": str,
                    "height": str,
                    "fixed_size": bool
                },
                "stylesheet": {
                    "QMainWindow": dict
                },
                "animation": {
                    "enabled": bool,
                    "duration": int,
                    "easing": str,
                    "initial_opacity": float,
                    "start_delay": int
                },
                "customizing": {
                    "title": str,
                    "icon_path": str
                }
            },
            "labels": list  # 라벨 설정을 배열로 변경
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
            
        Raises:
            FileNotFoundError: 설정 파일이 존재하지 않는 경우
            json.JSONDecodeError: 설정 파일이 유효한 JSON 형식이 아닌 경우
            ValueError: 필수 설정이 누락되었거나 타입이 맞지 않는 경우
        """
        if self._initialized:
            print("이미 초기화가 완료되었습니다.")
            return
        
        self._initialized = True
        self._config_file = config_file
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                self._config = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"설정 파일을 찾을 수 없습니다: {config_file}")
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"설정 파일이 유효한 JSON 형식이 아닙니다: {str(e)}", e.doc, e.pos)
            
        # 설정 검증
        self._validate_config()
    
    def _validate_config(self) -> None:
        """설정 파일의 필수 키와 값의 타입을 검증합니다.
        
        Raises:
            ValueError: 필수 설정이 누락되었거나 타입이 맞지 않는 경우
        """
        def validate_dict(config: dict, required: dict, path: str = "") -> None:
            for key, expected_type in required.items():
                current_path = f"{path}.{key}" if path else key
                
                if key not in config:
                    raise ValueError(f"필수 설정이 누락되었습니다: {current_path}")
                
                if isinstance(expected_type, dict):
                    if not isinstance(config[key], dict):
                        raise ValueError(f"설정 타입이 맞지 않습니다: {current_path} (기대: dict, 실제: {type(config[key])})")
                    validate_dict(config[key], expected_type, current_path)
                else:
                    if not isinstance(config[key], expected_type):
                        raise ValueError(f"설정 타입이 맞지 않습니다: {current_path} (기대: {expected_type}, 실제: {type(config[key])})")
        
        validate_dict(self._config, self._required_keys)
    
    def get(self, *keys: str) -> Any:
        """설정 값을 가져옵니다.
        
        Args:
            *keys: 가져올 설정의 키 값들 (여러 단계의 중첩된 키)
            
        Returns:
            Any: 설정 값
            
        Raises:
            KeyError: 설정 키가 존재하지 않는 경우
        """
        result = self._config
        for key in keys:
            if not isinstance(result, dict) or key not in result:
                raise KeyError(f"설정 키가 존재하지 않습니다: {'.'.join(keys)}")
            result = result[key]
        return result

    def set(self, value: Any, *keys: str) -> None:
        """설정 값을 업데이트합니다.
        
        Args:
            value: 설정할 값
            *keys: 업데이트할 설정의 키 값들 (여러 단계의 중첩된 키)
            
        Raises:
            KeyError: 설정 키가 존재하지 않는 경우
            ValueError: 설정 값의 타입이 맞지 않는 경우
        """
        if not keys:
            return
            
        # 타입 검증
        current = self._required_keys
        for key in keys[:-1]:
            if not isinstance(current, dict) or key not in current:
                raise KeyError(f"설정 키가 존재하지 않습니다: {'.'.join(keys)}")
            current = current[key]
            
        expected_type = current.get(keys[-1])
        if expected_type and not isinstance(value, expected_type):
            raise ValueError(f"설정 값의 타입이 맞지 않습니다: {'.'.join(keys)} (기대: {expected_type}, 실제: {type(value)})")
            
        # 값 설정
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
        """
        if config_file is None:
            config_file = self._config_file
            
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"설정 파일 저장 중 오류 발생: {str(e)}") 


# 싱글톤 인스턴스 생성
configuration_instance = Configuration()