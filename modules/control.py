import random
from collections import defaultdict

import cv2
import sys
import traceback
from datetime import datetime, timedelta

from PyQt5.QtCore import Qt
from PyQt5.QtCore import QThread
from PyQt5.QtCore import QTimer, pyqtSignal, QMutex

from modules.config import dm_find_color_sim, qiangdan_wait_screen_time, \
    after_stop_wait_show_normal_time, ENVIRONMENT, multi_line_offset, qiangdan_limit_time, \
    dm_top_xiadan_button_color_blue, find_dialog_window_position
from util import globalvar
from util.logger import logger
from util.tools import get_area_center_point, LazyImport, get_screen
from modules.position import get_qizhishijian_content, get_dialog_position


class GetBidStopTimeMonitor(QThread):
    _signal_data = pyqtSignal(dict)

    def __init__(self, interval_time, parent=None):
        """
        获取标段结束时间
        @param interval_time: 间隔时间毫秒
        @return 获取的时间字符串dict
        """
        super(GetBidStopTimeMonitor, self).__init__(parent)
        self._mutex = QMutex()
        self.interval_time = interval_time
        self.timer = QTimer(self)
        self.timer.setTimerType(Qt.PreciseTimer)  # 关键的一步，取消默认的精度设置
        self.timer.timeout.connect(self.run)
        self.timer.start(self.interval_time)

    def run(self):
        try:
            self._mutex.lock()
            screen = get_screen()
            result = get_qizhishijian_content(screen)
            self._mutex.unlock()
            self._signal_data.emit(result)
        except Exception as e:
            logger.error(e)
            logger.error(sys.exc_info()[0:2])  # 打印错误类型，错误值
            logger.error(traceback.extract_tb(sys.exc_info()[2]))  # 出错位置

    @property
    def signal_data(self):
        return self._signal_data

    @property
    def signal_screen(self):
        return self._signal_screen

    def stop(self):
        self.timer.stop()
        self.quit()
        if self.isRunning():
            self.terminate()

