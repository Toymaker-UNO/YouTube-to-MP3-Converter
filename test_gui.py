import sys
import time
from view.View import view_instance
from model.Model import model_instance
from controller.gui.LineEdit_URLInput import line_edit_url_input_instance
from controller.gui.PushButton_CheckURL import push_button_check_url_instance
from controller.gui.PushButton_Download import push_button_download_instance

def main():
    # Model 실행행
    model_instance.run('config.json')
    
    # View 초기화 및 GUI 실행
    app, window = view_instance.run()

    line_edit_url_input_instance.setup(window)
    line_edit_url_input_instance.disable()

    push_button_check_url_instance.setup(window)
    push_button_check_url_instance.disable()

    push_button_download_instance.setup(window)
    push_button_download_instance.disable()

    # 애플리케이션 실행
    sys.exit(app.exec_())

if __name__ == '__main__':
    main() 