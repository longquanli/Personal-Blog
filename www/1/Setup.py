#!/usr/bin/python
# -*- coding:utf8 -*-

from RespondDataProcess import multiVoice
from CheckAccuracy import CheckAccuracy
import os

@post('/api/onesentencerecogition/dataprocess')
async def dataprocess(*, name, audioAddress)
    config_dict = dict()
    with open('./config.txt', 'rb') as f:
        lines = f.readlines()
        for line in lines:
            try:
                lst = line.decode().strip().split('=>')
                k = lst[0]
                v = lst[1]
                config_dict[k] = v
            except ValueError as e:
                print('input is error.')
    TARGET_ADDRESS = config_dict['target_address']
    if name == 'Baidu':
        #BaiduSpeech test
        APP_ID = config_dict['APP_ID']
        API_KEY = config_dict['API_KEY']
        SECRET_KEY = config_dict['SECRET_KEY']
        AUDIO_ADDRESS = config_dict['AUDIO_ADDRESS']
        multi = multiVoice(TARGET_ADDRESS)
        #第一项是语音存在地址，第二项是百度 API_KEY, 第三项是百度APP_ID
        multi.ProcessBaiduInit(AUDIO_ADDRESS, SECRET_KEY, API_KEY, APP_ID)
    elif name == 'Tencent':
        SECRET_KEY = config_dict['SECRET_KEY']
        SECRET_ID = config_dict['SECRET_ID']
        AUDIO_ADDRESS = config_dict['AUDIO_ADDRESS']
        #地址为要写入的地址文件夹
        multi = multiVoice(TARGET_ADDRESS)
        #三个参量， 第一个为音频文件夹目录，第二个为腾讯云SecreteKey, 第三个是腾讯云SecreteId
        multi.ProcessTencentInit(AUDIO_ADDRESS, SECRET_KEY, SECRET_ID)
    elif name == 'Aliyun':
        SECRET_KEY = config_dict['SECRET_KEY']
        SECRET_ID = config_dict['SECRET_ID']
        AUDIO_ADDRESS = config_dict['AUDIO_ADDRESS']
        multi = multiVoice(TARGET_ADDRESS)
        multi.ProcessAliyunInit(AUDIO_ADDRESS, SECRET_ID, SECRET_KEY)
    else:
        #test Xunfei
        APP_id = config_dict['APP_id']
        APP_key = config_dict['APP_KEY']
        AUDIO_ADDRESS = config_dict['AUDIO_ADDRESS']
        multi = multiVoice(TARGET_ADDRESS)
        #三个参量， 第一个为音频文件夹目录，第二个为讯飞APP_id, 第三个是讯飞APP_key
        multi.ProcessXunfeiInit(AUDIO_ADDRESS, APP_id, APP_key)
#a = CheckAccuracy(name, label_address, TARGET_ADDRESS)
#a.process()
print('finished')