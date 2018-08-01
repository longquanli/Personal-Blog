
# coding: utf-8

#!/usr/bin/env python3

'VoiceToFile_labeled'
__author__ = 'Charles Li'

#1w条语音人工标注文件处理以及生成翻译的写入操作
import os
class VoiceToFile(object):
    __slots__ = 'readPath', 'targetPath'
    def __init__(self, readpath, targetpath):
        self.targetPath = targetpath
        self.readPath = readpath
    @property
    def read_path(self):
        return self.readPath
    @read_path.setter
    def read_path(self, readpath):
        if not isinstance(readpath, str):
            raise ValueError('Readpath must be string.')
        if len(readpath) == 0:
            raise ValueError('Readpath can not be empty.')
        self.readPath = readpath
    @property
    def target_path(self):
        return self.targetPath
    @target_path.setter
    def target_path(self, targetpath):
        if not isinstance(targetpath, str):
            raise ValueError('Targetpath must be string.')
        if len(targetpath) == 0:
            raise ValueError('Targetpath can not be empty.')
        self.targetPath = targetpath
    def write_result(self, str, address):
        with open(address, 'a', encoding='utf-8') as f:
            f.writelines(str + '\n')
        print('Write successully')
    def read(self):
        new_file = []
        files = os.listdir(self.readPath)
        for file in files:
            f = open(self.readPath + '/' + file, 'rb')
            iter_f = iter(f)
            str_head = ''
            for line in iter_f:
                head = line.decode().partition('00> ')
                str_head = head[2].replace(' ', '')
                lis = []
                for i in range(len(str_head)):
                    lis.append(str_head[i] + ' ')
                new = ''.join(lis)
            sentence = '%s(./data/{file[:-3]}wav)' % new
            f.close()
            address = self.targetPath
            self.write_result(sentence, address)
        print('Success')