class StartQiangDan(QThread):
    _signal_order = pyqtSignal()

    def __init__(self, top_xiadan_position: tuple, start_time: datetime, is_limit_price: bool, limit_price: str or None,
                 is_limit_time: bool, limit_time=2.6, scale_rate=1.0, is_continuous_order=False, parent=None):
        """
        开始抢单
        @param top_xiadan_position: 顶部下单位置
        @param start_time: 本节开始时间
        @param is_limit_price: 是否限价
        @param limit_price: 限价多少
        @param is_limit_time: 是否下单限时
        @param limit_time: 限时多少
        @param scale_rate: win放大倍数
        @param is_continuous_order: 是否连续下单 布尔
        """
        super(StartQiangDan, self).__init__(parent)
        self._mutex = QMutex()
        self.top_xiadan_position = top_xiadan_position
        self.start_time = start_time
        self.is_limit_price = is_limit_price
        self.limit_price = limit_price
        self.is_limit_time = is_limit_time
        self.limit_time = limit_time
        self.scale_rate = scale_rate
        self.is_order = False
        self.is_continuous_order = is_continuous_order

        if 'YlceMainWindow' in self.parent().__class__.__name__:
            self.mouse_keyboard = LazyImport('modules.mouse_keyboard').MouseKeyboard_wen()
        else:
            self.mouse_keyboard = LazyImport('modules.dm_plugin').dm

            # 关闭鼠标精度
            self.mouse_keyboard.EnableMouseAccuracy(0)  # 关闭鼠标提高指针精度
            # 设置鼠标速度
            self.mouse_keyboard.SetMouseSpeed(6)

    def run(self):
        try:
            # print("StartQiangDanInput!")
            self._mutex.lock()
            xiadan_center_point = get_area_center_point(self.top_xiadan_position)
            # 下单中心点偏移量
            xiadan_center_point = (xiadan_center_point[0] + 7, xiadan_center_point[1])
            # print("xiandan_chenter_point: ", xiadan_center_point)
            # 重置鼠标
            self.mouse_keyboard.reset_cursor()
            # 移动鼠标到下单中心点
            self.mouse_keyboard.mouse_move_to(xiadan_center_point[0],
                                              xiadan_center_point[1])

            dm = LazyImport('modules.dm_plugin').dm
            while not self.is_order:
                dm_find_color_result = dm.FindColorEx(self.top_xiadan_position[0][0],
                                                      self.top_xiadan_position[0][1],
                                                      self.top_xiadan_position[1][0],
                                                      self.top_xiadan_position[1][1],
                                                      dm_top_xiadan_button_color_blue, dm_find_color_sim, 0)
                if len(dm_find_color_result) > 15:
                    if self.is_continuous_order:
                        while self.is_continuous_order:
                            if self.is_limit_price:
                                QThread.msleep(150)
                                self.mouse_keyboard.press_Enter(is_fast=True)
                                self.mouse_keyboard.mouse_move_to(xiadan_center_point[0],
                                                                  xiadan_center_point[1])
                                # 等待下单按钮反应时间
                                QThread.msleep(150)
                                # 单击鼠标下单
                                self.mouse_keyboard.mouse_left_click(is_fast=True)
                                # 暂停xx毫秒 等待弹出小窗口绘制完成
                                if find_dialog_window_position:
                                    QThread.msleep(qiangdan_wait_screen_time)
                                    # 截屏
                                    screen = get_screen()
                                    dialog_position = get_dialog_position(screen)
                                else:
                                    # QThread.msleep(30)
                                    dialog_position = get_dialog_position(None)
                                # 寻找下单按钮中心点
                                queren_position = dialog_position["dialog_baojia_botton_position"]
                                queren_center_point = get_area_center_point(queren_position)
                                # 价格输入框后半段中心点位置
                                input_center_point = get_area_center_point(dialog_position['dialog_baojia_input_position'])
                                self.mouse_keyboard.mouse_move_to(input_center_point[0],
                                                                  input_center_point[1])
                                self.mouse_keyboard.mouse_left_double_click(is_fast=True)
                                self.mouse_keyboard.press_Backspace(is_fast=True)
                                self.mouse_keyboard.mouse_left_double_click(is_fast=True)
                                self.mouse_keyboard.press_Backspace(is_fast=True)
                                self.mouse_keyboard.mouse_left_click(is_fast=True)
                                self.mouse_keyboard.input(key=globalvar.get_value('limit_price'), is_fast=True)
                                self.mouse_keyboard.mouse_move_to(queren_center_point[0],
                                                                  queren_center_point[1])
                                self.mouse_keyboard.mouse_left_click(is_fast=True)
                                self.mouse_keyboard.press_Enter(is_fast=True)
                                self.mouse_keyboard.mouse_move_to(1119, 570)
                                QThread.msleep(150)
                                self.mouse_keyboard.mouse_left_click(is_fast=True)
                                self.mouse_keyboard.press_Enter(is_fast=True)
                                self.mouse_keyboard.mouse_move_to(1123, 595)
                                QThread.msleep(150)
                                self.mouse_keyboard.mouse_left_click(is_fast=True)
                                self.mouse_keyboard.press_Enter(is_fast=True)
                                QThread.msleep(60)
                            else:
                                QThread.msleep(120)
                                self.mouse_keyboard.press_Enter(is_fast=True)
                                self.mouse_keyboard.mouse_move_to(xiadan_center_point[0],
                                                                  xiadan_center_point[1])
                                # 等待下单按钮反应时间
                                QThread.msleep(120)
                                # 单击鼠标下单
                                self.mouse_keyboard.mouse_left_click(is_fast=True)
                                # 暂停xx毫秒 等待弹出小窗口绘制完成
                                if find_dialog_window_position:
                                    QThread.msleep(qiangdan_wait_screen_time)
                                    # 截屏
                                    screen = get_screen()
                                    dialog_position = get_dialog_position(screen)
                                else:

                                    # QThread.msleep(30)
                                    dialog_position = get_dialog_position(None)
                                # 寻找下单按钮中心点
                                queren_position = dialog_position["dialog_baojia_botton_position"]
                                queren_center_point = get_area_center_point(queren_position)
                                # 价格输入框后半段中心点位置
                                QThread.msleep(120)
                                self.mouse_keyboard.mouse_move_to(queren_center_point[0],
                                                                  queren_center_point[1])
                                self.mouse_keyboard.mouse_left_click(is_fast=True)
                                self.mouse_keyboard.press_Enter(is_fast=True)
                                self.mouse_keyboard.mouse_move_to(1119, 570)
                                QThread.msleep(150)
                                self.mouse_keyboard.mouse_left_click(is_fast=True)
                                self.mouse_keyboard.press_Enter(is_fast=True)
                                self.mouse_keyboard.mouse_move_to(1123, 595)
                                QThread.msleep(150)
                                self.mouse_keyboard.mouse_left_click(is_fast=True)
                                self.mouse_keyboard.press_Enter(is_fast=True)
                                QThread.msleep(150)

                    else:
                        # 等待下单按钮反应时间
                        QThread.msleep(80)
                        # 单击鼠标下单
                        self.mouse_keyboard.mouse_left_click(is_fast=True)
                        self.mouse_keyboard.mouse_left_click(is_fast=True)
                        # 暂停xx毫秒 等待弹出小窗口绘制完成
                        if find_dialog_window_position:
                            QThread.msleep(qiangdan_wait_screen_time)
                        else:
                            QThread.msleep(10)
                        # 截屏
                        screen = get_screen()
                        dialog_position = get_dialog_position(screen)
                        # 寻找下单按钮中心点
                        queren_position = dialog_position["dialog_baojia_botton_position"]
                        queren_center_point = get_area_center_point(queren_position)
                        if self.is_limit_price:
                            # 价格输入框后半段中心点位置
                            input_center_point = get_area_center_point(dialog_position['dialog_baojia_input_position'])
                            # print("xiadan_center_point: ", xiadan_center_point)
                            # 移动鼠标 单击 两次回车
                            self.mouse_keyboard.mouse_move_to(input_center_point[0],
                                                              input_center_point[1])
                            self.mouse_keyboard.mouse_left_double_click(is_fast=True)
                            self.mouse_keyboard.press_Backspace(is_fast=True)
                            self.mouse_keyboard.mouse_left_click(is_fast=True)

                            # 是否超过最低限时
                            time_now = datetime.now()
                            limit_time = self.start_time + timedelta(seconds=float(self.limit_time))
                            # logger.info("start_time: %s, limit_time: %s", self.start_time, self.limit_time)
                            # 等待限时
                            if self.is_limit_time:
                                while time_now < limit_time:
                                    if ENVIRONMENT == "dev":
                                        print("wait time")
                                    QThread.msleep(2)
                                    time_now = datetime.now()

                            self.mouse_keyboard.input(key=globalvar.get_value('limit_price'), is_fast=True)
                            self.mouse_keyboard.mouse_move_to(queren_center_point[0],
                                                              queren_center_point[1])
                            self.mouse_keyboard.mouse_left_click(is_fast=True)
                        else:
                            self.mouse_keyboard.mouse_move_to(queren_center_point[0],
                                                              queren_center_point[1])
                            # 不输入价格时的最低限时
                            # is_time_now(self.start_time, qiangdan_limit_time)
                            time_now = datetime.now()
                            limit_time = self.start_time + timedelta(seconds=float(self.limit_time))
                            # logger.info("start_time: %s, limit_time: %s", self.start_time, self.limit_time)
                            while time_now < limit_time:
                                if ENVIRONMENT == "dev":
                                    print("wait time")
                                QThread.msleep(2)
                                time_now = datetime.now()
                            self.mouse_keyboard.mouse_left_click(is_fast=True)
                        self.mouse_keyboard.press_Enter(is_fast=True)
                        self.mouse_keyboard.press_Enter(is_fast=True)
                        self.mouse_keyboard.mouse_move_to(1123,595)
                        QThread.msleep(150)
                        self.mouse_keyboard.mouse_left_click()
                        # 保存截图
                        # screen = get_screen()
                        # after_order_save_screen(screen)
                        self.mouse_keyboard.press_Enter()
                    # 结束下单
                    self.is_order = True
                    self.parent().del_global_var()
                    self.parent().top_xiadan_position_foobar_thd.stop()

                    self.mouse_keyboard.press_Enter()
                else:
                    if ENVIRONMENT == "dev":
                        print("dm_find_color_result: ", dm_find_color_result)
                    continue

            QThread.sleep(after_stop_wait_show_normal_time)
            self.signal_order.emit()
            self._mutex.unlock()
            # self._signal_screen.emit(screen)
            # self._signal_data.emit(result)
        except Exception as e:
            logger.error(e)
            logger.error(sys.exc_info()[0:2])  # 打印错误类型，错误值
            logger.error(traceback.extract_tb(sys.exc_info()[2]))  # 出错位置

    @property
    def signal_order(self):
        return self._signal_order

    def stop(self):
        self.is_order = False
        # self.timer.stop()
        self.quit()
        if self.isRunning():
            self.terminate()

