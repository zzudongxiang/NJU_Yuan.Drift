#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import numpy as np
import cv2


# 根据采集的图像处理偏移量
class Correct:
    # [全局参数]创建ORB对象, 用于提取图像的特征点
    _ORB = cv2.ORB_create()
    # [全局参数]创建BFMatcher对象, 用于匹配图像的特征点
    _BFM = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    # [全局参数]<只读>背景的相关数据(图片, 特征点等)
    _Background = {"Image": None, "KeyPoint": [], "Descriptor": None}

    # 传入配置对象, 初始化相关对象
    def __init__(self, ConfigObj):
        # [全局参数]有效特征点匹配半径(单位像素), 建议不超过50
        self._MRange = ConfigObj.Data["Correct"]["MatchRange"]
        # [全局参数]匹配到的有效特征点高于该值时视为有效匹配, 建议不超过20
        self._MCount = ConfigObj.Data["Correct"]["MatchCount"]

    # [私有方法]对图像进行预处理, 并提取图像的特征点数据
    def _Private_PreProcess(self, SrcImage):
        # 转化数据格式
        Image = np.array(SrcImage)
        Image = cv2.cvtColor(Image, cv2.COLOR_RGB2GRAY)

        # 提取图片的特征点数据, 并返回特征点数据
        KeyPoint, Descriptor = self._ORB.detectAndCompute(Image, None)
        return KeyPoint, Descriptor

    # [公有方法]处理背景图片信息, 并将其储存到全局变量中
    def SetBackground(self, SrcBackground):
        KeyPoint, Descriptor = self._Private_PreProcess(SrcBackground)
        if not Descriptor is None:
            # 储存全局变量
            self._Background["Image"] = SrcBackground
            self._Background["KeyPoint"] = KeyPoint
            self._Background["Descriptor"] = Descriptor
            return True
        else:
            return False

    # [公有方法]获取拼接的图片信息
    def GetOffset(self, CCDImage):
        # 预处理传入的图像, 并检查背景图像是否正常
        CCD_KeyPoint, CCD_Descriptor = self._Private_PreProcess(CCDImage)
        if self._Background["Descriptor"] is None or CCD_Descriptor is None:
            return False, (0, 0), CCDImage, CCDImage, []

        # 处理传入的图像, 获取其特征点, 并进行匹配
        Matches = self._BFM.match(self._Background["Descriptor"], CCD_Descriptor)
        Matches = sorted(Matches, key=lambda x: x.distance)

        # 计算可信赖距离阈值并初始化返回的相关参数
        AveDis = np.mean(list(Matches[i].distance for i in range(len(Matches))))
        Offset = np.zeros((1, 2), dtype=float)
        MatchPoint = []

        # 寻找有效的匹配特征点数据
        for i in range(len(Matches)):
            if Matches[i].distance > AveDis:
                break

            # 计算偏移误差
            BG_Point = self._Background["KeyPoint"][Matches[i].queryIdx].pt
            CCD_Point = CCD_KeyPoint[Matches[i].trainIdx].pt

            # 计算特征点之间的距离是否满足要求
            DeltaX = BG_Point[0] - CCD_Point[0]
            DeltaY = BG_Point[1] - CCD_Point[1]
            if np.power(DeltaX, 2) + np.power(DeltaY, 2) < np.power(self._MRange, 2):
                Offset = Offset + [DeltaX, DeltaY]
                MatchPoint.append([BG_Point, CCD_Point])

        # 求取偏移量的平均值并返回结果
        KPCount = len(MatchPoint)
        if KPCount > 0 and KPCount > self._MCount:
            Offset = Offset / KPCount
            Offset = tuple(Offset[0])
        else:
            return False, (0, 0), CCDImage, CCDImage, []

        # 计算偏移纠正后的图像数据
        TranMat = np.float32([[1, 0, Offset[0]], [0, 1, Offset[1]]])
        WarpImage = cv2.warpAffine(CCDImage, TranMat, None)

        # 计算传入图像与背景图像相减的图像数据
        AImage = np.array(cv2.cvtColor(WarpImage, cv2.COLOR_BGR2GRAY), np.uint8)
        BImage = np.array(cv2.cvtColor(self._Background["Image"], cv2.COLOR_BGR2GRAY), np.uint8)
        DiffImage = np.array(abs(AImage - BImage), np.uint8)
        DiffImage = cv2.cvtColor(DiffImage, cv2.COLOR_GRAY2BGR)

        # 返回结果
        return True, Offset, WarpImage, DiffImage, MatchPoint
