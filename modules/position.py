import sys
import cv2
import traceback
import numpy as np

from modules.baidu_api import baidu_ocr
from modules.config import find_dialog_window_position
from util.logger import logger
from util.tools import crop_image, find_image_postion


def get_qizhishijian_content(img: np.ndarray) -> dict:
    try:
        qizhishijian_img = cv2.imread(r'./position_pic/jiaoyixinxi.bmp')
        qizhishijian_postion = find_image_postion(img, qizhishijian_img)
        qizhishijian_content_position = ((qizhishijian_postion[0][0] + 44,
                                          qizhishijian_postion[0][1] + 89),
                                         (qizhishijian_postion[1][0] + 107,
                                          qizhishijian_postion[1][1] + 76))
        # 先用长条图片取百度识别
        qizhishijian_content_img_coped = crop_image(img, qizhishijian_content_position)
        baidu_result = baidu_ocr(qizhishijian_content_img_coped, False)

        if baidu_result['words_result_num']:
            qizhishijian_content_text = baidu_result['words_result'][0]['words']
            qizhishijian_list = qizhishijian_content_text.split('~')
            result = {'benjiekaishishijian': qizhishijian_list[0],
                      'benjiejieshushijian': qizhishijian_list[1]}
        else:
            raise ValueError("获取竞拍起止时间错误: %s", baidu_result)
        logger.info(result)
        return result
    except Exception as e:
        logger.error(e)
        logger.error(sys.exc_info()[0:2])  # 打印错误类型，错误值
        logger.error(traceback.extract_tb(sys.exc_info()[2]))  # 出错位置


def get_xiadan_zuiyoujia_position(img: np.ndarray) -> dict:
    try:
        gonggonghangqing_img = cv2.imread(r'./position_pic/gonggonghangqing.bmp')
        gonggonghangqing_position = find_image_postion(img, gonggonghangqing_img)
        xiadan_button_position = ((gonggonghangqing_position[0][0] + 1546 - 526,
                                   gonggonghangqing_position[0][1] + 345 - 242),
                                  (gonggonghangqing_position[1][0] + 1593 - 618,
                                   gonggonghangqing_position[1][1] + 368 - 284))

        zuiyoujia_position = ((gonggonghangqing_position[0][0] + 1393 - 526,
                               gonggonghangqing_position[0][1] + 336 - 242),
                              (gonggonghangqing_position[1][0] + 1512 - 618,
                               gonggonghangqing_position[1][1] + 378 - 284))
        result = {"xiadan_button_position": xiadan_button_position,
                  "zuiyoujia_position": zuiyoujia_position}
        return result
    except Exception as e:
        logger.error(e)
        logger.error(sys.exc_info()[0:2])  # 打印错误类型，错误值
        logger.error(traceback.extract_tb(sys.exc_info()[2]))  # 出错位置


def get_bottom_jiage_gaijia_position(img: np.ndarray) -> dict:
    try:
        dagnqianpipeiqingkuang_img = cv2.imread(r'./position_pic/dagnqianpipeiqingkuang_area.bmp')
        dagnqianpipeiqingkuang_position = find_image_postion(img, dagnqianpipeiqingkuang_img)
        jiage_text_input_postion = ((dagnqianpipeiqingkuang_position[0][0] + 1469 - 527,
                                     dagnqianpipeiqingkuang_position[0][1] + 486 - 400),
                                    (dagnqianpipeiqingkuang_position[1][0] + 1548 - 647,
                                     dagnqianpipeiqingkuang_position[1][1] + 514 - 440))
        logger.debug('bottom_jiage_text_input_postion: %s', jiage_text_input_postion)

        gaijia_button_position = ((dagnqianpipeiqingkuang_position[0][0] + 1559 - 527,
                                   dagnqianpipeiqingkuang_position[0][1] + 489 - 400),
                                  (dagnqianpipeiqingkuang_position[1][0] + 1606 - 647,
                                   dagnqianpipeiqingkuang_position[1][1] + 512 - 440))
        result = {"jiage_text_input_position": jiage_text_input_postion,
                  "gaijia_button_position": gaijia_button_position}
        return result
    except Exception as e:
        logger.error(e)
        logger.error(sys.exc_info()[0:2])  # 打印错误类型，错误值
        logger.error(traceback.extract_tb(sys.exc_info()[2]))  # 出错位置


def get_dialog_position(img: np.ndarray or None) -> dict:
    try:
        if find_dialog_window_position:
            dialog_title_img = cv2.imread(r'./position_pic/dialog_title.bmp')
            dialog_title_position = find_image_postion(img, dialog_title_img)

            dialog_baojia_input_position = ((dialog_title_position[0][0] + 712 - 645,
                                             dialog_title_position[0][1] + 530 - 426),
                                            (dialog_title_position[1][0] + 911 - 1274,
                                             dialog_title_position[1][1] + 561 - 469))
            dialog_shuliang_input_position = ((dialog_title_position[0][0] + 1017 - 645,
                                               dialog_title_position[0][1] + 530 - 426),
                                              (dialog_title_position[1][0] + 1217 - 1274,
                                               dialog_title_position[1][1] + 561 - 469))
            dialog_baojia_botton_position = ((dialog_title_position[0][0] + 875 - 645,
                                              dialog_title_position[0][1] + 609 - 426),
                                             (dialog_title_position[1][0] + 954 - 1274,
                                              dialog_title_position[1][1] + 637 - 469))
        else:
            dialog_baojia_input_position = ((712, 530), (911, 561))
            dialog_shuliang_input_position = ((1017, 530), (1217, 561))
            dialog_baojia_botton_position = (875, 609), (954, 637)

        result = {"dialog_baojia_input_position": dialog_baojia_input_position,
                  "dialog_shuliang_input_position": dialog_shuliang_input_position,
                  "dialog_baojia_botton_position": dialog_baojia_botton_position}
        return result
    except Exception as e:
        logger.error(e)
        logger.error(sys.exc_info()[0:2])  # 打印错误类型，错误值
        logger.error(traceback.extract_tb(sys.exc_info()[2]))  # 出错位置
