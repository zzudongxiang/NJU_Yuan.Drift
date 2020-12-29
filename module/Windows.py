#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import tkinter as TK
import tkinter.font as tkFont
from module.Config import Config
from win32api import GetMonitorInfo, MonitorFromPoint

Configure = Config()


# 获取抓取屏幕截图的窗口
def GetGrabWindows(OnClosing):
    global Configure

    # 读取配置文件中的数据
    WindowSize = Configure.ConfigObj["WindowSize"]

    # 初始化截图的窗口对象
    GrabWindows = TK.Tk()
    GrabWindows.attributes('-alpha', 0.5)
    GrabWindows.title('屏幕录制')
    GrabWindows.iconbitmap('./lib/NJU.ico')
    GrabWindows.geometry('%dx%d' % tuple(WindowSize))
    GrabWindows.wm_attributes('-topmost', 1)
    GrabWindows.protocol('WM_DELETE_WINDOW', OnClosing)

    # 添加控件
    TK.Label(GrabWindows, text='图像截取区域', foreground='red', font=('宋体', 50)).pack(expand=TK.YES)

    return GrabWindows


# 获取操作界面的TK窗口
def GetOperateWindows(OnClosing, BackgroundCB, ControlCB, ConfigCB, MoveCB):
    # 初始化操作面板对象
    OperateWindows = TK.Tk()
    OperateWindows.title('温漂补偿操作界面')
    OperateWindows.iconbitmap('./lib/NJU.ico')
    OperateWindows.wm_attributes('-topmost', 1)
    OperateWindows.protocol('WM_DELETE_WINDOW', OnClosing)

    # 添加操作面板内容
    LBSpeed = TK.Label(OperateWindows, text='温漂控制系统', font=('宋体', 14, tkFont.BOLD), width=12, height=1)
    LBSpeed.grid(row=0, columnspan=3)
    TK.Button(OperateWindows, text='抓取背景图', font=('宋体', 16), width=12, height=2, command=BackgroundCB).grid(row=1, columnspan=3)
    BtnControl = TK.Button(OperateWindows, text='温漂控制OFF', font=('宋体', 16), width=12, height=2, command=ControlCB)
    BtnControl.grid(row=2, columnspan=3)

    # 鼠标操作方向键
    Menu = [['↖', '↑', '↗'], ['←', '⊙', '→'], ['↙', '↓', '↘']]
    RowIndex = 3
    for Row in Menu:
        ColIndex = 0
        for Col in Row:
            BTN = TK.Button(OperateWindows, text=Col, font=('宋体', 20), name=Col)
            BTN.bind("<Button-1>", MoveCB)
            #BTN.bind("<ButtonRelease-1>", UPCB)
            BTN.grid(row=RowIndex, column=ColIndex)
            ColIndex += 1
        RowIndex += 1
    TK.Button(OperateWindows, text='装载配置文件', font=('宋体', 16), width=12, height=1, command=ConfigCB).grid(columnspan=3)
    OperateWindows.overrideredirect(1)

    # 将工具面板调整到桌面的右下角位置
    OperateWindows.update()
    WorkArea = GetMonitorInfo(MonitorFromPoint((0, 0))).get("Work")
    Width = WorkArea[2]
    Height = WorkArea[3]
    X = Width - OperateWindows.winfo_width()
    Y = Height - OperateWindows.winfo_height()
    OperateWindows.geometry('+%s+%s' % (X, Y))

    return OperateWindows, LBSpeed, BtnControl
