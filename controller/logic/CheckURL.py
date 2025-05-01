import re
import threading

class CheckURL:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(CheckURL, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        pass
        
    def is_valid_youtube_url(self, url):
        """YouTube URL의 유효성을 검사합니다."""
        youtube_regex = r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?([^"&?/s]{11})'
        return bool(re.match(youtube_regex, url))

# 싱글톤 인스턴스 생성
check_url_instance = CheckURL() 