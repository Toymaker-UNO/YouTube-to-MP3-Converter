import re
import yt_dlp
import os
from model.Log import Log
from controller.logic.YoutubeTitle import YoutubeTitle
from controller.logic.ConverterToMP3 import ConverterToMP3

class Converter:
    def __init__(self, save_path=None):
        # 저장 경로 설정
        if save_path is None:
            self.save_path = os.path.join(os.getcwd(), 'downloads')
        else:
            self.save_path = save_path
            
        # 저장 경로가 없으면 생성
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)
            
        self.log = Log()
        self.youtube_title = YoutubeTitle()
        self.converter_to_mp3 = ConverterToMP3()
        
    def sanitize_filename(self, filename):
        """파일 이름에서 특수 문자를 제거합니다."""
        # Windows에서 허용되지 않는 문자들을 제거
        invalid_chars = r'[<>:"/\\|?*]'
        sanitized = re.sub(invalid_chars, '_', filename)
        # 공백을 언더스코어로 대체
        sanitized = sanitized.replace(' ', '_')
        return sanitized
        
    def is_valid_youtube_url(self, url):
        """YouTube URL의 유효성을 검사합니다."""
        return self.youtube_title.is_valid_url(url)
        
    def get_video_title(self, url):
        """YouTube URL에서 비디오 제목을 가져옵니다."""
        return self.youtube_title.get(url)
            
    def convert_to_mp3(self, input_file, title, quality, progress_callback=None):
        """다운로드된 비디오를 MP3로 변환합니다."""
        sanitized_title = self.sanitize_filename(title)
        return self.converter_to_mp3.convert(input_file, sanitized_title, quality, self.save_path, progress_callback)