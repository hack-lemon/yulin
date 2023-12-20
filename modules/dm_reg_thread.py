import sys
import traceback

from PyQt5.QtCore import QThread, QMutex, pyqtSignal
from PyQt5.QtWidgets import QApplication

from util.logger import logger
from util.tools import LazyImport


class RegDM(QThread):
    _signal_data = pyqtSignal()

    def __init__(self, parent=None):
        super(RegDM, self).__init__(parent)
        self._mutex = QMutex()

    def run(self):
        try:
            self._mutex.lock()
            dm = LazyImport('modules.dm_plugin').dm
            dm.Reg()
            self._signal_data.emit()
            self._mutex.unlock()
        except Exception as e:
            logger.error(e)
            logger.error(sys.exc_info()[0:2])  # 打印错误类型，错误值
            logger.error(traceback.extract_tb(sys.exc_info()[2]))  # 出错位置

    @property
    def signal_data(self):
        return self._signal_data
