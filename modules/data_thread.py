import math
import sys
import traceback
from datetime import timedelta
from PyQt5.QtCore import QThread, pyqtSignal, QMutex

from util.logger import logger
from util.tools import  LazyImport


class GetPostionThreadDict(QThread):
    _signal_btn_status = pyqtSignal()
    _signal_data = pyqtSignal(dict)
    _signal_window = pyqtSignal()

    def __init__(self, screen, task, parent=None):
        super(GetPostionThreadDict, self).__init__(parent)
        self.screen = screen
        self.task = task
        self._mutex = QMutex()

    def run(self):
        try:
            self._mutex.lock()
            result = self.task(self.screen)
            self._mutex.unlock()
            self._signal_btn_status.emit()
            self._signal_data.emit(result)
            self._signal_window.emit()
        except Exception as e:
            logger.error(e)
            logger.error(sys.exc_info()[0:2])  # 打印错误类型，错误值
            logger.error(traceback.extract_tb(sys.exc_info()[2]))  # 出错位置

    @property
    def signal_btn_status(self):
        return self._signal_btn_status

    @property
    def signal_data(self):
        return self._signal_data

    @property
    def signal_window(self):
        return self._signal_window

    def stop(self):
        self.quit()
        if self.isRunning():
            self.terminate()


class GetPostionThreadTuple(QThread):
    _signal_data = pyqtSignal(tuple)

    def __init__(self, screen, task, parent=None):
        super(GetPostionThreadTuple, self).__init__(parent)
        self.screen = screen
        self.task = task
        self._mutex = QMutex()

    def run(self):
        try:
            self._mutex.lock()
            result = self.task(self.screen)
            self._signal_data.emit(result)
            self._mutex.unlock()
        except Exception as e:
            logger.error(e)
            logger.error(sys.exc_info()[0:2])  # 打印错误类型，错误值
            logger.error(traceback.extract_tb(sys.exc_info()[2]))  # 出错位置

    @property
    def signal_data(self):
        return self._signal_data

    def stop(self):
        self.quit()
        if self.isRunning():
            self.terminate()


class GetDelayTimeThread(QThread):
    _signal_data = pyqtSignal(timedelta)

    def __init__(self, screen, task, parent=None):
        super(GetDelayTimeThread, self).__init__(parent)
        self.screen = screen
        self.task = task
        self._mutex = QMutex()

    def run(self):
        try:
            self._mutex.lock()
            result = self.task(self.screen, self.parent().__class__.__name__)  # 传入调用窗口parent
            self._signal_data.emit(result)
            self._mutex.unlock()
        except Exception as e:
            logger.error(e)
            logger.error(sys.exc_info()[0:2])  # 打印错误类型，错误值
            logger.error(traceback.extract_tb(sys.exc_info()[2]))  # 出错位置

    @property
    def signal_data(self):
        return self._signal_data

    def stop(self):
        self.quit()
        if self.isRunning():
            self.terminate()


class GetTestThread(QThread):
    _signal_btn_status = pyqtSignal()
    _signal_window = pyqtSignal()

    def __init__(self, scale_rate, parent=None):
        super(GetTestThread, self).__init__(parent)
        self.scale_rate = scale_rate
        self._mutex = QMutex()

    def run(self):
        try:
            self._mutex.lock()
            mouse_keyboard = LazyImport('modules.mouse_keyboard').MouseKeyboard_wen()
            mouse_keyboard.reset_cursor()  # 重置鼠标
            QThread.msleep(500)
            mouse_keyboard.mouse_move_to(math.ceil(1920/ 2 / self.scale_rate),
                                         math.ceil(1080/ 2 / self.scale_rate))
            QThread.msleep(500)
            mouse_keyboard.mouse_move_to(math.ceil(30 / self.scale_rate),
                                         math.ceil(1060/ self.scale_rate))
            mouse_keyboard.mouse_left_click()
            QThread.msleep(500)
            self._mutex.unlock()
            self._signal_btn_status.emit()
            self._signal_window.emit()
        except Exception as e:
            logger.error(e)
            logger.error(sys.exc_info()[0:2])  # 打印错误类型，错误值
            logger.error(traceback.extract_tb(sys.exc_info()[2]))  # 出错位置

    @property
    def signal_btn_status(self):
        return self._signal_btn_status

    @property
    def signal_data(self):
        return self._signal_data

    @property
    def signal_window(self):
        return self._signal_window

    def stop(self):
        self.run_flag = False
        self.quit()
        if self.isRunning():
            self.terminate()
