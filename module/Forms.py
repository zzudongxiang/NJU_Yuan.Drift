#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import os
import cv2
import tkinter as TK
import tkinter.font as tkFont
from win32api import GetMonitorInfo, MonitorFromPoint


# 生成用户界面的对象
class Forms:
    # 读取配置文件, 初始化对象
    def __init__(self, ConfigObj, ControlCallBack, MoveCallBack):
        # 根据传入的配置对象获取相关的属性
        self.WindowSize = ConfigObj.Data["Windows"]["Size"]

        # 检查窗口的图标文件是否存在
        self.Logo = './lib/NJU.ico'
        self.UseLogo = os.path.exists(self.Logo)

        # 构造全局回调函数的相关变量
        self.ControlCallBack = ControlCallBack
        self.MoveCallBack = MoveCallBack

        # 构造相关的窗口对象
        self._Private_Grab()
        self._Private_Menu()

    # 更新窗口内容
    def Update(self):
        try:
            self.GrabForm.update()
            self.MenuForm.update()
            return True
        except:
            return False

    # 当窗口被关闭时, 自动关联全部窗口
    def _OnClosing(self):
        try:
            self.GrabForm.destroy()
        except:
            pass
        try:
            self.MenuForm.destroy()
        except:
            pass
        cv2.destroyAllWindows()

    # 生成抓取背景的窗体对象
    def _Private_Grab(self):
        self.GrabForm = TK.Tk()
        self.GrabForm.attributes('-alpha', 0.5)
        self.GrabForm.title('屏幕录制')
        if self.UseLogo:
            self.GrabForm.iconbitmap(self.Logo)
        self.GrabForm.geometry('%dx%d' % tuple(self.WindowSize))
        self.GrabForm.wm_attributes('-topmost', 1)
        self.GrabForm.protocol('WM_DELETE_WINDOW', self._OnClosing)
        TK.Label(self.GrabForm, text='图像截取区域', foreground='red', font=('宋体', 50)).pack(expand=TK.YES)

    # 生成菜单栏的窗口对象
    def _Private_Menu(self):
        # 初始化操作面板对象
        self.MenuForm = TK.Toplevel()
        self.MenuForm.title('温漂补偿操作界面')
        if self.UseLogo:
            self.MenuForm.iconbitmap(self.Logo)
        self.MenuForm.wm_attributes('-topmost', 1)
        self.MenuForm.protocol('WM_DELETE_WINDOW', self._OnClosing)
        self.MenuForm.overrideredirect(1)

        # 添加操作面板内容
        self.MenuTitle = TK.Label(self.MenuForm, text='NJU-温漂控制系统', font=('宋体', 14, tkFont.BOLD), width=17, height=1)
        self.MenuTitle.grid(row=0, column=0, columnspan=4)
        self.MenuSwitch = TK.Button(self.MenuForm, text='控\n制\n状\n态\n\nOFF', font=('宋体', 16), width=3, height=6,borderwidth=2, relief='groove', command=self.ControlCallBack)
        self.MenuSwitch.grid(row=1, column=3, rowspan=3)
        self.MenuStatus = TK.Label(self.MenuForm, text='设备在线 | 速度:10000', font=('宋体', 12), width=23, height=1)
        self.MenuStatus.grid(row=4, columnspan=4)

        # 鼠标操作方向键
        Menu = [['↖', '↑', '↗'], ['←', '⊙', '→'], ['↙', '↓', '↘']]
        RowIndex = 1
        for Row in Menu:
            ColIndex = 0
            for Col in Row:
                BTN = TK.Label(self.MenuForm, text=Col, font=('宋体', 20), name=Col, borderwidth=2, relief='groove')
                BTN.bind("<Button-1>", self.MoveCallBack)
                BTN.grid(row=RowIndex, column=ColIndex)
                ColIndex += 1
            RowIndex += 1

        # 将工具面板调整到桌面的右下角位置
        WorkArea = GetMonitorInfo(MonitorFromPoint((0, 0))).get("Work")
        Width = WorkArea[2]
        Height = WorkArea[3]
        X = Width - self.MenuForm.winfo_width()
        Y = Height - self.MenuForm.winfo_height()
        self.MenuForm.geometry('+%s+%s' % (X, Y))
        self.MenuForm.update()


if __name__ == "__main__":
    # 导入配置文件
    import time
    from Config import Config
    ConfigObj = Config()

    # 初始化界面
    FormsObj = Forms(ConfigObj, None, None)
    while FormsObj.Update():
        time.sleep(0.1)
