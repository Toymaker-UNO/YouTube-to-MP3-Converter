import os
from datetime import datetime
import ffmpeg
from model.Log import log
import subprocess
import re
import threading
import sys

class ConverterToMP3:
    _instance = None
    _lock = threading.Lock()
    _is_frozen = getattr(sys, 'frozen', False)
    _base_path = os.path.dirname(sys.executable) if _is_frozen else os.path.dirname(os.path.abspath(__file__))

    def __new__(cls) -> 'ConverterToMP3':
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(ConverterToMP3, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        pass

    def get_ffmpeg_path(self):
        if self._is_frozen:
            # PyInstaller로 패키징된 경우
            return os.path.join(self._base_path, 'resources', 'ffmpeg', 'ffmpeg.exe')
        else:
            # 개발 환경에서 실행되는 경우
            return 'ffmpeg'  # 시스템 PATH 사용
            
    def convert(self, input_file, title, quality, save_path, progress_callback=None):
        """다운로드된 비디오를 MP3로 변환합니다."""
        try:
            # 저장 경로가 없으면 생성
            if not os.path.exists(save_path):
                os.makedirs(save_path)
                
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
            temp_mp3 = os.path.join(save_path, f"temp_{int(datetime.now().timestamp())}.mp3")
            
            # ffmpeg 명령어 구성
            ffmpeg_path = self.get_ffmpeg_path()
            cmd = [
                ffmpeg_path,
                '-i', input_file,
                '-acodec', 'libmp3lame',
                '-b:a', f'{quality_map[quality]}k',
                '-y',  # 덮어쓰기
                temp_mp3
            ]
            
            # 진행률 추적을 위한 프로세스 실행
            process = subprocess.Popen(
                cmd,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            # 진행률 추적
            duration = None
            while True:
                line = process.stderr.readline()
                if not line and process.poll() is not None:
                    break
                    
                # duration 정보 추출
                if duration is None and 'Duration:' in line:
                    match = re.search(r'Duration: (\d{2}):(\d{2}):(\d{2})', line)
                    if match:
                        hours, minutes, seconds = map(int, match.groups())
                        duration = hours * 3600 + minutes * 60 + seconds
                        
                # 진행률 정보 추출
                if duration is not None and 'time=' in line:
                    match = re.search(r'time=(\d{2}):(\d{2}):(\d{2})', line)
                    if match:
                        hours, minutes, seconds = map(int, match.groups())
                        current_time = hours * 3600 + minutes * 60 + seconds
                        if progress_callback:
                            progress = (current_time / duration) * 100
                            progress_callback(progress)
                            
            # 프로세스 종료 확인
            if process.returncode != 0:
                raise Exception("ffmpeg 변환 실패")
            
            # 최종 파일명으로 변경
            final_filename = f"{title}.mp3"
            final_path = os.path.join(save_path, final_filename)
            
            # 파일명 중복 처리
            counter = 1
            while os.path.exists(final_path):
                final_filename = f"{title}_{counter}.mp3"
                final_path = os.path.join(save_path, final_filename)
                counter += 1
                
            os.rename(temp_mp3, final_path)
            
            # 임시 파일 삭제
            if os.path.exists(input_file):
                os.remove(input_file)
                
            return final_path
            
        except Exception as e:
            log.error(f"변환 중 오류 발생: {str(e)}")
            raise 

# 싱글톤 인스턴스 생성
converter_to_mp3_instance = ConverterToMP3()