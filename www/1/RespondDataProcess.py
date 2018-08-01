
# coding: utf-8
#!/usr/bin/env python3


'multiVoice API'
__author__ = 'Charles Li'

#腾讯百度讯飞API一句话识别请求以及文件的读写处理
from HttpRequest import tencentSpeech
from IOProcess import VoiceToFile
import json
import os
from aip import AipSpeech
from multiprocessing.dummy import Pool
import time
import urllib
import json
import hashlib
import base64
from urllib import request
from urllib.request import urlopen
from Aliyun import Aliyun

class multiVoice(object):
    __slots__ = 'SECRETID', 'SECRETKEY', 'APP_ID', 'WriteToAddress', 'OldAudioAddress'
    def __init__(self, writetoaddress):
        self.WriteToAddress = writetoaddress
    #get audio voice set()
    def createBodyPath(self, path):
        store = set()
        pathhead = path + '/'
        files = os.listdir(pathhead)
        for file in files:
            store.add(file)
        return store
    #写入错误文件
    def write_error_file(self, address, audioaddress):
            with open(address, 'a', encoding='utf-8') as f:
                    f.writelines(audioaddress + 'file has an error' + '\n')
    #生成的string以空格间隔开
    def process_string(self, string):
        ans = []
        for i in range(len(string)):
            if string[i].isalpha() or string[i].isdigit():
                ans.append(string[i] + ' ')
        return ''.join(ans)
    def ProcessAliyun(self, tmp):
        client = Aliyun(self.SECRETID, self.SECRETKEY)
        audioaddress = '%s/%s' % (self.OldAudioAddress, tmp)
        target = client.asr_rest_recognize(audioaddress)
        s = json.loads(target)
        path = self.WriteToAddress + '/test_data_Aliyun.txt'
        if 'result' in s:
            voicetofile = VoiceToFile("", "")
            pre_string = s['result']
            string = self.process_string(pre_string)
            string += '(./data/%s)' % tmp
            voicetofile.write_result(string, path)
        else:
            self.write_error_file('%s/error_voice_Aliyun.txt' % (self.WriteToAddress), audioaddress)
    def ProcessTencent(self, url):
        client = tencentSpeech(self.SECRETKEY, self.SECRETID)
        # audioaddress = '%s/%s' % (self.OldAudioAddress, tmp)
        target = client.ASR(url, 'wav', '0')
        #将json解析成dict
        s = json.loads(target)
        path = self.WriteToAddress + '/test_data_Tencent.txt'
        #识别服务器传回的数据
        if 'Response' in  s and 'Result' in s['Response']:
            if s['Response']['Result'][:-1] != '':
                voicetofile = VoiceToFile("", "")
                pre_string = s['Response']['Result'][:-1]
                string = self.process_string(pre_string)
                voicetofile.write_result(string, path)
            else:
                self.write_error_file('%s/error_voice_tencent.txt' % (self.WriteToAddress), self.OldAudioAddress)
        else:
            self.write_error_file('%s/error_voice_tencent.txt' % (self.WriteToAddress), self.OldAudioAddress)
    def ProcessBaidu(self, tmp):
        def get_file_content(filePath):
            with open(filePath, 'rb') as fp:
                return fp.read()
        #调用Baidu自己的api
        client = AipSpeech(self.APP_ID, self.SECRETID, self.SECRETKEY)
        audioaddress = '%s/%s' % (self.OldAudioAddress, tmp)
        target = client.asr(get_file_content(audioaddress), 'wav', 16000, {'dev_pid': 1536,})
        path = self.WriteToAddress + '/test_data_Baidu.txt'
        #write in to file
        if 'result' in target:
            pre_string = target['result'][0]
            string = self.process_string(pre_string)
            string += '(./data/%s)' % tmp
            voicetofile = VoiceToFile("", "")
            voicetofile.write_result(string, path)
        else:
            self.write_error_file('%s/error_voice_baidu.txt' % (self.WriteToAddress), audioaddress)
    def ProcessXunfei(self, tmp):
        url = 'http://api.xfyun.cn/v1/service/v1/iat'
        audioaddress = '%s/%s' % (self.OldAudioAddress, tmp)
        path = self.WriteToAddress + '/test_data_Xunfei.txt'
        f = open(audioaddress, 'rb')
        file_content = f.read()
        base64_audio = base64.b64encode(file_content)
        #url加密
        body = urllib.parse.urlencode({'audio': base64_audio}).encode()
        param = {"engine_type": "sms16k", "aue": "raw"}
        x_param = base64.b64encode(json.dumps(param).replace(' ', '').encode()).decode()
        x_time = int(int(round(time.time() * 1000)) / 1000)
        #md加密
        hash = hashlib.md5()
        hash.update(bytes(self.SECRETKEY + str(x_time) + x_param, encoding = 'utf-8'))
        x_checksum = hash.hexdigest()
        x_header = {'X-Appid': self.SECRETID,
                    'X-CurTime': x_time,
                    'X-Param': x_param,
                    'X-CheckSum': x_checksum,
                   }
        #发送请求
        req = request.Request(url, body, x_header)
        response = urlopen(req)
        result = json.loads(response.read().decode())
        if 'desc' in result and result['desc'] == 'success':
            voicetofile = VoiceToFile("", "")
            pre_string = result['data'][: -1]
            string = self.process_string(pre_string)
            string += '(./data/%s)' % tmp
            voicetofile.write_result(string, path)
        else:
            self.write_error_file('%s/error_voice_Xunfei.txt' % (self.WriteToAddress), audioaddress)
    #Tencent way
    def ProcessTencentInit(self, oldAudioAddress, secretkey, secretid):
        self.SECRETKEY = secretkey
        self.SECRETID = secretid
        self.OldAudioAddress = oldAudioAddress
        r = self.ProcessTencent(oldAudioAddress)
        # store = self.createBodyPath(oldAudioAddress)
        # #四核心一起工作
        # pool = Pool(4)
        # results = pool.map(self.ProcessTencent, store)
        # pool.close()
        # pool.join()
    #Baidu way
    def ProcessBaiduInit(self, oldAudioAddress, secretkey, secretid, appid):
        self.OldAudioAddress = oldAudioAddress
        self.SECRETKEY = secretkey
        self.SECRETID = secretid
        self.APP_ID = appid
        store = self.createBodyPath(oldAudioAddress)
        pool = Pool(4)
        results = pool.map(self.ProcessBaidu, store)
        pool.close()
        pool.join()
        print("ASR of Baidu has finished!")
    #Xunfei way
    def ProcessXunfeiInit(self, oldAudioAddress, x_appid, api_key):
        self.SECRETID = x_appid
        self.SECRETKEY = api_key
        self.OldAudioAddress = oldAudioAddress
        store = self.createBodyPath(oldAudioAddress)
        pool = Pool(4)
        results = pool.map(self.ProcessXunfei, store)
        pool.close()
        pool.join()
        print("ASR of Xunfei has finished!")
    #Aliyun
    def ProcessAliyunInit(self, oldAudioAddress, appid, appkey):
        self.SECRETID = appid
        self.SECRETKEY = appkey
        self.OldAudioAddress = oldAudioAddress
        store = self.createBodyPath(oldAudioAddress)
        pool = Pool(4)
        results = pool.map(self.ProcessAliyun, store)
        pool.close()
        pool.join()
        print("ASR of Aliyun has finished!")
