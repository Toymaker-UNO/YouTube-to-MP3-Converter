import os
import sys
from controller.Converter import Converter

def main():
    # 저장 경로 설정
    save_path = os.path.join(os.getcwd(), 'downloads')
    if not os.path.exists(save_path):
        os.makedirs(save_path)
        
    # Converter 인스턴스 생성
    converter = Converter(save_path=save_path)
    
    # 테스트할 YouTube URL
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Rick Astley - Never Gonna Give You Up
    
    try:
        # URL 유효성 검사
        if not converter.is_valid_youtube_url(test_url):
            print("유효하지 않은 YouTube URL입니다.")
            sys.exit(1)
            
        # 비디오 제목 가져오기
        title = converter.get_video_title(test_url)
        if not title:
            print("비디오 제목을 가져올 수 없습니다.")
            sys.exit(1)
            
        print(f"비디오 제목: {title}")
        
        # 진행 상황 콜백 함수
        def on_progress(percentage):
            print(f"다운로드 진행률: {percentage}%")
            
        def on_speed(speed):
            print(f"다운로드 속도: {speed}")
            
        # 다운로드 및 변환
        print("다운로드 시작...")
        downloaded_file, title = converter.download_video(
            url=test_url,
            quality="320K",
            progress_callback=on_progress,
            speed_callback=on_speed
        )
        
        print("MP3 변환 시작...")
        final_path = converter.convert_to_mp3(
            input_file=downloaded_file,
            title=title,
            quality="320K"
        )
        
        print(f"변환이 완료되었습니다: {final_path}")
        
    except Exception as e:
        print(f"오류가 발생했습니다: {str(e)}")
        sys.exit(1)
        
if __name__ == "__main__":
    main() 