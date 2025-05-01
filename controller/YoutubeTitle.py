import re
import yt_dlp
from model.Log import Log

class YoutubeTitle:
    def __init__(self):
        self.log = Log()
        
    def get(self, url):
        """YouTube URL에서 비디오 제목을 가져옵니다."""
        try:
            # URL 정규화
            if 'youtu.be' in url:
                video_id = url.split('youtu.be/')[-1].split('?')[0]
                url = f'https://www.youtube.com/watch?v={video_id}'
            elif '&' in url:
                url = url.split('&')[0]
                
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
                'noplaylist': True,
                'ignoreerrors': False,
                'verbose': False,
                'force_generic_extractor': False
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if info is None:
                    self.log.error("비디오 정보를 추출할 수 없습니다.")
                    return None
                    
                if 'entries' in info:  # 플레이리스트인 경우
                    self.log.error("플레이리스트 URL은 지원하지 않습니다.")
                    return None
                        
                if 'title' not in info:
                    self.log.error("제목 정보가 없습니다.")
                    return None
                    
                return info['title']
                
        except Exception as e:
            self.log.error(f"비디오 정보를 가져오는 중 오류 발생: {str(e)}")
            return None
            
    def is_valid_url(self, url):
        """YouTube URL의 유효성을 검사합니다."""
        youtube_regex = r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?([^"&?/s]{11})'
        return bool(re.match(youtube_regex, url)) 