# -- encoding:utf-8 --

import driver
from lxml import etree
from bs4 import BeautifulSoup
import re

main_url = driver.get_json_data("./Page_object/main_url.json")


class TestPage():
    def __init__(self, request_session, network_pre):
        self.request_session = request_session
        self.network_pre = network_pre
        self.project_list = []
        self.qa_response = self.goto_qa_page()

    def goto_qa_page(self):
        print("进入测试目录...")
        url = self.network_pre + main_url.get("qa").get("url")
        print("url: ", url)
        response = self.request_session.get(url)
        return response

    def get_project_info(self):
        """
        获取所有项目信息（项目id, 项目名，项目URL）
        :return:None
        """
        productid = ''
        url = ''
        productname = ''
        soup = BeautifulSoup(self.qa_response.text, 'lxml')
        navs = soup.find_all(class_="nav nav-stacked nav-secondary")
        for nav in navs:
            for tmp in nav:
                productid_re = re.match('^<li(.*?)productid="(.*?)">', str(tmp))
                if productid_re:
                    productid = productid_re.group(2)
                    url = self.network_pre + "/zentao/bug-browse-" + productid + ".html"
                productname_re = re.search('<a(.*?):;" title="(.*?)">(.*?)</a>', str(tmp))
                if productname_re:
                    productname = productname_re.group(3)
                    productname_dic = {
                        "name": productname,
                        "id": productid,
                        "url": url
                    }
                    self.project_list.append(productname_dic)
        # print(self.project_list)

    def get_bug_info(self, url):
        """
        获取单一bug的所有信息（ID，标题，内容，历史记录，基本信息）,并以字典形式存储返回。
        :param url:BUG链接
        :return:bug_info_dic
        """
        # url = "http://bugfree.3nod.com.cn:9000/zentao/bug-view-17578.html"
        data = self.request_session.get(url).text
        soup_page = BeautifulSoup(data, 'lxml')
        product = modle = bug_type = activation_num = activation_data = check_status = now_status = ''
        severity = priority = bug_status = ''
        # 获取BUG ID和标题
        for tmp in soup_page.findAll(class_="page-title"):
            text = tmp.get_text().encode('iso-8859-1').decode('utf-8')
        bug_id = text.split()[0]                    # BUG ID
        bug_title = text.split()[1]                 # BUG标题
        # 获取BUG内容
        for tmp2 in soup_page.findAll(class_="detail-content article-content"):
            bug_content = tmp2.get_text().encode('iso-8859-1').decode('utf-8', errors="ignore").split()  # BUG内容
        # 获取BUG"历史记录"
        for tmp3 in soup_page.findAll(class_="histories-list"):
            history_info_text = tmp3.get_text().encode('iso-8859-1').decode('utf-8', errors="ignore")  # 历史记录内容
            history_info = history_info_text.replace("\n\n", '\n').replace("  ", '')
        # 获取BUG"基本信息"中的数据
        for tmp4 in soup_page.find(class_="table table-data"):
            text4 = tmp4.encode('iso-8859-1').decode('utf-8', errors="ignore")
            if text4 != '':
                product_modele = re.findall(".*>(.*?)</a>", text4)
                if product_modele:
                    product = product_modele[0]     # 所属项目
                    try:
                        modle = product_modele[1]       # 所属模块s
                    except:
                        product = "None"
                all_td = re.findall("<td>(.*?)</td>", text4)
                if all_td:
                    bug_type = all_td[1]            # BUG类型
                    activation_num = all_td[4]      # 激活次数
                    activation_data = all_td[5]     # 激活日期
                    check_status = all_td[6]        # 是否确认（确认状态）
                    now_status = all_td[7]          # 当前指派（当前状态）
                all_span = re.findall("<span.*>(.*?)</span>", text4)
                if all_span:
                    severity = all_span[0]          # BUG严重程度
                    priority = all_span[1]          # 优先级
                    bug_status = all_span[2]        # BUG状态
        bug_info_dic = {
            "bug_id": bug_id,
            "bug_title": bug_title,
            "bug_content": bug_content,
            "history_info": history_info,
            "product": product,
            "modle": modle,
            "bug_type": bug_type,
            "severity": severity,
            "priority": priority,
            "bug_status": bug_status,
            "activation_num": activation_num,
            "check_status": check_status,
            "activation_data": activation_data,
            "now_status": now_status
        }
        # print(bug_info_dic)
        return bug_info_dic

    def get_bug_id_url(self, data):
        """
        获取当前页面所有bug的bug id和bug url，并以字典形式存储。例如：bug_info={"bug_id":"1111","bug_url":"xxx"}
        :data: 当前页面的解析数据，为str类型。例如：data = request.get(url).text
        :return:bug_info_list
        """
        bug_info_list = []
        soup = BeautifulSoup(data, "lxml")
        tbody = soup.select("#bugList > tbody")
        for tag in tbody:
            # 获取bug id以及bug url
            bugids = tag.findAll("input", {"type": "checkbox"})  # 筛选定位
            for bugid in bugids:
                bugid = bugid.get('value')  # 获取bug id的值
                if bugid:
                    bugid_encode = bugid.encode('iso-8859-1').decode('utf-8')
                    urls = 'http://bugfree.3nod.com.cn:9000/zentao/bug-view-' + bugid_encode + '.html'  # 每个bug对应的url
                    bug_info = {
                        "id": bugid_encode,
                        "url": urls
                    }
                    # print(bugid, urls)
                    bug_info_list.append(bug_info)
        return bug_info_list

    def get_all_bugpage_url(self, data):
        """
        获取一共有多少页bug,并将每页的URL进行拼接存储在列表all_page_url_list[]中
        :data: 当前页面的解析数据，为str类型。例如：data = request.get(url).text
        :return: all_page_url_list[]
        """
        all_page_url_list = []
        soup_page = BeautifulSoup(data, 'lxml')
        # data-link-creator= /zentao/bug-browse-301-0-all-0--122-{recPerPage}-{page}.html
        for tmp in soup_page.findAll(class_="pager"):
            data_rec_total = tmp.get("data-rec-total")  # 当前总BUG数
            data_rec_per_page = tmp.get("data-rec-per-page")  # 当前页面显示的最大bug数
            data_page = tmp.get("data-page")  # 当前处于第几页
            # 获取当前页面URL组成并替换相应值：/zentao/bug-browse-301-0-all-0--122-{recPerPage}-{page}.html
            data_link_recPerPage = tmp.get("data-link-creator").replace("{recPerPage}", data_rec_total)
            data_link_creator = data_link_recPerPage.replace("{page}", data_page)
            url = self.network_pre + data_link_creator  # 拼接URL
            page_nums = int(data_rec_total) // int(data_rec_per_page) + 1  # 获取总页面数
            # 循环遍历所有页数
            for i in range(1, page_nums + 1):
                new_link_creator = data_link_recPerPage.replace("{page}", str(i))
                new_url = self.network_pre + new_link_creator
                all_page_url_list.append(new_url)
        # print(all_page_url_list)
        return all_page_url_list

    def get_all_bugs_info(self, productid, second_id='0'):
        """
        获取"所有"中的所有BUG
        :productid:项目ID，str类型
        :second_id:部分项目有两级目录，该id为第二级目录ID。例如：/zentao/bug-browse-287-122.html中的second_id为"122"，该ID默认为0
        :return:None
        """
        # http://bugfree.3nod.com.cn:9000/zentao/bug-browse-301-0-all.html
        url = "/zentao/bug-browse-{}-{}-all.html".format(productid, second_id)
        url_pre = self.network_pre + url
        data = self.request_session.get(url_pre).text
        all_page_url_list = self.get_all_bugpage_url(data)
        print(all_page_url_list)
        page_url = all_page_url_list[0]     # 只需要根据第一个页面即可获取该项目的所有BUG，故只需要第一页的URL
        response = self.request_session.get(page_url).text
        bug_info_list = self.get_bug_id_url(response)
        print(len(bug_info_list))
        for one_bug_info in bug_info_list:
            bug_id = one_bug_info.get("id")
            bug_url = one_bug_info.get("url")
            print(bug_id, bug_url)

    def get_unclosebug_url(self):
        """
        获取未关闭BUG的URL
        :return:
        """
        # http://bugfree.3nod.com.cn:9000/zentao/bug-browse-301-0-unclosed.html

        pass

    def get_unclosed_buginfo(self):
        """
        获取未关闭bug信息
        :return:
        """


