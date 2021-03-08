# --encoding:utf-8 --

import requests
import login
import json
import driver
import test_page


main_json = driver.get_json_data("./Page_object/main_url.json")


class Zendao_Main():
    def __init__(self, account, password, network_pre):
        self.account = account
        self.password = password
        self.network_pre = network_pre
        self.resquest_session = login.login_out(self.account, self.password, self.network_pre)

    def goto_mypage(self):
        # 登陆后进入禅道个人主页
        # urlout_my = 'http://bugfree.3nod.com.cn:9000/zentao/my/'    # 禅道个人主页url
        urlout_my = self.network_pre + main_json["my"]["url"]
        print(urlout_my)
        response_my = self.resquest_session.get(urlout_my)  # 获取个人主页信息
        # 因为responsein.content返回的是list，所以需要通过json去解码返回值中的中文
        # data_project = json.dumps(responsein.content, encoding="utf-8", ensure_ascii=False) # python 2.7写法
        data_my = json.dumps(response_my.content.decode('utf-8'), ensure_ascii=False)
        # urlout_project = 'http://bugfree.3nod.com.cn:9000/zentao/project-index-no.html'
        urlout_project = self.network_pre + main_json["product"]["url"]
        response_project = self.resquest_session.get(urlout_project)  # 获取个人主页信息
        # data_project = json.dumps(response_project.content, encoding="utf-8", ensure_ascii=False) # python 2.7写法
        data_project = json.dumps(response_project.content.decode('utf-8'), ensure_ascii=False)  # python 3.6写法
        print(data_project)

    def test(self):
        test = test_page.TestPage(self.resquest_session, self.network_pre)
        test.get_all_bugs_info(productid="152", second_id='0')
        # test.get_bug_info() 301

if __name__ == "__main__":
    # account = input("请输入用户名： ")
    # password = input("请输入密码： ")
    network_mode = input("请选择网络类型：1.内网 2.外网 \n")
    account = 'cheng.long'
    password = 'QWER123456'
    if network_mode == '1':
        network_pre = "http://192.168.80.2:9000"
    elif network_mode == '2':
        network_pre = "http://bugfree.3nod.com.cn:9000"
    zendao = Zendao_Main(account=account, password=password, network_pre=network_pre)
    zendao.test()
