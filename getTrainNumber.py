from urllib.parse import urlparse
import requests
import xml.etree.ElementTree as ET
import time
import regex as re
import datetime

from urllib.request import urlopen,Request
from pyquery import PyQuery as pq
from urllib.parse import urljoin
from autoScrapy import siteMovieData
from tools import headers



class chooseMethon():
    def __init__(self):
        pass


    def getMsg(self,url,m):
        '''
        :param url: 接收一个影视url链接
        :return: 返回一个包含影片信息的字典
        '''
        # m = siteMovieData(url).getDic()[url]
        if 'title' in m.keys():
            try:
                # 清洗title中的多余信息，只保留影片名字
                try:
                    pattern = re.compile('.*《(.*?)》|(.*?) - .* - 酷云影视|(.*?) .*麦片好剧网|(.*?)[ -].*柠檬观看网|(.*?)\d+.*929电影网|(.*?)全集_.* - 66影视网|(.*?)_.* - 66影视网|(.*?) - 66影视网|(.*?) - 4K电影|(.*?)_.*天一影院|(.*?)_.*久爱电影网|-(.*?)手机在线观看-|(.*?) - 永久资源采集网|(.*?) - 最快资源采集网|(.*?)下载,|电影资源(.*?)在线播放|(.*?) - 免费完整版在线观看|(.*?)\d*_高清完整版.*-VIP电影|(.*?)全集在线观看|(.*?)\d+电影,|(.*?)电影,.*在线观看,|(.*?)电影在线观看,|(.*?)在线观看,|(.*?)-在线播放|(.*?)在线播放|(.*?)_.*_|(.*?)高清迅雷下载|(.*?)_高清完整版|(.*?)电影,|(.*?)详情介绍.*?电影在线观看|(.*?)电影在线观看|(.*?)电影高清免费|(.*?)电视剧全集免费|(.*?)详情介绍|(.*?)高清在线观看|(.*?)高清版观看|(.*?)-手机免费在线观看|(.*?)全集免费在线观看|(.*?)免费在线观看|(.*?)高清版/|(.*?)完整版在线观看|(.*?)\d+在线观看-|(.*?)在线观看|(.*?)剧情介绍|(.*?)MP4BT种子|(.*?)高清BT种子|.*\|(.*?)[(_/].*|(.*?)_.*')
                    name = pattern.findall(m['title'])[0]
                    name = [i for i in name if i != ''][0]
                    name=name.replace(' ','').replace('-','').replace('[','').replace(']','').replace('【','').replace('】','').replace('（','').replace('）','').replace('！','').replace('，','').replace('《','').replace('》','').replace('：','').replace(':','').replace('(','').replace(')','').replace('国语版','国语').replace('普通话版','国语').replace('普通话','国语').replace('英文版','英语').replace('英语版','英语').replace('Ⅰ','1').replace('Ⅱ','2').replace('Ⅲ','3').replace('Ⅳ','4').replace('Ⅴ','5').replace('Ⅵ','6').replace('Ⅶ','7').replace('Ⅷ','8').replace('Ⅸ','9').replace('Ⅹ','10')
                    name = name.split('DVD')[0].split('HD')[0]
                except Exception as reason:
                    name = m['title'][0]
                # 将电影信息保存进入字典并返回
                vodData = {}
                vodData['name'] = str(name)
                vodData['url'] = str(url)
                vodData['title'] = str(m.get('title'))
                vodData['updatetime'] = str(m.get('updatetime'))

                return vodData
            except Exception as reason:
                print('错误出现在(getTrainNumber.py)53-63行,错误原因 %s' % reason)
                return None



    def chooseMap(self,host):
        host = host.strip('/')
        try:
            lastIndex,id,tail = trainCheck(host).trainUpdateIndex()
            # urls = [id + str(i) + tail for i in range(1, lastIndex + 1)]

            for i in range(1, lastIndex + 1):
                url = id + str(i) + tail
                yield url
                # try:
                #     #获取数据
                #     vodData = self.getMsg(url)
                #
                #     if vodData is not None:
                #         # 暂时不保存入数据库
                #         print(vodData)
                #         # self.saveVodDataCache(vodData)
                # except Exception as reason:
                #     print('错误出现在(getTrainNumber.py)73-82行,错误原因 %s' % reason)
            # print('爬取完毕')
        except:
            urlList = sitemapXML(host).getSitemap()
            if len(urlList) > 0:
                # print(urlList)
                for url in urlList:
                    yield url
                    # try:
                    #     # 获取数据
                    #     vodData = self.getMsg(url)
                    #     if vodData is not None:
                    #         self.saveVodDataCache(vodData)
                    # except Exception as reason:
                    #     print('错误出现在(getTrainNumber.py)93-95行,错误原因 %s' % reason)
                map = sitemapXML(host).siteMapUrl()
            else:
                print('没有网站地图')


