#coding = 'utf-8'

import sys
import os
import math
import traceback
from PyQt5.QtWidgets import QWidget,  QApplication, QVBoxLayout,QHBoxLayout, QAction, QLabel,QTableWidget,QAbstractItemView,QTableWidgetItem,QPushButton
from PyQt5.QtGui import QImage,QPixmap,QIcon, QCursor
from PyQt5.QtCore import QSize,pyqtSignal,Qt
from Douyin_API import Douyin_API
from Douyin_NetThread import DownCoverThread


class Win_List(QWidget):
    #自定义消息
    video_Signel=pyqtSignal(int,str)
    def __init__(self,author_uid):
        self.pageIndex=0
        self.author_uid=author_uid
        super().__init__()
        self.Init_UI()

        
    def Init_UI(self):
        dy=Douyin_API()
        vbox = QVBoxLayout()
        self.setLayout(vbox)

        
        hbox=QHBoxLayout()  
        vbox.addLayout(hbox)

        self.sync_table = QTableWidget()
        
        self.sync_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.sync_table.clicked.connect(self.sync_table_clicked)  
        hbox.addWidget(self.sync_table)

        hbox2=QHBoxLayout()  
        vbox.addLayout(hbox2)

        # 翻页按钮
        btn_back = QPushButton(self)
        btn_back.setIcon(QIcon(dy.get_resource_path('back.jpg')))  # 设置按钮图标,下同
        btn_back.setIconSize(QSize(35,35))
        btn_back.setStyleSheet('''QPushButton{border:none;}QPushButton:hover{border:none;border-radius:35px;}''')
        btn_back.setCursor(QCursor(Qt.PointingHandCursor))
        btn_back.setToolTip("上一页")
        btn_back.setFlat(True)
        btn_back.clicked.connect(self.proc_back_page)
        hbox2.addWidget(btn_back)

        btn_next = QPushButton(self)
        btn_next.setIcon(QIcon(dy.get_resource_path('next.jpg')))  # 设置按钮图标,下同
        btn_next.setIconSize(QSize(35,35))
        btn_next.setStyleSheet('''QPushButton{border:none;}QPushButton:hover{border:none;border-radius:35px;}''')
        btn_next.setCursor(QCursor(Qt.PointingHandCursor))
        btn_next.setToolTip("下一页")
        btn_next.setFlat(True)
        btn_next.clicked.connect(self.proc_next_page)
        hbox2.addWidget(btn_next)
        
        self.setWindowTitle('DY-视频列表')
        self.bind_video_list()
        
    #计算页面显示的条数    
    def cal_table_count(self):
        desktop = QApplication.desktop()
        width=desktop.width()-100
        col_cnt=math.floor(width/180)-1
        if col_cnt==0:
            col_cnt=1
        height=desktop.height()-100
        row_cnt=math.floor(height/240)
        if row_cnt==0:
            row_cnt=1
        return row_cnt,col_cnt
    
    #绑定列表
    def bind_video_list(self):
        dy=Douyin_API()
        try:
            row_cnt,col_cnt=self.cal_table_count()
            dt=DownCoverThread(self.pageIndex,row_cnt*col_cnt,self.author_uid)
            dt.signal.connect(self.proc_preview_tbl)
            dt.start()    # 启动线程
        except Exception as e:
            dy.write_log(traceback.format_exc())  

    #响应列表被点击    
    def sync_table_clicked(self,index):
        dy=Douyin_API()
        try:    
            table_column = index.column()
            table_row = index.row()
            current_item = self.sync_table.item(table_row, table_column)
            current_widget = self.sync_table.cellWidget(table_row, table_column)
            #print(current_item.text())
            self.video_Signel.emit(0,current_item.text())
            self.close()
        except Exception as e:
            dy.write_log(traceback.format_exc())      
    #将数据绑定到表格    
    def proc_preview_tbl(self,finished):
        if finished!=1:
            return
        
        dy=Douyin_API()
        try:          
            row_cnt,col_cnt=self.cal_table_count()
            v_list=dy.get_video_list_local(self.pageIndex,col_cnt*row_cnt,self.author_uid)
            
            self.sync_table.setColumnCount(col_cnt)
            self.sync_table.setRowCount(row_cnt)
            
            desktop = QApplication.desktop()
            width=desktop.width()-100
            for i in range(col_cnt):  
                self.sync_table.setColumnWidth(i, math.ceil(width/col_cnt))
            for i in range(row_cnt):  
                self.sync_table.setRowHeight(i, math.ceil(width/col_cnt*4/3))
                
            positions = [(row,col) for row in range(row_cnt) for col in range(col_cnt)]
            i=0
            
            for row,col in positions:
                
                item=QTableWidgetItem()
                item.setText(v_list[i]['vid'])
                self.sync_table.setItem(row,col,item)
                lbl = QLabel("")
                lbl.setPixmap(QPixmap('cache/'+v_list[i]['cover_uri'].replace('/','_')+'.jpg'))
                lbl.setScaledContents (True)  # 让图片自适应label大小
                self.sync_table.setCellWidget(row,col,lbl)
                i=i+1
        except Exception as e:
            dy.write_log(traceback.format_exc())                   
    #下一页图标
    def proc_next_page(self):
        self.pageIndex=self.pageIndex+1
        self.bind_video_list()

    #上一页图标
    def proc_back_page(self):
        if self.pageIndex>1:
            self.pageIndex=self.pageIndex-1
        self.bind_video_list()    


            



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Win_List('')
    ex.showMaximized()
    app.exit(app.exec_())