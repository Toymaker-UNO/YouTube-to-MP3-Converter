import sys
from view.View import view_instance
from model.Model import model_instance
from controller.gui.URLInput import URLInput

def main():
    # Model 실행행
    model_instance.run('config.json')
    
    # View 초기화 및 GUI 실행
    app, window = view_instance.run()

    url_input_instance = URLInput()
    url_input_instance.setup(window)
    url_input_instance.disable()
    
    # 애플리케이션 실행
    sys.exit(app.exec_())

if __name__ == '__main__':
    main() 