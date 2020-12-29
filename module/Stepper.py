#!/usr/bin/python3
# -*- coding: UTF-8 -*-
from ctypes import windll, pointer
from module.Config import Config


# XY轴步进电机的相关参数
class Stepper:

    # 获取配置文件对象
    Configure = Config()
    # 创建MT设备
    MT_API = windll.LoadLibrary("./lib/MT_API_64.dll")
    # 设置MT设备运动的速度(脉冲个数)
    Speed = Configure.ConfigObj["Speed"]
    # 每个像素代表StepRate个脉冲个数
    StepRate = Configure.ConfigObj["StepRate"]

    # 构造相关函数
    def __init__(self):
        # 初始化资源并连接USB设备
        self.MT_API.MT_Init()
        self.MT_API.MT_Open_USB()
        self.MT_API.MT_Set_Axis_Halt_All()

        # 设置轴位置模式, 并配置速度与加速度
        for Index in range(2):
            self.MT_API.MT_Set_Axis_Mode_Position(Index)
            self.MT_API.MT_Set_Axis_Position_Acc(Index, self.Speed * 10)
            self.MT_API.MT_Set_Axis_Position_Dec(Index, self.Speed * 10)
            self.MT_API.MT_Set_Axis_Position_V_Max(Index, self.Speed)

        # 进行USB连接测试
        if self.MT_API.MT_Check() != 0:
            self.MT_API.MT_DeInit()
            self.MT_API = None
            return

    # 释放相关资源
    def __del__(self):
        # 变量检查
        if self.MT_API is None:
            return

        # 释放资源
        self.MT_API.MT_Set_Axis_Halt_All()
        self.MT_API.MT_Close_USB()
        self.MT_API.MT_DeInit()

    # 相对移动对应的轴
    def Move(self, Axis, Step):
        # 变量检查
        if self.MT_API is None:
            return

        # 相对移动对应的轴
        self.MT_API.MT_Set_Axis_Position_P_Target_Rel(Axis, Step)

    # 设置当前的偏移量
    def SetOffset(self, Offset):
        # 变量检查
        if self.MT_API is None:
            return

        # 计算偏移量, 换算位脉冲给到位移台
        for Index in range(2):
            Num = int(Offset[Index] * self.StepRate[Index])
            self.MT_API.MT_Set_Axis_Position_P_Target_Rel(Index, Num)
