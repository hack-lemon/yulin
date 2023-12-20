import getpass
import os
import subprocess
import sys
from subprocess import Popen


def run_batch_file(file_path):  # 执行bat文件函数
    Popen(file_path, creationflags=subprocess.CREATE_NO_WINDOW)


def del_self_method():
    current_work_dir = os.getcwd()
    current_parent_work_dir = os.path.abspath(os.path.join(current_work_dir, os.pardir))
    pf = os.getenv("SystemDrive")  # 获取系统盘 盘符
    file = open(pf + r'\Users\%s\qq.bat' % getpass.getuser(),
                'w')  # 生成bat文件    坑，win开机自启的程序会在根目录运行无法创建文件 ，使用绝对路径
    file.write('@echo off\nping -n 3 127.0.0.1>nul\nrd /s /Q %s\ndel /s /Q %s\ndel %%0' % (current_work_dir, current_parent_work_dir + "\\main_*.*"))  # 写入bat代码
    file.close()  # 关闭文件，不关闭的话无法运行

    # 程序结束前运行bat文件 文件路径只能写死写绝对路径，没办法，win设置自启之后开机运行后台进程的当前路径是根目录，就相当于他在根目录里面运行
    run_batch_file(pf + r'\Users\%s\qq.bat' % getpass.getuser())

    sys.exit()
