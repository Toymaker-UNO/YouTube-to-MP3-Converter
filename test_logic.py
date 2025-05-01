from controller.logic.YoutubeTitle import YoutubeTitle
from controller.logic.DownloadYoutubeAudio import DownloadYoutubeAudio
from controller.logic.ConverterToMP3 import ConverterToMP3
from controller.gui.PlainTextEdit_LogDisplay import plain_text_edit_log_display_instance
import os

def test_youtube_download_and_convert():
    # 테스트용 YouTube URL
    test_url = "https://youtu.be/L4XTJao2iLA"
    #test_url = "https://youtu.be/9VqMnuBFptQ"
    
    # YoutubeTitle 인스턴스 생성
    youtube_title = YoutubeTitle()
    
    # URL 유효성 검사
    if not youtube_title.is_valid_url(test_url):
        print("유효하지 않은 YouTube URL입니다.")
        return
    
    # 비디오 제목 가져오기
    title = youtube_title.get(test_url)
    if not title:
        print("비디오 제목을 가져올 수 없습니다.")
        return
    
    print(f"비디오 제목: {title}")
    
    # DownloadYoutubeAudio 인스턴스 생성
    downloader = DownloadYoutubeAudio()
    
    try:
        # 다운로드 진행 상황 콜백 함수
        def on_progress(percentage):
            progress_text = "다운로드: " + plain_text_edit_log_display_instance.create_progress_bar(percentage)
            print(progress_text)
            
        def on_speed(speed):
            print(f"다운로드 속도: {speed}")
            
        # 오디오 다운로드
        print("오디오 다운로드를 시작합니다...")
        downloaded_file, title = downloader.download_audio(
            url=test_url,
            quality="320K",  # 품질 옵션: "320K", "256K", "192K", "160K", "128K", "96K", "64K", "48K"
            progress_callback=on_progress,
            speed_callback=on_speed
        )
        
        print(f"다운로드 완료: {downloaded_file}")
        
        # ConverterToMP3 인스턴스 생성
        converter = ConverterToMP3()
        
        # MP3 변환 진행 상황 콜백 함수
        def on_convert_progress(percentage):
            progress_text = "MP3변환: " + plain_text_edit_log_display_instance.create_progress_bar(round(percentage, 2))
            print(progress_text)
            
        # MP3 변환
        print("MP3 변환을 시작합니다...")
        final_path = converter.convert(
            input_file=downloaded_file,
            title=title,
            quality="320K",
            save_path=os.path.join(os.getcwd(), 'downloads'),
            progress_callback=on_convert_progress
        )
        
        print(f"MP3 변환 완료: {final_path}")
        
    except Exception as e:
        print(f"오류가 발생했습니다: {str(e)}")

if __name__ == "__main__":
    test_youtube_download_and_convert() 