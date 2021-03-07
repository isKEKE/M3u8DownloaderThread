# Python3.8
# encoding:utf-8
# TS文件合并模块
from os import listdir,remove
from os.path import join,abspath
from Setting import TS_DOWNLOAD_PATH,MP4_JOIN_PATH

def join_ts(name=None):
    path = abspath(join(MP4_JOIN_PATH,f"{name}.mp4"))
    with open(path,'wb+') as f:
        ts_list = listdir(TS_DOWNLOAD_PATH) # 获取下载本地TS文件名称，返回列表
        for item in range(len(ts_list)):
            file_name = f'{item}.ts' # 合成文件名称
            if file_name in ts_list:
                ts_path = abspath(join(TS_DOWNLOAD_PATH,file_name))
                f.write(
                    open(ts_path,'rb').read()
                )
                remove(ts_path) # 删除文件
            else:
                print(f"{item}.ts不存在")

if __name__ == '__main__':
    pass