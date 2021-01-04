#!/usr/bin/python3
# -*- coding: UTF-8 -*-
from tkinter import messagebox
import numpy as np
import time
import cv2
import os

# User Module Import
from module.DataFile import DataFile
from module.Correct import Correct
from module.Stepper import Stepper
from module.Config import Config
from module.Forms import Forms
from module.Draw import Draw
from module.Grab import Grab

# 编译生成单个*.exe文件
# pyinstaller Setup.py -w -F -i "lib/NJU.ico"


# 开启或关闭温漂补偿功能
def ControlCallBack():
    # 生命全局变量并获取按下按键的具体数值
    global Processing, DataFileObj, GrabObj, FormsObj, CorrectObj, ShowIndex
    if not Processing:
        # 隐藏主窗口
        FormsObj.GrabForm.state('icon')
        time.sleep(0.25)

        # 截取一张背景图像, 并处理后传入参数
        Background = GrabObj.GrabImage(FormsObj)
        DrawObj.SetBackground(Background)
        CorrectObj.SetBackground(Background)
        DataFileObj.StartRecording(Background)
        FailedTime = time.time()
        ShowIndex = 0
        Processing = True
    else:
        # 弹窗显示文件记录位置
        DataFileObj.StopRecording()
        messagebox.showinfo('数据记录成功', '本次实验的记录已储存在%s文件路径下' % DataFileObj.DataPath)
        Processing = False


# 移动设备的回调函数
def MoveCallBack(event):
    global Processing, SpeedStep, SpeedIndex, StepperObj

    KeyDown = event.widget._name
    Step = SpeedStep[SpeedIndex]

    # 自动控制模式禁用手动控制
    if Processing:
        messagebox.showwarning("警告", "位移台暂时由温漂控制程序接管")
        return

    # 切换速度档位
    if KeyDown == '⊙':
        SpeedIndex = (SpeedIndex + 1) % len(SpeedStep)
    else:
        # X轴方向移动
        if KeyDown == '→' or KeyDown == '↗' or KeyDown == '↘':
            AxisStep = Step
        elif KeyDown == '←' or KeyDown == '↖' or KeyDown == '↙':
            AxisStep = -Step
        else:
            AxisStep = 0
        StepperObj.Move(0, Step)

        # Y轴方向移动
        if KeyDown == '↑' or KeyDown == '↖' or KeyDown == '↗':
            AxisStep = Step
        elif KeyDown == '↓' or KeyDown == '↙' or KeyDown == '↘':
            AxisStep = -Step
        else:
            AxisStep = 0
        StepperObj.Move(1, Step)


# 鼠标点击时操作
def OnCVMouse(event, x, y, flags, param):
    global ShowIndex
    if event == cv2.EVENT_LBUTTONDOWN:
        ShowIndex = (ShowIndex + 1) % 5


# 构造配置文件对象
ConfigObj = Config()
DataFileObj = DataFile()
DrawObj = Draw(ConfigObj, OnCVMouse)
FormsObj = Forms(ConfigObj, ControlCallBack, MoveCallBack)
CorrectObj = Correct(ConfigObj)
StepperObj = Stepper(ConfigObj)
GrabObj = Grab(ConfigObj)

# 方便调用的变量列表
SpeedStep = ConfigObj.Data["Stepper"]["SpeedStep"]
StrSize = ConfigObj.Data["Windows"]["StrSize"]
StrColor = ConfigObj.Data["Windows"]["StrColor"]
Processing = False
OldProcessing = True
SpeedIndex = 0
OldSpeedIndex = -1
FailedTime = 0
ShowIndex = 0

# 主程序刷新界面与内容
while FormsObj.Update():
    # 抓取图像并进行处理
    CCDImage = GrabObj.GrabImage(FormsObj)

    # 获取图像并处理图像数据
    if Processing:
        Ret, Offset, WarpImage, DiffImage, MatchPoint = CorrectObj.GetOffset(CCDImage)
        StepperObj.SetOffset(Offset)
        DataFileObj.Dump(CCDImage, Ret, Offset, WarpImage, DiffImage)

        # 更新显示的内容
        if ShowIndex == 0:
            IMG = DrawObj.DrawImage(CCDImage, MatchPoint)
        elif ShowIndex == 1:
            IMG = DrawObj.Background
        elif ShowIndex == 2:
            IMG = CCDImage
        elif ShowIndex == 3:
            IMG = WarpImage
        elif ShowIndex == 4:
            IMG = DiffImage

        # 判断是否有效抓取到对象
        if not Ret:
            if time.time() - FailedTime > 10:
                messagebox.showerror("无法识别特征", "无法识别图像的特征信息, 且等待恢复超时")
                ControlCallBack()
        else:
            FailedTime = time.time()
    else:
        IMG = CCDImage

    # 更新绘制
    Dic = ['MOKE Drift', 'Background', 'CCD Image', 'Warp Image', 'Diff Image']
    cv2.putText(IMG, Dic[ShowIndex], (5, 25 * StrSize), cv2.FONT_HERSHEY_COMPLEX, StrSize, StrColor, 1)
    cv2.imshow('Image', IMG)

    # 刷新设备的在线状态与速度
    if OldSpeedIndex != SpeedIndex:
        OldSpeedIndex = SpeedIndex
        if Stepper.Status:
            Color = 'green'
            Text = '设备在线 | 速度:%5d'
        else:
            Color = 'red'
            Text = '设备离线 | 速度:%5d'
        Text = Text % SpeedStep[SpeedIndex]
        FormsObj.MenuStatus.configure(text=Text, background=Color)

    # 刷新当前的记录状态
    if OldProcessing != Processing:
        OldProcessing = Processing
        if Processing:
            Color = 'green'
            Text = '控\n制\n状\n态\n\nON'
        else:
            Color = 'red'
            Text = '控\n制\n状\n态\n\nOFF'
        FormsObj.MenuSwitch.configure(text=Text, foreground=Color)