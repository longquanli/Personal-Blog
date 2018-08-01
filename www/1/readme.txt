1.脚本用于借用腾讯百度讯飞ASR语音识别技术识别<60s音频文件，并生成准确率相关报告
2.语音识别 Python SDK 格式目录：

├── README.md
├── http.py		           		    //http请求
├── IOProcess.py                   //读写数据处理
├── RespondDataProcess.py         //识别信息处理
├── setup.py                     //脚本文件 python3 Setup.py
├── CheckAccuracy.py            //运行sclite正确率报告软件
├── config.txt		           //要求填写用户相关信息
├── result_Name.txt           //脚本运行后自动生成的Name家GBK文件，用于正确率验证
├── label.txt                //人为标注文本，用户需自行转成GBK文件
├── wav_test		        //音频文件存放地址
└── sctk-2.4.10            //sclite软件
3.config.txt格式：
Baidu:
name=>Baidu
APP_ID=>11403433
API_KEY=>6YVnHLgTThHGREER9angUwYY
SECRET_KEY=>Vz7OkHfb55iD5g07sG40MY2QjtrSvZco
AUDIO_ADDRESS=>
target_address=>
label_address=>
Tencent:
name=>Tencent
SECRET_KEY=>wuneLtFRRFqJafYFn9JNGxSo0JTREqJf
SECRET_ID=>AKIDQlv18IVgx64qSyfSbYJugJk6TsAG36jP
AUDIO_ADDRESS=>
target_address=>
label_address=>
Xunfei:
APP_id=5b20dc20
APP_key=>1baf33ce3d7b26ee67dce7674804e418
AUDIO_ADDRESS=>
target_address=>
label_address=>
Aliyun:
name=>Aliyun
KEY_ID=>'LTAItu7ThdeOnE6l'
KEY_SECRET=>'DWwdiyP77gJtUKr5ndf2Y59RRPBXOU'
AUDIO_ADDRESS=>
target_address=>
label_address=>

4.脚本运行生成的语音识别文件存放在target_address目录下，utf-8
5.用户需要先授权sclite文件。 在 ./sctk-2.4.10/bin 目录下执行 chomd +x sclite
6.xun fei needs add ip into control desk
