import html
import regex as re
import requests
from bs4 import BeautifulSoup
from pyquery import PyQuery as pq

from tools import not_empty,findSplitSrt,lineLookup,characteristic,dataModel,headers



class siteMovieData():
    def __init__(self,url):
        self.missionList=url
        self.outputData={}
    # 以导演为目标获取前后共30行文字，减少语义识别计算量
    def shortList(self,inputList, findKeyword=characteristic,front=10,behind=20):
        num=0
        for line in inputList:
            if findKeyword in line:
                break
            num+=1
        return inputList[num-front:num+behind]


    # 使用urllib.request解析url获取r chardet title值
    def getDecode(self,inputUrl,characteristic='导演'):
        '''
        :param inputUrl:
        :param characteristic:
        :return: 利用request请求获取影视网站的网页html源码，和title标题
        '''
        siteHtml=requests.get(inputUrl,headers=headers,timeout=6)
        r=siteHtml.text
        # 矫正不规范网站编码
        if characteristic not in r:
            for siteCharset in [lineLookup(str(r), 'charset=', '"'),'utf-8']:
                siteHtml.encoding = siteCharset
                r = siteHtml.text
                if characteristic in r:
                    break
        bsObj = BeautifulSoup(r, 'lxml')
        title=bsObj.title.string
        return r,title

    def getMovieData(self,r):
        h=pq(r)
        result = html.unescape(re.sub(r'<.*?>', '', html.unescape(str(h))))
        list1=result.split('\n')
        listTemp=list(filter(not_empty, list1))
        dic={}
        missionList=list(dataModel.keys())
        # 不同的信息可能散落在不同的行里，也在同一行里，利用特征进行分隔
        for line in self.shortList(listTemp):
            # num=listTemp.index(line) 未完成 应对识别结果分行而不是冒号分隔的清洗方案,通过记录命中行编号，取最最小值行差识别选取不同的截取识别方案
            # begin---新增判断是否有其他信息在这一行，是的话进行分隔
            lineKeywordIn = {}
            for item in missionList:
                for keyword in dataModel[item]:
                    if keyword in line:
                        lineKeywordIn[item]=keyword
            if len(lineKeywordIn)>1:
                for i in lineKeywordIn.values():
                    line=line.replace(i,'\n'+i)
            # end---新增判断是否有其他信息在这一行，是的话进行分隔
            for templine in line.split('\n'):
                for tempItem in list(lineKeywordIn):
                    if lineKeywordIn[tempItem] in templine:
                        cutStr=findSplitSrt(templine)
                        tmp=templine.split(cutStr)
                        if len(tmp)>1:
                            dicVaule=tmp[1]
                            dicVaule=dicVaule.strip().replace('"','').replace('/','').replace('>','').replace('  ',',').replace('\xa0',',')
                            dic[tempItem]=dicVaule.replace(' ','') if ',' in dicVaule else dicVaule.replace(' ',',')
                            lineKeywordIn.pop(tempItem)
                            missionList.remove(tempItem)
        return dic


    def getDic(self):
        # 通过getDecode方法获取到该url的网页源码r, 和网页标题title
        r, title = self.getDecode(self.missionList)
        # 通过getMovieData方法获取到一个字典dic (根据tools里的dataModel)
        dic=self.getMovieData(r)

        dic['title']=title
        # 以该网页的url为键，刚刚获取的字典dic为值组装为新的outputData
        self.outputData[self.missionList]=dic
        return self.outputData

    def getIndex(self):
        r,title=self.getDecode('https://m.meijutt.com/')
        bsObj = BeautifulSoup(r, 'lxml')
        for i in bsObj.find_all('a'):
            if 'meiju' in i['href']:
                print(i['href'],i)
        return bsObj.find_all('a')

