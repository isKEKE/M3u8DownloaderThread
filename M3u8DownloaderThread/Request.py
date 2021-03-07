# Python3.8
# encoding:utf-8
# m3u8请求模块
import requests,re,random
from Setting import USER_AGENT
from time import sleep
from sys import exit

class Headers:
    ''' 请求头设置类 '''

    def __init__(self):
        self.__headers = {}

    @property
    def headers(self):
        return self.__headers

    @headers.getter
    def headers(self):
        self.__headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
        self.__headers["Accept-Encoding"] = "gzip, deflate"  # 注:requests不支持br解压
        self.__headers["Accept-Language"] = "Accept-Language: zh-CN,zh;q=0.9"
        self.__headers["Cache-Control"] = "no-store"  # 本地不保存缓存，每次请求服务器都需发送资源.
        self.__headers["Connection"] = "close"  # 关闭长连接
        self.__headers['User-Agent'] = random.choice(USER_AGENT)
        return self.__headers

    @headers.setter
    def headers(self,*args):
        for key,value in args[0].items():
            self.__headers[key] = value

class MyRequest(Headers):
    ''' 网络请求类 '''
    def __init__(self):
        Headers.__init__(self)
        self.__url = None
        self.__host = None

    @property
    def url(self):
        return self.__url

    @url.setter
    def url(self,value):
        self.__url = value

    @property
    def host(self):
        return self.__host

    @host.setter
    def host(self,value):
        # 获取host域名
        try:
            self.__host = re.search("(http|https)://(.*?)/", value).group(2)
        except TypeError:
            return None
        else:
            return self.__host

    @property
    def Get(self):
        count = 0
        while True:
            try:
                # timeout参数注释:1 - 连接超时;2 - 读取超时
                response = requests.get(url=self.url,headers=self.headers,timeout=(5,30))
            except requests.exceptions.MissingSchema:
                return "请先设置URL属性."
            except requests.exceptions.ConnectTimeout:
                count += 1 # 捕获连接超时异常,记数+1
            except requests.exceptions.ReadTimeout:
                count += 1 # 捕获读取超时异常,记数+1
            except requests.exceptions.ConnectionError:
                # 网络请求异常,可能连接过多，请求过快，Ip被封等...
                count += 1 # 记数+1
                sleep(3) # 休息3s
            else:
                count = 0
                self.url = None
                return response
            finally:
                if count == 10:
                    exit()

request = MyRequest()


def httpRequest_m3u8File_wapper(func):
    '''
     网络请求视频网址，尝试获得m3u8目录文件
    :param func: 要装饰的函数对象
    :return:m3u8目录文件内容
    '''
    def inner(*args,**kwargs):
        html = func(*args,**kwargs)
        # 正则：匹配m3u8目录超链接
        # html = "[('http://wy.bigmao.top/api/GetDownUrlMu/d273758be9f14821ab72792c80e0b3e2/7f78d872bcfa4afa87e0d5798f5cd7d5.m3u8', '')]"
        patt = re.compile("(https.+?m3u8)|(http:.+?m3u8)")
        try:
            m3u8_catalog_tuple = re.findall(patt, html)[0]
        except IndexError:
            # 匹配网页源代码中*.m3u8文本失败
            assert False,"Text matching failed."
        else:
            m3u8_catalog_list = [item for item in m3u8_catalog_tuple if item]
            for m3u8_url in m3u8_catalog_list:
                try:
                    if "\\" in m3u8_url:
                        raise AssertionError
                except AssertionError:
                    m3u8_url = m3u8_url.replace("\\",'')
                finally:
                    html = func(m3u8_url)
                    if "#EXTM3U" in html:
                        doc_list = [item for item in html.split() if item != '']
                        if len(doc_list) < 10:
                            if request.host in doc_list:
                                pass
                            else:
                                new_m3u8_url = f'{re.search("http.*/",m3u8_url).group(0)}{doc_list[-1]}'
                                try:
                                    html = func(new_m3u8_url)
                                    if not html:
                                        raise AssertionError
                                except AssertionError:
                                    request.host = m3u8_url
                                    new_m3u8_url = f"{re.search('(https)|(http)', m3u8_url).group(0)}://{request.host}/{doc_list[-1]}"
                                    html = func(new_m3u8_url)
                                    return (html,m3u8_url)
                                else:
                                    return (html,m3u8_url)
                        else:
                            return (html,m3u8_url)
    return inner

@httpRequest_m3u8File_wapper
def httpRequest_m3u8File(url):
    request.url = url
    response = request.Get
    html = response.text
    return html

def match_tsUrl(html,url):
    '''
    处理M3U8文档中*.ts文本为超链接
    :param html: M3U8文件文档
    :param url: 获得M3U8文件文档的超链接
    :param uid: 判断*.ts文本匹配模式
    :return:HTTP/HTTPS*.ts超链接[列表]
    '''
    if html:
        ts_list = []
        for item in html.split('\n'):
            try:
                if "\r" in item:
                    raise AssertionError
            except AssertionError:
                item = item.replace('\r', '')
            finally:
                if "http" in item:
                    ts_list.append(item)
                elif "ts" in item and not "http" in item:
                    ts_url = f'{re.search("http.*/", url).group(0)}{item}'
                    ts_list.append(ts_url)
                elif "ts" in item and "http" in item:
                    ts_list.append(item)
        return ts_list
    else:
        assert False,"Invalid HTML document."

def getDoc_to_tsCatalog(url,like=False):
    '''
    函数封装
    :param url: 视频播放页面链接|视频M3U8文档链接
    :param like: 模式:若为True，启动M3U8文档链接请求匹配，否则播放页面链接请求匹配，默认False
    :return: HTTP\HTTPS*.ts超链接文档
    '''
    if not like:
        try:
            done = httpRequest_m3u8File(url)
        except AssertionError:
            return getDoc_to_tsCatalog(url,False)
        else:
            html,m3u8_url = done
            ts_urls = match_tsUrl(html,m3u8_url)
            return ts_urls
    else:
        request.url = url
        html = request.Get.text
        ts_urls = match_tsUrl(html,url)
        return ts_urls

if __name__ == '__main__':
    url = "https://www.nfmovies.com/video/61579-2-0.html"
    url2 = "https://www.zhenbuka.com/vodplay/74367-1-1/"
    result = getDoc_to_tsCatalog(url)
