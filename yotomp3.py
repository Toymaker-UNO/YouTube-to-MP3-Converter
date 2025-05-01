import sys
from view.View import view_instance
from model.Model import model_instance
from controller.Controller import controller_instance

def main():
    # Model 실행행
    model_instance.run('config.json')
    
    # View 초기화 및 GUI 실행
    app, window = view_instance.run()

    # Controller 실행
    controller_instance.run(window)
    
    # 애플리케이션 실행
    sys.exit(app.exec_())

if __name__ == '__main__':
    main() 