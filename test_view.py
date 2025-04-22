import sys
from PyQt5.QtWidgets import QApplication
from view.View import view_instance
from model.Configuration import configuration_instance

def main():
    # DPI 인식 설정 초기화
    view_instance.initialize()
    
    # Configuration 초기화
    configuration_instance.initialize('youtube_to_mp3.config.json')
    
    # QApplication 생성
    app = QApplication(sys.argv)
    
    # GUI 실행 및 윈도우 객체 저장
    window = view_instance.run(app)
    
    # 애플리케이션 실행
    sys.exit(app.exec_())

if __name__ == '__main__':
    main() 