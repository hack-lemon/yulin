import sys
import math
import traceback
from datetime import timedelta, datetime

from system_hotkey import SystemHotkey, SystemRegisterError
from PyQt5.QtCore import pyqtSignal, QThread
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QApplication

from modules.config import ENVIRONMENT, show_position_rect, after_stop_wait_show_normal_time, version,zuigaojia_limit
from modules.data_thread import GetPostionThreadDict
from modules.dm_foobar_thread import FoobarDrawRectSingle, FoobarNoticeNowPrice
from modules.position import get_bottom_jiage_gaijia_position, get_xiadan_zuiyoujia_position, get_qizhishijian_content
from modules.time_thread import TimeThread, CountDownOnceTimeThread, FoobarLimitTimeThread
from modules.control import GetBidStopTimeMonitor, StartQiangDan, \
    StartQiangDanMulti
from modules.ocr import GetFastOCRThreadDm, best_price_result_judgment
from modules.response_time import ResponseTime, ServerResponseFluctuation


from ui.single_main_window import Ui_MainWindow
from util import globalvar
from util.logger import logger
from util.tools import LazyImport, get_screen, get_area_center_point, func_time


class SingleMainWindow(QMainWindow, Ui_MainWindow):
    signal_hotkey = pyqtSignal(str)

    def __init__(self, parent=None):
        try:
            super(SingleMainWindow, self).__init__(parent)
            self.setupUi(self)

            self.setWindowOpacity(0.97)  # 窗口透明度
            self.setFixedSize(self.width(), self.height())  # 固定窗口高度宽度
            self.setWindowTitle("Coal Assistant  version: " + version)

            self.xitongshijian_thd = None
            self.benjieshijian_thd = None
            self.main_data_thd = None
            self.main_postion_thd = None
            self.get_server_response_time_thd = None
            self.get_server_response_fluctuation_thd = None
            self.main_data = None
            self.click_delay_time = []
            self.countdown_thd = None
            self.limit_thd = None
            self.zuiyoujia_monitor_thd = None
            self.test_orders_daley_time_thd = None
            self.jiage_text_input_position = None
            self.jiage_input_postion_right = None
            self.gaijia_button_position = None
            self.mouse_keyboard = None
            self.zuiyoujia_content = None
            self.bottom_xiadan_center = None
            self.zuiyoujia_position = None
            self.foobar_thd = None
            self.qiangdan_foobar_thd = None
            self.zuiyoujia_position_foobar_thd = None
            self.jiage_text_input_position_foobar_thd = None
            self.gaijia_button_position_foobar_thd = None
            self.reset_mouse_input_click_order_thd = None
            self.controlled_scale_rate = 1
            # 最优价识别错误计数
            self.zuiyoujia_ocr_error_time = 0
            # 最优价识别计数器
            self.zuiyoujia_ocr_times = 0

            # 配置按钮
            self.radioButton_20_secend.setChecked(True)
            self.start_btn.clicked.connect(self.click_start_btn)
            self.buttonGroup.buttonClicked.connect(self.button_group_time_interval_toggled)
            self.qiangdan_btn.clicked.connect(self.click_qiangdan_btn)
            self.start_duishi_btn.clicked.connect(self.precise_time_set)

            # 配置加价幅度下拉框
            self.comboBox_jiajiafudu.addItem("1元")  # 0
            self.comboBox_jiajiafudu.addItem("2元")  # 1
            self.comboBox_jiajiafudu.addItem("3元")  # 2
            self.comboBox_jiajiafudu.addItem("4元")  # 3
            self.comboBox_jiajiafudu.addItem("5元")  # 4
            self.comboBox_jiajiafudu.addItem("6元")  # 5
            self.comboBox_jiajiafudu.addItem("7元")  # 6
            self.comboBox_jiajiafudu.addItem("8元")  # 7
            self.comboBox_jiajiafudu.addItem("9元")  # 8
            self.comboBox_jiajiafudu.addItem("10元")  # 9
            self.comboBox_jiajiafudu.addItem("13元")  # 10
            self.comboBox_jiajiafudu.addItem("15元")  # 11
            self.comboBox_jiajiafudu.addItem("17元")  # 12

            self.comboBox_jiajiafudu.setCurrentIndex(1)

            # 配置几个复选框
            self.checkBox_qiangdanxianshi.setChecked(True)

            # 全局热键
            self.signal_hotkey.connect(self.MKey_pressEvent)
            try:
                self.hk_stop, self.hk_up, self.hk_down, self.hk_esc = \
                    SystemHotkey(), SystemHotkey(), SystemHotkey(), SystemHotkey()
                self.hk_stop.register(('alt', 'f2'), callback=lambda x: self.send_key_event("stop"))
                self.hk_up.register(('control', 'up'), callback=lambda x: self.send_key_event("up"))
                self.hk_down.register(('control', 'down'), callback=lambda x: self.send_key_event("down"))
                self.hk_esc.register(('alt', 'q'), callback=lambda x: self.send_key_event("quit"))
            except SystemRegisterError as e:
                self.message_box_warn("error","热键注册失败！")

            # 启动服务器响应波动log获取线程
            self.get_server_response_fluctuation_thd = ServerResponseFluctuation()
            self.get_server_response_fluctuation_thd.signal_data.connect(self.render_server_response_fluctuation)
            self.get_server_response_fluctuation_thd.start()  # 渲染界面后启动一次

        except Exception as e:
            logger.error(e)
            logger.error(sys.exc_info()[0:2])  # 打印错误类型，错误值
            logger.error(traceback.extract_tb(sys.exc_info()[2]))  # 出错位置

    def MKey_pressEvent(self, hot_key_str):
        if hot_key_str == 'stop':
            try:
                self.reset_mouse_input_click_order_thd.stop()
                if ENVIRONMENT == 'dev':
                    print('self.reset_mouse_input_click_order_thd.stop() finished')
            except AttributeError:
                if ENVIRONMENT == 'dev':
                    print('self.reset_mouse_input_click_order_thd.stop() AttributeError')
            try:
                self.foobar_thd.stop()
                if ENVIRONMENT == 'dev':
                    print('self.foobar_thd.stop() finished')
            except AttributeError:
                if ENVIRONMENT == 'dev':
                    print('self.foobar_thd.stop() ArgumentError')
            try:
                self.benjieshijian_thd.stop()
                if ENVIRONMENT == 'dev':
                    print('self.benjieshijian_thd.stop() finished')
            except AttributeError:
                if ENVIRONMENT == 'dev':
                    print('self.benjieshijian_thd.stop() AttributeError')
            try:
                self.test_orders_daley_time_thd.stop()
                if ENVIRONMENT == 'dev':
                    print('self.test_orders_daley_time_thd.stop() finished')
            except AttributeError:
                if ENVIRONMENT == 'dev':
                    print('self.test_orders_daley_time_thd.stop() AttributeError')
            try:
                self.zuiyoujia_monitor_thd.stop()
                if ENVIRONMENT == 'dev':
                    print('self.zuigaojia_monitor_thd.stop() finished')
            except AttributeError:
                if ENVIRONMENT == 'dev':
                    print('self.zuigaojia_monitor_thd.stop() AttributeError')
            try:
                self.countdown_thd.stop()
                if ENVIRONMENT == 'dev':
                    print('self.countdown_thd.stop() finished')
            except AttributeError:
                if ENVIRONMENT == 'dev':
                    print('self.countdown_thd.stop() AttributeError')
            try:
                self.limit_thd.stop()
                if ENVIRONMENT == 'dev':
                    print('self.limit_thd.stop() finished')
            except AttributeError:
                if ENVIRONMENT == 'dev':
                    print('self.limit_thd.stop() AttributeError')
            try:
                self.main_postion_thd.stop()
                if ENVIRONMENT == 'dev':
                    print('self.main_postion_thd.stop() finished')
            except AttributeError:
                if ENVIRONMENT == 'dev':
                    print('self.main_postion_thd.stop() AttributeError')
            try:
                self.main_data_thd.stop()
                if ENVIRONMENT == 'dev':
                    print('self.main_data_thd finished')
            except AttributeError:
                if ENVIRONMENT == 'dev':
                    print('self.main_data_thd AttributeError')
            try:
                self.zuiyoujia_position_foobar_thd.stop()
                if ENVIRONMENT == 'dev':
                    print('self.zuigaojia_postion_foobar_thd.stop() finished')
            except AttributeError:
                if ENVIRONMENT == 'dev':
                    print('self.zuigaojia_postion_foobar_thd.stop() AttributeError')
            try:
                self.jiage_text_input_position_foobar_thd.stop()
                if ENVIRONMENT == 'dev':
                    print('self.jiage_text_input_position_foobar_thd.stop() finished')
            except AttributeError:
                if ENVIRONMENT == 'dev':
                    print('self.jiage_text_input_position_foobar_thd.stop() AttributeError')
            try:
                self.gaijia_button_position_foobar_thd.stop()
                if ENVIRONMENT == 'dev':
                    print('self.gaijia_button_position_foobar_thd.stop() finished')
            except AttributeError:
                if ENVIRONMENT == 'dev':
                    print('self.gaijia_button_position_foobar_thd.stop() AttributeError')
            try:
                self.bottom_xiadan_jiage_input_postion_thd.stop()
                if ENVIRONMENT == 'dev':
                    print('self.bottom_xiadan_postion_thd.stop() finished')
            except AttributeError:
                if ENVIRONMENT == 'dev':
                    print('self.bottom_xiadan_postion_thd.stop() AttributeError')
            try:
                self.zuiyoujia_position_thd.stop()
                if ENVIRONMENT == 'dev':
                    print('self.zuigaojia_postion_thd.stop() finished')
            except AttributeError:
                if ENVIRONMENT == 'dev':
                    print('self.zuigaojia_postion_thd.stop() AttributeError')
            try:
                self.limit_foobar_thd.stop()
                if ENVIRONMENT == 'dev':
                    print('self.limit_foobar_thd.stop() finished')
            except AttributeError:
                if ENVIRONMENT == 'dev':
                    print('self.limit_foobar_thd.stop() AttributeError')
            try:
                self.test_key_mouse_thd.stop()
                if ENVIRONMENT == 'dev':
                    print('self.test_key_mouse_thd.stop() finished')
            except AttributeError:
                if ENVIRONMENT == 'dev':
                    print('self.test_key_mouse_thd.stop() AttributeError')
            try:
                self.qiangdan_thd.is_continuous_order = False
                self.qiangdan_thd.is_order = True
                self.qiangdan_thd.stop()
                if ENVIRONMENT == 'dev':
                    print('self.qiangdan_thd.stop() finished')
            except AttributeError:
                if ENVIRONMENT == 'dev':
                    print('self.qiangdan_thd.stop() AttributeError')
            try:
                self.top_xiadan_position_foobar_thd.stop()
                if ENVIRONMENT == 'dev':
                    print('self.top_xiadan_position_foobar_thd.stop() finished')
            except AttributeError:
                if ENVIRONMENT == 'dev':
                    print('self.top_xiadan_position_foobar_thd.stop() AttributeError')
            finally:
                # QThread.sleep(after_stop_wait_show_normal_time)
                self.showNormal()
                self.start_btn.setEnabled(True)
        elif hot_key_str == "up":
            self.update_qiangdan_limit_price(True, self.lineEdit_qiangdanxianjia.text())
        elif hot_key_str == "down":
            self.update_qiangdan_limit_price(False, self.lineEdit_qiangdanxianjia.text())
        else:
            sys.exit(0)

    def send_key_event(self, hot_key_str):
        self.signal_hotkey.emit(hot_key_str)

    @staticmethod
    def message_box_warn(m_level, m_content):
        msg_box = QMessageBox(QMessageBox.Warning, m_level, m_content)
        msg_box.exec_()

    @staticmethod
    def message_box_info(m_level, m_content):
        msg_box = QMessageBox(QMessageBox.Information, m_level, m_content)
        msg_box.exec_()

    def button_group_time_interval_toggled(self):
        try:
            if self.radioButton_20_secend.isChecked():
                self.get_server_response_time_thd.toggled(20000)
            elif self.radioButton_40_secend.isChecked():
                self.get_server_response_time_thd.toggled(40000)
            else:
                self.get_server_response_time_thd.toggled(60000)
        except Exception as e:
            logger.error(e)
            logger.error(sys.exc_info()[0:2])  # 打印错误类型，错误值
            logger.error(traceback.extract_tb(sys.exc_info()[2]))  # 出错位置

    def precise_time_set(self):
        self.get_server_response_time_thd.run(is_set_local_time=True)

    def start_time_thd(self):
        try:
            # 服务器响应时间获取线程
            self.get_server_response_time_thd = ResponseTime()
            self.get_server_response_time_thd.signal_data.connect(self.render_response)
            self.get_server_response_time_thd.run()  # 定时10秒后，先启动运行一次
            self.get_server_response_time_thd.run(is_set_local_time=True)  # 第二次运行，对时
            self.button_group_time_interval_toggled()  # 判断自动根据ui界面选择初始化

            # 系统时间
            self.xitongshijian_thd = TimeThread()
            self.xitongshijian_thd.signal_millisecond.connect(self.render_time)
        except Exception as e:
            logger.error(e)
            logger.error(sys.exc_info()[0:2])  # 打印错误类型，错误值
            logger.error(traceback.extract_tb(sys.exc_info()[2]))  # 出错位置

    def render_time(self, result):
        try:
            self.system_time_text.setText(result)
            QApplication.processEvents()
            # print(self.xitongshijian_thd.result)
        except Exception as e:
            logger.error(e)
            logger.error(sys.exc_info()[0:2])  # 打印错误类型，错误值
            logger.error(traceback.extract_tb(sys.exc_info()[2]))  # 出错位置

    def render_response(self, result):
        try:
            self.server_response_time_text.setText(result['rich_text'])
            self.get_server_response_fluctuation_thd.start()  # 界面渲染完执行服务器时间对时统计
        except Exception as e:
            logger.error(e)
            logger.error(sys.exc_info()[0:2])  # 打印错误类型，错误值
            logger.error(traceback.extract_tb(sys.exc_info()[2]))  # 出错位置
            logger.error(traceback.extract_tb(sys.exc_info()[2]))  # 出错位置

    def render_server_response_fluctuation(self, result):
        try:
            if len(result) > 0:
                self.average_response_time_text.setText(result['average_response_time_rich_text'])
                self.intermediate_response_time_text.setText(result['intermediate_response_time_rich_text'])
                self.ninety_percent_response_time_text.setText(result['ninety_percent_response_time_rich_text'])
                self.minimum_response_time_text.setText(result['minimum_response_time_rich_text'])
                self.maximum_response_time_text.setText(result['maximum_response_time_rich_text'])
            if 'time_comparison' in result.keys():
                self.time_status_progressBar.setValue(result['time_comparison'])
            else:
                self.time_status_progressBar.setValue(0)

        except Exception as e:
            logger.error(e)
            logger.error(sys.exc_info()[0:2])  # 打印错误类型，错误值
            logger.error(traceback.extract_tb(sys.exc_info()[2]))  # 出错位置
            logger.error(traceback.extract_tb(sys.exc_info()[2]))  # 出错位置

    def check_shicha_range(self) -> bool:
        try:
            shicha = float(self.lineEdit_shicha.text())
            if 1<shicha or shicha<0:
                self.message_box_warn("wran", "时差超出范围0~1，请修改！")
                return False
            else:
                return True
        except ValueError:
            self.message_box_warn("wran", "请输入正确的时差范围！")
            return False

    def click_start_btn(self):
        if self.check_shicha_range():
            try:
                self.check_shicha_range()
                self.zuiyoujia_ocr_times = 0
                self.zuiyoujia_ocr_error_time = 0
                self.showMinimized()
                QThread.msleep(50)
                try:
                    self.main_postion_rect_thd.stop()  # 关闭位置获取中的矩形框
                    if self.main_postion_rect_thd.isRunning():
                        self.main_postion_rect_thd.terminate()
                except AttributeError:
                    pass
                # 提前加载dm
                self.dm = LazyImport('modules.dm_plugin').dm

                self.start_btn.setEnabled(False)
                self.benjieshijian_thd = GetBidStopTimeMonitor(3000)
                self.benjieshijian_thd.signal_data.connect(self.benjieshijian_data)
                self.benjieshijian_thd.start()

                # 准备设置字符串
                setting_str = self.get_setting_str()

                self.foobar_thd = FoobarNoticeNowPrice(setting_str)
                self.foobar_thd.show_foobar()
            except Exception as e:
                logger.error(e)
                logger.error(sys.exc_info()[0:2])  # 打印错误类型，错误值
                logger.error(traceback.extract_tb(sys.exc_info()[2]))  # 出错位置

    def get_setting_str(self):
        # 准备设置字符串
        setting_str = ""
        if self.checkBox_zuidijiagejingpai.isChecked():
            setting_str = setting_str + "最低价竞拍"
        else:
            setting_str = setting_str + "最高价竞拍"
        if self.checkBox_jingpaixianjia.isChecked():
            setting_str = setting_str + "  限价: " + self.lineEdit_jingpaixianjia.text()
        else:
            setting_str = setting_str + "  不限价"
        setting_str = setting_str + "   竞价幅度：" + str(self.get_jingjiafudu()) + "元"
        return setting_str

    def store_zuiyoujia_position_start_monitor(self, thd_data):
        try:
            self.zuiyoujia_position = thd_data["zuiyoujia_position"]

            self.zuiyoujia_monitor_thd = GetFastOCRThreadDm(self.zuiyoujia_position)
            self.zuiyoujia_monitor_thd.signal_data.connect(self.zuiyoujia_data)
            self.zuiyoujia_monitor_thd.start()

            self.show_rect()  # 统一绘制位置框
        except Exception as e:
            logger.error(e)
            logger.error(sys.exc_info()[0:2])  # 打印错误类型，错误值
            logger.error(traceback.extract_tb(sys.exc_info()[2]))  # 出错位置

    def store_bottom_xiadan_postion(self, thd_data):
        try:
            self.gaijia_button_position = thd_data["gaijia_button_position"]
            self.gaijia_button_position_center = get_area_center_point(self.gaijia_button_position)
            self.gaijia_button_position_center = (self.gaijia_button_position_center[0],
                                                  self.gaijia_button_position_center[1])
            logger.info('gaijia_button_position_center: %s', self.gaijia_button_position_center)

            self.jiage_text_input_position = thd_data["jiage_text_input_position"]
            jiage_input_postion_center = get_area_center_point(self.jiage_text_input_position)
            self.jiage_input_postion_right = (jiage_input_postion_center[0] +
                                              int((self.jiage_text_input_position[1][0] -
                                                   self.jiage_text_input_position[0][
                                                       0]- 25) /2),
                                              jiage_input_postion_center[1])
            logger.info('jiage_input_postion_right: %s', self.jiage_text_input_position)

            self.show_rect()  # 统一绘制位置框
        except Exception as e:
            logger.error(e)
            logger.error(sys.exc_info()[0:2])  # 打印错误类型，错误值
            logger.error(traceback.extract_tb(sys.exc_info()[2]))  # 出错位置

    def benjieshijian_data(self, benjieshijian):
        try:
            if len(benjieshijian['benjiejieshushijian']) > 0:  # 判断数据是否获取成功，长度大于0
                self.benjieshijian_thd.stop()
                globalvar.set_value('benjiejieshushijian', benjieshijian['benjiejieshushijian'])
                globalvar.set_value('benjiekaishishijian', benjieshijian['benjiekaishishijian'])
                self.start_monitor(benjieshijian)
                # 开始获取最高价位置，监测最高价格

        except Exception as e:
            logger.error(e)
            logger.error(sys.exc_info()[0:2])  # 打印错误类型，错误值
            logger.error(traceback.extract_tb(sys.exc_info()[2]))  # 出错位置

    def start_monitor(self, benjieshijian):
        try:
            if ENVIRONMENT == "pro":
                now_date = str(datetime.now().date())
                stop_time = benjieshijian['benjiejieshushijian']
                stop_time = now_date + ' ' + stop_time
                stop_time = datetime.strptime(stop_time, '%Y-%m-%d %H:%M:%S')
            else:
                stop_time = datetime.now() + timedelta(seconds=25)
            # 读取修正后的停止竞拍时间
            if self.checkBox_super_fast.isChecked(): # 修正停止时间添加键鼠操作节省的0.05秒
                stop_time_after_correction = stop_time + timedelta(
                    seconds=(float(self.lineEdit_shicha.text()) + float(self.lineEdit_yuliang.text()) - 0.005 + 0.05))
            else:
                stop_time_after_correction = stop_time + timedelta(
                    seconds=(float(self.lineEdit_shicha.text()) + float(self.lineEdit_yuliang.text()) - 0.005))
            # print("stop_time_after_correction: ", stop_time_after_correction)
            QApplication.processEvents()
            countdown_time = stop_time_after_correction - datetime.now() - timedelta(seconds=10)  # 倒计10秒时间
            countdown_interval_time = int(countdown_time.total_seconds() * 1000)
            logger.info('countdown_interval_time: %d', countdown_interval_time)

            # 启动倒计时10秒线程
            self.countdown_thd = CountDownOnceTimeThread(countdown_interval_time, self.start_10_sec_do, parent=self)

            time_limit = float(self.lineEdit_lastlimit.text())  # 最后限时   0.4-0.2 之间
            limit_interval_time = stop_time_after_correction - datetime.now() - timedelta(seconds=time_limit)
            limit_interval_time = int(limit_interval_time.total_seconds() * 1000 - 5)  # 单位毫秒
            logger.info('limit_interval_time: %d', limit_interval_time)
            # 启动倒计时操作键鼠线程
            self.limit_thd = CountDownOnceTimeThread(limit_interval_time, self.input_newprice_click_order, parent=self)
            # 启动倒计时foobar线程
            self.limit_foobar_thd = FoobarLimitTimeThread(stop_time_after_correction, time_limit)
            self.limit_foobar_thd.signal_millisecond.connect(self.foobar_thd.update_countdown)

            self.screen = get_screen()

            self.bottom_xiadan_jiage_input_postion_thd = GetPostionThreadDict(self.screen,
                                                                              get_bottom_jiage_gaijia_position)
            self.bottom_xiadan_jiage_input_postion_thd.signal_data.connect(self.store_bottom_xiadan_postion)
            self.bottom_xiadan_jiage_input_postion_thd.start()

            # 开始获取最高价位置，监测最高价格
            self.zuiyoujia_position_thd = GetPostionThreadDict(self.screen, get_xiadan_zuiyoujia_position)
            self.zuiyoujia_position_thd.signal_data.connect(self.store_zuiyoujia_position_start_monitor)
            self.zuiyoujia_position_thd.start()
            QApplication.processEvents()
        except Exception as e:
            logger.error(e)
            logger.error(sys.exc_info()[0:2])  # 打印错误类型，错误值
            logger.error(traceback.extract_tb(sys.exc_info()[2]))  # 出错位置

    def start_10_sec_do(self):
        # self.get_bottom_xiadan_postion()
        if self.mouse_keyboard is None:
            self.mouse_keyboard = LazyImport('modules.dm_plugin').dm
        self.mouse_keyboard.reset_cursor()  # 重置鼠标
        # 移动鼠标到输入框
        self.mouse_keyboard.mouse_move_to(self.jiage_input_postion_right[0], self.jiage_input_postion_right[1])
        # 双击鼠标
        self.mouse_keyboard.mouse_left_double_click()
        # 删除选中内容
        self.mouse_keyboard.press_Backspace()
        # 鼠标移动到改价按钮
        self.mouse_keyboard.mouse_move_to(self.gaijia_button_position_center[0], self.gaijia_button_position_center[1])

    def zuiyoujia_data(self, data):
        try:
            if best_price_result_judgment(data):
                self.zuiyoujia_ocr_times += 1
                data_str = data.replace('D', '')
                data_str = data_str.replace(',', '')
                self.zuiyoujia_content = data_str
                self.foobar_thd.update_price(self.zuiyoujia_content)
            else:
                self.zuiyoujia_ocr_error_time += 1
                globalvar.set_value("zuiyoujia_ocr_error_time", self.zuiyoujia_ocr_error_time)
                if ENVIRONMENT == "pro":
                    logger.warn("zuiyoujia_ocr_error_time: %d try ocr again...", self.zuiyoujia_ocr_error_time)
                else:
                    self.zuiyoujia_content = "666"
                if self.zuiyoujia_ocr_times > 20:
                    if 15 >= self.zuiyoujia_ocr_error_time > 3:
                        logger.warn('zuiyoujia_content re match error! try init positioning again...')
                        # QThread.msleep(500)
                        self.init_dm()
                    elif self.zuiyoujia_ocr_error_time > 15:
                        self.out_times_stop()
            if ENVIRONMENT == 'dev':
                print('\r zuiyoujia: '.format(data) + str(data), end="")
        except Exception as e:
            logger.error(e)
            logger.error(sys.exc_info()[0:2])  # 打印错误类型，错误值
            logger.error(traceback.extract_tb(sys.exc_info()[2]))  # 出错位置

    def out_times_stop(self):
        self.zuiyoujia_monitor_thd.stop()
        self.foobar_thd.stop()
        self.limit_foobar_thd.stop()
        self.MKey_pressEvent("stop")
        if show_position_rect:
            try:
                self.zuiyoujia_position_foobar_thd.stop()
                self.jiage_text_input_position_foobar_thd.stop()
                self.gaijia_button_position_foobar_thd.stop()
                if self.zuiyoujia_position_foobar_thd.isRunning():
                    self.zuiyoujia_position_foobar_thd.terminate()
                if self.jiage_text_input_position_foobar_thd.isRunning():
                    self.jiage_text_input_position_foobar_thd.terminate()
                if self.gaijia_button_position_foobar_thd.isRunning():
                    self.gaijia_button_position_foobar_thd.terminate()
            except Exception as e:
                logger.error(e)
                logger.error(sys.exc_info()[0:2])  # 打印错误类型，错误值
                logger.error(traceback.extract_tb(sys.exc_info()[2]))  # 出错位置

    def show_rect(self):
        try:
            if show_position_rect:  # 绘制矩形框
                # 绘制最绘制最高价位置框
                if self.zuiyoujia_position:
                    if self.zuiyoujia_position_foobar_thd is None:
                        self.zuiyoujia_position_foobar_thd = FoobarDrawRectSingle(self.zuiyoujia_position)
                        self.zuiyoujia_position_foobar_thd.start()
                    else:
                        self.zuiyoujia_position_foobar_thd.start()
                # 绘制价格输入框 的矩形框
                if self.jiage_text_input_position:
                    if self.jiage_text_input_position_foobar_thd is None:
                        self.jiage_text_input_position_foobar_thd = FoobarDrawRectSingle(self.jiage_text_input_position)
                        self.jiage_text_input_position_foobar_thd.start()
                    else:
                        self.jiage_text_input_position_foobar_thd.start()
                # 绘制底部下单矩形框
                if self.gaijia_button_position:
                    if self.gaijia_button_position_foobar_thd is None:
                        self.gaijia_button_position_foobar_thd = FoobarDrawRectSingle(self.gaijia_button_position)
                        self.gaijia_button_position_foobar_thd.start()
                    else:
                        self.gaijia_button_position_foobar_thd.start()
        except Exception as e:
            logger.error(e)
            logger.error(sys.exc_info()[0:2])  # 打印错误类型，错误值
            logger.error(traceback.extract_tb(sys.exc_info()[2]))  # 出错位置

    def init_dm(self):
        try:
            self.foobar_thd.stop()
            QApplication.processEvents()
        except AttributeError:
            pass
        except TypeError as e:
            logger.error(e)
        try:
            self.zuiyoujia_monitor_thd.stop()
            QApplication.processEvents()
        except AttributeError:
            pass
        except TypeError as e:
            logger.error(e)
        try:
            self.zuiyoujia_position_foobar_thd.stop()
            QApplication.processEvents()
        except AttributeError:
            pass
        except TypeError as e:
            logger.error(e)
        try:
            self.jiage_text_input_position_foobar_thd.stop()
            QApplication.processEvents()
        except AttributeError:
            pass
        try:
            self.gaijia_button_position_foobar_thd.stop()
            QApplication.processEvents()
        except AttributeError:
            pass

        self.dm.__init__()
        QApplication.processEvents()
        # self.dm.Reg()
        QApplication.processEvents()
        self.zuiyoujia_position = get_xiadan_zuiyoujia_position(get_screen())["zuiyoujia_position"]
        self.zuiyoujia_monitor_thd.update_postion(self.zuiyoujia_position)
        self.show_rect()
        self.foobar_thd.show_foobar()
        globalvar.set_value("zuiyoujia_ocr_error_time", self.zuiyoujia_ocr_error_time)

    def update_qiangdan_limit_price(self, price_up: bool, old_price: float) -> None:
        try:
            tmp_price = float(old_price)
            new_price = tmp_price
            if price_up is True and tmp_price < zuigaojia_limit:
                new_price = tmp_price + 1
            elif price_up is False and tmp_price > 2:
                new_price = tmp_price - 1
            new_price = round(new_price, 1)
            globalvar.set_value("limit_price", new_price)
            self.lineEdit_qiangdanxianjia.setText(str(new_price))
            self.qiangdan_foobar_thd.update_price(new_price)

        except Exception as e:
            logger.error(e)
            logger.error(sys.exc_info()[0:2])  # 打印错误类型，错误值
            logger.error(traceback.extract_tb(sys.exc_info()[2]))  # 出错位置

    def click_qiangdan_btn(self):
        globalvar.set_value('limit_price',self.lineEdit_qiangdanxianjia.text())
        self.showMinimized()
        # 获取本节开始时间
        self.get_benjiekaishishijian_thd = GetPostionThreadDict(get_screen(), get_qizhishijian_content, self)
        self.get_benjiekaishishijian_thd.signal_data.connect(self.after_get_benjieshijian)
        self.get_benjiekaishishijian_thd.start()

    def after_get_benjieshijian(self, benjieshijian):
        try:
            # 获取“最高价格(元/吨)”标题位置
            xiadan_zuiyoujia_position_dict = get_xiadan_zuiyoujia_position(get_screen())
            if ENVIRONMENT == "dev":
                print("xiadan_zuiyoujia_position_dict: ", xiadan_zuiyoujia_position_dict)
            zuiyoujia_position = xiadan_zuiyoujia_position_dict["zuiyoujia_position"]
            xiadan_button_position = xiadan_zuiyoujia_position_dict["xiadan_button_position"]

            if len(benjieshijian["benjiekaishishijian"]) < 8:
                raise ValueError('get benjiekaishishijian error! len(benjieshijian["benjiekaishishijian"]) < 8')
            now_date = str(datetime.now().date())
            benjiekaishishijian = benjieshijian['benjiekaishishijian']
            benjiekaishishijian = now_date + ' ' + benjiekaishishijian
            benjiekaishishijian = datetime.strptime(benjiekaishishijian, '%Y-%m-%d %H:%M:%S')
            if float(self.lineEdit_shicha.text()) == 0:
                time_after_correction = benjiekaishishijian + timedelta(seconds=float(self.lineEdit_shicha.text()))
            else:
                time_after_correction = benjiekaishishijian + timedelta(
                    seconds=(float(self.lineEdit_shicha.text()) + float(self.lineEdit_yuliang.text())))
            if ENVIRONMENT == "dev":
                benjiekaishishijian = datetime.now() + timedelta(seconds=10)
            # 启动绘制“下单”位置方框线程
            if show_position_rect:
                self.top_xiadan_position_foobar_thd = FoobarDrawRectSingle(xiadan_button_position)
                self.top_xiadan_position_foobar_thd.start()
            if self.checkBox_duobao.isChecked():
                package_num = int(self.lineEdit_duobao.text())
                if package_num < 0:
                    raise ValueError("多包抢单模式，包数错误！")
                self.qiangdan_thd = StartQiangDanMulti(top_xiadan_position=xiadan_button_position,
                                                       zuiyoujia_position=zuiyoujia_position,
                                                       start_time=benjiekaishishijian,
                                                       is_limit_price=self.checkBox_qiangdanxianjia.isChecked(),
                                                       limit_price=globalvar.get_value('limit_price'),
                                                       is_limit_time=self.checkBox_qiangdanxianshi.isChecked(),
                                                       limit_time=float(self.lineEdit_qiangdanxianshi.text()),
                                                       package_num=package_num,
                                                       scale_rate=self.controlled_scale_rate,
                                                       parent=self)
                self.qiangdan_thd.signal_order.connect(self.showNormal)
                self.qiangdan_thd.start()
            elif self.checkBox_qiangdanxianjia.isChecked():
                if float(self.lineEdit_qiangdanxianjia.text()) < 3:
                    self.message_box_warn("警告", "请输入正确的限价")
                else:
                    self.qiangdan_thd = StartQiangDan(top_xiadan_position=xiadan_button_position,
                                                      start_time=time_after_correction,
                                                      is_limit_price=self.checkBox_qiangdanxianjia.isChecked(),
                                                      limit_price=globalvar.get_value('limit_price'),
                                                      is_limit_time=self.checkBox_qiangdanxianshi.isChecked(),
                                                      limit_time=float(self.lineEdit_qiangdanxianshi.text()),
                                                      scale_rate=self.controlled_scale_rate,
                                                      is_continuous_order=self.checkBox_is_continuous_order.isChecked(),
                                                      parent=self)
                    # print("self.checkBox_qiangdanxianshi.isChecked(): ", self.checkBox_qiangdanxianshi.isChecked())
                    self.qiangdan_thd.signal_order.connect(self.showNormal)
                    self.qiangdan_thd.start()
            else:
                self.qiangdan_thd = StartQiangDan(top_xiadan_position=xiadan_button_position,
                                                  start_time=time_after_correction,
                                                  is_limit_price=False,
                                                  limit_price=None,
                                                  is_limit_time=self.checkBox_qiangdanxianshi.isChecked(),
                                                  limit_time=float(self.lineEdit_qiangdanxianshi.text()),
                                                  scale_rate=self.controlled_scale_rate,
                                                  is_continuous_order=self.checkBox_is_continuous_order.isChecked(),
                                                  parent=self)
                self.qiangdan_thd.signal_order.connect(self.showNormal)
                self.qiangdan_thd.start()
                # print("self.checkBox_qiangdanxianshi.isChecked(): ", self.checkBox_qiangdanxianshi.isChecked())

            self.qiangdan_foobar_thd = FoobarNoticeNowPrice("    下单时间：  " + self.lineEdit_qiangdanxianshi.text())
            self.qiangdan_foobar_thd.show_foobar()
            if self.lineEdit_qiangdanxianjia.text() is None:
                self.qiangdan_foobar_thd.update_price('起拍价')
            else:
                self.qiangdan_foobar_thd.update_price(globalvar.get_value('limit_price'))
        except ValueError as e:
            logger.error(e)

    def get_jingjiafudu(self):
        # 竞价幅度
        if self.comboBox_jiajiafudu.currentIndex() == 0:
            jingjiafudu = 1
        elif self.comboBox_jiajiafudu.currentIndex() == 1:
            jingjiafudu = 2
        elif self.comboBox_jiajiafudu.currentIndex() == 2:
            jingjiafudu = 3
        elif self.comboBox_jiajiafudu.currentIndex() == 3:
            jingjiafudu = 4
        elif self.comboBox_jiajiafudu.currentIndex() == 4:
            jingjiafudu = 5
        elif self.comboBox_jiajiafudu.currentIndex() == 5:
            jingjiafudu = 6
        elif self.comboBox_jiajiafudu.currentIndex() == 6:
            jingjiafudu = 7
        elif self.comboBox_jiajiafudu.currentIndex() == 7:
            jingjiafudu = 8
        elif self.comboBox_jiajiafudu.currentIndex() == 8:
            jingjiafudu = 9
        elif self.comboBox_jiajiafudu.currentIndex() == 9:
            jingjiafudu = 10
        elif self.comboBox_jiajiafudu.currentIndex() == 10:
            jingjiafudu = 13
        elif self.comboBox_jiajiafudu.currentIndex() == 11:
            jingjiafudu = 15
        else:
            jingjiafudu = 17
        return jingjiafudu

    def input_newprice_click_order(self):  # 当前时间最后限时内 重置鼠标、输入：最高价+1，鼠标点击：下单
        try:
            self.limit_foobar_thd.stop()
            # while True:
            #     if best_price_result_judgment(self.zuiyoujia_content):
            #         break
            #     else:
            #         logger.warn('memory zuigaojia_content re match error! try it again...')
            if ENVIRONMENT == 'dev':
                print('reset_mouse_input_click_order zuigaojia:', self.zuiyoujia_content)
                print('bottom_xiadan_center:', self.gaijia_button_position_center)

            # 新价格
            if self.checkBox_zuidijiagejingpai.isChecked():
                new_price = str(math.ceil(float(self.zuiyoujia_content) - self.get_jingjiafudu()))
            else:
                new_price = str(math.ceil(float(self.zuiyoujia_content) + self.get_jingjiafudu()))

            # 停止dm数字识别线程
            self.zuiyoujia_monitor_thd.stop()
            # TODO 重写logger，message信息
            # 判断是否限价 以及是否超过限价
            if self.checkBox_jingpaixianjia.isChecked():
                # 如果最低价格竞拍
                if self.checkBox_zuidijiagejingpai.isChecked():
                    # 价格大于限价就继续下单
                    if float(self.zuiyoujia_content) > float(self.lineEdit_jingpaixianjia.text()):
                        self.key_mouse_operate(new_price)
                        logger.info("完成加价，当前价格：%s, 下单价为：%s", self.zuiyoujia_content, new_price)
                        self.stop_order_do()
                        self.message_box_info("完成", "下单完成，当前下单价格为：" + new_price)
                    else:
                        # self.key_mouse_operate(self.lineEdit_jingpaixianjia.text())
                        logger.warn("当前价格: %s，低于限价%s，没有下单！", self.zuiyoujia_content,
                                    self.lineEdit_jingpaixianjia.text())
                        self.stop_order_do()
                        raise ValueError(
                            "当前价格" + self.zuiyoujia_content + "超过最高限价 " + self.lineEdit_jingpaixianjia.text() + "，没有下单！")
                # 价格小于限价，加价下单
                elif float(self.zuiyoujia_content) < float(self.lineEdit_jingpaixianjia.text()):
                    self.key_mouse_operate(new_price)
                    logger.info("完成加价，当前价格：%s, 下单价为：%s", self.zuiyoujia_content, new_price)
                    self.stop_order_do()
                    self.message_box_info("完成", "下单完成，当前价格为：" + self.zuiyoujia_content + "下单价格为：" + new_price)
                else:
                    # self.key_mouse_operate(self.lineEdit_jingpaixianjia.text())
                    logger.warn("当前价格: %s，高于限价%s，没有下单！", self.zuiyoujia_content,
                                self.lineEdit_jingpaixianjia.text())
                    self.stop_order_do()
                    raise ValueError(
                        "当前价格" + self.zuiyoujia_content + "超过最高限价 " + self.lineEdit_jingpaixianjia.text() + "，没有下单！")
            # 无限价直接操作下单
            else:
                self.key_mouse_operate(new_price)
                self.stop_order_do()
                logger.info("完成加价，当前价格：%s, 下单价为：%s", self.zuiyoujia_content, new_price)
                self.message_box_info("完成", "下单完成，当前价格为：" + self.zuiyoujia_content + "下单价格为：" + new_price)

        except ValueError as e:
            self.message_box_warn("警告", str(e))
            self.stop_order_do()

    def stop_order_do(self):
        self.limit_foobar_thd.stop()
        self.zuiyoujia_monitor_thd.stop()
        # 停止矩形框线程
        if show_position_rect:
            try:
                self.zuiyoujia_position_foobar_thd.stop()
                self.jiage_text_input_position_foobar_thd.stop()
                self.gaijia_button_position_foobar_thd.stop()
                if self.zuiyoujia_position_foobar_thd.isRunning():
                    self.zuiyoujia_position_foobar_thd.terminate()
                if self.jiage_text_input_position_foobar_thd.isRunning():
                    self.jiage_text_input_position_foobar_thd.terminate()
                if self.gaijia_button_position_foobar_thd.isRunning():
                    self.gaijia_button_position_foobar_thd.terminate()
            except Exception as e:
                logger.error(e)
                logger.error(sys.exc_info()[0:2])  # 打印错误类型，错误值
                logger.error(traceback.extract_tb(sys.exc_info()[2]))  # 出错位置

        self.foobar_thd.stop()
        self.start_btn.setEnabled(True)
        # self.MKey_pressEvent("stop")

        QThread.sleep(after_stop_wait_show_normal_time)  # 恢复正常窗口之前等待时间
        self.showNormal()  # 恢复屏幕到正常窗口

    # @func_time
    def key_mouse_operate(self, new_price):
        # 判断是否极限竞拍
        if self.checkBox_super_fast.isChecked():
            self.mouse_keyboard.input(new_price, is_fast=True)  # 输入价格
            self.mouse_keyboard.mouse_left_click(is_fast=True)  # 单击鼠标下单

        else:
            self.mouse_keyboard.mouse_move_to(self.jiage_input_postion_right[0],
                                              self.jiage_input_postion_right[1])  # 移动鼠标到输入框
            self.mouse_keyboard.mouse_left_click(is_fast=True)

            self.mouse_keyboard.input(new_price, is_fast=True)  # 输入价格
            self.mouse_keyboard.mouse_move_to(self.gaijia_button_position_center[0],
                                              self.gaijia_button_position_center[1])  # 鼠标移动到下单位置
            self.mouse_keyboard.mouse_left_click(is_fast=True)  # 单击鼠标下单

        self.mouse_keyboard.press_Enter(is_fast=True)
        self.mouse_keyboard.press_Enter(is_fast=True)

    @staticmethod
    def del_global_var():
        # 清除全局变量
        globalvar.set_value("zuiyoujia_ocr_error_time", None)
        globalvar.set_value("benjiekaishishijian", None)
        globalvar.set_value("benjiejieshushijian", None)
        globalvar.set_value("bottom_xiadan_postion", None)
