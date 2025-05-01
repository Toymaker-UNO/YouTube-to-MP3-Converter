import re

class CheckURL:
    def __init__(self):
        pass
        
    def is_valid_youtube_url(self, url):
        """YouTube URL의 유효성을 검사합니다."""
        youtube_regex = r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?([^"&?/s]{11})'
        return bool(re.match(youtube_regex, url)) 