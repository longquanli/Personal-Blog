import base64 
import hashlib 
import hmac 
import datetime 
import ssl 
import urllib.request
import json
class Aliyun(object): 
	""" Http工具类，封装了鉴权 """ 
	def __init__(self, ak_id, ak_secret): 
		self.__ak_id = ak_id 
		self.__ak_secret = ak_secret  
	def md5_base64(self, body): 
		hash = hashlib.md5() 
		hash.update(body) # print(hash.digest()) 
		return base64.b64encode(hash.digest()).decode('utf-8') 
	def sha1_base64(self, str_to_sign, secret): 
		hmacsha1 = hmac.new(secret.encode('utf-8'), str_to_sign.encode('utf-8'), hashlib.sha1) 
		return base64.b64encode(hmacsha1.digest()).decode('utf-8') 
	def asr_rest_recognize(self, path): 
		request_url = "http://nlsapi.aliyun.com/recognize?version=2.0&model=chat" 
		audioaddress = path
		method = 'POST' 
		accept = 'application/json' 
		content_type = 'audio/pcm; samplerate=16000'
		GMT_FORMAT = '%a, %d %b %Y %H:%M:%S GMT'
		time = datetime.datetime.utcnow().strftime(GMT_FORMAT)  
		with open(audioaddress, mode='rb') as f: 
			body = f.read() 
		body_md5 = self.md5_base64(body) 
		body_md52 = self.md5_base64(bytes(body_md5, 'utf-8')) 
		sign_str = method + "\n" + accept + "\n" + body_md52 + "\n" + content_type + "\n" + time 
		signature = self.sha1_base64(sign_str, self.__ak_secret)
		auth_header = "Dataplus " + self.__ak_id + ":" + signature
		ssl._create_default_https_context = ssl._create_unverified_context 
		req = urllib.request.Request(request_url) 
		req.add_header("Accept", accept)
		req.add_header("Content-Type", content_type)
		req.add_header("Date", time)
		req.add_header("Authorization", auth_header)
		response = urllib.request.urlopen(req, body)
		result = response.read().decode("utf-8")
		return result