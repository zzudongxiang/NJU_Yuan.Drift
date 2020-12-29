#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import json
import os


# 配置文件对象
class Config:
    # 配置文件储存路径
    ConfigPath = './lib/Config.json'

    # 默认配置文件参数
    ConfigObj = {
        "MatchRange": 50,
        "MatchCount": 20,
        "WindowSize": [500, 500],
        "Speed": 5000,
        "StepRate": [5, 5],
        "SpeedLevel": [1, 10, 100, 500, 1000],
        "StepInvert": [0, 0],
        "Paint": {
            "LSize": 2,
            "LColor": (0, 0, 255),
            "SSize": 0.8,
            "SHeight": 20,
            "SColor": (255, 255, 0),
            "ResizeRate": 0.3
        },
    }

    # 保存当前的配置文件数据
    def Save(self):
        try:
            with open(self.ConfigPath, 'w') as JsonFile:
                json.dump(self.ConfigObj, JsonFile, indent=4)
            return True
        except:
            return False

    # 从本地配置文件中读取相关的配置信息
    def __init__(self):

        # 检查json文件是否存在, 如果不存在则新建
        if not os.path.exists(self.ConfigPath):
            return self.Save()

        # 从本地读取配置文件数据
        with open(self.ConfigPath, 'r') as JsonFile:
            LoadConfig = json.load(JsonFile)

        # 匹配本地文件中配置文件信息与默认信息差异
        for Key in self.ConfigObj.keys():
            if Key in LoadConfig.keys():
                self.ConfigObj[Key] = LoadConfig[Key]