class trainCheck():
    def __init__(self,host):
        self.host=host.strip('/')

    def trainCheck(self):
        requestHost = Request(self.host, headers=headers)
        html = urlopen(requestHost,timeout=5).read()
        urls = [urljoin(self.host, i.attr.href) for i in pq(html)('a').items()]
        trainList = ['vod','detail', 'content','/xq/','index','/hd/','show','/m/','movie','Movie','video','view','mov','/bu/ka','/v/','/bbb/','/con_tytyh/','/c/','/html/','/d/','/taijula/','mlpdy.com']
        urlList=[]
        for i in trainList:
            hostList = [x for x in urls if i in x]
            urlList+=hostList
        if len(urlList)>0:
            return urlList
        else:
            print('没有火车头')

    def trainUpdateIndex(self):
        try:
            urlList=self.trainCheck()
            indexList=[]
            pattern = re.compile('(\d+).html|(\d+).Html|(\d+)/|/d/(\d+)')
            for i in urlList:
                try:
                    index = pattern.findall(i)[0]
                    index = [i for i in index if i != ''][0]
                    index = int(index)
                    indexList.append(index)
                except:
                    pass
            indexList = sorted(indexList, reverse=True)
            urlTrain = []
            for i in urlList:
                if str(indexList[0]) in i:
                    urlTrain.append(i)
            id = urlTrain[0].split(str(indexList[0]))[0]
            tail=urlTrain[0].split(str(indexList[0]))[1]
            return indexList[0],id,tail
        except Exception as reason:
            print('错误出现在(getTrainNumber.py)127-145行,错误原因 %s'%reason)


class sitemapXML():
    '''
    检查网站siteMap地图的方法
    '''
    def __init__(self,host):
        xmlList=['sitemap.xml','baidu.xml','google.xml','rss.xml']
        for endUrl in xmlList:
            url =host.strip('/')+'/'+endUrl
            # print('begin url')
            try:
                self.status = requests.get(url,headers=headers,timeout=1).status_code
                if self.status==200:
                    self.sitemapURl =url
                    # print(url)
                    break
                else:
                    pass
            except Exception as reason:
                print('错误出现在(getTrainNumber.py)160-167行,错误原因 %s'%reason)


    def siteMapUrl(self):
        try:
            url = self.sitemapURl
            return url
        except:
            print('无网站地图')


    # 火车头url过少采取火车头命名法扩容
    def sitemapLocoy(self, locList, minLen=30):
        if len(locList) <= minLen:
            maxNum = 0
            l = []
            for url in locList:
                num = int(re.search(r'\d+', urlparse(url).query).group())
                maxNum = num if num > maxNum else maxNum
                for i in range(1, maxNum + 1):
                    l.append(url.replace(str(num), str(i)))
            locList = l
        return locList

    def getLoc(self, url='', isXmlMap=False):
        if not url:
            url = self.siteMapUrl()
        locList = []
        try:
            time.sleep(0.5)
            s = urlopen(url).read()
            root = ET.fromstring(s)
            for i in root.iter():
                if i.tag == 'sitemapindex':
                    isXmlMap = True
                if i.tag == 'loc':
                    locList.append(i.text)
        except Exception as reason:
            print('错误出现在(getTrainNumber.py)200-207行,错误原因 %s'%reason)
        return locList, isXmlMap

    def getSitemap(self, url=''):
        locList, isXmlMap = self.getLoc(url)
        if isXmlMap:
            temp = []
            l = list(locList)
            for j in l:
                # print('parse %s'% j)
                temp += self.getLoc(url=j)[0]
            result = temp
            return result
        else:
            return self.sitemapLocoy(locList)