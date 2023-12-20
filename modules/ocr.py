import gc
import sys
import numpy as np
import traceback
from datetime import datetime
from PyQt5.QtCore import QThread, pyqtSignal, QMutex

from util.logger import logger
from util.tools import crop_image, LazyImport
from modules.config import dm_num_color, dm_num_sim, zuigaojia_limit, ENVIRONMENT, ocr_capture
from modules.baidu_api import baidu_ocr


def get_single_content_baidu_ocr(img: np.ndarray, postion: tuple) -> str:
    try:
        cropped = crop_image(img, postion)
        text = ''
        if len(cropped) > 20:
            baidu_result = baidu_ocr(cropped, False, "CHN_ENG")
            logger.debug('baidu_result: %s', baidu_result)
            if baidu_result["words_result_num"] == 0:
                text = ''
            else:
                text = baidu_result["words_result"][0]["words"]
        del cropped
        del img
        gc.collect()
        return text
    except Exception as e:
        logger.error(e)
        logger.error(sys.exc_info()[0:2])  # 打印错误类型，错误值
        logger.error(traceback.extract_tb(sys.exc_info()[2]))  # 出错位置


class GetFastOCRThreadDm(QThread):
    _signal_data = pyqtSignal(str)
    def __init__(self, postion, parent=None):
        super(GetFastOCRThreadDm, self).__init__(parent)
        self.postion = postion
        self._mutex = QMutex()
        self.isRun = True
        self.dm = LazyImport('modules.dm_plugin').dm


    def run(self):
        try:
            self._mutex.lock()
            while self.isRun:
                result = self.dm.Ocr(self.postion[0][0], self.postion[0][1], self.postion[1][0], self.postion[1][1],
                                     dm_num_color, dm_num_sim)
                self._signal_data.emit(result)
                if not best_price_result_judgment(result):
                    if ENVIRONMENT == "pro" and ocr_capture:
                        time_str = datetime.now().strftime("%Y%m%d%H%M%S%f")[:-2]  # 每0.1秒 存储一张图片 覆盖写入
                        path_str = "./log/zuiyoujia_miss_" + time_str + ".bmp"
                        self.dm.Capture(self.postion[0][0], self.postion[0][1], self.postion[1][0], self.postion[1][1],
                                        path_str)
            self._mutex.unlock()
        except Exception as e:
            logger.error(e)
            logger.error(sys.exc_info()[0:2])  # 打印错误类型，错误值
            logger.error(traceback.extract_tb(sys.exc_info()[2]))  # 出错位置

    @property
    def signal_data(self):
        return self._signal_data

    def update_postion(self, postion):
        self.postion = postion

    def stop(self):
        self.isRun = False
        self.quit()
        if self.isRunning():
            self.terminate()

def best_price_result_judgment(data):  # 最高价正则判断
    try:
        if data:
            data_replace = data.replace("D", "")
            data_replace = data_replace.replace(",", "")
            if 2 <= float(data_replace) < zuigaojia_limit:
                return True
            else:
                return False
        else:
            return False
    except Exception:
        return False
