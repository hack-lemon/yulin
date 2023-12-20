
from PyQt5.QtCore import QTimer, pyqtSignal, QMutex
from datetime import datetime, timedelta
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QThread
from modules.config import margin_time
from PyQt5.QtWidgets import QApplication

class TimeThread(QThread):
    _signal_millisecond = pyqtSignal(str)

    def __init__(self, parent=None):
        """
        获取本地时间，精确到0.1秒
        @return: 富文本时间字符串
        """
        super(TimeThread, self).__init__(parent)
        self._mutex = QMutex()
        self.timer = QTimer(self)
        self.timer.setTimerType(Qt.PreciseTimer)  # 关键的一步，取消默认的精度设置
        self.timer.timeout.connect(self.run)
        self.timer.start(33)  # 定时为33毫秒触发

    def run(self):
        self._mutex.lock()
        QApplication.processEvents()
        result = '<html><head/><body><p><span style=" font-size:14pt; font-weight:600; color:#ff9900;">' + \
                 datetime.now().strftime('%H:%M:%S.%f')[:-5] + '</span></p></body></html>'
        self._signal_millisecond.emit(result)
        QApplication.processEvents()  # 刷新界面
        self._mutex.unlock()

    @property
    def signal_millisecond(self):
        return self._signal_millisecond


class CountDownOnceTimeThread(QThread):
    def __init__(self, interval, task, parent=None):
        """
        定时间隔结束后执行一次任务
        @param interval: 多少毫秒后执行
        @param task: 任务函数
        @param parent: 父继承默认None
        """
        super(CountDownOnceTimeThread, self).__init__(parent)
        self.task = task
        self._mutex = QMutex()
        self.timer = QTimer(self)
        self.timer.setTimerType(Qt.PreciseTimer)  # 关键的一步，取消默认的精度设置
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.run)
        self.timer.start(interval)

    def run(self):
        self._mutex.lock()
        self.task()
        self._mutex.unlock()

    def stop(self):
        self.timer.stop()
        self.quit()
        if self.isRunning():
            self.terminate()


class FoobarLimitTimeThread(QThread):
    _signal_millisecond = pyqtSignal(str)

    def __init__(self, stop_time, last_limit_time, parent=None):
        """
        foobar 倒计时
        @return: 时间字符串
        """
        super(FoobarLimitTimeThread, self).__init__(parent)
        self._mutex = QMutex()
        self.timer = QTimer(self)
        self.timer.setTimerType(Qt.PreciseTimer)  # 关键的一步，取消默认的精度设置
        self.timer.timeout.connect(self.run)
        self.stop_time = stop_time
        self.last_limit_time = last_limit_time
        self.timer.start(33)  # 定时为33毫秒触发

    def run(self):
        self._mutex.lock()
        # 当前时间减去结束时间，每33毫秒更新一次
        now_limit = str((self.stop_time - datetime.now() - timedelta(seconds=self.last_limit_time)).total_seconds())[:-5]
        QApplication.processEvents()  # 刷新界面
        self._signal_millisecond.emit(now_limit)
        self._mutex.unlock()

    @property
    def signal_millisecond(self):
        return self._signal_millisecond

    def stop(self):
        self.timer.stop()
        self.quit()
        if self.isRunning():
            self.terminate()