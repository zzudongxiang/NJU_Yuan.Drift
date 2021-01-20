#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from datetime import datetime
import numpy as np
import time
import cv2
import os


# 储存数据和图像对象
class DataFile:

    # 当前文件对象的索引序号
    FileIndex = 0
    # 当前数据要储存的文件夹名称
    DataPath = './data/tmp/'
    # 日志写入对象
    LogWriter = None
    # 记录开始的时间
    StartTime = time.time()

    # 加载配置文件, 生成配置对象
    def __init__(self, ConfigObj):
        self.RawData = ConfigObj.Data["RawData"]

    # [私有方法] 获取对应的文件名对象
    def _Private_FileName(self, Ret, Offset):
        # 计算对应的文件名对象以及图片后缀
        MillSecond = int((time.time() - self.StartTime) * 1000)
        FileName = "%06d-%08dms-(%.3f,%.3f)" % (self.FileIndex, MillSecond, Offset[0], Offset[1])
        if not Ret:
            FileName += '-Failed'
        FileName += '.bmp'

        # 检查文件夹是否存在, 如果不存在则新建文件夹
        PathList = ['Ori', 'Warp', 'Sub']
        for DirPath in PathList:
            tmpPath = self.DataPath + '/' + DirPath
            if not os.path.exists(tmpPath):
                os.makedirs(tmpPath)

        # 返回文件名(不带有文件路径)
        self.FileIndex += 1
        return FileName

    # 新建数据储存的工程目录
    def StartRecording(self, Background):
        # 生成新的文件夹路径
        self.DataPath = './data/' + datetime.now().strftime('%Y-%m-%d_%H-%M-%S.%f')[:-3] + '/'
        os.makedirs(self.DataPath)
        self.FileIndex = 0
        self.StartTime = time.time()

        # 储存背景图像
        cv2.imwrite(self.DataPath + "/Background.bmp", Background)

        # 生成日志写入对象
        self.StopRecording()
        self.LogWriter = open(self.DataPath + 'Logs.dat', 'w')
        self.LogWriter.write('DateTime, Offset_X, Offset_Y, Ret\n')

    # 停止记录数据
    def StopRecording(self):
        if not self.LogWriter is None:
            self.LogWriter.close()
            self.LogWriter = None

    # 写入一个数据对象
    def Dump(self, CCDImage, Ret, Offset, WrapImage, DiffImage):
        # 生成对应的文件名
        FileName = self._Private_FileName(Ret, Offset)

        # 储存图像数据
        if self.RawData["Ori"] != 0:
            cv2.imwrite(self.DataPath + "/Ori/" + FileName, CCDImage)
        if self.RawData["Warp"] != 0:
            cv2.imwrite(self.DataPath + "/Warp/" + FileName, WrapImage)
        if self.RawData["Sub"] != 0:
            cv2.imwrite(self.DataPath + "/Sub/" + FileName, DiffImage)

        # 储存Log文件
        if not self.LogWriter is None:
            DateTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            self.LogWriter.write('%s, %f, %f, %s\n' % (DateTime, Offset[0], Offset[1], Ret))
