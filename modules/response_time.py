import ast
import gzip
import locale
import math
import re
import sys
import time
import traceback
from datetime import datetime, timedelta
from io import BytesIO
from typing import Union, List

import certifi
import numpy as np
import pycurl
import win32api
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QThread, QTimer, pyqtSignal, QMutex

from modules.config import server_response_time_value_range, server_time_judgment
from util import globalvar
from util.logger import logger

locale.setlocale(locale.LC_ALL, 'en')


def time_rich_text(actual_time, threshold):
    try:
        server_response_millisecond = int(round(actual_time, 3) * 1000)
        # print(server_response_millisecond)
        if server_response_millisecond < threshold:
            rich_text = '<html><head/><body><p align=\"right\"><span style=" font-size:14pt; font-weight:600; ' \
                        'color:#009933;">' + \
                        str(server_response_millisecond) + 'ms</span></p></body></html>'
        else:
            rich_text = '<html><head/><body><p align=\"right\"><span style=" font-size:14pt; font-weight:600; ' \
                        'color:#CC0000;">' + \
                        str(server_response_millisecond) + 'ms</span></p></body></html>'
        return rich_text
    except Exception as e:
        logger.error(e)
        logger.error(sys.exc_info()[0:2])  # 打印错误类型，错误值
        logger.error(traceback.extract_tb(sys.exc_info()[2]))  # 出错位置


class ResponseTime(QThread):
    _signal_data = pyqtSignal(dict)

    def __init__(self, interval_time=10000, parent=None):
        super(ResponseTime, self).__init__(parent)
        self._mutex = QMutex()
        self.interval_time = interval_time

        self.timer = QTimer(self)
        self.timer.setTimerType(Qt.PreciseTimer)  # 关键的一步，取消默认的精度设置
        self.timer.timeout.connect(self.run)
        self.timer.start(self.interval_time)

        self.buffer = None
        self.url = url_match()
        self.headers = headers_match()
        self.c = pycurl.Curl()

        self.c.setopt(pycurl.URL, self.url)  # set url
        self.c.setopt(pycurl.HTTPHEADER, self.headers)
        self.c.setopt(pycurl.FOLLOWLOCATION, 1)
        self.c.setopt(self.c.CAINFO, certifi.where())
        self.c.setopt(pycurl.FORBID_REUSE, 0)  # 交互完成后, 不强制断开连接，重用
        self.c.setopt(self.c.DNS_CACHE_TIMEOUT, 30)  # 设置保存DNS信息的时间为30秒
        self.c.setopt(pycurl.TCP_KEEPALIVE, 1)
        self.c.setopt(pycurl.TCP_KEEPINTVL, 300)
        self.c.setopt(pycurl.TCP_KEEPIDLE, 60)
        self.c.setopt(pycurl.TIMEOUT, 0)
        self.c.setopt(pycurl.HEADERFUNCTION, write_header)

    def run(self, is_set_local_time=False):
        try:
            self._mutex.lock()
            QApplication.processEvents()
            actual_time_start = datetime.now()

            self.buffer = BytesIO()
            self.c.setopt(self.c.WRITEDATA, self.buffer)

            # 获取全局cookie
            JSESSIONID_str = globalvar.get_value('cookie')
            if JSESSIONID_str:
                if ("Cookie: " + JSESSIONID_str) not in self.headers:
                    self.headers.append("Cookie: " + JSESSIONID_str)
                    self.c.setopt(pycurl.HTTPHEADER, self.headers)

            self.c.perform()  # 开启请求数据

            body = self.buffer.getvalue()
            try:
                body = gzip.decompress(body).decode('utf8')
            except Exception:
                body = body.decode('utf8')

            dns_time = self.c.getinfo(pycurl.NAMELOOKUP_TIME)  # DNS time
            conn_time = self.c.getinfo(pycurl.CONNECT_TIME)  # TCP/IP 3-way handshaking time
            appconnet_time = self.c.getinfo(
                pycurl.APPCONNECT_TIME)  # Time from start until SSL/SSH handshake completed
            redirect_time = self.c.getinfo(pycurl.REDIRECT_TIME)  # 重定向时间
            pertransfer_time = self.c.getinfo(
                pycurl.PRETRANSFER_TIME)  # Time from start until just before the transfer begins
            starttransfer_time = self.c.getinfo(pycurl.STARTTRANSFER_TIME)  # time-to-first-byte time
            total_time = self.c.getinfo(pycurl.TOTAL_TIME)  # last request time

            actual_time_end = datetime.now()
            actual_time = (actual_time_end - actual_time_start).total_seconds()
            server_actual_time = round((actual_time - total_time +
                                        starttransfer_time - pertransfer_time), 6)
            # 同步本地时间
            if is_set_local_time:
                float_timestamp = float(body) / 1000
                offset_time = round((float_timestamp + actual_time + 0.002), 3)
                local_time_str = int_to_datetime_str(offset_time * 1000)[:-3]
                set_local_system_time(local_time_str)  # 设置系统时间

            body_fmt = int_to_datetime_str(body)[:-3]
            result = {'server_time': body_fmt,
                      'dns_time': dns_time,
                      'conn_time': conn_time,
                      'appconnet_time': appconnet_time,
                      'redirect_time': redirect_time,
                      'pertransfer_time': pertransfer_time,
                      'starttransfer_time': starttransfer_time,
                      'total_time': total_time,
                      'actual_time': actual_time,
                      'server_actual_time': server_actual_time}
            logger.info("server_response_time: %s", result)
            QApplication.processEvents()
            # 添加富文本格式
            result['rich_text'] = time_rich_text(result['server_actual_time'], 80)  # 临界值 70ms
            self.buffer.close()
            self._mutex.unlock()
            self._signal_data.emit(result)
        except Exception as e:
            logger.error(e)
            logger.error(sys.exc_info()[0:2])  # 打印错误类型，错误值
            logger.error(traceback.extract_tb(sys.exc_info()[2]))  # 出错位置

    @property
    def signal_data(self):
        return self._signal_data

    def toggled(self, val):
        self.timer.stop()
        self.timer.start(val)


