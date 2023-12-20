#!/usr/bin/python
# coding=gbk
import sys
import traceback
from ctypes import windll
from comtypes.client import CreateObject
from random import randint
from time import sleep

from modules.config import dm_keys, dm_reg_ip
from util.logger import logger
from util.tools import func_time


# @func_time
class Dm(object):
    @func_time
    # @logger.catch()
    def __init__(self):
        try:
            dms = windll.LoadLibrary(r'./util/DmReg.dll')
            dms.SetDllPathW(r'./util/dm.dll', 0)
            self._dm = CreateObject('dm.dmsoft')
        except Exception as err:
            logger.error('%s: %s', type(err), err)
        else:
            self._dm.SetDict(0, r'./util/num')
            self._dm.SetDict(1, r'./util/chinese')
            self._dm.EnableRealMouse(2, 5, 50)  # 80-150ms
            self._dm.EnableRealKeypad(1)  # 180ms
            self._dm.SetShowErrorMsg(0)
            # self._dm.SetPath("./")
            # self.Reg()

    @func_time
    # @logger.catch()
    def Reg(self):
        try:
            dm_reg = 0
            for i in range(0, len(dm_keys)):
                dm_reg = self._dm.RegEx(dm_keys[i], 'test', dm_reg_ip)
                if dm_reg == -1:
                    logger.warn('dm_reg error, Cannot connect the host, try it again...')
                    dm_reg = self._dm.RegEx(dm_keys[i], 'HR', dm_reg_ip)
                    if dm_reg == -1:
                        logger.error('dm_reg error, Cannot connect the host! Please check Network Connections!')
                        break
                else:
                    if dm_reg != 1:
                        logger.error('dm_reg return is: %s, try another key in progress...', dm_reg)
                    else:
                        logger.debug('dm register OK!')
                        break
            else:
                logger.error("dm_reg error, return code: %s, and keys is over!", dm_reg)
        except Exception as e:
            logger.error(e)
            logger.error(sys.exc_info()[0:2])  # 打印错误类型，错误值
            logger.error(traceback.extract_tb(sys.exc_info()[2]))  # 出错位置

    def GetDmCount(self) -> int:
        '''
        返回当前进程已经创建的dm对象个数
        :return: int
        '''
        return self._dm.GetDmCount()

    def GetID(self) -> int:
        '''
        返回当前大漠对象的ID值，这个值对于每个对象是唯一存在的。可以用来判定两个大漠对象是否一致.
        :return:
        '''
        return self._dm.GetID()

    def GetLastError(self) -> int:
        '''
        获取插件命令的最后错误
        -1 : 表示你使用了绑定里的收费功能，但是没注册，无法使用.
        -2 : 使用模式0 2 时出现，因为目标窗口有保护. 常见于win7以上系统.或者有安全软件拦截插件.解决办法: 关闭所有安全软件，然后再重新尝试. 如果还不行就可以肯定是目标窗口有特殊保护.
        -3 : 使用模式0 2 时出现，可能目标窗口有保护，也可能是异常错误. 可以尝试换绑定模式或许可以解决.
-4 : 使用模式101 103时出现，这是异常错误.
-5 : 使用模式101 103时出现, 这个错误的解决办法就是关闭目标窗口，重新打开再绑定即可. 也可能是运行脚本的进程没有管理员权限.
-6 : 被安全软件拦截。典型的是金山.360等. 如果是360关闭即可。 如果是金山，必须卸载，关闭是没用的.
-7 -9 : 使用模式101 103时出现,异常错误. 还有可能是安全软件的问题，比如360等。尝试卸载360.
-8 -10 : 使用模式101 103时出现, 目标进程可能有保护,也可能是插件版本过老，试试新的或许可以解决. -8可以尝试使用DmGuard中的np2盾配合.
-11 : 使用模式101 103时出现, 目标进程有保护. 告诉我解决。
-12 : 使用模式101 103时出现, 目标进程有保护. 告诉我解决。
-13 : 使用模式101 103时出现, 目标进程有保护. 或者是因为上次的绑定没有解绑导致。 尝试在绑定前调用ForceUnBindWindow.
-37 : 使用模式101 103时出现, 目标进程有保护. 告诉我解决。
-14 : 可能系统缺少部分DLL,尝试安装d3d. 或者是鼠标或者键盘使用了dx.mouse.api或者dx.keypad.api，但实际系统没有插鼠标和键盘. 也有可能是图色中有dx.graphic.3d之类的,但相应的图色被占用,比如全屏D3D程序.
-16 : 可能使用了绑定模式 0 和 101，然后可能指定了一个子窗口.导致不支持.可以换模式2或者103来尝试. 另外也可以考虑使用父窗口或者顶级窗口.来避免这个错误。还有可能是目标窗口没有正常解绑然后再次绑定的时候.
-17 : 模式101 103时出现. 这个是异常错误. 告诉我解决.
-18 : 句柄无效.
-19 : 使用模式0 11 101时出现,这是异常错误,告诉我解决.
-20 : 使用模式101 103 时出现,说明目标进程里没有解绑，并且子绑定达到了最大. 尝试在返回这个错误时，调用ForceUnBindWindow来强制解除绑定.
-21 : 使用模式任何模式时出现,说明目标进程已经存在了绑定(没有正确解绑就退出了?被其它软件绑定?,或者多个线程同时进行了绑定?). 尝试在返回这个错误时，调用ForceUnBindWindow来强制解除绑定.或者检查自己的代码.
-22 : 使用模式0 2,绑定64位进程窗口时出现,因为安全软件拦截插件释放的EXE文件导致.
-23 : 使用模式0 2,绑定64位进程窗口时出现,因为安全软件拦截插件释放的DLL文件导致.
-24 : 使用模式0 2,绑定64位进程窗口时出现,因为安全软件拦截插件运行释放的EXE.
-25 : 使用模式0 2,绑定64位进程窗口时出现,因为安全软件拦截插件运行释放的EXE.
-26 : 使用模式0 2,绑定64位进程窗口时出现, 因为目标窗口有保护. 常见于win7以上系统.或者有安全软件拦截插件.解决办法: 关闭所有安全软件，然后再重新尝试. 如果还不行就可以肯定是目标窗口有特殊保护.
-27 : 绑定64位进程窗口时出现，因为使用了不支持的模式，目前暂时只支持模式0 2 11 13 101 103
-28 : 绑定32位进程窗口时出现，因为使用了不支持的模式，目前暂时只支持模式0 2 11 13 101 103
-38 : 是用了大于2的绑定模式,并且使用了dx.public.inject.c时，分配内存失败. 可以考虑开启memory系列盾来尝试.
-39 : 是用了大于2的绑定模式,并且使用了dx.public.inject.c时的异常错误. 可以联系我解决.
-40 : 是用了大于2的绑定模式,并且使用了dx.public.inject.c时, 写入内存失败. 可以考虑开启memory系列盾来尝试.
-41 : 是用了大于2的绑定模式,并且使用了dx.public.inject.c时的异常错误. 可以联系我解决.
-42 : 绑定时,创建映射内存失败. 这是个异常错误. 一般不会出现. 如果出现了，检查下代码是不是有同个对象同时绑定的情况.
-43 : 绑定时,映射内存失败. 这是个异常错误. 一般不会出现. 如果出现了，检查下代码是不是有同个对象同时绑定的情况.或者同个对象同时进行了绑定和解绑的操作.实在不行,那就多绑定几次.
-44 : 无效的参数,通常是传递了不支持的参数.
-45 : 绑定时,创建互斥信号失败. 这个是一场错误. 一般不会出现. 如果出现了检查进程是否有句柄泄漏的情况.

-100 : 调用读写内存函数后，发现无效的窗口句柄
-101 : 读写内存函数失败
-200 : AsmCall失败
        :return: int,返回值表示错误值。 0表示无错误.
        '''
        return self._dm.GetLastError()

    def Ocr(self, x1: int, y1: int, x2: int, y2: int, color_format: str, sim: float) -> str:
        """
        识别屏幕范围(x1,y1,x2,y2)内符合color_format的字符串,并且相似度为sim,sim取值范围(0.1-1.0),这个值越大越精确,越大速度越快,越小速度越慢,请斟酌使用!
        :param x1: 区域的左上X坐标
        :param y1: 区域的左上Y坐标
        :param x2: 区域的右下X坐标
        :param y2: 区域的右下Y坐标
        :param color_format: 颜色格式串. 可以包含换行分隔符,语法是","后加分割字符串. 具体可以查看下面的示例.注意，RGB和HSV,以及灰度格式都支持.
        :param sim: 相似度,取值范围0.1-1.0
        :return: 返回识别到的字符串
        """
        self._dm.UseDict(0)
        return self._dm.Ocr(x1, y1, x2, y2, color_format, sim)

    def OcrInFile(self, x1:int, y1:int, x2:int, y2:int, pic_name:str, color_format:str, sim:float) -> str:
        '''

        :param x1: 区域的左上X坐标
        :param y1: 区域的左上Y坐标
        :param x2: 区域的右下X坐标
        :param y2: 区域的右下Y坐标
        :param pic_name: 图片文件名
        :param color_format: 颜色格式串.注意，RGB和HSV,以及灰度格式都支持
        :param sim: 相似度,取值范围0.1-1.0
        :return: 返回识别到的字符串
        '''
        self._dm.UseDict(0)
        return self._dm.OcrInFile(x1, y1, x2, y2, pic_name, color_format, sim)
    def reset_cursor(self):
        pass

    def EnableMouseAccuracy(self, enable:int):
        return self._dm.EnableMouseAccuracy(enable)

    def SetMouseSpeed(self, speed:int) -> int:
        """
        设置系统鼠标的移动速度.
        :param speed: 鼠标移动速度, 最小1，最大11.  居中为6. 推荐设置为6
        :return: 0:失败;1:成功
        """
        return self._dm.SetMouseSpeed(speed)

    def MoveToEx(self, x, y):
        return self._dm.MoveToEx(x, y, 20, 3)
    # @func_time
    def mouse_move_to(self, x: int, y: int) -> int:
        return self._dm.MoveToEx(x, y, 1, 1)

    def KeyDown(self, v_code):
        return self._dm.KeyDown(v_code)

    def KeyUp(self, v_code):
        return self._dm.KeyUp(v_code)

    # @func_time
    def mouse_left_click(self, is_fast=False):
        if is_fast:
            self._dm.LeftDown()
            self._dm.LeftUp()
        else:
            self._dm.LeftDown()
            sleep(randint(25, 45) / 1000)
            self._dm.LeftUp()
            sleep(randint(15, 25) / 1000)

    # @func_time
    def mouse_left_double_click(self,is_fast=False):
        if is_fast:
            self._dm.LeftDown()
            self._dm.LeftUp()
            sleep(15/1000)
            self._dm.LeftDown()
            self._dm.LeftUp()
        else:
            self._dm.LeftDown()
            sleep(randint(15, 25) / 1000)
            self._dm.LeftUp()
            sleep(randint(15, 25) / 1000)
            self._dm.LeftDown()
            sleep(randint(15, 25) / 1000)
            self._dm.LeftUp()
            sleep(randint(15, 25) / 1000)
    # @func_time
    def input(self, key: str, is_fast=False) -> int:  # 三个数字输入 190ms
        """
        根据指定的字符串序列，依次按顺序按下其中的字符.
        :param key: 需要按下的字符串序列. 比如"1234","abcd","7389,1462"等.
        :param delay: 每按下一个按键，需要延时多久. 单位毫秒.这个值越大，按的速度越慢。
        :return: 0:失败;1:成功
        """
        if is_fast:
            return  self._dm.KeyPressStr(key, 0)
        else:
            return self._dm.KeyPressStr(key, 30)

    def press_Backspace(self, is_fast=False):
        if is_fast:
            self._dm.KeyDown(8)
            self._dm.KeyUp(8)
        else:
            self._dm.KeyDown(8)
            sleep(randint(25, 45) / 1000)
            self._dm.KeyUp(8)

    def press_Enter(self, is_fast=False):
        if is_fast:
            self._dm.KeyDown(13)
            self._dm.KeyUp(13)
        else:
            self._dm.KeyDown(13)
            sleep(randint(25, 45) / 1000)
            self._dm.KeyUp(13)


    @func_time
    def FindStrEx(self, x1: int, y1: int, x2: int, y2: int, string: str, color_formats: str, sim: float) -> list:
        """
        在屏幕范围(x1,y1,x2,y2)内,查找string(可以是任意个字符串的组合),并返回符合color_format的坐标位置,相似度sim同Ocr接口描述
        @param x1: 区域的左上X坐标
        @param y1: 区域的左上Y坐标
        @param x2: 区域的右下Y坐标
        @param y2: 区域的右下Y坐标
        @param string: 待查找字符串元组，如('长安', '洛阳', '大雁塔')
        @param color_formats: 字符串:颜色格式串, '颜色1-偏差1|颜色2-偏差2'
        @return: (True/False, 找到的字符串, x, y)
        """
        self._dm.UseDict(1)
        sss = self._dm.FindStrEx(x1, y1, x2, y2, string, color_formats, sim)
        # logger.debug("FindStrEx return: {}", sss)
        rr = []
        if len(sss) > 0:
            for ss in sss.split('|'):
                r = []
                s = ss.split(',')
                r.append(string[int(s[0])])
                r.append(int(s[1]))
                r.append(int(s[2]))
                rr.append(tuple(r))
        return rr

    def FindWindow(self, class_, title_):
        return self._dm.FindWindow(class_, title_)

    def FindWindowByProcess(self, process_name_, class_, title_):
        return self._dm.FindWindowByProcess(process_name_, class_, title_)

    def SetWindowState(self, hwnd_, flag_):
        return self._dm.SetWindowState(hwnd_, flag_)

    def FindColor(self, x1, y1, x2, y2, color, sim, dirs):
        return self._dm.FindColor(x1, y1, x2, y2, color, sim, dirs)

    def FindColorEx(self, x1:int, y1:int, x2:int, y2:int, color:str, sim:float, dir:int):
        """
        查找指定区域内的所有颜色,颜色格式"RRGGBB-DRDGDB",注意,和按键的颜色格式相反
        :param x1: 区域的左上X坐标
        :param y1: 区域的左上Y坐标
        :param x2: 区域的右下X坐标
        :param y2: 区域的右下Y坐标
        :param color: 颜色 格式为"RRGGBB-DRDGDB" 比如"aabbcc-000000|123456-202020".注意，这里只支持RGB颜色.
        :param sim: 相似度,取值范围0.1-1.0
        :param dir: 查找方向 0: 从左到右,从上到下
             1: 从左到右,从下到上
             2: 从右到左,从上到下
             3: 从右到左,从下到上
             5: 从上到下,从左到右
             6: 从上到下,从右到左
             7: 从下到上,从左到右
             8: 从下到上,从右到左
        :return: 返回所有颜色信息的坐标值,然后通过GetResultCount等接口来解析 (由于内存限制,返回的颜色数量最多为1800个左右)
        """
        return self._dm.FindColorEx(x1, y1, x2, y2, color, sim, dir)

    def Guard(self, enable_num, type_str):
        try:
            return self._dm.DmGuard(enable_num, type_str)
        except Exception as e:
            logger.error(e)

    def BindWindow(self, hwnd, display, mouse, keypad, mode):
        return self._dm.BindWindow(hwnd, display, mouse, keypad, mode)

    def BindWindowEx(self, hwnd, display, mouse, keypad, public, mode):
        return self._dm.BindWindowEx(hwnd, display, mouse, keypad, public, mode)

    def IsBind(self, hwnd):
        return self._dm.IsBind(hwnd)

    def FindPicEx(self, x1:int, y1: int, x2: int, y2: int, pic_name: str, delta_color: str, sim: float, dir: int) -> list:
        """
        查找指定区域内的图片,位图必须是24位色格式,支持透明色,当图像上下左右4个顶点的颜色一样时,则这个颜色将作为透明色处理. 可以查找多个图片,并且返回所有找到的图像的坐标.
        @param x1: 区域的左上X坐标
        @param y1: 区域的左上Y坐标
        @param x2: 区域的右下X坐标
        @param y2: 区域的右下Y坐标
        @param pic_name: 图片名,可以是多个图片,比如"test.bmp|test2.bmp|test3.bmp"
        @param delta_color: 颜色色偏 比如"203040" 表示RGB的色偏分别是20 30 40 (这里是16进制表示) . 如果这里的色偏是2位，表示使用灰度找图. 比如"20"
        @param sim: 相似度,取值范围0.1-1.0
        @param dir: 查找方向 0: 从左到右,从上到下 1: 从左到右,从下到上 2: 从右到左,从上到下 3: 从右到左, 从下到上
        @return: 所有找到的坐标格式如下:"id,x,y|id,x,y..|id,x,y" (图片左上角的坐标); 比如"0,100,20|2,30,40" 表示找到了两个,第一个,对应的图片是图像序号为0的图片,坐标是(100,20),第二个是序号为2的图片,坐标(30,40)
        """
        sss = self._dm.FindPicEx(x1, y1, x2, y2, pic_name, delta_color, sim, dir)
        rr = []
        index = 0
        if len(sss) > 0:
            for ss in sss.split('|'):
                r = []
                s = ss.split(',')
                r.append(index)
                r.append(int(s[1]))
                r.append(int(s[2]))
                rr.append(tuple(r))
                index += 1
        return rr

    def Capture(self, x1: int, y1: int, x2: int, y2: int, file: str) -> int:
        """
        抓取指定区域(x1, y1, x2, y2)的图像,保存为file(24位位图)
        @param x1: 区域的左上X坐标
        @param y1: 区域的左上Y坐标
        @param x2: 区域的右下X坐标
        @param y2: 区域的右下Y坐标
        @param file: 保存的文件名,保存的地方一般为SetPath中设置的目录, 当然这里也可以指定全路径名.
        @return: 0:失败;1:成功
        """
        return self._dm.Capture(x1, y1, x2, y2, file)

    def CreateFoobarRoundRect(self, hwnd: int, x: int, y: int, w: int, h: int, rw: int, rh: int) -> int:
        """
        创建一个圆角矩形窗口
        @param hwnd: 指定的窗口句柄,如果此值为0,那么就在桌面创建此窗口
        @param x: 左上角X坐标(相对于hwnd客户区坐标)
        @param y: 左上角Y坐标(相对于hwnd客户区坐标)
        @param w: 矩形区域的宽度
        @param h: 矩形区域的高度
        @param rw: 圆角的宽度
        @param rh: 圆角的高度
        @return: 创建成功的窗口句柄
        """
        return self._dm.CreateFoobarRoundRect(hwnd, x, y, w, h, rw, rh)

    def CreateFoobarRect(self, hwnd: int, x: int, y: int, w: int, h: int) -> int:
        """
        创建一个矩形窗口
        @param hwnd: 指定的窗口句柄,如果此值为0,那么就在桌面创建此窗口
        @param x: 左上角X坐标(相对于hwnd客户区坐标)
        @param y: 左上角Y坐标(相对于hwnd客户区坐标)
        @param w: 矩形区域的宽度
        @param h: 矩形区域的高度
        @return: 创建成功的窗口句柄
        """
        return self._dm.CreateFoobarRect(hwnd, x, y, w, h)

    def FoobarSetTrans(self, hwnd: int, is_trans: int, color: str, sim: float) -> int:
        """
        设置指定Foobar窗口的是否透明
        @param hwnd: 指定的Foobar窗口句柄,此句柄必须是通过CreateFoobarxxx创建而来
        @param is_trans: 是否透明. 0为不透明(此时,color和sim无效)，1为透明.
        @param color: 透明色(RGB)
        @param sim: 透明色的相似值 0.1-1.0
        @return: 0:失败;1:成功
        """
        return self._dm.FoobarSetTrans(hwnd, is_trans, color, sim)

    def FoobarClearText(self, hwnd: int) -> int:
        """
        清除指定的Foobar滚动文本区
        @param hwnd: 指定的Foobar窗口句柄,此句柄必须是通过CreateFoobarxxx创建而来
        @return: 0:失败;1:成功
        """
        return self._dm.FoobarClearText(hwnd)

    def FoobarClose(self, hwnd: int) -> int:
        """
        关闭一个Foobar,注意,必须调用此函数来关闭窗口,用SetWindowState也可以关闭,但会造成内存泄漏.
        @param hwnd: 指定的Foobar窗口句柄
        @return: 0:失败;1:成功
        """
        return self._dm.FoobarClose(hwnd)

    def FoobarSetFont(self, hwnd: int, font_name: str, size: int, flag: int) -> int:
        """
        设置指定Foobar窗口的字体
        @param hwnd: 指定的Foobar窗口句柄,此句柄必须是通过CreateFoobarxxx创建而来
        @param font_name: 系统字体名,注意,必须保证系统中有此字体
        @param size: 字体大小
        @param flag: 取值定义:0:正常字体,1:粗体,2:斜体,4:下划线;文字可以是以上的组合 比如粗斜体就是1+2,斜体带下划线就是:2+4等.
        @return: 0:失败;1:成功
        """
        return self._dm.FoobarSetFont(hwnd, font_name, size, flag)

    def FoobarDrawText(self, hwnd: int, x: int, y: int, w: int, h: int, text: str, color: str, align: int) -> int:
        """
        在指定的Foobar窗口绘制文字
        @param hwnd: 指定的Foobar窗口,注意,此句柄必须是通过CreateFoobarxxxx系列函数创建出来的
        @param x: 左上角X坐标(相对于hwnd客户区坐标)
        @param y: 左上角Y坐标(相对于hwnd客户区坐标)
        @param w: 矩形区域的宽度
        @param h: 矩形区域的高度
        @param text: 字符串
        @param color: 文字颜色值 ff0000
        @param align: 取值定义:1:左对齐,2:中间对齐,4:右对齐
        @return: 0:失败;1:成功
        """
        return self._dm.FoobarDrawText(hwnd, x, y, w, h, text, color, align)

    def FoobarDrawLine(self, hwnd: int, x1:int, y1: int, x2: int, y2: int,color: str, style: int, width: int) -> int:
        """
        在指定的Foobar窗口内部画线条.
        @param hwnd: 指定的Foobar窗口,注意,此句柄必须是通过CreateFoobarxxxx系列函数创建出来的
        @param x1: 左上角X坐标(相对于hwnd客户区坐标)
        @param y1: 左上角Y坐标(相对于hwnd客户区坐标)
        @param x2: 右下角X坐标(相对于hwnd客户区坐标)
        @param y2: 右下角Y坐标(相对于hwnd客户区坐标)
        @param color: 填充的颜色值
        @param style: 画笔类型. 0为实线. 1为虚线
        @param width: 线条宽度.
        @return: 0:失败;1:成功
        """
        return self._dm.FoobarDrawLine(hwnd, x1, y1, x2, y2, color, style, width)

    def FoobarPrintText(self, hwnd: int, text: str, color: str) -> int:
        """
        向指定的Foobar窗口区域内输出滚动文字
        @param hwnd: 指定的Foobar窗口句柄,此句柄必须是通过CreateFoobarxxx创建而来
        @param text: 文本内容
        @param color: 文本颜色 ff0000
        @return: 0:失败;1:成功
        """
        return self._dm.FoobarPrintText(hwnd, text, color)

    def FoobarTextLineGap(self, hwnd: int, line_gap: int) -> int:
        """
        设置滚动文本区的文字行间距,默认是3
        @param hwnd: 指定的Foobar窗口句柄,此句柄必须是通过CreateFoobarxxx创建而来
        @param line_gap: 文本行间距
        @return: 0:失败;1:成功
        """
        return self._dm.FoobarTextLineGap(hwnd, line_gap)

    def FoobarUpdate(self, hwnd: int) -> int:
        """
        刷新指定的Foobar窗口
        @param hwnd: 指定的Foobar窗口,注意,此句柄必须是通过CreateFoobarxxxx系列函数创建出来的
        @return: 0:失败;1:成功
        """
        return self._dm.FoobarUpdate(hwnd)

    def FoobarTextRect(self, hwnd: int, x: int, y: int, w: int, h: int) -> int:
        """
        设置指定Foobar窗口的滚动文本框范围,默认的文本框范围是窗口区域
        @param hwnd: 指定的Foobar窗口句柄,此句柄必须是通过CreateFoobarxxx创建而来
        @param x: x坐标
        @param y: y坐标
        @param w: 宽度
        @param h: 高度
        @return: 0:失败;1:成功
        """
        return self._dm.FoobarTextRect(hwnd, x, y, w, h)

    def FoobarFillRect(self, hwnd: int, x1: int, y1: int, x2: int, y2: int, color: str) -> int:
        """
        在指定的Foobar窗口内部填充矩形
        @param hwnd: 指定的Foobar窗口,注意,此句柄必须是通过CreateFoobarxxxx系列函数创建出来的
        @param x1: 左上角X坐标(相对于hwnd客户区坐标)
        @param y1: 左上角Y坐标(相对于hwnd客户区坐标)
        @param x2: 右下角X坐标(相对于hwnd客户区坐标)
        @param y2: 右下角Y坐标(相对于hwnd客户区坐标)
        @param color: 填充的颜色值
        @return: 0:失败;1:成功
        """
        return self._dm.FoobarFillRect(hwnd, x1, y1, x2, y2, color)

    def FoobarLock(self, hwnd: int) -> int:
        """
        锁定指定的Foobar窗口,不能通过鼠标来移动
        @param hwnd: 指定的Foobar窗口句柄,此句柄必须是通过CreateFoobarxxx创建而来
        @return: 0:失败;1:成功
        """
        return self._dm.FoobarLock(hwnd)


# 必须有这行，不然lazy不能导入
dm = Dm()
