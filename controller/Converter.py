import re
import yt_dlp
from datetime import datetime
import os
import time
import ffmpeg
from model.Log import Log

class Converter:
    def __init__(self, ffmpeg_path=None, save_path=None):
        self.ffmpeg_path = ffmpeg_path or "ffmpeg"  # 시스템 PATH에서 ffmpeg를 찾음
        self.save_path = save_path
        self.log = Log()
        
    def is_valid_youtube_url(self, url):
        """YouTube URL의 유효성을 검사합니다."""
        youtube_regex = r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?([^"&?/s]{11})'
        return bool(re.match(youtube_regex, url))
        
    def get_video_title(self, url):
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
            
    def download_video(self, url, quality, progress_callback=None, speed_callback=None):
        """YouTube 비디오를 다운로드합니다."""
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
            
            # 임시 파일명 생성
            temp_filename = f"temp_{int(datetime.now().timestamp())}"
            temp_path = os.path.join(self.save_path, f"{temp_filename}.%(ext)s")
            
            ydl_opts = {
                'format': f'bestaudio[abr<={quality_map[quality]}]',
                'outtmpl': temp_path,
                'progress_hooks': [lambda d: self._progress_hook(d, progress_callback, speed_callback)],
                'noplaylist': True,
                'extract_flat': False,
                'quiet': True,
                'no_warnings': True
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                
                # 다운로드된 파일 경로 찾기
                downloaded_files = [f for f in os.listdir(self.save_path) if f.startswith(temp_filename)]
                if not downloaded_files:
                    raise FileNotFoundError("다운로드된 파일을 찾을 수 없습니다.")
                    
                downloaded_file = os.path.join(self.save_path, downloaded_files[0])
                return downloaded_file, info['title']
                
        except Exception as e:
            self.log.error(f"다운로드 중 오류 발생: {str(e)}")
            raise
            
    def convert_to_mp3(self, input_file, title, quality):
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
                loglevel='error'
            )
            
            try:
                ffmpeg.run(stream, capture_stdout=True, capture_stderr=True)
            except ffmpeg.Error as e:
                raise Exception(f"FFmpeg 변환 실패: {e.stderr.decode()}")
                
            # 최종 파일명으로 변경
            final_filename = f"{title}.mp3"
            final_path = os.path.join(self.save_path, final_filename)
            
            # 파일명 중복 처리
            counter = 1
            while os.path.exists(final_path):
                final_filename = f"{title}_{counter}.mp3"
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
            
    def _progress_hook(self, d, progress_callback, speed_callback):
        """다운로드 진행 상황을 추적하고 콜백을 호출합니다."""
        if d['status'] == 'downloading':
            try:
                total = d.get('total_bytes', 0)
                downloaded = d.get('downloaded_bytes', 0)
                speed = d.get('speed', 0)
                
                if total > 0 and progress_callback:
                    percentage = int((downloaded / total) * 100)
                    progress_callback(percentage)
                    
                if speed and speed_callback:
                    speed_str = f"{speed/1024/1024:.1f} MB/s"
                    speed_callback(speed_str)
                    
            except Exception as e:
                self.log.error(f"진행 상황 업데이트 중 오류 발생: {str(e)}") 