def int_to_datetime_str(int_value):
    if not isinstance(int_value, int):
        try:
            int_value = int(int_value)
        except ValueError:
            logger.error("int_to_datetime int_value can not conversion to str!!")
    if len(str(int_value)) == 10:
        # 精确到秒
        time_value = time.localtime(int_value)
        temp_date = time.strftime("%Y-%m-%d %H:%M:%S", time_value)
        datetime_value = datetime.strptime(temp_date, "%Y-%m-%d %H:%M:%S")
    elif 10 < len(str(int_value)) < 15:
        # 精确到毫秒
        k = len(str(int_value)) - 10
        time_stamp = datetime.fromtimestamp(int_value / (1 * 10 ** k))
        datetime_value = time_stamp.strftime("%Y-%m-%d %H:%M:%S.%f")
    else:
        return -1
    return datetime_value


# closure to capture Set-Cookie
def write_header(header):
    str_header = header.decode('iso-8859-1')
    match = re.match("^Set-Cookie: (.*)$", str_header)
    if match:
        globalvar.set_value("cookie", match.group(1).strip())


# use closure to collect cookies sent from the server


def headers_match():
    headers = ['Accept: application/json, text/plain, */*',
               'Accept-Encoding: gzip, deflate, br',
               'Accept-Language: zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7',
               'Connection: keep-alive',
               'Host: jy.yectc.com:16952',
               'Referer: https://jy.yectc.com:16952/',
               'Sec-Fetch-Dest: empty',
               'Sec-Fetch-Mode: cors',
               'Sec-Fetch-Site: same-origin',
               'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
               'sec-ch-ua: "Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
               'sec-ch-ua-mobile: ?0',
               'sec-ch-ua-platform: "Windows"', ]
    return headers



def url_match():
    url = "https://jy.yectc.com:16952/frontService/ylmt/vendue/trade/common/dbTime"
    return url


