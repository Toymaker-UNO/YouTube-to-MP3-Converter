import json
import os
import shutil
from typing import Dict, Any

class Configuration:
    _instance = None
    _config: Dict[str, Any] = None
    _config_file: str = None
    
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
            cls._instance._config = {}
            cls._instance._config_file = None
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
        # 내부 변수 초기화
        self._config = {}
        self._config_file = config_file
        
        try:
            # 설정 파일이 존재하지 않으면 기본 설정 파일 생성
            if not os.path.exists(config_file):
                self._create_default_config(config_file)
                
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

    def _create_default_config(self, config_file: str) -> None:
        """기본 설정 파일을 생성합니다.
        
        Args:
            config_file (str): 생성할 설정 파일의 경로
        """
        # 기본 설정 내용
        default_config = {
            "logging": {
                "enable_logging": False,
                "log_file": "log.txt",
                "max_log_size_mb": 10,
                "max_backup_count": 2,
                "encoding": "utf-8",
                "log_level": "DEBUG",
                "enable_performance_logging": True
            },
            "gui": {
                "main_window": {
                    "position": {
                        "x": "100px",
                        "y": "100px",
                        "width": "800px",
                        "height": "350px",
                        "fixed_size": True
                    },
                    "stylesheet": {
                        "QMainWindow": {
                            "background-color": "#2b2b2b",
                            "color": "#ffffff",
                            "border": "1px solid #3c3f41",
                            "border-radius": "5px",
                            "padding": "20px",
                            "margin": "5px"
                        }
                    },
                    "animation": {
                        "enabled": False,
                        "duration": 300,
                        "easing": "OutCubic",
                        "initial_opacity": 1.0,
                        "start_delay": 100
                    },
                    "customizing": {
                        "title": "YouTube to MP3",
                        "icon_path": "resources/icon.png"
                    }
                },
                "labels": [
                    {
                        "id": "url_label",
                        "position": {
                            "x": "30px",
                            "y": "30px",
                            "alignment": "left",
                            "margin": {
                                "top": "10px",
                                "right": "10px",
                                "bottom": "10px",
                                "left": "10px"
                            }
                        },
                        "stylesheet": {
                            "QLabel": {
                                "color": "#ffffff",
                                "font-size": "14px",
                                "font-family": "Arial",
                                "font-weight": "normal",
                                "background-color": "transparent",
                                "border": "0px solid transparent",
                                "border-radius": "0px",
                                "padding": "5px"
                            }
                        },
                        "animation": {
                            "enabled": False,
                            "duration": 200,
                            "easing": "OutCubic",
                            "initial_opacity": 0.0,
                            "start_delay": 0
                        },
                        "customizing": {
                            "text": "YouTube URL:"
                        }
                    },
                    {
                        "id": "quality_label",
                        "position": {
                            "x": "30px",
                            "y": "70px",
                            "alignment": "left",
                            "margin": {
                                "top": "10px",
                                "right": "10px",
                                "bottom": "10px",
                                "left": "10px"
                            }
                        },
                        "stylesheet": {
                            "QLabel": {
                                "color": "#ffffff",
                                "font-size": "14px",
                                "font-family": "Arial",
                                "font-weight": "normal",
                                "background-color": "transparent",
                                "border": "0px solid transparent",
                                "border-radius": "0px",
                                "padding": "5px"
                            }
                        },
                        "animation": {
                            "enabled": False,
                            "duration": 200,
                            "easing": "OutCubic",
                            "initial_opacity": 0.0,
                            "start_delay": 0
                        },
                        "customizing": {
                            "text": "Audio Quality:"
                        }
                    }
                ],
                "line_edits": [
                    {
                        "id": "url_input",
                        "position": {
                            "x": "150px",
                            "y": "30px",
                            "width": "450px",
                            "height": "30px"
                        },
                        "stylesheet": {
                            "QLineEdit": {
                                "color": "#ffffff",
                                "background-color": "#3c3f41",
                                "border": "1px solid #4d4d4d",
                                "border-radius": "3px",
                                "padding": "5px",
                                "font-size": "14px",
                                "font-family": "Arial"
                            },
                            "QLineEdit:disabled": {
                                "background-color": "#2b2b2b",
                                "color": "#555555",
                                "border": "1px solid #3c3f41"
                            }
                        },
                        "animation": {
                            "enabled": False,
                            "duration": 200,
                            "easing": "OutCubic",
                            "initial_opacity": 1.0,
                            "start_delay": 0
                        },
                        "customizing": {
                            "placeholder_text": "Enter YouTube URL here...",
                            "max_length": 1000,
                            "enabled": True
                        }
                    }
                ],
                "push_buttons": [
                    {
                        "id": "check_url",
                        "position": {
                            "x": "620px",
                            "y": "30px",
                            "width": "150px",
                            "height": "30px"
                        },
                        "stylesheet": {
                            "QPushButton": {
                                "background-color": "#2b2b2b",
                                "color": "#ffffff",
                                "border": "2px solid #3b3b3b",
                                "font-size": "12px"
                            },
                            "QPushButton:hover": {
                                "background-color": "#3b3b3b"
                            },
                            "QPushButton:pressed": {
                                "background-color": "#1b1b1b",
                                "border": "2px solid #2b2b2b"
                            },
                            "QPushButton:disabled": {
                                "background-color": "#2b2b2b",
                                "color": "#555555"
                            }
                        },
                        "animation": {
                            "enabled": False,
                            "duration": 200,
                            "easing": "OutCubic",
                            "initial_opacity": 1.0,
                            "start_delay": 0
                        },
                        "customizing": {
                            "text": "Check URL",
                            "icon_path": "resources/check_url_button.png",
                            "tooltip": "Check URL"
                        }
                    },
                    {
                        "id": "download",
                        "position": {
                            "x": "620px",
                            "y": "70px",
                            "width": "150px",
                            "height": "30px"
                        },
                        "stylesheet": {
                            "QPushButton": {
                                "background-color": "#2b2b2b",
                                "color": "#ffffff",
                                "border": "2px solid #3b3b3b",
                                "font-size": "12px"
                            },
                            "QPushButton:hover": {
                                "background-color": "#3b3b3b"
                            },
                            "QPushButton:pressed": {
                                "background-color": "#1b1b1b",
                                "border": "2px solid #2b2b2b"
                            },
                            "QPushButton:disabled": {
                                "background-color": "#2b2b2b",
                                "color": "#555555"
                            }
                        },
                        "animation": {
                            "enabled": False,
                            "duration": 200,
                            "easing": "OutCubic",
                            "initial_opacity": 1.0,
                            "start_delay": 0
                        },
                        "customizing": {
                            "text": "Download",
                            "icon_path": "resources/download.png",
                            "tooltip": "Start downloading MP3",
                            "enabled": False
                        }
                    }
                ],
                "combo_boxes": [
                    {
                        "id": "audio_quality",
                        "position": {
                            "x": "150px",
                            "y": "70px",
                            "width": "450px",
                            "height": "30px"
                        },
                        "stylesheet": {
                            "QComboBox": {
                                "background-color": "#3c3f41",
                                "color": "#ffffff",
                                "border": "1px solid #4d4d4d",
                                "border-radius": "3px",
                                "padding": "5px",
                                "font-size": "14px",
                                "font-family": "Arial"
                            },
                            "QComboBox:disabled": {
                                "background-color": "#2b2b2b",
                                "color": "#555555",
                                "border": "1px solid #3c3f41"
                            },
                            "QComboBox QAbstractItemView": {
                                "background-color": "#2b2b2b",
                                "color": "#ffffff",
                                "selection-background-color": "#3c3f41",
                                "border": "1px solid #3c3f41",
                                "outline": "none"
                            }
                        },
                        "animation": {
                            "enabled": False,
                            "duration": 200,
                            "easing": "OutCubic",
                            "initial_opacity": 1.0,
                            "start_delay": 0
                        },
                        "customizing": {
                            "items": [
                                "320K", 
                                "256K", 
                                "192K", 
                                "160K", 
                                "128K", 
                                "96K", 
                                "64K", 
                                "48K"],
                            "default_index": 0,
                            "enabled": False
                        }
                    }
                ],
                "plain_text_edits": [
                    {
                        "id": "log_display",
                        "position": {
                            "x": "30px",
                            "y": "120px",
                            "width": "740px",
                            "height": "200px"
                        },
                        "stylesheet": {
                            "QPlainTextEdit": {
                                "background-color": "#2b2b2b",
                                "color": "#ffffff",
                                "border": "1px solid #3c3f41",
                                "border-radius": "3px",
                                "padding": "5px",
                                "font-family": "Consolas, 'Courier New', monospace",
                                "font-size": "12px"
                            },
                            "QScrollBar:vertical": {
                                "background-color": "#2b2b2b",
                                "width": "12px",
                                "margin": "0px"
                            },
                            "QScrollBar::handle:vertical": {
                                "background-color": "#3c3f41",
                                "min-height": "20px",
                                "border-radius": "6px"
                            },
                            "QScrollBar::handle:vertical:hover": {
                                "background-color": "#4a90e2"
                            },
                            "QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical": {
                                "height": "0px"
                            }
                        },
                        "customizing": {
                            "editable": False,
                            "text_interaction": "TextSelectableByMouse",
                            "line_wrap": False,
                            "tab_stop_width": 4,
                            "scroll_bar_vertical": True,
                            "scroll_bar_horizontal": True,
                            "cursor_visible": False
                        }
                    }
                ]
            }
        }
        
        try:
            # 설정 파일 생성
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2, ensure_ascii=False)
            #print(f"기본 설정 파일이 생성되었습니다: {config_file}")
            
        except Exception as e:
            print(f"기본 설정 파일 생성 중 오류 발생: {str(e)}")
            raise


# 싱글톤 인스턴스 생성
configuration_instance = Configuration()