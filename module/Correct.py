#!/usr/bin/python3
# -*- coding: UTF-8 -*-
from module.Config import Config
from datetime import datetime
import numpy as np
import cv2


class Correct:

    # 获取配置文件对象
    Configure = Config()
    # 设置当前运行模式是否为Debug模式
    _Debug = False
    # [全局参数]创建ORB对象, 用于提取图像的特征点
    _ORB = cv2.ORB_create()
    # [全局参数]创建BFMatcher对象, 用于匹配图像的特征点
    _BFM = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    # [全局参数]有效特征点匹配半径(单位像素), 建议不超过50
    _MRange = Configure.ConfigObj["MatchRange"]
    # [全局参数]匹配到的有效特征点高于该值时视为有效匹配, 建议不超过20
    _MCount = Configure.ConfigObj["MatchCount"]
    # [全局参数]设置绘图的相关参数, 包括笔刷大小与颜色(GBR格式)等
    _Paint = Configure.ConfigObj["Paint"]
    # [全局参数]<只读>背景的相关数据(图片, 特征点等)
    _Background = {"Image": None, "KeyPoint": [], "Descriptor": None}

    # [私有方法]对图像进行预处理, 并提取图像的特征点数据
    def _Private_PreProcess(self, SrcImage):
        # 转化数据格式
        Image = np.array(SrcImage)
        Image = cv2.cvtColor(Image, cv2.COLOR_RGB2GRAY)

        # 提取图片的特征点数据, 并返回特征点数据
        KeyPoint, Descriptor = self._ORB.detectAndCompute(Image, None)
        return KeyPoint, Descriptor

    # [私有方法]重新缩放图片大小, 并将其添加到背景图像中
    def _Private_ResizeImage(self, SrcImage, MainImage, Title, TopLeft=True):
        # 对图片进行指定倍率的缩放操作
        Height, Width = SrcImage.shape[:2]
        Image = cv2.resize(SrcImage, (int(Width * self._Paint["ResizeRate"]), int(Height * self._Paint["ResizeRate"])))
        Height, Width = Image.shape[:2]

        # 计算图片叠加的指定位置对应的像素坐标
        if TopLeft:
            X = 0
            Y = 0
        else:
            X = MainImage.shape[1] - Width
            Y = MainImage.shape[0] - Height

        # 将图片叠加到指定位置
        MainImage[Y:Y + Height, X:X + Width, :] = Image

        # 给子图添加标题和边框, 并返回绘制结果
        Position = (5 + X, 5 + self._Paint["SHeight"] + Y)
        cv2.putText(MainImage, Title, Position, cv2.FONT_HERSHEY_COMPLEX, self._Paint["SSize"], self._Paint["SColor"], 1)
        cv2.rectangle(MainImage, (X, Y), (X + Width, Y + Height), self._Paint["LColor"], self._Paint["LSize"])
        return MainImage

    # [公有方法]处理背景图片信息, 并将其储存到全局变量中
    def SetBackground(self, SrcBackground):
        KeyPoint, Descriptor = self._Private_PreProcess(SrcBackground)
        if not Descriptor is None:
            # 储存全局变量
            self._Background["Image"] = SrcBackground
            self._Background["KeyPoint"] = KeyPoint
            self._Background["Descriptor"] = Descriptor

            # 设置窗口格式
            if self._Debug:
                cv2.namedWindow('Image', cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)
                cv2.resizeWindow('Image', SrcBackground.shape[1], SrcBackground.shape[0])
            return True
        else:
            return False

    # [公有方法]获取拼接的图片信息
    def GetOffset(self, CCDImage):
        # 处理一帧图像, 并获取处理时间的数据
        StartTime = datetime.now()
        CCD_KeyPoint, CCD_Descriptor = self._Private_PreProcess(CCDImage)
        if self._Background["Descriptor"] is None or CCD_Descriptor is None:
            cv2.putText(CCDImage, "Background Error", (5, self._Paint["SHeight"]), cv2.FONT_HERSHEY_COMPLEX, self._Paint["SSize"], (0, 0, 255), 1)
            return CCDImage, (0, 0), -1

        # 匹配两张图之间的特征
        Matches = self._BFM.match(self._Background["Descriptor"], CCD_Descriptor)
        Matches = sorted(Matches, key=lambda x: x.distance)

        # 计算可信赖距离阈值并初始化返回的相关参数
        AveDis = np.mean(list(Matches[i].distance for i in range(len(Matches))))
        Offset = np.zeros((1, 2), dtype=float)
        MatchPoint = []

        # 寻找有效的匹配特征点数据
        for i in range(len(Matches)):
            Distance = Matches[i].distance
            if Distance > AveDis:
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
            Text = 'Offset: (%+.2f, %+.2f)' % Offset
        else:
            Offset = (0, 0)
            MatchPoint = []
            Text = 'Invalid Feature'

        # 在CCD图上添加背景子图与修正后的子图
        TranMat = np.float32([[1, 0, Offset[0]], [0, 1, Offset[1]]])
        WarpImage = cv2.warpAffine(CCDImage, TranMat, None)
        AImage = np.array(cv2.cvtColor(WarpImage, cv2.COLOR_BGR2GRAY), np.uint8)
        BImage = np.array(cv2.cvtColor(self._Background["Image"], cv2.COLOR_BGR2GRAY), np.uint8)
        if AImage.shape != BImage.shape:
            return CCDImage, (0, 0), -1
        DiffImage = np.array(abs(AImage - BImage), np.uint8)
        CCDImage = self._Private_ResizeImage(WarpImage, CCDImage, "Corrected", False)
        CCDImage = self._Private_ResizeImage(self._Background["Image"], CCDImage, "Background", True)

        # 绘制全部的点信息
        for i in range(len(MatchPoint)):
            # 获取特征点的坐标信息
            M_Point = MatchPoint[i]
            BG_Point = (int(M_Point[0][0] * self._Paint["ResizeRate"]), int(M_Point[0][1] * self._Paint["ResizeRate"]))
            CCD_Point = tuple(map(int, M_Point[1]))

            # 绘制特征点与关联线
            WLimit = CCDImage.shape[1] * self._Paint["ResizeRate"]
            HLimit = CCDImage.shape[0] * self._Paint["ResizeRate"]
            if CCD_Point[0] > WLimit or CCD_Point[1] > HLimit:
                cv2.circle(CCDImage, BG_Point, self._Paint["LSize"], self._Paint["LColor"], self._Paint["LSize"])
                cv2.circle(CCDImage, CCD_Point, self._Paint["LSize"], self._Paint["LColor"], self._Paint["LSize"])
                cv2.line(CCDImage, BG_Point, CCD_Point, self._Paint["LColor"], 1)

        # 显示当前的帧率与偏移等信息
        FPS = (datetime.now() - StartTime).total_seconds()
        if FPS > 0:
            FPS_V = (1 / FPS)
            FPS = 'FPS:%.1f' % FPS_V
            if not (KPCount > 0 and KPCount > self._MCount):
                FPS_V = -1
        else:
            FPS_V = -1
            FPS = 'FPS:--.-'
        cv2.putText(CCDImage, FPS, (CCDImage.shape[1] - 130, 5 + self._Paint["SHeight"]), cv2.FONT_HERSHEY_COMPLEX, self._Paint["SSize"], self._Paint["SColor"], 1)
        cv2.putText(CCDImage, Text, (5, CCDImage.shape[0] - 5), cv2.FONT_HERSHEY_COMPLEX, self._Paint["SSize"], self._Paint["SColor"], 2)

        # 返回结果
        return CCDImage, Offset, FPS_V


