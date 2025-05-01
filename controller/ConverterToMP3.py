import os
from datetime import datetime
import ffmpeg
from model.Log import Log

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