import yt_dlp
import os
from datetime import datetime
from model.Log import log_instance

class DownloadYoutubeAudio:
    def __init__(self):
        pass
            
    def download_audio(self, url, quality, save_path=None, progress_callback=None, speed_callback=None):
        """YouTube 비디오에서 오디오만 다운로드합니다."""
        try:
            # 저장 경로 설정
            save_path = self._setup_save_path(save_path)
            
            # 임시 파일명 생성
            temp_filename = f"temp_{int(datetime.now().timestamp())}"
            temp_path = os.path.join(save_path, f"{temp_filename}.%(ext)s")
            
            # yt_dlp 옵션 설정
            ydl_opts = self._make_ydl_option(quality, temp_path, progress_callback, speed_callback)
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                
                # 다운로드된 파일 경로 찾기
                downloaded_files = [f for f in os.listdir(save_path) if f.startswith(temp_filename)]
                if not downloaded_files:
                    raise FileNotFoundError("다운로드된 파일을 찾을 수 없습니다.")
                    
                downloaded_file = os.path.join(save_path, downloaded_files[0])
                return downloaded_file, info['title']
                
        except Exception as e:
            log_instance.error(f"다운로드 중 오류 발생: {str(e)}")
            raise
            
    def _setup_save_path(self, save_path):
        """저장 경로를 설정하고 필요한 경우 생성합니다."""
        if save_path is None:
            save_path = os.path.join(os.getcwd(), 'downloads')
            
        if not os.path.exists(save_path):
            os.makedirs(save_path)
            
        return save_path
            
    def _make_ydl_option(self, quality, temp_path, progress_callback, speed_callback):
        """yt_dlp 옵션을 생성합니다."""
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
        
        return {
            'format': f'bestaudio[abr<={quality_map[quality]}]',
            'outtmpl': temp_path,
            'progress_hooks': [lambda d: self._progress_hook(d, progress_callback, speed_callback)],
            'noplaylist': True,
            'extract_flat': False,
            'quiet': True,
            'no_warnings': True,
            'noprogress': True,
            'logger': log_instance,
            'verbose': False,
            'ignoreerrors': False
        }
            
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
                log_instance.error(f"진행 상황 업데이트 중 오류 발생: {str(e)}") 