# [测试方法]测试视频素材
def _Test_Video(C, VideoPath):
    # 读取测试视频素材
    VCapture = cv2.VideoCapture(VideoPath)

    # 读取第一帧为背景图片
    if VCapture.isOpened():
        _, SrcBackground = VCapture.read()
        C.SetBackground(SrcBackground)
    else:
        return

    # 依次读取每一帧处理图片
    while VCapture.isOpened():
        _, RealImage = VCapture.read()
        if RealImage is None or cv2.waitKey(1) == 27:
            break
        Image, _, _ = C.GetOffset(RealImage)
        cv2.imshow('Image', Image)

    # 释放视频播放的资源
    VCapture.release()


# [测试方法]测试文件夹素材
def _Test_Folder(C, FolderPath):
    import os

    # 读取所有图片的内容(*.jpg, *.png, *.gif, *.bmp, *.jpeg, *.tif)
    ImageExtension = ['.jpg', '.png', '.gif', '.bmp', '.jpeg', '.tif']
    FilePath = os.listdir(FolderPath)
    Files = []
    for File in FilePath:
        FileExtension = os.path.splitext(File)[-1].lower()
        if not os.path.isdir(File) and FileExtension in ImageExtension:
            Files.append(FolderPath + '/' + File)
    Files.sort()

    # 读取背景并进行处理
    C.SetBackground(cv2.imread(Files[0]))

    # 处理每一帧图片
    for i in range(len(Files) - 1):
        RealImage = cv2.imread(Files[i + 1])
        if cv2.waitKey(1) == 27:
            break
        Image, _, _ = C.GetOffset(RealImage)
        cv2.imshow('Image', Image)


# 主程序运行入口
if __name__ == "__main__":
    C = Correct()
    #cv2.namedWindow('Image', cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)
    #cv2.waitKey(0)
    #_Test_Video(C, './sample/p1red_14.avi')
    #_Test_Video(C, './sample/201119214538.mp4')
    #_Test_Folder(C, './sample/p1_red')
    #_Test_Folder(C, './sample/p1_red_domian')
    cv2.waitKey(0)