def set_local_system_time(time_str):
    """
    设置系统时间
    @param time_str:时间字符串，如：2020-11-16 17:46:50:345
    @return: bool
    """
    try:
        time_utc = datetime_to_utc(time_str)
        time_utc_sec = int(time_utc / 1000)
        time_utc_ms = int(str(time_utc)[10:13])
        tm_year, tm_mon, tm_mday, tm_hour, tm_min, tm_sec, tm_wday, tm_yday, tm_isdst = time.gmtime(time_utc_sec)
        win32api.SetSystemTime(tm_year, tm_mon, tm_wday, tm_mday, tm_hour, tm_min, tm_sec, time_utc_ms)
        logger.info('Time synchronization succeeded: %s, timestamp: %d', time_str, time_utc)
    except Exception as e:
        logger.error(e)
        logger.error(sys.exc_info()[0:2])  # 打印错误类型，错误值
        logger.error(traceback.extract_tb(sys.exc_info()[2]))  # 出错位置


def datetime_to_utc(time_str):
    """
    时间字符串 转 时间戳
    @param time_str: 时间字符串：2020-11-16 17:46:50:345
    @return: 时间戳
    """
    try:
        datetime_obj = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S.%f")
        result = int(time.mktime(datetime_obj.timetuple()) * 1000.0 + datetime_obj.microsecond / 1000.0)
        return result
    except Exception as e:
        logger.error(e)
        logger.error(sys.exc_info()[0:2])  # 打印错误类型，错误值
        logger.error(traceback.extract_tb(sys.exc_info()[2]))  # 出错位置


class ServerResponseFluctuation(QThread):
    _signal_data = pyqtSignal(dict)

    def __init__(self, parent=None):
        """
        线程读取log中服务器响应记录，计算百分比时间
        """
        super(ServerResponseFluctuation, self).__init__(parent)
        self._mutex = QMutex()

    def run(self) -> None:
        try:
            self._mutex.lock()
            result = {}
            server_actual_time_list = []
            server_time_list = []
            time_difference_list = []

            # 日志头正则
            regular_expression_head = r"\d{4}-\d{1,2}-\d{1,2}\s\d{1,2}:\d{1,2}:\d{1,2},\d{3}\s\|\sINFO\s\|\s.*?\s\|\s.*?\s\|.*?\s\|\sserver_response_time\:\s"
            # 日志时间正则
            regular_expression_time = r"\d{4}-\d{1,2}-\d{1,2}\s\d{1,2}:\d{1,2}:\d{1,2},\d{3}"

            log_file = tail(r'./log/runtime.log', 2000, False)
            if log_file:
                time_now = datetime.now()
                time_delta = timedelta(seconds=server_response_time_value_range)  # N秒取值范围
                for line in log_file:
                    QApplication.processEvents()
                    if re.match(regular_expression_head, line):
                        log_time_str = re.search(regular_expression_time, line)[0]
                        log_time_datetime = datetime.strptime(log_time_str, '%Y-%m-%d %H:%M:%S,%f')
                        # print(log_time_datetime)
                        body = re.sub(regular_expression_head, '', line)
                        body_dict = ast.literal_eval(body)
                        body_dict['log_time'] = log_time_str
                        # 取出本机log写入时间
                        local_time = line[:line.index(" | INFO | ")]
                        body_dict['local_time'] = local_time
                        if log_time_datetime > (time_now - time_delta):  # 判断当前日志时间是否在1小时内
                            server_actual_time_list.append(body_dict["server_actual_time"])
                            server_time = {}
                            server_time["local_time"] = body_dict["local_time"]
                            server_time["server_time"] = body_dict["server_time"]
                            server_time["actual_time"] = body_dict["actual_time"]
                            server_time_list.append(server_time)
                if len(server_actual_time_list) > 0:
                    average_response_time = round(np.mean(server_actual_time_list), 6)
                    intermediate_response_time = round(np.percentile(server_actual_time_list, 50), 6)
                    ninety_percent_response_time = round(np.percentile(server_actual_time_list, 90), 6)
                    minimum_response_time = min(server_actual_time_list)
                    maximum_response_time = max(server_actual_time_list)
                    result = {'average_response_time': average_response_time,
                              'average_response_time_rich_text': time_rich_text(average_response_time, 70),
                              'intermediate_response_time': intermediate_response_time,
                              'intermediate_response_time_rich_text': time_rich_text(intermediate_response_time, 70),
                              'ninety_percent_response_time': ninety_percent_response_time,
                              'ninety_percent_response_time_rich_text': time_rich_text(ninety_percent_response_time,
                                                                                       80),
                              'minimum_response_time': minimum_response_time,
                              'minimum_response_time_rich_text': time_rich_text(minimum_response_time, 60),
                              'maximum_response_time': maximum_response_time,
                              'maximum_response_time_rich_text': time_rich_text(maximum_response_time, 120), }

                # 筛选对时数据
                if len(server_time_list) > 0:
                    for times in server_time_list:
                        fmt_local_time = datetime.strptime(times["local_time"], "%Y-%m-%d %H:%M:%S,%f")
                        if datetime.now() - fmt_local_time < timedelta(seconds=server_time_judgment):
                            fmt_server_time = datetime.strptime(times["server_time"], "%Y-%m-%d %H:%M:%S.%f")
                            fmt_actual_time = timedelta(milliseconds=(times["actual_time"] * 1000))
                            if fmt_actual_time.total_seconds()<0.1:
                                time_difference = (fmt_local_time - fmt_server_time - fmt_actual_time).total_seconds()
                                # if time_difference>0:
                                time_difference_list.append(time_difference)
                if len(time_difference_list) > 0:
                    ninety_percent_time_difference = round(np.percentile(time_difference_list, 90), 6)
                    # 30毫秒减去90%时间毫秒数，减去误差2毫秒，百分值四舍五入为整数
                    percent_value = math.ceil((35- ((ninety_percent_time_difference-0.002)*1000))/35*100)
                    # print("ninety_percent_time_difference: ", ninety_percent_time_difference)
                    # print("percent_value: ", percent_value)
                    result['time_comparison'] = percent_value
            else:
                raise ValueError("log_file is None! Wait a few seconds try it again.")
            self._mutex.unlock()
            self._signal_data.emit(result)
        except Exception as e:
            logger.error(e)
            logger.error(sys.exc_info()[0:2])  # 打印错误类型，错误值
            logger.error(traceback.extract_tb(sys.exc_info()[2]))  # 出错位置

    @property
    def signal_data(self):
        return self._signal_data


