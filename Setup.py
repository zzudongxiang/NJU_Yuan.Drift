#!/usr/bin/python3
# -*- coding: UTF-8 -*-
from tkinter import messagebox
from PIL import ImageGrab
import tkinter as TK
import numpy as np
import time
import cv2
import os

# User Import
from module.Windows import *
from module.Config import Config
from module.Stepper import Stepper
from module.Correct import Correct

# 设置环境变量, 创建温漂控制的核心部分对象
CorrectImage = Correct()
StepMotor = Stepper()
Configure = Config()
_SetBackground = False
_ControlStatus = False
_WindowsClosed = False
_WindowSize = []

# 手动移动电机的相关参数
SpeedLevel = Configure.ConfigObj["SpeedLevel"]
StepInvert = Configure.ConfigObj["StepInvert"]
_LevelIndex = 2
_OldSpeed = -1

# 偏移量的平均值
MaxLen = 36000000
OffsetList = np.zeros((MaxLen, 3))
OffsetIndex = 0


# 设置背景图片的功能
def SetBackgroundCallBack():
    global _SetBackground
    _SetBackground = True


# 使用温漂控制系统进行控制
def ControlCallBack():
    global _ControlStatus, BtnControl, OffsetList, OffsetIndex
    _ControlStatus = ~_ControlStatus
    if ~_ControlStatus:
        Text = '温漂控制OFF'
        Color = 'black'
        #OffsetList = np.delete(OffsetList, range(OffsetIndex, MaxLen), axis=0)
        DirPath = './logs/'
        if not os.path.exists(DirPath):
            os.makedirs(DirPath)
        FilePath = DirPath + '%d.dat' % time.time()
        np.savetxt(FilePath, OffsetList[:OffsetIndex, :], delimiter=',')
        #messagebox.showinfo("记录成功", "当前记录储存在: %s" % FilePath)
    else:
        OffsetList = np.zeros((36000000, 3))
        OffsetIndex = 0
        Text = '温漂控制ON'
        Color = 'red'
    BtnControl.configure(text=Text, foreground=Color)


# 装载配置文件
def SetConfigCallBack():
    global Configure, StepMotor, SpeedLevel, StepInvert, AveLen
    Configure = Config()
    StepMotor = Stepper()
    SpeedLevel = Configure.ConfigObj["SpeedLevel"]
    StepInvert = Configure.ConfigObj["StepInvert"]
    AveLen = Configure.ConfigObj["AverageLen"]
    messagebox.showinfo("操作成功", "成功加载配置文件!")


# 点击鼠标移动相对应的距离
def MoveCallBack(event):
    global _ControlStatus, _LevelIndex, SpeedLevel, StepInvert, StepMotor

    KeyDown = event.widget._name
    Step = SpeedLevel[_LevelIndex]
    Move = [0, 0]

    # 自动控制模式禁用手动控制
    if _ControlStatus:
        messagebox.showinfo("警告", "当前位移台由程序控制!")
        return

    # 切换速度档位
    if KeyDown == '⊙':
        tmp_LevelIndex = _LevelIndex + 1
        if tmp_LevelIndex >= len(SpeedLevel):
            _LevelIndex = 0
        else:
            _LevelIndex = tmp_LevelIndex
    else:
        # X轴正方向
        if KeyDown == '→' or KeyDown == '↗' or KeyDown == '↘':
            if StepInvert[0] != 0:
                Move[0] = -Step
            else:
                Move[0] = Step

        # X轴负方向
        elif KeyDown == '←' or KeyDown == '↖' or KeyDown == '↙':
            if StepInvert[0] == 0:
                Move[0] = -Step
            else:
                Move[0] = Step

        # Y轴正方向
        if KeyDown == '↑' or KeyDown == '↖' or KeyDown == '↗':
            if StepInvert[1] != 0:
                Move[1] = -Step
            else:
                Move[1] = Step

        # Y轴负方向
        elif KeyDown == '↓' or KeyDown == '↙' or KeyDown == '↘':
            if StepInvert[1] == 0:
                Move[1] = -Step
            else:
                Move[1] = Step

        # 移动电机到指定位置
        for Axis in range(2):
            if Move[Axis] != 0:
                StepMotor.Move(Axis, Move[Axis])


# 关闭窗口之前关闭关联的窗口
def OnClosing():
    global GrabWindows, OperateWindows, _WindowsClosed
    _WindowsClosed = True
    GrabWindows.destroy()
    OperateWindows.destroy()


# 获取TK的窗口, 并开启手动操作线程
GrabWindows = GetGrabWindows(OnClosing)
OperateWindows, LBSpeed, BtnControl = GetOperateWindows(OnClosing, SetBackgroundCallBack, ControlCallBack, SetConfigCallBack, MoveCallBack)

# 连续捕获每一帧图像并进行处理
while not _WindowsClosed:
    # 计算当前捕捉的位置和大小
    try:
        GrabWindows.update()
        OperateWindows.update()
        WindowSize = [GrabWindows.winfo_width(), GrabWindows.winfo_height()]
        SPoint = (GrabWindows.winfo_x() + 8, GrabWindows.winfo_y() + 30)
        EPoint = (SPoint[0] + WindowSize[0], SPoint[1] + WindowSize[1])
        Box = (SPoint[0], SPoint[1], EPoint[0], EPoint[1])
        if _WindowSize != WindowSize:
            _WindowSize = WindowSize
            cv2.resizeWindow("Image", WindowSize[0], WindowSize[1])
            Configure.ConfigObj["WindowSize"] = WindowSize
            Configure.Save()
    except Exception as Ex:
        break

    # 抓取屏幕图像, 然后转为OpenCV的GBR格式
    GrabScreen = ImageGrab.grab(bbox=Box)
    Image = cv2.cvtColor(np.array(GrabScreen), cv2.COLOR_RGB2BGR)
    if _SetBackground:
        CorrectImage.SetBackground(Image)
        _SetBackground = False
    else:
        Image, Offset, FPS = CorrectImage.GetOffset(Image)
        if _ControlStatus:
            try:
                if OffsetIndex < MaxLen:
                    OffsetList[OffsetIndex, :] = [Offset[0], Offset[1], FPS]
                    OffsetIndex += 1
                StepMotor.SetOffset(Offset)
                Text = '温漂控制系统'
            except Exception as Ex:
                messagebox.showinfo("Error", Ex)
        else:
            # 修改当前的速度标识
            if _LevelIndex >= len(SpeedLevel):
                _LevelIndex = len(SpeedLevel) - 1
                _OldSpeed = -1
            if _OldSpeed != SpeedLevel[_LevelIndex]:
                _OldSpeed = SpeedLevel[_LevelIndex]
            Text = '步长:%d' % _OldSpeed
        LBSpeed.configure(text=Text)

    # 显示图像并配置为窗口程序的主循环
    cv2.imshow("Image", Image)
cv2.destroyAllWindows()