def after_order_save_screen(screen):
    # 保存图像之前 BGR RGB转换
    # final_img = cv2.cvtColor(screen, cv2.COLOR_BGR2RGB)
    # final_img = screen[:, :, [2, 1, 0]]  # 效果同上
    time_str = datetime.now().strftime("%Y%m%d%H%M%S%f")
    path_str = "./log/screen/" + time_str + ".png"
    # 保存弹框截图
    cv2.imwrite(path_str, screen)


class StartQiangDanMulti(QThread):
    _signal_order = pyqtSignal()

    def __init__(self, top_xiadan_position: tuple, zuiyoujia_position: tuple, package_num:int, start_time: datetime,
                 is_limit_price: bool, limit_price: str or None, is_limit_time: bool, limit_time=2.6, scale_rate=1.25,
                 parent=None):
        """
        开始多包抢单
        @param top_xiadan_position: 顶部下单位置
        @param zuiyoujia_position: 最高价格位置
        @param start_time: 本节开始时间
        @param is_limit_price: 是否限价
        @param limit_price: 限价多少
        @param is_limit_time: 是否下单限时
        @param limit_time: 限时多少
        @param package_num: 标的（包）数量
        @param scale_rate: win放大倍数
        """
        super(StartQiangDanMulti, self).__init__(parent)
        self._mutex = QMutex()
        self.top_xiadan_position = top_xiadan_position
        self.zuiyoujia_position = zuiyoujia_position
        self.start_time = start_time
        self.is_limit_price = is_limit_price
        self.limit_price = limit_price
        self.is_limit_time = is_limit_time
        self.limit_time = limit_time
        self.package_num = package_num
        self.scale_rate = scale_rate

        self.is_order = False
        self.package_dict = defaultdict(dict)
        # 拼接package的下单位置，最高价位置
        for i in range(0, package_num):
            key = "line_" + str(i)
            offset_zuigaojia_position = ((zuiyoujia_position[0][0],
                                          zuiyoujia_position[0][1] + (i * multi_line_offset)),
                                         (zuiyoujia_position[1][0],
                                          zuiyoujia_position[1][1] + (i * multi_line_offset)))
            offset_top_xiadan_position = ((top_xiadan_position[0][0],
                                           top_xiadan_position[0][1] + (i * multi_line_offset)),
                                         (top_xiadan_position[1][0],
                                          top_xiadan_position[1][1] + (i * multi_line_offset)))
            self.package_dict[key] = {"serial_num": i, "is_order": False,
                                      "zuigaojia_position": offset_zuigaojia_position,
                                      "top_xiadan_position": offset_top_xiadan_position}

        if 'YlceMainWindow' in self.parent().__class__.__name__:
            self.mouse_keyboard = LazyImport('modules.mouse_keyboard').MouseKeyboard_wen()
        else:
            self.mouse_keyboard = LazyImport('modules.dm_plugin').dm
            self.scale_rate = 1  # dm不需要设置放大倍率
            # 关闭鼠标精度
            self.mouse_keyboard.EnableMouseAccuracy(0)  # 关闭鼠标提高指针精度
            # 设置鼠标速度
            self.mouse_keyboard.SetMouseSpeed(6)
        # 重置鼠标
        self.mouse_keyboard.reset_cursor()

    def run(self):
        try:
            self._mutex.lock()
            dm = LazyImport('modules.dm_plugin').dm

            # TODO 更换为检测最高价 判断是否下单
            # screen = self.parent().screen
            # for line in self.package_dict:
            #     print("line: ", self.package_dict[line]["zuigaojia_position"])
            #     cv2.rectangle(screen, self.package_dict[line]["zuigaojia_position"][0],
            #                   self.package_dict[line]["zuigaojia_position"][1], (36, 255, 12), 1)
            # cv2.imshow("screen", screen)
            # cv2.waitKey(0)
            # cv2.destroyAllWindows()

            # 随机取三个不同行
            first_line_key = random.choice(list(self.package_dict))
            secend_line_key = first_line_key
            while first_line_key == secend_line_key:
                secend_line_key = random.choice(list(self.package_dict))
            third_line_key = first_line_key
            while third_line_key == first_line_key or third_line_key == secend_line_key:
                third_line_key = random.choice(list(self.package_dict))
            print(first_line_key,secend_line_key,third_line_key)
            line_key_list = []
            line_key_list.append(first_line_key)
            line_key_list.append(secend_line_key)
            # line_key_list.append(third_line_key)

            # 下单时间间隔
            offset_time = 0

            for key in line_key_list:
                xiadan_center_point = get_area_center_point(self.package_dict[key]["top_xiadan_position"])
                # 下单中心点偏移量
                xiadan_center_point = (xiadan_center_point[0] + 7, xiadan_center_point[1])
                # print("xiandan_chenter_point: ", xiadan_center_point)

                # 移动鼠标到下单中心点
                self.mouse_keyboard.mouse_move_to(xiadan_center_point[0],
                                                  xiadan_center_point[1])
                self.is_order=False
                dm_find_color_result = ''
                while not self.is_order:
                    if len(dm_find_color_result) > 15:
                        # 单击鼠标下单
                        self.mouse_keyboard.mouse_left_click(is_fast=True)
                        # 暂停xx毫秒 等待弹出小窗口绘制完成
                        QThread.msleep(qiangdan_wait_screen_time)
                        # 截屏
                        screen = get_screen()
                        dialog_position = get_dialog_position(screen)
                        # 寻找下单按钮中心点
                        queren_position = dialog_position["dialog_baojia_botton_position"]
                        queren_center_point = get_area_center_point(queren_position)
                        if self.is_limit_price:
                            # 价格输入框后半段中心点位置
                            input_center_point = get_area_center_point(dialog_position['dialog_baojia_input_position'])
                            # print("xiadan_center_point: ", xiadan_center_point)
                            # 移动鼠标 单击 两次回车
                            self.mouse_keyboard.mouse_move_to(input_center_point[0],
                                                              input_center_point[1])
                            self.mouse_keyboard.mouse_left_double_click(is_fast=True)
                            self.mouse_keyboard.press_Backspace(is_fast=True)
                            self.mouse_keyboard.mouse_left_click(is_fast=True)
                            self.mouse_keyboard.input(key=self.limit_price,is_fast=True)
                        self.mouse_keyboard.mouse_move_to(queren_center_point[0],
                                                          queren_center_point[1])
                        # 人工抢单 随机时间模拟，区分输入价格、不输入价格
                        if self.is_limit_price:
                            time_now = datetime.now()
                            limit_time = self.start_time + timedelta(seconds=float(self.limit_time + offset_time))
                            logger.info("start_time: %s, limit_time: %s", self.start_time, limit_time)
                            while time_now < limit_time:
                                if ENVIRONMENT == "dev":
                                    print("wait time")
                                QThread.msleep(10)
                                time_now = datetime.now()
                            offset_time = offset_time + 1.1
                        else:
                            # is_time_now(self.start_time, qiangdan_limit_time + offset_time)
                            time_now = datetime.now()
                            limit_time = self.start_time + timedelta(seconds=float(qiangdan_limit_time + offset_time))
                            logger.info("start_time: %s, limit_time: %s", self.start_time, limit_time)
                            while time_now < limit_time:
                                if ENVIRONMENT == "dev":
                                    print("wait time")
                                QThread.msleep(10)
                                time_now = datetime.now()
                            offset_time = offset_time + 1.1
                        self.mouse_keyboard.mouse_left_click(is_fast=True)
                        self.mouse_keyboard.press_Enter(is_fast=True)
                        self.mouse_keyboard.press_Enter(is_fast=True)
                        self.mouse_keyboard.press_Enter()

                        self.is_order = True
                        # 保存第二次截图
                        # after_order_save_screen(screen)
                    else:
                        dm_find_color_result = dm.FindColorEx(self.top_xiadan_position[0][0],
                                                              self.top_xiadan_position[0][1],
                                                              self.top_xiadan_position[1][0],
                                                              self.top_xiadan_position[1][1],
                                                              dm_top_xiadan_button_color_blue, dm_find_color_sim, 0)
                    if ENVIRONMENT == "dev":
                        print("dm_find_color_result: ", dm_find_color_result)

            self.parent().del_global_var()
            self.parent().top_xiadan_postion_foobar_thd.stop()

            QThread.sleep(after_stop_wait_show_normal_time)
            self.signal_order.emit()
            self._mutex.unlock()
            # self._signal_screen.emit(screen)
            # self._signal_data.emit(result)
        except Exception as e:
            logger.error(e)
            logger.error(sys.exc_info()[0:2])  # 打印错误类型，错误值
            logger.error(traceback.extract_tb(sys.exc_info()[2]))  # 出错位置

    @property
    def signal_order(self):
        return self._signal_order

    def stop(self):
        self.is_order = False
        # self.timer.stop()
        self.quit()
        if self.isRunning():
            self.terminate()
