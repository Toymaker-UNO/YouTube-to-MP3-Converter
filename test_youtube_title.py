from controller.YoutubeTitle import YoutubeTitle

def test_youtube_title():
    # YoutubeTitle 인스턴스 생성
    youtube_title = YoutubeTitle()
    
    # 테스트할 URL 목록
    test_urls = [
        # 일반 YouTube URL
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        # 짧은 URL
        "https://youtu.be/dQw4w9WgXcQ",
        # 잘못된 URL
        "https://www.youtube.com/watch?v=invalid",
        # 플레이리스트 URL
        "https://www.youtube.com/playlist?list=PL1234567890",
        # 비어있는 URL
        ""
    ]
    
    print("YouTube URL 테스트 시작...\n")
    
    for url in test_urls:
        print(f"테스트 URL: {url}")
        
        # URL 유효성 검사
        is_valid = youtube_title.is_valid_url(url)
        print(f"URL 유효성: {'유효' if is_valid else '유효하지 않음'}")
        
        if is_valid:
            # 제목 가져오기
            title = youtube_title.get(url)
            if title:
                print(f"비디오 제목: {title}")
            else:
                print("제목을 가져올 수 없습니다.")
        print("-" * 50)
    
    print("\n테스트 완료")

if __name__ == "__main__":
    test_youtube_title() 