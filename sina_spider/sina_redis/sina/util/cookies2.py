import json
import time
import base64
import rsa
import math
import random
import binascii
import requests
import re
from urllib.parse import quote_plus
from verify import code_verificate
from fake_useragent import UserAgent

accountPwdPool = [
    {'user': '13113121202', 'pwd': '12321hjz'},
    # {'user': '0066970202729', 'pwd': 'bingo520'},
    # {'user': '0013203357052', 'pwd': 'fa331595'},
    # {'user': '0013203357079', 'pwd': 'fa237181'},
    # {'user': '0013203357201', 'pwd': 'fa652193'},
    # {'user': '0013203357286', 'pwd': 'fa848138'},
]

headers = {
    'User-Agent': UserAgent().random
}
session = requests.session()

# 访问 初始页面带上 cookie
index_url = "http://weibo.com/login.php"
yundama_username = 'Hjz59'
yundama_password = '12321hjz'
verify_code_path = './pincode.png'

cookies = []

def get_pincode_url(pcid):
    size = 0
    url = "http://login.sina.com.cn/cgi/pin.php"
    pincode_url = '{}?r={}&s={}&p={}'.format(url, math.floor(random.random() * 100000000), size, pcid)
    return pincode_url


def get_img(url):
    resp = requests.get(url, headers=headers, stream=True)
    with open(verify_code_path, 'wb') as f:
        for chunk in resp.iter_content(1000):
            f.write(chunk)

def get_su(username):
    username_quote = quote_plus(username)
    username_base64 = base64.b64encode(username_quote.encode("utf-8"))
    return username_base64.decode("utf-8")

# 预登陆获得 servertime, nonce, pubkey, rsakv
def get_server_data(su):
    pre_url = "http://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su="
    pre_url = pre_url + su + "&rsakt=mod&checkpin=1&client=ssologin.js(v1.4.18)&_="
    prelogin_url = pre_url + str(int(time.time() * 1000))
    pre_data_res = session.get(prelogin_url, headers=headers)
    sever_data = eval(pre_data_res.content.decode("utf-8").replace("sinaSSOController.preloginCallBack", ''))
    return sever_data

# 这一段用户加密密码，需要参考加密文件
def get_password(password, servertime, nonce, pubkey):
    rsaPublickey = int(pubkey, 16)
    key = rsa.PublicKey(rsaPublickey, 65537)  # 创建公钥,
    message = str(servertime) + '\t' + str(nonce) + '\n' + str(password)  # 拼接明文js加密文件中得到
    message = message.encode("utf-8")
    passwd = rsa.encrypt(message, key)  # 加密
    passwd = binascii.b2a_hex(passwd)  # 将加密信息转换为16进制。
    return passwd

def login(accountPwds):
    # su 是加密后的用户名
    for i in accountPwds:
        # try:
        username = i['user']
        password = i['pwd']
        su = get_su(username)
        sever_data = get_server_data(su)
        servertime = sever_data["servertime"]
        nonce = sever_data['nonce']
        rsakv = sever_data["rsakv"]
        pubkey = sever_data["pubkey"]
        password_secret = get_password(password, servertime, nonce, pubkey)

        postdata = {
            'entry': 'weibo',
            'gateway': '1',
            'from': '',
            'savestate': '7',
            'useticket': '1',
            'pagerefer': "http://login.sina.com.cn/sso/logout.php?entry=miniblog&r=http%3A%2F%2Fweibo.com%2Flogout.php%3Fbackurl",
            'vsnf': '1',
            'su': su,
            'service': 'miniblog',
            'servertime': servertime,
            'nonce': nonce,
            'pwencode': 'rsa2',
            'rsakv': rsakv,
            'sp': password_secret,
            'sr': '1920*1080',
            'encoding': 'UTF-8',
            'prelt': '115',
            'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
            'returntype': 'META'
            }

        need_pin = sever_data['showpin']
        if need_pin == 1:
            # 你也可以改为手动填写验证码
            if not yundama_username:
                raise Exception('由于本次登录需要验证码，请配置顶部位置云打码的用户名{}和及相关密码'.format(yundama_username))
            pcid = sever_data['pcid']
            postdata['pcid'] = pcid
            img_url = get_pincode_url(pcid)
            get_img(img_url)
            verify_code = code_verificate(yundama_username, yundama_password, verify_code_path)
            postdata['door'] = verify_code

        login_url = 'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.18)'
        login_page = session.post(login_url, data=postdata, headers=headers, verify=False)
        login_loop = (login_page.content.decode("GBK"))
        pa = r'location\.replace\([\'"](.*?)[\'"]\)'
        loop_url = re.findall(pa, login_loop)[0]
        login_index = session.get(loop_url, headers=headers, verify=False)
        uuid = login_index.text
        uuid_pa = r'"uniqueid":"(.*?)"'
        uuid_res = re.findall(uuid_pa, uuid, re.S)[0]
        web_weibo_url = "http://weibo.com/%s/profile?topnav=1&wvr=6&is_all=1" % uuid_res
        weibo_page = session.get(web_weibo_url, headers=headers, verify=False)
        weibo_pa = r'<title>(.*?)</title>'
        user_name = re.findall(weibo_pa, weibo_page.content.decode("utf-8", 'ignore'), re.S)[0]
        print('登陆成功，你的用户名为：' + user_name)
        # print(weibo_page.content.decode('utf8'))
        cookie = session.cookies.get_dict()
        cookies.append(cookie)
    return cookies

cookies = login(accountPwdPool)