def test():
    network_pre = "http://bugfree.3nod.com.cn:9000"
    # http://bugfree.3nod.com.cn:9000/zentao/bug-browse-301-0-bymodule-0-assignedTo_asc-87-35.html
    data = driver.read_file("./qa.text")
    all_page_url_list = []
    soup_page = BeautifulSoup(data, 'lxml')
    product = modle = bug_type = activation_num = activation_data = check_status = now_status = ''
    severity = priority = bug_status = ''
    # 获取BUG ID和标题
    for tmp in soup_page.findAll(class_="page-title"):
        text = tmp.get_text().encode('iso-8859-1').decode('utf-8')
    bug_id = text.split()[0]    # BUG ID
    bug_title = text.split()[1]    # BUG标题
    # 获取BUG内容
    for tmp2 in soup_page.findAll(class_="detail-content article-content"):
        bug_content = tmp2.get_text().encode('iso-8859-1').decode('utf-8', errors="ignore").split()     # BUG内容
    # 获取BUG"历史记录"
    for tmp3 in soup_page.findAll(class_="histories-list"):
        history_info_text = tmp3.get_text().encode('iso-8859-1').decode('utf-8', errors="ignore")    # 历史记录内容
        history_info = history_info_text.replace("\n\n", '\n').replace("  ", '')
        # print(history_info)
    # 获取BUG"基本信息"
    for tmp4 in soup_page.find(class_="table table-data"):
        text4 = tmp4.encode('iso-8859-1').decode('utf-8', errors="ignore")
        # print(text4)
        if text4 != '':
            product_modele = re.findall(".*>(.*?)</a>", text4)
            if product_modele:
                product = product_modele[0]     # 所属项目
                modle = product_modele[1]       # 所属模块s
            all_td = re.findall("<td>(.*?)</td>", text4)
            # print(all_td)
            if all_td:
                bug_type = all_td[1]    # BUG类型
                activation_num = all_td[4]    # 激活次数
                activation_data = all_td[5]     # 激活日期
                check_status = all_td[6]        # 是否确认（确认状态）
                now_status = all_td[7]          # 当前指派（当前状态）
            all_span = re.findall("<span.*>(.*?)</span>", text4)
            if all_span:
                severity = all_span[0]      # BUG严重程度
                priority = all_span[1]      # 优先级
                bug_status = all_span[2]    # BUG状态
    bug_info_dic = {
        "bug_id": bug_id,
        "bug_title": bug_title,
        "bug_content": bug_content,
        "history_info": history_info,
        "product": product,
        "modle": modle,
        "bug_type": bug_type,
        "severity": severity,
        "priority": priority,
        "bug_status": bug_status,
        "activation_num": activation_num,
        "check_status": check_status,
        "activation_data": activation_data,
        "now_status": now_status
    }
    # print(bug_info_dic)
    return bug_info_dic


test()

