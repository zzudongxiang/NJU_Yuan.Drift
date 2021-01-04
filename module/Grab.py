#!/usr/bin/python3
# -*- coding: UTF-8 -*-
from PIL import ImageGrab
import numpy as np
import cv2


# 抓取桌面一定区域的图像
class Grab:
    # 初始化属性, 保存当前窗体大小
    def __init__(self, ConfigObj):
        self.OldSize = ConfigObj.Data["Windows"]["Size"]
        self.ConfigObj = ConfigObj

    # 抓取指定区域的图像
    def GrabImage(self, FormsObj):
        # 获取要截取的屏幕区域
        WindowSize = [FormsObj.GrabForm.winfo_width(), FormsObj.GrabForm.winfo_height()]
        SPoint = (FormsObj.GrabForm.winfo_x() + 8, FormsObj.GrabForm.winfo_y() + 30)
        EPoint = (SPoint[0] + WindowSize[0], SPoint[1] + WindowSize[1])
        Box = (SPoint[0], SPoint[1], EPoint[0], EPoint[1])

        # 检查窗口大小是否发生了改变
        if self.OldSize != WindowSize:
            self.OldSize = WindowSize
            self.ConfigObj.Data["Windows"]["Size"] = WindowSize
            self.ConfigObj.Save()

        # 转化图像格式并返回图像对象
        GrabScreen = ImageGrab.grab(bbox=Box)
        return cv2.cvtColor(np.array(GrabScreen), cv2.COLOR_RGB2BGR)