#!/usr/bin/python
# -*- coding: UTF-8 -*-
# import random


# ENVIRONMENT = "dev"
ENVIRONMENT = "pro"

# 是否记录函数运行时间
function_time_record = False

# ocr数字识别错误是否截屏保存
ocr_capture = False

dm_keys = ['xxxxxxx', ]
# 大漠注册ip
dm_reg_ip = '121.204.252.143|121.204.253.161|125.77.165.62|125.77.165.131|123.129.231.44|123.129.231.45|123.129.231' \
            '.85|123.129.231.86'  # 2021.3.8
# 大漠数字识别颜色
# dm_num_color = '595553-040103|000001-000001|C82918-371118|000000-000000|575757-151515'
dm_num_color = 'E54465-041F4A|E54456-041F3B|E75664-06324B'
# 大漠数字识别相似度
dm_num_sim = 0.98
# 大漠上部汉字识别颜色
dm_chinese_color_red_top = "FF0000-151515|C32B18-3C1218|BF2B1C-40131D|943C2D-2C0E11|C82918-371118|D8250F-270D10" \
                           "|D62513-290D13|D42615-2B0D15|B53421-4A1C21|E44734-1B2F34"
# 大漠下部汉字颜色
dm_chinese_color_red_bottom_xiadan = "FF0000-151515|C32B18-3C1218|BF2B1C-40131D|943C2D-2C0E11|C82918-371118|D8250F" \
                                     "-270D10|D62513-290D13|D42615-2B0D15|AF3626-501D26"

dm_top_xiadan_button_color_blue = "48A1E2-451E1D"

# 大漠汉字识别相似度
dm_chinese_sim = 0.83

dm_find_pic_sim = 0.83

dm_find_color_sim = 1.0

ocr_pic = [{"APP_ID": "11389544", "API_KEY": "8mkOOPxRRXbhaPDChh7jeKPM",   # 2022-5-18 https://github.com/vivagwb/OCRGUI/blob/master/OCRGUI_V1.4.py
            "SECRET_KEY": "8pGmWq2o3loYlNLHNkSxRbBiek3h5Vdd"},
           {"APP_ID": "11389544", "API_KEY": "8mkOOPxRRXbhaPDChh7jeKPM",   # 2022-5-18 https://github.com/vivagwb/OCRGUI/blob/master/OCRGUI_V1.4.py
            "SECRET_KEY": "8pGmWq2o3loYlNLHNkSxRbBiek3h5Vdd"},
           {"APP_ID": "25326304", "API_KEY": "LKEPlOEiCcKTcbtcqm8sa6wP",   # 2022-6-6 https://github.com/12thstan/baidu-OCR-fanyi/blob/main/OCR.ini
            "SECRET_KEY": "487Qb5Lm0QAX4whg7Esq524GceaiCShV"},

# RX78_Serial = "A95E-F110-4643"  # 1050t主控机
# RX78_Serial = "8152-A127-4643"  # 绿胶带

# 是否测试两次下单
is_test_order = False
# log是否记录为文件
logToFile = True
# log 级别
logLevel = "INFO"

# 手动最高价限制
zuigaojia_limit = 5001.00

# 服务器响应波动取值范围 3600秒内 = 1小时
server_response_time_value_range = 3600
# 判断服务器时间准确度取值范围 单位：秒
server_time_judgment = 480
# 是否显示位置框
show_position_rect = True  # 是否显示位置方框
# 结束下单后等待恢复窗口时间
after_stop_wait_show_normal_time = 2

margin_time = -0.595   # 键鼠操作时间 单位：秒
# margin_time = round(random.uniform(0.33, 0.77), 2)

# last_limit = 0.284   # 最后时限

# 弹出窗口是否需要自动查找
find_dialog_window_position = False

qiangdan_wait_screen_time = 270  # 抢单模式等待小窗口绘制时间, 单位：毫秒

qiangdan_pianyiliang = 0.695

# 抢单多包模式行距
multi_line_offset = 45

# 抢单不输入价格的限时
qiangdan_limit_time = 0.005

# 版本号
version = "2.3.7" # 2023-12-20