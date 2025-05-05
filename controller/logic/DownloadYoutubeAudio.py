import yt_dlp
import os
import threading
from datetime import datetime
from model.Log import log

class DownloadYoutubeAudio:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(DownloadYoutubeAudio, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        pass
            
    def download_audio(self, url, quality, save_path=None, progress_callback=None, speed_callback=None):
        """YouTube 비디오에서 오디오만 다운로드합니다."""
        try:
            log.info(f"다운로드 시작 - URL: {url}")
            log.info(f"다운로드 설정 - 품질: {quality}")
            
            # 저장 경로 설정
            save_path = self._setup_save_path(save_path)
            log.info(f"저장 경로: {save_path}")
            
            # 임시 파일명 생성
            temp_filename = f"temp_{int(datetime.now().timestamp())}"
            temp_path = os.path.join(save_path, f"{temp_filename}.%(ext)s")
            log.info(f"임시 파일 경로: {temp_path}")
            
            # yt_dlp 옵션 설정
            ydl_opts = self._make_ydl_option(quality, temp_path, progress_callback, speed_callback)
            log.info(f"yt-dlp 옵션: {ydl_opts}")
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                log.info("비디오 정보 추출 중...")
                info = ydl.extract_info(url, download=True)
                log.info(f"비디오 제목: {info['title']}")
                
                # 다운로드된 파일 경로 찾기
                downloaded_files = [f for f in os.listdir(save_path) if f.startswith(temp_filename)]
                if not downloaded_files:
                    error_msg = "다운로드된 파일을 찾을 수 없습니다."
                    log.error(error_msg)
                    raise FileNotFoundError(error_msg)
                    
                downloaded_file = os.path.join(save_path, downloaded_files[0])
                log.info(f"다운로드 완료: {downloaded_file}")
                return downloaded_file, info['title']
                
        except Exception as e:
            log.error(f"다운로드 중 오류 발생: {str(e)}")
            log.exception("상세 오류 정보:")
            raise
            
    def _setup_save_path(self, save_path):
        """저장 경로를 설정하고 필요한 경우 생성합니다."""
        if save_path is None:
            save_path = os.path.join(os.getcwd(), 'downloads')
            log.info(f"기본 저장 경로 사용: {save_path}")
            
        if not os.path.exists(save_path):
            log.info(f"저장 경로 생성: {save_path}")
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
        
        log.info(f"선택된 품질: {quality} ({quality_map[quality]}kbps)")
        
        return {
            'format': f'bestaudio[abr<={quality_map[quality]}]',
            'outtmpl': temp_path,
            'progress_hooks': [lambda d: self._progress_hook(d, progress_callback, speed_callback)],
            'noplaylist': True,
            'extract_flat': False,
            'quiet': True,
            'no_warnings': True,
            'noprogress': True,
            'logger': log,
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
                    log.debug(f"다운로드 진행률: {percentage}%")
                    
                if speed and speed_callback:
                    speed_str = f"{speed/1024/1024:.1f} MB/s"
                    speed_callback(speed_str)
                    log.debug(f"다운로드 속도: {speed_str}")
                    
            except Exception as e:
                log.error(f"진행 상황 업데이트 중 오류 발생: {str(e)}")
                log.exception("상세 오류 정보:")

# 싱글톤 인스턴스 생성
download_youtube_audio_instance = DownloadYoutubeAudio() 