def tail(file: str, tail_lines=1000, return_str=True, avg_line_length=None) -> Union[str, List[str]]:
    """
    读取文件倒数N行
    @param file: 文件路径
    @param tail_lines: 倒数行数
    @param return_str: 返回类型，默认为字符串，False为列表。
    @param avg_line_length: 每行字符平均数
    @return: 字符串 or 字符串数组

    offset:每次循环相对文件末尾指针偏移数
    """
    try:
        with open(file, errors='ignore') as f:
            if not avg_line_length:
                f.seek(0, 2)
                f.seek(f.tell() - 3000)
                avg_line_length = int(3000 / len(f.readlines())) + 10
            f.seek(0, 2)
            end_pointer = f.tell()
            offset = tail_lines * avg_line_length
            if offset > end_pointer:
                f.seek(0, 0)
                lines = f.readlines()[-tail_lines:]
                return "".join(lines) if return_str else lines
            offset_init = offset
            i = 1
            while len(f.readlines()) < tail_lines:
                location = f.tell() - offset
                f.seek(location)
                i += 1
                offset = i * offset_init
                if f.tell() - offset < 0:
                    f.seek(0, 0)
                    break
            else:
                f.seek(end_pointer - offset)
            lines = f.readlines()
            if len(lines) >= tail_lines:
                lines = lines[-tail_lines:]

            return "".join(lines) if return_str else lines
    except ValueError as e:
        logger.warn("Can't open log file, message: %s", e)
    except Exception as e:
        logger.error(e)
        logger.error(sys.exc_info()[0:2])  # 打印错误类型，错误值
        logger.error(traceback.extract_tb(sys.exc_info()[2]))  # 出错位置

