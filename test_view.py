import sys
from view.View import view_instance
from model.Model import model_instance

def main():
    # Model 초기화
    model_instance.initialize('youtube_to_mp3.config.json')
    
    # View 초기화 및 GUI 실행
    app, window = view_instance.initialize()
    
    # 애플리케이션 실행
    sys.exit(app.exec_())

if __name__ == '__main__':
    main() 