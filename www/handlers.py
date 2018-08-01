#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from coroweb import get, post
from models import User, Comment, Blog, next_id, Audio
import re, time, json, logging, hashlib, base64, asyncio 
import logging; logging.basicConfig(level=logging.INFO)
from apis import Page, APIValueError, APIResourceNotFoundError, APIError
from config import configs
import markdown2
from aiohttp import web
import requests
from RespondDataProcess import multiVoice 

COOKIE_NAME = 'awesession'
_COOKIE_KEY = configs.session.secret
#_COOKIE_KEY = configs['session']['secret']

def user2cookie(user, max_age):
    expires = str(int(time.time()) + max_age)
    s = '%s-%s-%s-%s' % (user.id, user.passwd, expires, _COOKIE_KEY)
    L = [user.id, expires, hashlib.sha1(s.encode('utf-8')).hexdigest()]
    return '-'.join(L)

def get_page_index(page_str):
	p = 1
	try:
		p = int(page_str)
	except ValueError as e:
		pass
	if p < 1:
		p = 1
	return p

async def cookie2user(cookie_str):
    if not cookie_str:
        return None
    try:
        L = cookie_str.split('-')
        if len(L) != 3:
            return None
        uid, expires, sha1 = L
        if float(expires) < time.time():
            return None
        user = await User.find(uid)
        if user is None:
            return None
        s = '%s-%s-%s-%s' % (uid, user.passwd, expires, _COOKIE_KEY)
        if sha1 != hashlib.sha1(s.encode('utf-8')).hexdigest():
            logging.info('invalid sha1')
            return None
        user.passwd = '******'
        return user
    except Exception as e:
        logging.exception(e)
        return None
def check_admin(request):
	if request.__user__ is None or not request.__user__.admin:
		raise APIPermissionError()

#more efficient
def text2html(text):
	lines = map(lambda s: '<p>%s</p>' % s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'), 
		filter(lambda s : s.strip() != '', text.split('\n')))
	return ''.join(lines)

@get('/')  
async def index(*, page='1'):  
    page_index = get_page_index(page)
    num = await Blog.findNumber('count(id)')
    page = Page(num, page_index)
    if num == 0:
    	blogs = []
    else:
    	blogs = await Blog.findAll(orderBy='created_at desc', limit=(page.offset, page.limit))
    return {
    	'__template__' : 'blogs.html',
    	'blogs' : blogs,
        'page' : page
    }

@get('/register')
def register():
    return {
        '__template__': 'register.html'
    }

@get('/signin')
def signin():
    return {
        '__template__': 'signin.html'
    }

@post('/api/authenticate')
async def authenticate(*, email, passwd):
    if not email:
        raise APIValueError('email', 'Invalid email.')
    if not passwd:
        raise APIValueError('Passwd', 'Invalid password.')
    users = await User.findAll('email=?', [email])
    if len(users) == 0:
        raise APIValueError('email', 'Email not exist.')
    user = users[0]
    # check passwd
    sha1 = hashlib.sha1()
    sha1.update(user.id.encode())
    sha1.update(b':')
    sha1.update(passwd.encode())
    if user.passwd != sha1.hexdigest():
        raise APIValueError('passwd', 'Invalid passwd.')
    # success, create cookie
    r = web.Response()
    r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age=86400, httponly=True)
    user.passwd = '******'
    r.content_type = 'application/json'
    # make json string
    r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
    return r
#Directly go back to the previous page or home page.
@get('/signout')
def signout(request):
    # referer parameter tells about the previous link to this place
    referer = request.headers.get('Referer')
    r = web.HTTPFound(referer or '/')
    r.set_cookie(COOKIE_NAME, '-deleted-', max_age=0, httponly=True)
    logging.info('user signed out.')
    return r

_RE_EMAIL = re.compile(r'^[a-z0-9\.\-\_]+\@[a-z0-9\-\_]+(\.[a-z0-9\-\_]+){1,4}$')
_RE_PASSWD = re.compile(r'^[\w\.]{40}')

