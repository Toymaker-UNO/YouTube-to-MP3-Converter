import os
from datetime import datetime
import ffmpeg
from model.Log import Log
import subprocess
import re

class ConverterToMP3:
    def __init__(self):
        self.log = Log()
            
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
            cmd = [
                'ffmpeg',
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
            self.log.error(f"변환 중 오류 발생: {str(e)}")
            raise 