#coding = 'utf-8'
from PyQt5.QtCore import pyqtSignal,QThread
from Douyin_API import Douyin_API
import os
import time
import traceback

class DownListThread(QThread):
    signal = pyqtSignal(int,str)    # 括号里填写信号传递的参数
    def __init__(self):
        super().__init__()

    def __del__(self):
        self.wait()

    def run(self):
        # 进行任务操作
        dy=Douyin_API()
        try:
            #dy.get_hotsearch_user()
            self.signal.emit(0,'正在提取热门直播用户') 
            dy.get_hotsearch_video()
            self.signal.emit(0,'正在提取热门视频') 

            user_list=dy.get_user_info_local()
            for u in user_list:            
                dy.get_video_list_by_secid(u['author_sec_uid'])
                self.signal.emit(0,'正在更新用户：'+u['nickname'])    # 发射信号
                
            dy.update_user_aweme_count()
            self.signal.emit(1,'全部用户更新完成')    # 发射信号
        except Exception as e:
            dy.write_log(traceback.format_exc())  
            
class DownCoverThread(QThread):
    signal = pyqtSignal(int)    # 括号里填写信号传递的参数
    def __init__(self,pageIndex,count,author_uid):
        super().__init__()
        self.pageIndex=pageIndex
        self.count=count
        self.author_uid=author_uid
        
    def __del__(self):
        self.wait()

    def run(self):
        # 进行任务操作
        dy=Douyin_API()
        try:
            v_list=dy.get_video_list_local(self.pageIndex,self.count,self.author_uid)
            for v in v_list:
                cover_uri=v['cover_uri']
                cover_url=v['cover_url']
                if not os.path.exists('cache/'+cover_uri+'.jpg'):
                    dy.down_cover(cover_uri,cover_url)
            self.signal.emit(1)    # 发射信号
        except Exception as e:
            dy.write_log(traceback.format_exc())              