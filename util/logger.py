import os
import sys
import traceback
import logging
import colorlog
from logging import handlers
from modules.config import logLevel

if not os.path.exists("./log/"):  # 如不存在目标目录则创建
    os.makedirs("./log/")
    # os.makedirs("./log/screen")


def color_logger(log_to_file=True, log_level=logLevel) -> logging.Logger:
    try:
        log_format = "%(asctime)s | %(levelname)s | %(threadName)s | %(filename)s:%(lineno)d | %(funcName)s | %(message)s"
        bold_seq = '\033[1m'
        colorlog_format = (
            f'{bold_seq} '
            '%(log_color)s '
            f'{log_format}'
        )
        colorlog.basicConfig(format=colorlog_format)
        logger_ = logging.getLogger()
        logger_.setLevel(log_level)
        # Output full log
        if log_to_file:
            fh = logging.handlers.RotatingFileHandler('./log/runtime.log', 'a',
                                                      3000000, backupCount=5, encoding='utf-8')
            formatter = logging.Formatter(log_format)
            fh.setFormatter(formatter)
            logger_.addHandler(fh)
        return logger_
    except Exception as e:
        logger.error(e)
        logger.error(sys.exc_info()[0:2])  # 打印错误类型，错误值
        logger.error(traceback.extract_tb(sys.exc_info()[2]))  # 出错位置

logger = color_logger()
