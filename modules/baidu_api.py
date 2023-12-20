#!/usr/bin/python
# -*- coding: UTF-8 -*-
# import cv2
import sys
import traceback

import cv2
import numpy as np
from aip import AipOcr
from requests.exceptions import ProxyError
from util.tools import func_time, preprocess_image_to_ocr, image_array_to_bytes
from util.logger import logger
from modules.config import ocr_pic
from util import globalvar as global_var
from func_timeout import func_timeout, FunctionTimedOut


@func_time
# @logger.catch
def baidu_ocr(image: np.ndarray, turn_over=False, language="CHN_ENG", preprocess=True, timeout=4) -> dict:
    """
    百度ocr接口
    @param image: 需要识别的图片
    @param turn_over: 背景色是否需要翻转
    @param language: 图片中的语言：CHN_ENG, ENG
    @param timeout: 网络连接超时限制秒数
    @return: 识别好的结果

    """
    baidu_temp_key = global_var.get_value('baidu_temp_key')
    if baidu_temp_key is None:
        baidu_temp_key = []
    # logger.debug('gm.get_value() :{}', baidu_temp_key)
    target = image
    # TODO
    # 图片传进来之前就做好灰度二值化处理
    if preprocess:
        target = preprocess_image_to_ocr(image)
    if turn_over:
        target = 255 - target
    # cv2.imshow("target", target)
    # cv2.waitKey(0)

    # TODO
    # 图片传进来之前就做好二进制转换
    target = image_array_to_bytes(target)
    result = {}
    options = {"recognize_granularity": "big", "language_type": language, "vertexes_location": "false"}

    """ 带参数调用通用文字识别（含位置高精度版） """
    response = {}
    try:
        # logger.info("response is: {}", response)
        for i in range(len(ocr_pic)):
            if len(baidu_temp_key) < 1:
                client = AipOcr(ocr_pic[i]["APP_ID"], ocr_pic[i]["API_KEY"], ocr_pic[i]["SECRET_KEY"])
                baidu_temp_key.clear()
                baidu_temp_key.append(ocr_pic[i]["APP_ID"])
                baidu_temp_key.append(ocr_pic[i]["API_KEY"])
                baidu_temp_key.append(ocr_pic[i]["SECRET_KEY"])
                global_var.set_value("baidu_temp_key", baidu_temp_key)
            else:
                client = AipOcr(*baidu_temp_key)
            # response = client.accurate(target, options)
            # 添加网络连接时间限制，超时后自动重试一次。
            try:
                response = func_timeout(timeout, client.basicAccurate, args=(target, options))
            except FunctionTimedOut:
                logger.warn("baidu ocr connect time out, try it again...")
                try:
                    response = func_timeout(timeout, client.basicAccurate, args=(target, options))
                except FunctionTimedOut:
                    logger.error("baidu ocr connect time out, please check network!")
                except Exception as e:
                    logger.error(e)
                    logger.error(sys.exc_info()[0:2])  # 打印错误类型，错误值
                    logger.error(traceback.extract_tb(sys.exc_info()[2]))  # 出错位置
            except Exception as e:
                logger.error(e)
                logger.error(sys.exc_info()[0:2])  # 打印错误类型，错误值
                logger.error(traceback.extract_tb(sys.exc_info()[2]))  # 出错位置
            if response.__contains__("log_id"):
                break
            elif response["error_code"] == 14:
                baidu_temp_key.clear()
                global_var.set_value("baidu_temp_key", baidu_temp_key)
                logger.warn("Baidu Ocr error: %s, try change Key_%d...", response["error_msg"], i + 1)
            elif response["error_code"] == 17:
                baidu_temp_key.clear()
                global_var.set_value("baidu_temp_key", baidu_temp_key)
                logger.warn("Baidu Ocr error: %s, try change Key_%d...", response["error_msg"], i + 1)
            else:
                logger.error("Baidu Ocr error: %s,", response)
        else:
            logger.error("Baidu Ocr error: %s, and keys is over!", response)

        if len(response["words_result"]) == response["words_result_num"]:
            result = response
        else:
            logger.error("Baidu Ocr response length error! Please try again.")
        return result
    except ProxyError:
        logger.error("ProxyError! Plesse check Network Connections!")
    except KeyError as e:
        logger.error("baidu ocr result KeyError, message is: %s", e)