#make user login api
@post('/api/users')
async def api_post_users(*, email, name, passwd):
    if not name or not name.strip():
        raise APIValueError('name')
    #match() check from the first one character.
    if not email or not _RE_EMAIL.match(email):
        raise APIValueError('email')
    if not passwd or not _RE_PASSWD.match(passwd):
        raise APIValueError('passwd')
    users = await User.findAll('email=?', [email])
    if len(users) > 0:
        raise APIError('register: failed', 'email', 'Email is already in use, please try again.')
    uid = next_id()
    sha1_passwd = '%s:%s' %(uid, passwd)
    user = User(id=uid, name=name.strip(), email=email, passwd=hashlib.sha1(sha1_passwd.encode('utf-8')).hexdigest(), image='https://videoll.oss-cn-shenzhen.aliyuncs.com/ea88ff5a130bfcb56abbe2a8ca660799.jpg')
    await user.save()
    #make a session cookie
    r = web.Response()
    #Js can not read cookie information when httponly = True, avoid xss attact.
    r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age=86400, httponly=True)
    #shield password
    user.passwd = '*******'
    r.content_type = 'application/json'
    r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
    #can add a successful page
    return r
@get('/api/users')
async def api_get_users(*, page='1'):
	page_index = get_page_index(page)
	num = await User.findNumber('count(id)')
	p = Page(num, page_index)
	if num == 0:
		return dict(page=p, users=())
	users = await User.findAll(orderBy='created_at desc', limit=(p.offset, p.limit))
	for user in users:
		user.passwd = '*******'
	return dict(page=p, users=users)

@get('/manage/')
def manage():
	return 'redirect:/manage/comments'

@get('/manage/comments')
def manage_comments(*, page='1'):
	return {
		'__template__': 'manage_comments.html',
		'page_index' : get_page_index(page)
	}

@get('/api/comments')
async def api_comments(*, page='1'):
	page_index = get_page_index(page)
	num = await Comment.findNumber('count(id)')
	p = Page(num, page_index)
	if num == 0:
		return dict(page=p, comments=())
	comments = await Comment.findAll(orderBy='created_at desc', limit=(p.offset, p.limit))
	return dict(page=p, comments=comments)

@post('/api/blogs')
async def api_create_blog(request, *, name, summary, content):
	check_admin(request)
	if not name or not name.strip():
	    raise APIValueError('name', 'name cannot be empty.')
	if not summary or not summary.strip():
	    raise APIValueError('summary', 'summary cannot be empty.')
	if not content or not content.strip():
	    raise APIValueError('content', 'content cannot be empty.')
	blog = Blog(user_id=request.__user__.id, user_name=request.__user__.name, user_image=request.__user__.image, name=name.strip(), summary=summary.strip(), content=content.strip())
	await blog.save()
	return blog

@post('/api/blogs_edit')
async def api_update_blog(request, *, name, summary, content, id, created_at):
	check_admin(request)
	if not name or not name.strip():
		raise APIValueError('name', 'name cannot be empty.')
	if not summary or not summary.strip():
		raise APIValueError('summary', 'summary cannot be empty')
	if not content or not content.strip():
		raise APIValueError('content', 'content cannot be empty')
	blog = Blog(user_id =request.__user__.id, user_name=request.__user__.name, 
			user_image=request.__user__.image, name=name.strip(), summary=summary.strip(), content=content.strip(), created_at=created_at, id=id)
	await blog.update()
	return blog

#Show blogs list, the blogs data are picked from database using findAll  
@get('/api/blogs')
async def api_blogs(*, page='1'):
	page_index = get_page_index(page)
	num = await Blog.findNumber('count(id)')
	p = Page(num, page_index)
	if num == 0:
		return dict(page=p, blogs=())
	blogs = await Blog.findAll(orderBy='created_at desc', limit=(p.offset, p.limit))
	return dict(page=p, blogs=blogs)

@get('/api/blogs/{id}')
async def api_get_blog(*, id):
	blog = await Blog.find(id)
	return blog

