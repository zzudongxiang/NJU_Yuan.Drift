#!/usr/bin/python3
# -*- coding: UTF-8 -*-
from ctypes import windll, pointer


# 位移台步进电机的相关参数
class Stepper:
    # 创建MT设备
    MT_API = windll.LoadLibrary("./lib/MT_API_64.dll")
    # 当前设备的连接状态
    Status = False

    # 构造相关函数
    def __init__(self, ConfigObj):
        # 在进行温漂控制时单次移动的步长大小(脉冲个数)
        self.CorrectStep = ConfigObj.Data["Stepper"]["CorrectStep"]
        # 用户可以切换的脉冲速度范围
        self.SpeedStep = ConfigObj.Data["Stepper"]["SpeedStep"]
        # 位移台两个轴是否反转
        self.SteperInvert = ConfigObj.Data["Stepper"]["SteperInvert"]

        # 尝试连接设备并进行设备初始化
        self.MT_API.MT_Init()
        self.MT_API.MT_Open_USB()
        if self.MT_API.MT_Check() != 0:
            self.MT_API.MT_DeInit()
            self.Status = False
        else:
            self.Status = True
            self.SetSpeed(5000)

    # 设置位移台的移动速度, 同时修改其运动加速度
    def SetSpeed(self, Speed):
        # 设置轴位置模式, 并配置速度与加速度
        self.MT_API.MT_Set_Axis_Halt_All()
        for Index in range(2):
            self.MT_API.MT_Set_Axis_Mode_Position(Index)
            self.MT_API.MT_Set_Axis_Position_Acc(Index, Speed * 10)
            self.MT_API.MT_Set_Axis_Position_Dec(Index, Speed * 10)
            self.MT_API.MT_Set_Axis_Position_V_Max(Index, Speed)

    # 释放相关资源
    def __del__(self):
        self.MT_API.MT_Set_Axis_Halt_All()
        self.MT_API.MT_Close_USB()
        self.MT_API.MT_DeInit()

    # 相对移动对应的轴
    def Move(self, Axis, Step):
        if self.Status and Step != 0:
            # 计算指定的轴是否需要运动反转
            if self.SteperInvert[Axis] != 0:
                Step = -Step
            # 相对移动对应的轴
            self.MT_API.MT_Set_Axis_Position_P_Target_Rel(Axis, Step)

    # 设置当前的偏移量
    def SetOffset(self, Offset):
        if self.Status:
            # 计算偏移量, 换算位脉冲给到位移台
            for Index in range(2):
                Num = int(Offset[Index] * self.CorrectStep[Index])
                self.Move(Index, Num)
