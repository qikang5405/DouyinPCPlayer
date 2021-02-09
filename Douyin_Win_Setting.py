#coding = 'utf-8'

import sys
import os
import math
import traceback
from requests import Session
from PyQt5.QtWidgets import QWidget,  QApplication, QVBoxLayout, QHBoxLayout, QLabel,QLineEdit,QPushButton,QTableView,QHeaderView
from requests import Session
from PyQt5.QtGui import QImage,QPixmap,QIcon
from PyQt5.QtGui import QStandardItemModel,QStandardItem

from PyQt5.QtCore import QSize,pyqtSignal
from Douyin_API import Douyin_API
from Douyin_NetThread import DownListThread

class Win_Setting(QWidget):
    #自定义消息
    video_Signel=pyqtSignal(int,str)
    def __init__(self):
        super().__init__()
        self.Init_UI()
        self.req=Session()
        
    def Init_UI(self):
        

        self.grid = QVBoxLayout()
        self.setLayout(self.grid)  
        hbox=QHBoxLayout()   
        hbox.addStretch(0)
        lbl = QLabel()
        lbl.setText('用户分享地址')
        hbox.addWidget(lbl)
        self.le=QLineEdit()
        hbox.addWidget(self.le)
        btn=QPushButton('添加')
        btn.clicked.connect(self.add_fav_user)
        hbox.addWidget(btn)
        btn2=QPushButton('清理视频')
        btn2.clicked.connect(self.del_fav_user)
        hbox.addWidget(btn2)     

        dl_thead=DownListThread()
        dl_thead.signal.connect(self.update_progress)        
        btn3=QPushButton('更新数据')        
        btn3.clicked.connect(lambda :dl_thead.start())
        hbox.addWidget(btn3)        
        hbox.addStretch(0)


        self.grid.addLayout(hbox)
        
        #实例化表格视图，设置模型为自定义的模型
        self.tableView=QTableView()      
        #水平方向标签拓展剩下的窗口部分，填满表格
        self.tableView.horizontalHeader().setStretchLastSection(True)
        #水平方向，表格大小拓展到适当的尺寸      
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)     

        
        hbox_main=QHBoxLayout()
        hbox_main.addWidget(self.tableView)
        self.grid.addLayout(hbox_main)

        self.lbl_status = QLabel()
        self.lbl_status.setText('准备就绪')
        self.grid.addWidget(self.lbl_status)
        self.bind_user_list()
        
        self.grid.setStretchFactor(hbox,1)
        self.grid.setStretchFactor(hbox_main,8)
        
        

        #self.statusBar().showMessage('准备就绪
    def add_fav_user(self):
        dy=Douyin_API()
        try:            
            url_list=self.le.text().split(';')
            for url in url_list:
                if url=='':
                    continue
                sec_id=dy.get_sec_uid(url)
                dy.get_user_info(sec_id,url)
            self.bind_user_list()
        except Exception as e:
            dy.write_log(traceback.format_exc()) 
    def del_fav_user(self):
        dy=Douyin_API()
        try:         
            dy.clean_video_without_user()
            self.lbl_status.setText('清理完成')
        except Exception as e:
            dy.write_log(traceback.format_exc()) 
        
    def update_progress(self,status,mesg):        
        self.lbl_status.setText(mesg)
        if status==1:
            self.bind_user_list()
        
        
    def bind_user_list(self):
        dy=Douyin_API()
        try:            
            user_list=dy.get_user_info_local()
            self.model=QStandardItemModel(0,5)
            #设置水平方向四个头标签文本内容
            self.model.setHorizontalHeaderLabels(['数字ID','抖音号','昵称','视频数','完成下载'])
            self.tableView.setModel(self.model)        

            for u in user_list:
                self.model.appendRow([
                    QStandardItem(u['author_uid']),
                    QStandardItem(u['author_unique_id']),
                    QStandardItem(u['nickname']),
                    QStandardItem('%d'%u['aweme_count']),
                    QStandardItem('%d'%u['firstfinished'])
                ])
        except Exception as e:
            dy.write_log(traceback.format_exc()) 
        
        
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Win_Setting()
    ex.showMaximized()
    app.exit(app.exec_())