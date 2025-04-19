import sys
from PyQt5.QtWidgets import QApplication
from view.GUIBuilder import GUIBuilder
from model.Configuration import Configuration

def main():
    # Configuration 초기화
    config = Configuration()
    config.initialize('youtube_to_mp3.config.json')
    
    # QApplication 생성
    app = QApplication(sys.argv)
    
    # GUIBuilder를 사용하여 메인 윈도우 생성
    builder = GUIBuilder()
    window = builder.create_main_window()
    
    # 윈도우 표시
    window.show()
    
    # 애플리케이션 실행
    sys.exit(app.exec_())

if __name__ == '__main__':
    main() 