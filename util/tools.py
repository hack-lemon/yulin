#!/usr/bin/python
# -*- coding: UTF-8 -*-
import gc
import sys
import traceback

import cv2
import mss
import mss.tools
import numpy as np
import importlib
from re import sub
from time import perf_counter
from functools import wraps

from PyQt5.QtCore import QThread

from modules.config import function_time_record
from util.logger import logger


def func_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if function_time_record:
            start = perf_counter()
            # start = time.process_time()
            r = func(*args, **kwargs)
            end = perf_counter()
            # end = time.process_time()
            logger.debug('{}.{} spend {} second'.format(func.__module__, func.__name__, end - start))
            return r
        else:
            return func(*args, **kwargs)

    return wrapper


@func_time
# @logger.catch
def get_screen(var=None):
    """
    截屏
    @param var: 屏幕坐标 {"top": 0, "left": 0, "width": 1024, "height": 1024} 或者((0,0), (1920,1080))
    @return: img: np.array图片矩阵
    """
    if var is None:
        area = {"top": 0, "left": 0, "width": 1920, "height": 1080}
    elif type(var) == tuple and len(var) < 3:
        area = position_trans(var)
    else:
        area = var
    with mss.mss() as sct:
        try:
            sct_img = sct.grab(area)
            # noinspection PyTypeChecker
            img = np.array(sct_img)
            return img
        except Exception as e:
            logger.error(e)
            logger.error(sys.exc_info()[0:2])  # 打印错误类型，错误值
            logger.error(traceback.extract_tb(sys.exc_info()[2]))  # 出错位置


@func_time
# @logger.catch
def find_image_postion(img: np.ndarray, template: np.ndarray) -> tuple:
    """
    寻找坐标位置
    @param img: 原图
    @param template: 目标图
    @return: top_left,bottom_right: 目标图左上角、右下角坐标点
    """
    try:
        h, w = template.shape[:2]  # rows->h, cols->w
        gc.collect()
        res = None
        result = None
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        img_banalization = preprocess_image_to_ocr(img)
        template_banalization = preprocess_image_to_ocr(template)

        def match_template_opencv(img, template):
            res = None
            res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
            top_left = max_loc
            bottom_right = (top_left[0] + w, top_left[1] + h)
            gc.collect()
            return top_left, bottom_right

        times = 0  # TODO 整体用 try except else finally 重构
        while result is None:  # 二值化寻找opencv先找2遍
            try:
                result = match_template_opencv(img_banalization, template_banalization)
            except cv2.error:
                times += 1
                gc.collect()
                QThread.sleep(1)
                logger.warn("caution:opencv error, times: %d", times)
                if times > 1:
                    break
            continue
        if result is None:  # opencv灰度图再找一遍
            gc.collect()
            result = match_template_opencv(img_gray, template_gray)
            logger.warn("use match_template_opencv and banalization find postion")

        logger.debug("image postion is: %s", result)
        del img_gray, img_banalization, template_gray, template_banalization
        gc.collect()
        return result
    except Exception as e:
        logger.error(e)
        logger.error(sys.exc_info()[0:2])  # 打印错误类型，错误值
        logger.error(traceback.extract_tb(sys.exc_info()[2]))  # 出错位置


def crop_image(image, box):
    """
    截图
    @param image: 原图
    @param box: 位置
    @return: 被截取的图像
    """
    try:
        xs = [x[0] for x in box]
        ys = [x[1] for x in box]
        img = image[min(ys):max(ys), min(xs):max(xs)]  # 最小y开始，最大y结束，最小x开始，最大x结束
        return img
    except Exception as e:
        logger.error(e)
        logger.error(sys.exc_info()[0:2])  # 打印错误类型，错误值
        logger.error(traceback.extract_tb(sys.exc_info()[2]))  # 出错位置


def re_sub(text: str) -> str:
    """
    正则去掉特殊字符
    @param text: 需要处理的字符串
    @return: 处理好的结果
    """
    # 正则过滤掉特殊字符
    try:
        assert len(text) > 0
        text = sub(r'["/:?\\|<>″′‖ 〈\n,]', "", text)
        text = sub(
            '[\001\002\003\004\005\006\007\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19'
            '\x1a]+',
            '', text)
        return text
    except Exception as e:
        logger.error(e)
        logger.error(sys.exc_info()[0:2])  # 打印错误类型，错误值
        logger.error(traceback.extract_tb(sys.exc_info()[2]))  # 出错位置


