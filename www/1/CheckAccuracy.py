#!/usr/bin/python
# -*- coding:utf8 -*-
import os
class CheckAccuracy(object):
    def __init__(self, name, label_address, result_address):
        self.name = name
        self.label_address = label_address
        self.result_address = result_address
    def process(self):
        file_list = []
        file_list.append(self.result_address + 'result_Baidu.txt')
        file_list.append(self.result_address + 'result_Tencent.txt')
        file_list.append(self.result_address + 'result_Xunfei.txt')
        file_list.append(self.result_address + 'result_Aliyun.txt')
        for file_name in file_list:
            if os.path.exists(file_name):
                os.remove(file_name)
        def write(string, address):
            with open(address, 'a', encoding='GBK') as f:
                f.writelines(string + '\n')
        if self.name == 'Baidu':
            with open('%s/test_data_Baidu.txt' % self.result_address, 'rb') as f:
                lines = f.readlines()
                for line in lines:
                    string = line.decode().strip()
                    write(string, '%s/result_Baidu.txt' % self.result_address)
        elif self.name == 'Tencent':
            with open('%s/test_data_Tencent.txt' % self.result_address, 'rb') as f:
                lines = f.readlines()
                for line in lines:
                    string = line.decode().strip()
                    write(string, '%s/result_Tencent.txt' % self.result_address)
        elif self.name == 'Xunfei':
            with open('%s/test_data_Xunfei.txt' % self.result_address, 'rb') as f:
                lines = f.readlines()
                for line in lines:
                    string = line.decode().strip()
                    write(string, '%s/result_Xunfei.txt' % self.result_address)
        else:
            with open('%s/test_data_Aliyun.txt' % self.result_address, 'rb') as f:
                lines = f.readlines()
                for line in lines:
                    string = line.decode().strip()
                    write(string, '%s/result_Aliyun.txt' % self.result_address)

        if self.name == 'Baidu':
            os.system('./sctk-2.4.10/bin/sclite -r %s/label.txt -h %s/result_Baidu.txt -i wsj -e gb -w unity  -o all  -O %s/' % (self.label_address, self.result_address, self.result_address))
            os.system('./sctk-2.4.10/bin/sclite -r %s/label.txt -h %s/result_Baidu.txt -i wsj -e gb -w unity  -o dtl  -O %s/' % (self.label_address, self.result_address, self.result_address))
        elif self.name == 'Tencent':
            os.system('./sctk-2.4.10/bin/sclite -r %s/label.txt -h %s/result_Tencent.txt -i wsj -e gb -w unity  -o all  -O %s/' % (self.label_address, self.result_address, self.result_address))
            os.system('./sctk-2.4.10/bin/sclite -r %s/label.txt -h %s/result_Tencent.txt -i wsj -e gb -w unity  -o dtl  -O %s/' % (self.label_address, self.result_address, self.result_address))
        elif self.name == 'Xunfei':
            os.system('./sctk-2.4.10/bin/sclite -r %s/label.txt -h %s/result_Xunfei.txt -i wsj -e gb -w unity  -o all  -O %s/' % (self.label_address, self.result_address, self.result_address))
            os.system('./sctk-2.4.10/bin/sclite -r %s/label.txt -h %s/result_Xunfei.txt -i wsj -e gb -w unity  -o dtl  -O %s/' % (self.label_address, self.result_address, self.result_address))
        else:
            os.system('./sctk-2.4.10/bin/sclite -r %s/label.txt -h %s/result_Aliyun.txt -i wsj -e gb -w unity  -o all  -O %s/' % (self.label_address, self.result_address, self.result_address))
            os.system('./sctk-2.4.10/bin/sclite -r %s/label.txt -h %s/result_Aliyun.txt -i wsj -e gb -w unity  -o dtl  -O %s/' % (self.label_address, self.result_address, self.result_address))
        print('Finished, you can check accuracy in tmp file!')
