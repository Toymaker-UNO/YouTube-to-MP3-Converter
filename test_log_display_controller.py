import sys
from view.View import view_instance
from model.Model import model_instance
from controller.Controller import controller_instance
from controller.LogDisplayController import log_display_controller_instance

def main():
    # Model 실행
    model_instance.run('config.json')
    
    # View 초기화 및 GUI 실행
    app, window = view_instance.run()
    
    # 테스트 로그 출력
    log_display_controller_instance.initialize(window)
    log_display_controller_instance.print("테스트 로그 메시지입니다.")

    # 애플리케이션 실행
    sys.exit(app.exec_())

if __name__ == '__main__':
    main() 