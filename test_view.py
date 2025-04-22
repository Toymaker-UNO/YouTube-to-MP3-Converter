import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from view.View import view_instance
from model.Model import model_instance

def main():
    # Model 초기화
    model_instance.initialize('youtube_to_mp3.config.json')
    
    # Windows DPI 인식 설정 초기화
    view_instance.initialize()
    
    # QApplication 생성
    app = QApplication(sys.argv)
    
    # GUI 실행 및 윈도우 객체 저장
    window = view_instance.run(app)
    
    # 애플리케이션 실행
    sys.exit(app.exec_())

if __name__ == '__main__':
    main() 