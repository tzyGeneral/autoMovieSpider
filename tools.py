

# tools模块中使用
def not_empty(s):
    return s and s.strip()
# 识别字符串适合用什么符号分割成list
def findSplitSrt(line,cutStrList=['：',':']):
    for str in cutStrList:
        if str in line:
            break
    return str
def lineLookup(str, frontStr, behindStr):
    beginNum = str.find(frontStr) + len(frontStr)
    endNum = str.find(behindStr,beginNum)
    result = ''
    if endNum != -1 and str.find(frontStr) != -1:
        result = str[beginNum:endNum]
    return result

characteristic='导演'
dataModel = {
    'actor': ['主演'],
    'types': ['类型'],
    'director': ['导演'],
    'publisharea': ['地区','产地','年代','国家/地区','国家'],
    'publishyear': ['年份','上映','年分'],
    'content': ['剧情介绍：','简介'],
    'language': ['语言','语言/字幕'],
    'tags': ['别名'],
    'updatetime': ['更新时间','更新：','更新'],
    'other': ['详情','更多']
}
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36',
    'Connection': 'close',
}