def preprocess_image_to_ocr(img):
    """
    图片灰度二值化预处理
    @param img: 需要处理的图片
    @return : 处理完成的图片
    """
    try:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # 灰度图片
        ret, th = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)  # Otsu阈值法二值化
        return th
    except Exception as e:
        logger.error(e)
        logger.error(sys.exc_info()[0:2])  # 打印错误类型，错误值
        logger.error(traceback.extract_tb(sys.exc_info()[2]))  # 出错位置


def image_array_to_bytes(img):
    try:
        return cv2.imencode('.jpg', img)[1].tobytes()
    except Exception as e:
        logger.error(e)
        logger.error(sys.exc_info()[0:2])  # 打印错误类型，错误值
        logger.error(traceback.extract_tb(sys.exc_info()[2]))  # 出错位置


# @logger.catch
def relative_absolute(relative: dict, offset: tuple) -> dict:
    """
    相对坐标转换绝对坐标
    @param relative: 相对坐标 左上，右下
    @param offset: 偏移坐标 左上，右下
    @return: 绝对坐标
    """
    try:
        relative_keys = relative.keys()
        absolute = {}
        for key in relative_keys:
            absolute[key] = ((relative[key][0][0] + offset[0][0], relative[key][0][1] + offset[0][1]),
                             (relative[key][1][0] + offset[0][0], relative[key][1][1] + offset[0][1]))
        return absolute
    except Exception as e:
        logger.error(e)
        logger.error(sys.exc_info()[0:2])  # 打印错误类型，错误值
        logger.error(traceback.extract_tb(sys.exc_info()[2]))  # 出错位置


def get_min_list(data):
    """
    返回dict最小值列表
    @param data: dict
    @return: 最小值list
    """
    try:
        ml = []
        min_key = min(data, key=data.get)
        for key in data:
            if int(data[min_key]) == int(data[key]):
                ml.append({key: data[key]})
        return ml
    except ValueError as e:
        logger.warn("ValueError: %s", e)
    except Exception as e:
        logger.error(e)
        logger.error(sys.exc_info()[0:2])  # 打印错误类型，错误值
        logger.error(traceback.extract_tb(sys.exc_info()[2]))  # 出错位置


# print(get_min_list({'PUM-A2020081403': '244', 'PUM-A2020081404': '243', 'PUM-A2020081405': '243',
#                      'PUM-A2020081406': '244', 'PUM-A2020081407': '243'}))


def get_max_list(data):
    """
    返回dict最小值列表
    @param data: dict
    @return: 最小值list
    """
    ml = []
    min_key = max(data, key=data.get)
    for key in data:
        if int(data[min_key]) == int(data[key]):
            ml.append({key: data[key]})
    return ml


def get_area_center_point(area: tuple):
    """
    获取屏幕指定区域中心点
    @param area: 区域坐标，左上角，右下角
    @return: 中心点x，y
    """
    try:
        x = int((area[0][0] +
                 area[1][0]) / 2 - 2)
        y = int((area[0][1] +
                 area[1][1]) / 2)
        # logger.debug("get_area_center_point is: %d, %d", x, y)
        return x, y
    except Exception as e:
        logger.error(e)
        logger.error(sys.exc_info()[0:2])  # 打印错误类型，错误值
        logger.error(traceback.extract_tb(sys.exc_info()[2]))  # 出错位置


def position_trans(left_top_right_bottom: tuple):
    try:
        if left_top_right_bottom:
            return {'top': left_top_right_bottom[0][1], 'left': left_top_right_bottom[0][0],
                    'width': abs(left_top_right_bottom[1][0] - left_top_right_bottom[0][0]),
                    'height': abs(left_top_right_bottom[1][1] - left_top_right_bottom[0][1])}

    except Exception as e:
        logger.error(e)
        logger.error(sys.exc_info()[0:2])  # 打印错误类型，错误值
        logger.error(traceback.extract_tb(sys.exc_info()[2]))  # 出错位置


class LazyImport(object):
    """使用
    os = LazyImport("os", globals(), locals()) # 此时还未导入os,这一行可以写在文件开始,import区域
    os.getpid() # 调用__getattr__导入/从cache里获取
    """

    def __init__(self, name):
        self.cache = {}
        self.mod_name = name

    def __getattr__(self, name):
        try:
            mod = self.cache.get(self.mod_name)
            if not mod:
                mod = importlib.import_module(self.mod_name)
                self.cache[self.mod_name] = mod
            return getattr(mod, name)
        except ImportError as e:
            logger.error(e)
        except Exception as e:
            logger.error(e)
            logger.error(sys.exc_info()[0:2])  # 打印错误类型，错误值
            logger.error(traceback.extract_tb(sys.exc_info()[2]))  # 出错位置
