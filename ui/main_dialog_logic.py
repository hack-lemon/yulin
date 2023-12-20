import sys
import traceback

from PyQt5.QtWidgets import QMainWindow, QApplication

from ui.main_dialog import Ui_Dialog
from ui.single_main_window_logic import SingleMainWindow
from util.logger import logger
from modules.dm_reg_thread import RegDM

class MyDialog(QMainWindow, Ui_Dialog):
    def __init__(self, parent=None):
        super(MyDialog, self).__init__(parent)

        self.reg_dm_thd = RegDM()  # 注册dm
        self.reg_dm_thd.signal_data.connect(self.dm_reg_change_btn_enable)
        self.reg_dm_thd.start()

        self.setupUi(self)
        self.setWindowOpacity(0.95)  # 窗口透明度
        # self.single_btn.setEnabled(False)
        self.single_btn.clicked.connect(self.click_single_btn)
        self.show()
        self.setFixedSize(self.width(), self.height())
        self.single_main_window = None
        self.double_main_window = None

    def dm_reg_change_btn_enable(self):
        self.single_btn.setEnabled(True)

    def click_single_btn(self):
        try:
            self.single_main_window = SingleMainWindow()
            self.single_main_window.show()
            self.single_main_window.start_time_thd()
            self.close()
        except Exception as e:
            logger.error(e)
            logger.error(sys.exc_info()[0:2])  # 打印错误类型，错误值
            logger.error(traceback.extract_tb(sys.exc_info()[2]))  # 出错位置

