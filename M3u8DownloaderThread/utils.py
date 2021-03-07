from Request import getDoc_to_tsCatalog
from ThreadSpider import downloader
from ExistsFolder import FolderPath
from TsFileJoin import join_ts
'''
     - M3U8多线程下载器1.0.
     - 注意：不支持M3U8加密下载.
     - 并发数量请到Setting.py文件中修改.
'''
def main(url,mode=False):
    '''
     主函数
    :param url:视频播放页面链接|视频M3U8文档链接
    :param mode: 若为True，启动M3U8文档链接请求匹配，否则播放页面链接请求匹配，默认False
    :return: None
    '''
    # 创建存储文件夹
    FolderPath.exists()
    # 获取*.TS文件超链接列表
    ts_list = getDoc_to_tsCatalog(url,mode)
    # 多线程下载器
    name = downloader(ts_list)
    # 合并*.TS文件为MP4文件
    join_ts(name)


if __name__ == '__main__':
    url = "https://www.nfmovies.com/video/61579-2-0.html"
    url2 = "https://www.zhenbuka.com/vodplay/74367-1-1/"
    main(url)