#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import numpy as np
import cv2
import os


# 绘制综合显示的图像内容
class Draw:

    # 传入配置文件, 初始化相关的设置
    def __init__(self, ConfigObj, OnCVMouse):
        # 子图像缩放的比例
        self.ThumbRate = ConfigObj.Data["Windows"]["ThumbRate"]
        # 读取绘制的线宽度
        self.LineSize = ConfigObj.Data["Windows"]["LineSize"]
        # 读取绘制的线颜色
        self.LineColor = ConfigObj.Data["Windows"]["LineColor"]
        # 读取绘制的字符串大小
        self.StrSize = ConfigObj.Data["Windows"]["StrSize"]
        # 读取绘制的字符串颜色
        self.StrColor = ConfigObj.Data["Windows"]["StrColor"]
        # 显示图片的窗口设置
        cv2.namedWindow('Image')
        cv2.setMouseCallback('Image', OnCVMouse)

    # [私有方法]重新缩放图片大小, 并将其添加到背景图像中
    def _Private_ResizeImage(self, ThumbImage, MainImage):
        # 对图片进行指定倍率的缩放操作
        Height, Width = ThumbImage.shape[:2]
        tmp_Image = cv2.resize(ThumbImage, (int(Width * self.ThumbRate), int(Height * self.ThumbRate)))
        Height, Width = tmp_Image.shape[:2]

        # 将图片叠加到指定位置
        MainImage[0:Height, 0:Width, :] = tmp_Image

        # 给子图添加标题和边框, 并返回绘制结果
        Position = (5, 5 + self.StrSize * 5)
        cv2.rectangle(MainImage, (0, 0), (Width, Height), self.LineColor, self.LineSize)
        return MainImage

    # 传入图片, 显示一帧图片
    def DrawImage(self, CCDImage, MatchPoint):
        SrcImage = CCDImage.copy()
        if self.Background is None:
            self.Background = CCDImage

        # 将背景图片添加到左上角
        SrcImage = self._Private_ResizeImage(self.Background, SrcImage)

        # 绘制关联的直线
        for i in range(len(MatchPoint)):
            # 获取特征点的坐标信息
            M_Point = MatchPoint[i]
            BG_Point = (int(M_Point[0][0] * self.ThumbRate), int(M_Point[0][1] * self.ThumbRate))
            CCD_Point = tuple(map(int, M_Point[1]))

            # 绘制特征点与关联线
            WLimit = SrcImage.shape[1] * self.ThumbRate
            HLimit = SrcImage.shape[0] * self.ThumbRate
            if CCD_Point[0] > WLimit or CCD_Point[1] > HLimit:
                cv2.circle(SrcImage, BG_Point, self.LineSize + 1, self.LineColor, self.LineSize)
                cv2.circle(SrcImage, CCD_Point, self.LineSize + 1, self.LineColor, self.LineSize)
                cv2.line(SrcImage, BG_Point, CCD_Point, self.LineColor, 1)

        # 绘制图像
        return SrcImage

    # 设置背景图片
    def SetBackground(self, Background):
        self.Background = Background
