#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import json
import os


# 关于读写配置文件对象的内容
class Config:

    # 配置文件储存路径
    ConfigPath = './lib/Config.json'

    # 默认配置文件参数
    Data = {
        # 温漂图像纠正部分的参数设置
        "Correct": {
            # 当前匹配点搜索的像素范围
            "MatchRange": 50,
            # 最小置信匹配点个数
            "MatchCount": 20,
        },

        # 步进电机的相关设置
        "Stepper": {
            # 每次修正的步长大小(脉冲个数)
            "CorrectStep": [5, 5],
            # 可以循环切换的速度值范围(脉冲/秒)
            "SpeedStep": [1, 10, 100, 500, 1000],
            # 指定两个轴的运动方向与操作方向是否反向
            "SteperInvert": [0, 0],
        },

        # 窗口的相关样式设置
        "Windows": {
            # 屏幕截取的窗口大小
            "Size": [500, 500],
            # 子图像缩放的比例
            "ThumbRate": 0.3,
            # 绘制的线的宽度
            "LineSize": 2,
            # 绘制的线的颜色GBR格式
            "LineColor": [0, 0, 255],
            # 绘制的字符串大小
            "StrSize": 1,
            # 绘制的字符串颜色GBR格式
            "StrColor": [0, 255, 0]
        },
    }

    # 保存当前的配置文件数据
    def Save(self):
        try:
            with open(self.ConfigPath, 'w') as JsonFile:
                json.dump(self.Data, JsonFile, indent=4)
            return True
        except:
            return False

    # 从本地读取配置文件数据
    def Load(self):
        # 检查json文件是否存在, 如果不存在则新建
        if not os.path.exists(self.ConfigPath):
            return self.Save()

        try:
            # 从本地读取配置文件数据
            with open(self.ConfigPath, 'r') as JsonFile:
                LoadConfig = json.load(JsonFile)

            # 匹配本地文件中配置文件信息与默认信息差异
            for Key in self.Data.keys():
                if Key in LoadConfig.keys():
                    self.Data[Key] = LoadConfig[Key]
        except:
            pass

    # 从本地配置文件中读取相关的配置信息
    def __init__(self):
        self.Load()


# 测试函数
if __name__ == "__main__":
    ConfigObj = Config()
    print(ConfigObj.Data["Stepper"]["CorrectStep"])
