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
            logger.error(sys.exc_info()[0:2])  # ��ӡ�������ͣ�����ֵ
            logger.error(traceback.extract_tb(sys.exc_info()[2]))  # ����λ��

    def GetDmCount(self) -> int:
        '''
        ���ص�ǰ�����Ѿ�������dm�������
        :return: int
        '''
        return self._dm.GetDmCount()

    def GetID(self) -> int:
        '''
        ���ص�ǰ��Į�����IDֵ�����ֵ����ÿ��������Ψһ���ڵġ����������ж�������Į�����Ƿ�һ��.
        :return:
        '''
        return self._dm.GetID()

    def GetLastError(self) -> int:
        '''
        ��ȡ��������������
        -1 : ��ʾ��ʹ���˰�����շѹ��ܣ�����ûע�ᣬ�޷�ʹ��.
        -2 : ʹ��ģʽ0 2 ʱ���֣���ΪĿ�괰���б���. ������win7����ϵͳ.�����а�ȫ������ز��.����취: �ر����а�ȫ�����Ȼ�������³���. ��������оͿ��Կ϶���Ŀ�괰�������Ᵽ��.
        -3 : ʹ��ģʽ0 2 ʱ���֣�����Ŀ�괰���б�����Ҳ�������쳣����. ���Գ��Ի���ģʽ������Խ��.
-4 : ʹ��ģʽ101 103ʱ���֣������쳣����.
-5 : ʹ��ģʽ101 103ʱ����, �������Ľ���취���ǹر�Ŀ�괰�ڣ����´��ٰ󶨼���. Ҳ���������нű��Ľ���û�й���ԱȨ��.
-6 : ����ȫ������ء����͵��ǽ�ɽ.360��. �����360�رռ��ɡ� ����ǽ�ɽ������ж�أ��ر���û�õ�.
-7 -9 : ʹ��ģʽ101 103ʱ����,�쳣����. ���п����ǰ�ȫ��������⣬����360�ȡ�����ж��360.
-8 -10 : ʹ��ģʽ101 103ʱ����, Ŀ����̿����б���,Ҳ�����ǲ���汾���ϣ������µĻ�����Խ��. -8���Գ���ʹ��DmGuard�е�np2�����.
-11 : ʹ��ģʽ101 103ʱ����, Ŀ������б���. �����ҽ����
-12 : ʹ��ģʽ101 103ʱ����, Ŀ������б���. �����ҽ����
-13 : ʹ��ģʽ101 103ʱ����, Ŀ������б���. ��������Ϊ�ϴεİ�û�н���¡� �����ڰ�ǰ����ForceUnBindWindow.
-37 : ʹ��ģʽ101 103ʱ����, Ŀ������б���. �����ҽ����
-14 : ����ϵͳȱ�ٲ���DLL,���԰�װd3d. �����������߼���ʹ����dx.mouse.api����dx.keypad.api����ʵ��ϵͳû�в����ͼ���. Ҳ�п�����ͼɫ����dx.graphic.3d֮���,����Ӧ��ͼɫ��ռ��,����ȫ��D3D����.
-16 : ����ʹ���˰�ģʽ 0 �� 101��Ȼ�����ָ����һ���Ӵ���.���²�֧��.���Ի�ģʽ2����103������. ����Ҳ���Կ���ʹ�ø����ڻ��߶�������.������������󡣻��п�����Ŀ�괰��û���������Ȼ���ٴΰ󶨵�ʱ��.
-17 : ģʽ101 103ʱ����. ������쳣����. �����ҽ��.
-18 : �����Ч.
-19 : ʹ��ģʽ0 11 101ʱ����,�����쳣����,�����ҽ��.
-20 : ʹ��ģʽ101 103 ʱ����,˵��Ŀ�������û�н�󣬲����Ӱ󶨴ﵽ�����. �����ڷ����������ʱ������ForceUnBindWindow��ǿ�ƽ����.
-21 : ʹ��ģʽ�κ�ģʽʱ����,˵��Ŀ������Ѿ������˰�(û����ȷ�����˳���?�����������?,���߶���߳�ͬʱ�����˰�?). �����ڷ����������ʱ������ForceUnBindWindow��ǿ�ƽ����.���߼���Լ��Ĵ���.
-22 : ʹ��ģʽ0 2,��64λ���̴���ʱ����,��Ϊ��ȫ������ز���ͷŵ�EXE�ļ�����.
-23 : ʹ��ģʽ0 2,��64λ���̴���ʱ����,��Ϊ��ȫ������ز���ͷŵ�DLL�ļ�����.
-24 : ʹ��ģʽ0 2,��64λ���̴���ʱ����,��Ϊ��ȫ������ز�������ͷŵ�EXE.
-25 : ʹ��ģʽ0 2,��64λ���̴���ʱ����,��Ϊ��ȫ������ز�������ͷŵ�EXE.
-26 : ʹ��ģʽ0 2,��64λ���̴���ʱ����, ��ΪĿ�괰���б���. ������win7����ϵͳ.�����а�ȫ������ز��.����취: �ر����а�ȫ�����Ȼ�������³���. ��������оͿ��Կ϶���Ŀ�괰�������Ᵽ��.
-27 : ��64λ���̴���ʱ���֣���Ϊʹ���˲�֧�ֵ�ģʽ��Ŀǰ��ʱֻ֧��ģʽ0 2 11 13 101 103
-28 : ��32λ���̴���ʱ���֣���Ϊʹ���˲�֧�ֵ�ģʽ��Ŀǰ��ʱֻ֧��ģʽ0 2 11 13 101 103
-38 : �����˴���2�İ�ģʽ,����ʹ����dx.public.inject.cʱ�������ڴ�ʧ��. ���Կ��ǿ���memoryϵ�ж�������.
-39 : �����˴���2�İ�ģʽ,����ʹ����dx.public.inject.cʱ���쳣����. ������ϵ�ҽ��.
-40 : �����˴���2�İ�ģʽ,����ʹ����dx.public.inject.cʱ, д���ڴ�ʧ��. ���Կ��ǿ���memoryϵ�ж�������.
-41 : �����˴���2�İ�ģʽ,����ʹ����dx.public.inject.cʱ���쳣����. ������ϵ�ҽ��.
-42 : ��ʱ,����ӳ���ڴ�ʧ��. ���Ǹ��쳣����. һ�㲻�����. ��������ˣ�����´����ǲ�����ͬ������ͬʱ�󶨵����.
-43 : ��ʱ,ӳ���ڴ�ʧ��. ���Ǹ��쳣����. һ�㲻�����. ��������ˣ�����´����ǲ�����ͬ������ͬʱ�󶨵����.����ͬ������ͬʱ�����˰󶨺ͽ��Ĳ���.ʵ�ڲ���,�ǾͶ�󶨼���.
-44 : ��Ч�Ĳ���,ͨ���Ǵ����˲�֧�ֵĲ���.
-45 : ��ʱ,���������ź�ʧ��. �����һ������. һ�㲻�����. ��������˼������Ƿ��о��й©�����.

-100 : ���ö�д�ڴ溯���󣬷�����Ч�Ĵ��ھ��
-101 : ��д�ڴ溯��ʧ��
-200 : AsmCallʧ��
        :return: int,����ֵ��ʾ����ֵ�� 0��ʾ�޴���.
        '''
        return self._dm.GetLastError()

    def Ocr(self, x1: int, y1: int, x2: int, y2: int, color_format: str, sim: float) -> str:
        """
        ʶ����Ļ��Χ(x1,y1,x2,y2)�ڷ���color_format���ַ���,�������ƶ�Ϊsim,simȡֵ��Χ(0.1-1.0),���ֵԽ��Խ��ȷ,Խ���ٶ�Խ��,ԽС�ٶ�Խ��,������ʹ��!
        :param x1: ���������X����
        :param y1: ���������Y����
        :param x2: ���������X����
        :param y2: ���������Y����
        :param color_format: ��ɫ��ʽ��. ���԰������зָ���,�﷨��","��ӷָ��ַ���. ������Բ鿴�����ʾ��.ע�⣬RGB��HSV,�Լ��Ҷȸ�ʽ��֧��.
        :param sim: ���ƶ�,ȡֵ��Χ0.1-1.0
        :return: ����ʶ�𵽵��ַ���
        """
        self._dm.UseDict(0)
        return self._dm.Ocr(x1, y1, x2, y2, color_format, sim)

    def OcrInFile(self, x1:int, y1:int, x2:int, y2:int, pic_name:str, color_format:str, sim:float) -> str:
        '''

        :param x1: ���������X����
        :param y1: ���������Y����
        :param x2: ���������X����
        :param y2: ���������Y����
        :param pic_name: ͼƬ�ļ���
        :param color_format: ��ɫ��ʽ��.ע�⣬RGB��HSV,�Լ��Ҷȸ�ʽ��֧��
        :param sim: ���ƶ�,ȡֵ��Χ0.1-1.0
        :return: ����ʶ�𵽵��ַ���
        '''
        self._dm.UseDict(0)
        return self._dm.OcrInFile(x1, y1, x2, y2, pic_name, color_format, sim)
    def reset_cursor(self):
        pass

    def EnableMouseAccuracy(self, enable:int):
        return self._dm.EnableMouseAccuracy(enable)

    def SetMouseSpeed(self, speed:int) -> int:
        """
        ����ϵͳ�����ƶ��ٶ�.
        :param speed: ����ƶ��ٶ�, ��С1�����11.  ����Ϊ6. �Ƽ�����Ϊ6
        :return: 0:ʧ��;1:�ɹ�
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
    def input(self, key: str, is_fast=False) -> int:  # ������������ 190ms
        """
        ����ָ�����ַ������У����ΰ�˳�������е��ַ�.
        :param key: ��Ҫ���µ��ַ�������. ����"1234","abcd","7389,1462"��.
        :param delay: ÿ����һ����������Ҫ��ʱ���. ��λ����.���ֵԽ�󣬰����ٶ�Խ����
        :return: 0:ʧ��;1:�ɹ�
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
        ����Ļ��Χ(x1,y1,x2,y2)��,����string(������������ַ��������),�����ط���color_format������λ��,���ƶ�simͬOcr�ӿ�����
        @param x1: ���������X����
        @param y1: ���������Y����
        @param x2: ���������Y����
        @param y2: ���������Y����
        @param string: �������ַ���Ԫ�飬��('����', '����', '������')
        @param color_formats: �ַ���:��ɫ��ʽ��, '��ɫ1-ƫ��1|��ɫ2-ƫ��2'
        @return: (True/False, �ҵ����ַ���, x, y)
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
        ����ָ�������ڵ�������ɫ,��ɫ��ʽ"RRGGBB-DRDGDB",ע��,�Ͱ�������ɫ��ʽ�෴
        :param x1: ���������X����
        :param y1: ���������Y����
        :param x2: ���������X����
        :param y2: ���������Y����
        :param color: ��ɫ ��ʽΪ"RRGGBB-DRDGDB" ����"aabbcc-000000|123456-202020".ע�⣬����ֻ֧��RGB��ɫ.
        :param sim: ���ƶ�,ȡֵ��Χ0.1-1.0
        :param dir: ���ҷ��� 0: ������,���ϵ���
             1: ������,���µ���
             2: ���ҵ���,���ϵ���
             3: ���ҵ���,���µ���
             5: ���ϵ���,������
             6: ���ϵ���,���ҵ���
             7: ���µ���,������
             8: ���µ���,���ҵ���
        :return: ����������ɫ��Ϣ������ֵ,Ȼ��ͨ��GetResultCount�Ƚӿ������� (�����ڴ�����,���ص���ɫ�������Ϊ1800������)
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
        ����ָ�������ڵ�ͼƬ,λͼ������24λɫ��ʽ,֧��͸��ɫ,��ͼ����������4���������ɫһ��ʱ,�������ɫ����Ϊ͸��ɫ����. ���Բ��Ҷ��ͼƬ,���ҷ��������ҵ���ͼ�������.
        @param x1: ���������X����
        @param y1: ���������Y����
        @param x2: ���������X����
        @param y2: ���������Y����
        @param pic_name: ͼƬ��,�����Ƕ��ͼƬ,����"test.bmp|test2.bmp|test3.bmp"
        @param delta_color: ��ɫɫƫ ����"203040" ��ʾRGB��ɫƫ�ֱ���20 30 40 (������16���Ʊ�ʾ) . ��������ɫƫ��2λ����ʾʹ�ûҶ���ͼ. ����"20"
        @param sim: ���ƶ�,ȡֵ��Χ0.1-1.0
        @param dir: ���ҷ��� 0: ������,���ϵ��� 1: ������,���µ��� 2: ���ҵ���,���ϵ��� 3: ���ҵ���, ���µ���
        @return: �����ҵ��������ʽ����:"id,x,y|id,x,y..|id,x,y" (ͼƬ���Ͻǵ�����); ����"0,100,20|2,30,40" ��ʾ�ҵ�������,��һ��,��Ӧ��ͼƬ��ͼ�����Ϊ0��ͼƬ,������(100,20),�ڶ��������Ϊ2��ͼƬ,����(30,40)
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
        ץȡָ������(x1, y1, x2, y2)��ͼ��,����Ϊfile(24λλͼ)
        @param x1: ���������X����
        @param y1: ���������Y����
        @param x2: ���������X����
        @param y2: ���������Y����
        @param file: ������ļ���,����ĵط�һ��ΪSetPath�����õ�Ŀ¼, ��Ȼ����Ҳ����ָ��ȫ·����.
        @return: 0:ʧ��;1:�ɹ�
        """
        return self._dm.Capture(x1, y1, x2, y2, file)

    def CreateFoobarRoundRect(self, hwnd: int, x: int, y: int, w: int, h: int, rw: int, rh: int) -> int:
        """
        ����һ��Բ�Ǿ��δ���
        @param hwnd: ָ���Ĵ��ھ��,�����ֵΪ0,��ô�������洴���˴���
        @param x: ���Ͻ�X����(�����hwnd�ͻ�������)
        @param y: ���Ͻ�Y����(�����hwnd�ͻ�������)
        @param w: ��������Ŀ��
        @param h: ��������ĸ߶�
        @param rw: Բ�ǵĿ��
        @param rh: Բ�ǵĸ߶�
        @return: �����ɹ��Ĵ��ھ��
        """
        return self._dm.CreateFoobarRoundRect(hwnd, x, y, w, h, rw, rh)

    def CreateFoobarRect(self, hwnd: int, x: int, y: int, w: int, h: int) -> int:
        """
        ����һ�����δ���
        @param hwnd: ָ���Ĵ��ھ��,�����ֵΪ0,��ô�������洴���˴���
        @param x: ���Ͻ�X����(�����hwnd�ͻ�������)
        @param y: ���Ͻ�Y����(�����hwnd�ͻ�������)
        @param w: ��������Ŀ��
        @param h: ��������ĸ߶�
        @return: �����ɹ��Ĵ��ھ��
        """
        return self._dm.CreateFoobarRect(hwnd, x, y, w, h)

    def FoobarSetTrans(self, hwnd: int, is_trans: int, color: str, sim: float) -> int:
        """
        ����ָ��Foobar���ڵ��Ƿ�͸��
        @param hwnd: ָ����Foobar���ھ��,�˾��������ͨ��CreateFoobarxxx��������
        @param is_trans: �Ƿ�͸��. 0Ϊ��͸��(��ʱ,color��sim��Ч)��1Ϊ͸��.
        @param color: ͸��ɫ(RGB)
        @param sim: ͸��ɫ������ֵ 0.1-1.0
        @return: 0:ʧ��;1:�ɹ�
        """
        return self._dm.FoobarSetTrans(hwnd, is_trans, color, sim)

    def FoobarClearText(self, hwnd: int) -> int:
        """
        ���ָ����Foobar�����ı���
        @param hwnd: ָ����Foobar���ھ��,�˾��������ͨ��CreateFoobarxxx��������
        @return: 0:ʧ��;1:�ɹ�
        """
        return self._dm.FoobarClearText(hwnd)

    def FoobarClose(self, hwnd: int) -> int:
        """
        �ر�һ��Foobar,ע��,������ô˺������رմ���,��SetWindowStateҲ���Թر�,��������ڴ�й©.
        @param hwnd: ָ����Foobar���ھ��
        @return: 0:ʧ��;1:�ɹ�
        """
        return self._dm.FoobarClose(hwnd)

    def FoobarSetFont(self, hwnd: int, font_name: str, size: int, flag: int) -> int:
        """
        ����ָ��Foobar���ڵ�����
        @param hwnd: ָ����Foobar���ھ��,�˾��������ͨ��CreateFoobarxxx��������
        @param font_name: ϵͳ������,ע��,���뱣֤ϵͳ���д�����
        @param size: �����С
        @param flag: ȡֵ����:0:��������,1:����,2:б��,4:�»���;���ֿ��������ϵ���� �����б�����1+2,б����»��߾���:2+4��.
        @return: 0:ʧ��;1:�ɹ�
        """
        return self._dm.FoobarSetFont(hwnd, font_name, size, flag)

    def FoobarDrawText(self, hwnd: int, x: int, y: int, w: int, h: int, text: str, color: str, align: int) -> int:
        """
        ��ָ����Foobar���ڻ�������
        @param hwnd: ָ����Foobar����,ע��,�˾��������ͨ��CreateFoobarxxxxϵ�к�������������
        @param x: ���Ͻ�X����(�����hwnd�ͻ�������)
        @param y: ���Ͻ�Y����(�����hwnd�ͻ�������)
        @param w: ��������Ŀ��
        @param h: ��������ĸ߶�
        @param text: �ַ���
        @param color: ������ɫֵ ff0000
        @param align: ȡֵ����:1:�����,2:�м����,4:�Ҷ���
        @return: 0:ʧ��;1:�ɹ�
        """
        return self._dm.FoobarDrawText(hwnd, x, y, w, h, text, color, align)

    def FoobarDrawLine(self, hwnd: int, x1:int, y1: int, x2: int, y2: int,color: str, style: int, width: int) -> int:
        """
        ��ָ����Foobar�����ڲ�������.
        @param hwnd: ָ����Foobar����,ע��,�˾��������ͨ��CreateFoobarxxxxϵ�к�������������
        @param x1: ���Ͻ�X����(�����hwnd�ͻ�������)
        @param y1: ���Ͻ�Y����(�����hwnd�ͻ�������)
        @param x2: ���½�X����(�����hwnd�ͻ�������)
        @param y2: ���½�Y����(�����hwnd�ͻ�������)
        @param color: ������ɫֵ
        @param style: ��������. 0Ϊʵ��. 1Ϊ����
        @param width: �������.
        @return: 0:ʧ��;1:�ɹ�
        """
        return self._dm.FoobarDrawLine(hwnd, x1, y1, x2, y2, color, style, width)

    def FoobarPrintText(self, hwnd: int, text: str, color: str) -> int:
        """
        ��ָ����Foobar���������������������
        @param hwnd: ָ����Foobar���ھ��,�˾��������ͨ��CreateFoobarxxx��������
        @param text: �ı�����
        @param color: �ı���ɫ ff0000
        @return: 0:ʧ��;1:�ɹ�
        """
        return self._dm.FoobarPrintText(hwnd, text, color)

    def FoobarTextLineGap(self, hwnd: int, line_gap: int) -> int:
        """
        ���ù����ı����������м��,Ĭ����3
        @param hwnd: ָ����Foobar���ھ��,�˾��������ͨ��CreateFoobarxxx��������
        @param line_gap: �ı��м��
        @return: 0:ʧ��;1:�ɹ�
        """
        return self._dm.FoobarTextLineGap(hwnd, line_gap)

    def FoobarUpdate(self, hwnd: int) -> int:
        """
        ˢ��ָ����Foobar����
        @param hwnd: ָ����Foobar����,ע��,�˾��������ͨ��CreateFoobarxxxxϵ�к�������������
        @return: 0:ʧ��;1:�ɹ�
        """
        return self._dm.FoobarUpdate(hwnd)

    def FoobarTextRect(self, hwnd: int, x: int, y: int, w: int, h: int) -> int:
        """
        ����ָ��Foobar���ڵĹ����ı���Χ,Ĭ�ϵ��ı���Χ�Ǵ�������
        @param hwnd: ָ����Foobar���ھ��,�˾��������ͨ��CreateFoobarxxx��������
        @param x: x����
        @param y: y����
        @param w: ���
        @param h: �߶�
        @return: 0:ʧ��;1:�ɹ�
        """
        return self._dm.FoobarTextRect(hwnd, x, y, w, h)

    def FoobarFillRect(self, hwnd: int, x1: int, y1: int, x2: int, y2: int, color: str) -> int:
        """
        ��ָ����Foobar�����ڲ�������
        @param hwnd: ָ����Foobar����,ע��,�˾��������ͨ��CreateFoobarxxxxϵ�к�������������
        @param x1: ���Ͻ�X����(�����hwnd�ͻ�������)
        @param y1: ���Ͻ�Y����(�����hwnd�ͻ�������)
        @param x2: ���½�X����(�����hwnd�ͻ�������)
        @param y2: ���½�Y����(�����hwnd�ͻ�������)
        @param color: ������ɫֵ
        @return: 0:ʧ��;1:�ɹ�
        """
        return self._dm.FoobarFillRect(hwnd, x1, y1, x2, y2, color)

    def FoobarLock(self, hwnd: int) -> int:
        """
        ����ָ����Foobar����,����ͨ��������ƶ�
        @param hwnd: ָ����Foobar���ھ��,�˾��������ͨ��CreateFoobarxxx��������
        @return: 0:ʧ��;1:�ɹ�
        """
        return self._dm.FoobarLock(hwnd)


# ���������У���Ȼlazy���ܵ���
dm = Dm()
