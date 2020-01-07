import threading
import queue
import requests
import time
import random
import re
import pymysql
from pyquery import PyQuery as pq
from lxml import etree

from getTrainNumber import chooseMethon
from autoScrapy import siteMovieData

lock = threading.Lock()


class Db(object):
    def __init__(self, host='localhost', username='root', pwd='123456', dbname='calen'):
        self.pool = {}
        self.host = host
        self.username = username
        self.pwd = pwd
        self.dbname = dbname

    def get_instance(self, ):
        name = threading.current_thread().name
        if name not in self.pool:
            conn = pymysql.connect(self.host, self.username, self.pwd, self.dbname)
            self.pool[name] = conn
        return self.pool[name]


class Parse(threading.Thread):
    def __init__(self, number, data_list, req_thread):
        super(Parse, self).__init__()
        self.number = number  # 线程编号
        self.data_list = data_list  # 数据队列
        self.req_thread = req_thread  # 请求队列，为了判断采集线程存活状态
        self.is_parse = True  # 判断是否从队列中提取数据
        self.db = Db()  # 插入的数据库
        self.dataList = []

    def run(self):
        print('启动%d号解析线程' % self.number)
        # 循环
        while True:
            # 如何判断解析线程的结束条件
            for t in self.req_thread:  # 循环所有采集线程
                if t.is_alive():  # 判断线程是否存活
                    break
            else:
                # 如何循环完毕，没有执行break语音，则进入else
                if self.data_list.qsize() == 0:
                    # 判断数据队列书否为空
                    self.is_parse = False
                    # 设置解析为 False
            # 判断是否继续解析
            if self.is_parse:  # 解析
                try:
                    data = self.data_list.get(timeout=3)  # 从数据队列里提取一个数据
                except Exception as e:  # 超时以后进入异常
                    data = None
                # 如果成功拿到数据，则调用解析方法
                if data is not None:
                    self.parse(data)  # 调用解析方法
            else:
                break # 结束while循环
        print('退出%d号解析线程' % self.number)

    # 页面解析函数
    def parse(self, data):

        m = data['response']  # 请求url的结果
        url = data['url']  # url链接

        data = chooseMethon().getMsg(url,m)

        if data:
            print(data)
            # append进去的需要是一个元祖类型数据
            # self.dataList.append(data)
            # print(len(self.dataList))
            # 批量插入数据库,数量可以自定义
            # if len(self.dataList) >= 50:
            #     self.saveData(self.dataList)
            #     self.dataList = []

    def saveData(self, dataList):
        db = self.db.get_instance()
        cursor = db.cursor()

        try:
            sql = "INSERT INTO test_data(test) VALUES(%s)"
            cursor.executemany(sql, dataList)
            db.commit()
        except:
            print("插入数据库错误")
            db.rollback()


class Crawl(threading.Thread):
    def __init__(self, number, req_list, data_list):
        # 调用Thread 父类方法
        super(Crawl, self).__init__()
        # 初始化子类属性
        self.number = number
        self.req_list = req_list
        self.data_list = data_list
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cache-Control': 'max-age=0',
            'Connection': 'close',
            'Cookie': 'TYCID=f657fa70a21311e9a0d117a6c02d6d60; undefined=f657fa70a21311e9a0d117a6c02d6d60; ssuid=9974144094; _ga=GA1.2.333871572.1562654224; bannerFlag=true; aliyungf_tc=AQAAANT5jG0Ljw4ALFFXbkdfeHGje7Qb; csrfToken=r3pMS5LT2IcFEKaVEAVsW5o9; Hm_lvt_d5ceb643638c8ee5fbf79d207b00f07e=1563427306,1563427731,1563427894,1563427914; cloud_token=6ae28ffc77264501bae3a032be519a85; _gid=GA1.2.975705087.1563761850; jsid=SEM-BAIDU-PZ1907-SY-000100; Hm_lvt_e92c8d65d92d534b0fc290df538b4758=1563771039,1563785647,1563785675,1563785700; Hm_lpvt_e92c8d65d92d534b0fc290df538b4758=1563785700; _gat_gtag_UA_123487620_1=1; Hm_lpvt_d5ceb643638c8ee5fbf79d207b00f07e=1563786077',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1',
            'Host': 'm.tianyancha.com',
            'Upgrade-Insecure-Requests': '1'
        }

    def getHtml(self, url):
        try:
            response = requests.get(url, headers=self.headers, timeout=5)
            if response.status_code == 200:
                return response.text
        except Exception:
            return None

    # 线程启动的时候调用
    def run(self):
        # 输出启动线程信息
        print('启动采集线程%d号' % self.number)
        # 如果请求队列不为空，则无限循环，从请求队列里拿请求url
        while self.req_list.qsize() > 0:
            # 从请求队列里提取url
            url = self.req_list.get()
            print('%d号线程采集：%s' % (self.number, url))
            # 防止请求频率过快，随机设置阻塞时间
            # time.sleep(random.randint(1, 2))
            # 发起http请求，获取响应内容，追加到数据队列里，等待解析
            try:
                response = siteMovieData(url).getDic()[url]
            except Exception as e:
                print(e)
                response = None
            if response:
                data = {
                    'response': response,
                    'url': url
                }
                self.data_list.put(data)  # 向数据队列里追加


def get_url(host):

    urls = chooseMethon().chooseMap(host)
    return urls


def main():
    concurrent = 8  # 采集线程数
    conparse = 8  # 解析线程数
    # 生成请求队列
    req_list = queue.Queue()
    # 生成数据队列 ，请求以后，响应内容放到数据队列里
    data_list = queue.Queue()
    # 循环生成多个请求url
    urls = get_url('http://dyw9955.com/')
    for url in urls:
        # 加入请求队列
        url = url.replace('\n', '').replace(' ', '')
        req_list.put(url)
    # 生成N个采集线程
    req_thread = []
    for i in range(concurrent):
        t = Crawl(i + 1, req_list, data_list)  # 创造线程
        t.start()
        req_thread.append(t)
    # 生成N个解析线程
    parse_thread = []
    for i in range(conparse):
        t = Parse(i + 1, data_list, req_thread)  # 创造解析线程
        t.start()
        parse_thread.append(t)
    for t in req_thread:
        t.join()
    for t in parse_thread:
        t.join()


if __name__ == "__main__":
    main()
