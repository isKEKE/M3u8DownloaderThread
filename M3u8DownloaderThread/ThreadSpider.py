# Python3.8
# encoding:utf-8
# 多线程爬虫-*.TS超链接HTTP请求
import requests,threading,queue
from re import search
from Request import Headers
from Setting import ThreadConcurrentNumber,TS_DOWNLOAD_PATH
from os.path import join,abspath
from time import time
from copy import deepcopy

exit = 0
class Counter():
    def __init__(self,count):
        self.count = count
        self.length = deepcopy(count)

    def __iter__(self):
        return self

    def __next__(self):
        self.count -= 1
        if self.count == 0:
            raise StopIteration
        return f"下载成功,已完成:{self.length - self.count}/{self.length}."

def consumer(q,lock,counter):
    while True:
        try:
            url,path = q.get(block=False)
        except queue.Empty:
            pass
        else:
            host = search("(http|https)://(.*?)/", url).group(2)
            headers = Headers().headers
            headers["Host"] = host
            try:
                response = requests.get(url=url,headers=headers,timeout=(3,15),stream=True)
            except requests.exceptions.ConnectTimeout:
                q.put((url,path))
            except requests.exceptions.ReadTimeout:
                q.put((url,path))  # 捕获读取超时异常,记数+1
            else:
                with open(path,'wb') as f:
                    for chunk in response.iter_content(chunk_size=512):
                        f.write(chunk)
                    with lock:
                        try:
                            print(counter.__next__())
                        except StopIteration:
                            print("下载完成...")
                response.close()
            finally:
                q.task_done()
                if exit:
                    break

class ThreadHttpSpider(threading.Thread):
    def __init__(self,q,l,c):
        threading.Thread.__init__(self)
        self.q = q
        self.l = l
        self.c = c

    def run(self):
        consumer(self.q,self.l,self.c)

def downloader(urls=None,con=ThreadConcurrentNumber):
    '''
     多线程下载主函数
    :param urls: *.ts文件超链接[列表]
    :param con: 下载并发数量，默认值16
    :return: 返回一个时间戳
    '''
    global exit
    dataQueue = queue.Queue()  # 存放数据队列实例
    safePrint = threading.Lock() # 输出流线程锁
    if urls:
        length = len(urls)
        counter = Counter(length)
        # 创建消费者线程-请求*.ts文档超链接&下载线程
        for _ in range(con):
            thread = ThreadHttpSpider(dataQueue,safePrint,counter)
            thread.daemon = True
            thread.start()

        # url和path存放至队列
        for index,url in enumerate(urls):
            path = abspath(join(TS_DOWNLOAD_PATH,f"{index}.ts"))
            dataQueue.put((url,path))

        dataQueue.join()
        exit = 1
        return int(time())
    else:
        return None


if __name__ == '__main__':
    pass