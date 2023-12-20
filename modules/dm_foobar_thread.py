import sys
import traceback

from PyQt5.QtCore import QThread, QMutex, QTimer, Qt

from util.logger import logger
from util.tools import LazyImport, position_trans


class FoobarNoticeNowPrice(QThread):

    def __init__(self, setting="", parent=None):
        try:
            super(FoobarNoticeNowPrice, self).__init__(parent)
            self._mutex = QMutex()
            self.notice_foobar = None
            self.now_price_foobar = None
            self.notice = '结束运行：Alt + F2;    ' + setting
            self.dm = LazyImport('modules.dm_plugin').dm
        except Exception as e:
            logger.error(e)
            logger.error(sys.exc_info()[0:2])  # 打印错误类型，错误值
            logger.error(traceback.extract_tb(sys.exc_info()[2]))  # 出错位置

    def show_foobar(self):
        try:

            self.notice_foobar = self.dm.CreateFoobarRect(0, 1, 1, 850, 45)
            self.now_price_foobar = self.dm.CreateFoobarRoundRect(0, 1000, 1, 255, 45, 5, 5)
            self.time_countdown = self.dm.CreateFoobarRoundRect(0, 1400, 1, 185, 45, 5, 5)
            self.dm.FoobarSetFont(self.notice_foobar, '宋体', 19, 1)
            # # 背景透明
            # dm.FoobarSetTrans(notice_foobar, 1, 'ffffff', 1.0)
            # dm.FoobarFillRect(notice_foobar, 0, 0, 655, 35, 'ffffff')
            self.dm.FoobarDrawText(self.notice_foobar, 10, 8, 840, 23, self.notice, 'CC3300', 1)
            self.dm.FoobarUpdate(self.notice_foobar)
            self.dm.FoobarLock(self.notice_foobar)

            self.dm.FoobarSetFont(self.now_price_foobar, '宋体', 19, 1)
            self.dm.FoobarDrawText(self.now_price_foobar, 10, 8, 180, 23, '最优价：', '000099', 1)
            self.dm.FoobarUpdate(self.now_price_foobar)
            self.dm.FoobarTextRect(self.now_price_foobar, 115, 7, 150, 40)
            self.dm.FoobarSetFont(self.now_price_foobar, '宋体', 19, 0)
            self.dm.FoobarClearText(self.now_price_foobar)
            self.dm.FoobarPrintText(self.now_price_foobar, '---', '000099')
            self.dm.FoobarLock(self.now_price_foobar)

            self.dm.FoobarSetFont(self.time_countdown, '宋体', 19, 1)
            self.dm.FoobarDrawText(self.time_countdown, 10, 8, 180, 23, '倒计时：', '000099', 1)
            self.dm.FoobarTextRect(self.time_countdown, 105, 7, 180, 40)
            self.dm.FoobarSetFont(self.time_countdown, '宋体', 19, 0)
            self.dm.FoobarUpdate(self.time_countdown)
            self.dm.FoobarLock(self.time_countdown)
        except Exception as e:
            logger.error(e)
            logger.error(sys.exc_info()[0:2])  # 打印错误类型，错误值
            logger.error(traceback.extract_tb(sys.exc_info()[2]))  # 出错位置

    # @func_time    # 1-2ms
    def update_price(self, price):
        try:
            self._mutex.lock()
            if price is None or price == '' or price.strip()=='':
                self.dm.FoobarClearText(self.now_price_foobar)
                self.dm.FoobarPrintText(self.now_price_foobar, 'Error!', 'ff0000')
                self.dm.FoobarUpdate(self.now_price_foobar)
            else:
                if type(price) != str:
                    price = str(price)
                # print('self.now_price_foobar:', self.now_price_foobar)
                self.dm.FoobarClearText(self.now_price_foobar)
                self.dm.FoobarPrintText(self.now_price_foobar, price, '000000')
                self.dm.FoobarUpdate(self.now_price_foobar)
            self._mutex.unlock()
        except Exception as e:
            logger.error(e)
            logger.error(sys.exc_info()[0:2])  # 打印错误类型，错误值
            logger.error(traceback.extract_tb(sys.exc_info()[2]))  # 出错位置

    def update_countdown(self, times):
        try:
            self._mutex.lock()
            if times is None or times == '':
                self.dm.FoobarClearText(self.time_countdown)
                self.dm.FoobarPrintText(self.time_countdown, 'Error!', 'ff0000')
                self.dm.FoobarUpdate(self.time_countdown)
            else:
                if type(times) != str:
                    times = str(times)
                # print('self.now_price_foobar:', self.now_price_foobar)
                self.dm.FoobarClearText(self.time_countdown)
                self.dm.FoobarPrintText(self.time_countdown, times, '000099')
                self.dm.FoobarUpdate(self.time_countdown)
            self._mutex.unlock()
        except Exception as e:
            logger.error(e)
            logger.error(sys.exc_info()[0:2])  # 打印错误类型，错误值
            logger.error(traceback.extract_tb(sys.exc_info()[2]))  # 出错位置

    def stop(self):
        self.dm.FoobarClose(self.notice_foobar)
        self.dm.FoobarClose(self.now_price_foobar)
        self.dm.FoobarClose(self.time_countdown)
        self.quit()
        if self.isRunning():
            self.terminate()

class FoobarDrawRectSingle(QThread):

    def __init__(self, position: tuple, parent=None):
        try:
            super(FoobarDrawRectSingle, self).__init__(parent)
            self._mutex = QMutex()
            self.position = position_trans(position)
            # print('FoobarDrawRectSingle position: ', position)
            self.foobar = None
            self.dm = LazyImport('modules.dm_plugin').dm
        except Exception as e:
            logger.error(e)
            logger.error(sys.exc_info()[0:2])  # 打印错误类型，错误值
            logger.error(traceback.extract_tb(sys.exc_info()[2]))  # 出错位置

    def run(self):
        try:
            if self.position:
                self.foobar = self.dm.CreateFoobarRect(0, self.position['left'] - 2, self.position['top'] - 2, self.position['width'] + 4, self.position['height'] + 4)
                # 背景透明
                self.dm.FoobarSetTrans(self.foobar, 1, 'ffffff', 1.0)
                self.dm.FoobarFillRect(self.foobar, 0, 0, self.position['width'] + 4, self.position['height'] + 4, 'ffffff')
                # 画出矩形
                # color = 'FF00FF'
                color = '00CC33'
                self.dm.FoobarDrawLine(self.foobar, 2, 2, self.position['width'] + 2, 2, color, 1, 1)
                self.dm.FoobarDrawLine(self.foobar, 2, 2, 2, self.position['height'] + 2, color, 1, 1)
                self.dm.FoobarDrawLine(self.foobar, 2, self.position['height'] + 2, self.position['width'] + 2, self.position['height'] + 2, color, 1, 1)
                self.dm.FoobarDrawLine(self.foobar, self.position['width'] + 2, 2, self.position['width'] + 2, self.position['height'] + 2, color, 1, 1)
                self.dm.FoobarUpdate(self.foobar)
                self.dm.FoobarLock(self.foobar)
        except Exception as e:
            logger.error(e)
            logger.error(sys.exc_info()[0:2])  # 打印错误类型，错误值
            logger.error(traceback.extract_tb(sys.exc_info()[2]))  # 出错位置
    def stop(self):
        self.dm.FoobarClose(self.foobar)
        self.quit()
        if self.isRunning():
            self.terminate()