@get('/manage/blogs')
def manage_blogs(*, page='1'):
	return {
		'__template__': 'manage_blogs.html',
		'page_index': get_page_index(page)
	}

@get('/manage/blogs/create')
def manage_create_blog():
	return {
		'__template__' : 'manage_blog_edit.html',
		'id' : '',
		'action' : '/api/blogs'
	}

@get('/manage/blogs/edit/{id}')
def manage_edit_blog(*, id):
	return {
		'__template__' : 'manage_blog_edit.html',
		'id' : id,
		'action' : '/api/blogs_edit'
	}

@get('/manage/users')
def manage_users(*, page='1'):
	return {
		'__template__': 'manage_users.html',
		'page_index': get_page_index(page)
	}

@post('/api/comments/{id}/delete')
async def delete_comments(id, request):
	check_admin(request)
	comment = await Comment.find(id)
	if comment is None:
		raise APIResourceNotFoundError('Comment')
	await comment.remove()
	return dict(id=id)

@get('/blog/{id}')
async def get_blog(id):
	blog = await Blog.find(id)
	comments = await Comment.findAll('blog_id=?', [id], orderBy='created_at desc')
	for comment in comments:
		comment.html_content = text2html(comment.content)
	blog.html_content = markdown2.markdown(blog.content)
	return {
		'__template__' : 'blog.html',
		'blog' : blog,
		'comments' : comments
	}

@post('/api/blogs/{id}/delete')
async def delete2(id):
    blog = await Blog.find(id)
    await blog.remove()
    return blog

@post('/api/blogs/{id}/comments')
async def store_comments(request, *, id, content):
	comment = Comment(blog_id=id, user_id =request.__user__.id, user_name=request.__user__.name, user_image=request.__user__.image, content=content)
	await comment.save()
	return comment

#API for ASR
@get('/api/audios')
async def api_audios(request, *, page='1'):
    page_index = get_page_index(page)
    num = 0
    try:
        name = request.__user__.name
        num = await Audio.findNumber('count(id)', where="user_name='%s'" % (name))
        p = Page(num, page_index)
    except:
        p = Page(1, page_index)
    if not num:
        return dict(page=p, audios=())
    audios = await Audio.findAll(orderBy='created_at desc', where="user_name='%s'" % (name), limit=(p.offset, p.limit))
    return dict(page=p, audios=audios)

@get('/management/audios')
def manage_audios(request, *, page='1'):
    return {
        '__template__': 'manage_audios.html',
        'page_index': get_page_index(page)
    }

@get('/api/oneSentenceRecognition/addInfo')
def add_info():
    return {
        '__template__' : 'audioInfo.html'
    }

#store in db
#Get an error with 200 for a long time, because this does't need return type, but I initialized ajax with json return type. 
#So since I always initialize ajax with return type, json. I need to return json type everytime.
@post('/api/oneSentenceRecognition/processData')
async def process_data(request, *, name, url):
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
    SECRET_KEY = config_dict['SECRET_KEY']
    SECRET_ID = config_dict['SECRET_ID']
    AUDIO_ADDRESS = url
    #地址为要写入的地址文件夹
    multi = multiVoice('./result')
    #三个参量， 第一个为音频文件夹目录，第二个为腾讯云SecreteKey, 第三个是腾讯云SecreteId
    multi.ProcessTencentInit(url, SECRET_KEY, SECRET_ID)
    content = []
    try: 
        with open('./result/test_data_Tencent.txt', 'rb') as f:
            lines = f.readlines()
            content = lines[-1].decode().strip()
    except:
        raise APIValueError('url', 'url is invalid.')
    audio = Audio(user_name=request.__user__.name, audio_name=name, content=content, url=url)
    await audio.save()
    return audio

@get('/api/audio/{id}')
async def check_result(id):
    audio = await Audio.find(id)
    return {
        '__template__' : 'audioResult.html',
        'audio': audio
    }

@post('/api/audios/{id}/delete')
async def delete(id):
    audio = await Audio.find(id)
    await audio.remove()
    return audio