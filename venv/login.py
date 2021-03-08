#-- coding:UTF-8 --

import requests
from lxml import html
import hashlib
from bs4 import BeautifulSoup
import json


def login_out(account, password, netword_pre):
    """
    局域网登陆url
    urlout = "http://192.168.80.2:9000/zentao/"
    外网登陆url
    urlout = 'http://bugfree.3nod.com.cn:9000/zentao/'

    打开登陆页面的时候页面产生一个zentaosid的唯一标识，以及一个verifyRand随机值
    对输入的密码进行md5加密
    已经加密的密码+verifyRand再一次md5加密
    然后post请求登陆地址根据唯一的zentaosid验密
    :param account: 账号
    :param password: 密码
    :return: 登陆成功后的session
    """
    print("开始登陆禅道")
    # urlout = "http://bugfree.3nod.com.cn:9000/zentao/user-login.html"
    urlout = netword_pre + "/zentao/user-login.html"
    response = requests.Session()
    loginpage = response.get(urlout)
    SID = loginpage.cookies['zentaosid']    # 获取zentaosid的唯一标识
    # 获取Referer的值
    loginTree = html.fromstring(loginpage.text)
    verifyRand = loginTree.xpath('//*[@id="verifyRand"]')
    if verifyRand:
        verifyRand = verifyRand[0].attrib['value']
    # 对输入的密码进行md5加密
    hl = hashlib.md5()      # MD5第一次加密
    hl.update(password.encode(encoding='utf-8'))
    passwordResult = hl.hexdigest() + verifyRand
    hlLast = hashlib.md5()      # MD5第二次加密
    hlLast.update(passwordResult.encode(encoding='utf-8'))
    # 需要post的数据
    postdata = {
        "account": account,
        "password": hlLast.hexdigest(),
        "referer":  netword_pre + "/zentao/user-login.html",
        "verifyRand": verifyRand,
    }
    # header头部信息
    header = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Referer': 'http://bugfree.3nod.com.cn:9000/zentao/user-login-L3plbnRhby8=.html',
    }
    # 将数据post上去，进行登陆
    requestslogin = response.post(urlout, data=postdata, headers=header)
    # 判断是否登陆成功
    if "parent.location='/zentao/index.html" in requestslogin.text:
        print("----登陆成功！！----")
        return response
    else:
        print("----登陆失败！！----")

