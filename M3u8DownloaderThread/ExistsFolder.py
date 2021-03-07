# Python3.8
# encoding:utf-8
# 创建TS存储文件夹和MP4存储文件夹
from os import makedirs
from os.path import exists as es,abspath
from Setting import TS_DOWNLOAD_PATH,MP4_JOIN_PATH

class FolderPath:
    @staticmethod
    def exists():
        # 判断文件夹是否存在
        ts_folder_path = abspath(TS_DOWNLOAD_PATH)
        mp4_folder_paht = abspath(MP4_JOIN_PATH)
        try:
            if not es(ts_folder_path):
                makedirs(ts_folder_path)

            if not es(mp4_folder_paht):
                makedirs(mp4_folder_paht)
        except:
            return False
        else:
            return True

if __name__ == '__main__':
    FolderPath.exists()