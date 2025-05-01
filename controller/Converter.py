import re
import yt_dlp
from datetime import datetime
import os
import time
import ffmpeg
from model.Log import Log
from controller.YoutubeTitle import YoutubeTitle

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
        try:
            quality_map = {
                '320K': '320',
                '256K': '256',
                '192K': '192',
                '160K': '160',
                '128K': '128',
                '96K': '96',
                '64K': '64',
                '48K': '48'
            }
            
            # 임시 MP3 파일 경로
            temp_mp3 = os.path.join(self.save_path, f"temp_{int(datetime.now().timestamp())}.mp3")
            
            # ffmpeg-python을 사용하여 변환
            stream = ffmpeg.input(input_file)
            stream = ffmpeg.output(
                stream,
                temp_mp3,
                acodec='libmp3lame',
                audio_bitrate=f'{quality_map[quality]}k',
                loglevel='info'
            )
            
            # 진행률 콜백을 위한 프로브
            probe = ffmpeg.probe(input_file)
            total_duration = float(probe['format']['duration'])
            
            # 변환 실행
            ffmpeg.run(stream, capture_stdout=True, capture_stderr=True)
            
            # 최종 파일명으로 변경
            final_filename = f"{self.sanitize_filename(title)}.mp3"
            final_path = os.path.join(self.save_path, final_filename)
            
            # 파일명 중복 처리
            counter = 1
            while os.path.exists(final_path):
                final_filename = f"{self.sanitize_filename(title)}_{counter}.mp3"
                final_path = os.path.join(self.save_path, final_filename)
                counter += 1
                
            os.rename(temp_mp3, final_path)
            
            # 임시 파일 삭제
            if os.path.exists(input_file):
                os.remove(input_file)
                
            return final_path
            
        except Exception as e:
            self.log.error(f"변환 중 오류 발생: {str(e)}")
            raise