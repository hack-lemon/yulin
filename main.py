import sys
import os
import traceback

from modules.del_self import del_self_method

import ctypes

import qdarkstyle
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QStyleFactory
from ui.main_dialog_logic import MyDialog
from util import globalvar as global_var
from util.logger import logger


global_var.init()


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if __name__ == '__main__':
    if is_admin():
        pass
    else:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
        sys.exit(1)

    try:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        sys.path.append(BASE_DIR)
        sys.path.append(os.path.join(BASE_DIR, 'client'))

        QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
        app = QApplication(sys.argv)

        app.setStyle(QStyleFactory.create('Fusion'))

        host_scale_rate = app.screens()[0].logicalDotsPerInch() / 96  # 获取第一个屏幕的放大倍率
        global_var.set_value("host_scale_rate", host_scale_rate)
        # 初始化
        dialog = MyDialog()
        sys.exit(app.exec())

    except Exception as e:
        logger.error(e)
        logger.error(sys.exc_info()[0:2])  # 打印错误类型，错误值
        logger.error(traceback.extract_tb(sys.exc_info()[2]))  # 出错位置
