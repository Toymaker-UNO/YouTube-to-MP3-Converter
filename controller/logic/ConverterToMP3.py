import os
from datetime import datetime
import ffmpeg
from model.Log import log
import subprocess
import re
import threading
import sys

def get_application_path():
    if getattr(sys, 'frozen', False):
        # PyInstaller로 패키징된 경우
        return os.path.dirname(sys.executable)
    else:
        # 개발 환경
        return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class ConverterToMP3:
    _instance = None
    _lock = threading.Lock()
    _is_frozen = getattr(sys, 'frozen', False)
    _base_path = get_application_path()

    def __new__(cls) -> 'ConverterToMP3':
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(ConverterToMP3, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        pass

    def get_ffmpeg_path(self):
        if getattr(sys, 'frozen', False):
            # PyInstaller로 패키징된 경우
            ffmpeg_path = os.path.join(self._base_path, 'resources', 'ffmpeg', 'ffmpeg.exe')
            if not os.path.exists(ffmpeg_path):
                # 상대 경로로 시도
                ffmpeg_path = os.path.join('resources', 'ffmpeg', 'ffmpeg.exe')
            log.info(f"FFmpeg 경로 (패키징): {ffmpeg_path}")
            return ffmpeg_path
        else:
            # 개발 환경
            log.info("FFmpeg 경로 (개발): 시스템 PATH 사용")
            return 'ffmpeg'  # 시스템 PATH 사용
            
    def convert(self, input_file, title, quality, save_path, progress_callback=None):
        """다운로드된 비디오를 MP3로 변환합니다."""
        try:
            log.info(f"MP3 변환 시작 - 입력 파일: {input_file}")
            log.info(f"변환 설정 - 제목: {title}, 품질: {quality}, 저장 경로: {save_path}")
            
            # 저장 경로가 없으면 생성
            if not os.path.exists(save_path):
                log.info(f"저장 경로 생성: {save_path}")
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
            log.info(f"임시 MP3 파일 경로: {temp_mp3}")
            
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
            log.info(f"FFmpeg 명령어: {' '.join(cmd)}")
            
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
                        log.info(f"변환할 파일 길이: {hours}시간 {minutes}분 {seconds}초")
                        
                # 진행률 정보 추출
                if duration is not None and 'time=' in line:
                    match = re.search(r'time=(\d{2}):(\d{2}):(\d{2})', line)
                    if match:
                        hours, minutes, seconds = map(int, match.groups())
                        current_time = hours * 3600 + minutes * 60 + seconds
                        if progress_callback:
                            progress = (current_time / duration) * 100
                            progress_callback(progress)
                            log.debug(f"변환 진행률: {progress:.1f}%")
                            
            # 프로세스 종료 확인
            if process.returncode != 0:
                error_msg = f"FFmpeg 변환 실패 (종료 코드: {process.returncode})"
                log.error(error_msg)
                raise Exception(error_msg)
            
            # 최종 파일명으로 변경
            final_filename = f"{title}.mp3"
            final_path = os.path.join(save_path, final_filename)
            log.info(f"최종 파일 경로: {final_path}")
            
            # 파일명 중복 처리
            counter = 1
            while os.path.exists(final_path):
                final_filename = f"{title}_{counter}.mp3"
                final_path = os.path.join(save_path, final_filename)
                counter += 1
                log.info(f"파일명 중복으로 변경: {final_filename}")
                
            log.info(f"임시 파일을 최종 파일로 이동: {temp_mp3} -> {final_path}")
            os.rename(temp_mp3, final_path)
            
            # 임시 파일 삭제
            if os.path.exists(input_file):
                log.info(f"원본 임시 파일 삭제: {input_file}")
                os.remove(input_file)
                
            log.info(f"MP3 변환 완료: {final_path}")
            return final_path
            
        except Exception as e:
            log.error(f"변환 중 오류 발생: {str(e)}")
            log.exception("상세 오류 정보:")
            raise 

# 싱글톤 인스턴스 생성
converter_to_mp3_instance = ConverterToMP3()