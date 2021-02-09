# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, qApp,QWidget,QMessageBox, QSlider, QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtMultimedia import QMediaPlayer,QMediaContent
from PyQt5.QtGui import QIcon,QPalette
from PyQt5.QtCore import QRect,QUrl, Qt,QBuffer,QByteArray,QIODevice,QEvent
import sys
import os
import traceback
from datetime import datetime
from Douyin_Win_List import Win_List
from Douyin_Win_Setting import Win_Setting
from Douyin_API import Douyin_API
from Douyin_VideoWidget import VideoWidget



class Win_Play(QMainWindow):
    def __init__(self):
        self.vid =''
        self.lastTime=datetime.now()
        self.lastY=-1
        super(Win_Play,self).__init__()
        self.InitUI()
        self.load_Next_Video(0)

    #对界面进行初始化
    def InitUI(self):
        dy=Douyin_API()

        widget= QWidget(self)
        #self.statusBar().showMessage('准备就绪')
        self.setWindowIcon(QIcon(dy.get_resource_path('dy.ico')))  # 程序图标
        self.setWindowTitle('DY播放器')
        vbox=QVBoxLayout()
        self.setCentralWidget(widget)
        widget.setLayout(vbox)


       
        
        #视频插件
        self.video_widget = VideoWidget(self)
        self.video_palette = QPalette()
        #self.video_palette.setColor(QPalette.Background, Qt.black)  # 设置播放器背景
        self.video_widget.setPalette(self.video_palette)
        video_widget_color="background-color:#000000"
        self.video_widget.setStyleSheet(video_widget_color)
        self.video_widget.mouse_Signal.connect(self.video_Slide_change)
        hbox_video=QHBoxLayout()
        hbox_video.addWidget(self.video_widget)


        vbox.addLayout(hbox_video)

        hbox=QHBoxLayout()
        vbox.addLayout(hbox)

        
        
        # 设置播放器
        self.player = QMediaPlayer(self)   
        self.player.setVideoOutput(self.video_widget) 
        self.player.positionChanged.connect(self.slide_change)      # change Slide     
        self.player.durationChanged.connect(self.duration_change)
        self.player.mediaStatusChanged.connect(self.playerStatusChanged)        
        
        #视频进度标签
        self.now_position = QLabel("00:00")   # 目前时间进度
        self.all_duration = QLabel('/00:00')   # 总的时间进度
        self.all_duration.setStyleSheet('''QLabel{color:#000000}''')
        self.now_position.setStyleSheet('''QLabel{color:#000000}''')   
        hbox.addWidget(self.now_position)
        hbox.addWidget(self.all_duration)
        
        
        
        #视频播放进度条        
        self.video_slider = QSlider(Qt.Horizontal, self)  # 视频进度拖拖动
        self.video_slider.setMinimum(0)   # 视频进度0到100%
        #self.video_slider.setMaximum(100)
        style_vs='''QSlider{}
                QSlider::sub-page:horizontal:disabled{background: #00009C;  border-color: #999;  }
                QSlider::add-page:horizontal:disabled{background: #eee;  border-color: #999; }
                QSlider::handle:horizontal:disabled{background: #eee;  border: 1px solid #aaa; border-radius: 4px;  }
                QSlider::add-page:horizontal{background: #575757;  border: 0px solid #777;  height: 10px;border-radius: 2px; }
                QSlider::handle:horizontal:hover{background:qradialgradient(spread:pad, cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5, stop:0.6 #2A8BDA,   stop:0.778409 rgba(255, 255, 255, 255));  width: 11px;  margin-top: -3px;  margin-bottom: -3px;  border-radius: 5px; }
                QSlider::sub-page:horizontal{background: qlineargradient(x1:0, y1:0, x2:0, y2:1,   stop:0 #B1B1B1, stop:1 #c4c4c4);  background: qlineargradient(x1: 0, y1: 0.2, x2: 1, y2: 1,stop: 0 #5DCCFF, stop: 1 #1874CD);  border: 1px solid #4A708B;  height: 10px;  border-radius: 2px;  }
                QSlider::groove:horizontal{border: 1px solid #4A708B;  background: #C0C0C0;  height: 5px;  border-radius: 1px;  padding-left:-1px;  padding-right:-1px;}
                QSlider::handle:horizontal{background: qradialgradient(spread:pad, cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5,   stop:0.6 #45ADED, stop:0.778409 rgba(255, 255, 255, 255));  width: 11px;  margin-top: -3px;  margin-bottom: -3px;  border-radius: 5px; }'''
        self.video_slider.setStyleSheet(style_vs)
        self.video_slider.setSingleStep(1)
        self.video_slider.setGeometry(QRect(0, 0, 200, 10))
        self.video_slider.sliderReleased.connect(self.video_silder_released)
        self.video_slider.sliderPressed.connect(self.video_silder_pressed)  
        hbox.addWidget(self.video_slider)

        #用户姓名显示
        self.lbl_user = QLabel(" ")   # 用户姓名显示
        hbox.addWidget(self.lbl_user)

        #设置菜单


        exitAct = QAction(QIcon(dy.get_resource_path('quit.jpg')), '退出(&E)', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('退出程序')
        exitAct.triggered.connect(qApp.quit)

        lstAct = QAction(QIcon(dy.get_resource_path('list.jpg')),'列表(&L)',self)
        lstAct.setShortcut('Ctrl+L')
        lstAct.setStatusTip('打开视频列表')
        lstAct.triggered.connect(lambda:self.open_List_Window())
        
        setAct = QAction(QIcon(dy.get_resource_path('setting.jpg')),'设置(&L)',self)
        setAct.setShortcut('Ctrl+T')
        setAct.setStatusTip('打开设置')  
        setAct.triggered.connect(lambda:self.open_Setting_Window())
        
        savAct = QAction(QIcon(dy.get_resource_path('save.jpg')),'下载(&L)',self)
        savAct.setShortcut('Ctrl+S')
        savAct.setStatusTip('下载视频')  
        #savAct.clicked.connect(self.openVideoFile)   # 打开视频文件按钮        
        savAct.triggered.connect(lambda:self.load_Next_Video)

        toolbar = self.addToolBar('工具栏')
        toolbar.addAction(savAct)
        toolbar.addAction(lstAct)        
        toolbar.addAction(setAct)
        toolbar.addAction(exitAct)

        vbox.setStretchFactor(hbox_video,90)  
        vbox.setStretchFactor(hbox,1)    
        
    #响应事件过滤器
    def eventFilter(self,obj, event):
        if obj==self.lbl_user:
            if event.type() == QEvent.MouseButtonPress and event.button()==Qt.LeftButton:#mouse button pressed
                if self.lbl_user.text().find('_')>0:
                    author_uid=self.lbl_user.text()[0:self.lbl_user.text().find('_')]
                    self.player.pause()
                    self.ls = Win_List(author_uid)
                    self.ls.video_Signel.connect(self.slot_video_clicked)
                    self.ls.showMaximized()
        return super().eventFilter(obj, event)

        
    def load_Next_Video(self,direction=0):
        dy=Douyin_API()
        try:        
            self.vid,url,author_uid,nickname,v_date=dy.get_next_video_local(self.vid,direction)
            if self.vid is None:
                res = QMessageBox.information(self, "提示", "没有找到可供播放的内容\r\n请重新加载试试或者在设置中关注更新用户视频", QMessageBox.Yes )
                return
            self.lbl_user.setText(author_uid+'_'+nickname+':'+v_date)
            dy.update_play_status(self.vid)
            self.player.setMedia(QMediaContent(QUrl(url)))            
            self.player.play() 
        except Exception as e:
            dy.write_log(traceback.format_exc())

    def duration_change(self, d):
        try:
            all_second = int(d / 1000 % 60)  # 视频播放时间
            all_minute = int(d / 1000 / 60)
            self.all_duration.setText('/%02d:%02d'%(all_minute,all_second))
            self.video_slider.setMaximum(self.player.duration())
        except Exception as e:
            pass  
            
     # 视频进度条自动释放与播放时间
    def slide_change(self,position):
        dy=Douyin_API()
        try:        
            self.vidoeLength = self.player.duration()+0.1
            self.video_slider.setValue(position)
            now_second = int(position / 1000 % 60)
            now_minute = int(position / 1000 / 60)   
            self.now_position.setText('%02d:%02d'%(now_minute,now_second))
            
        except Exception as e:
            dy.write_log(traceback.format_exc()) 



    def video_silder_released(self):  # 释放滑条时,改变视频播放进度
        dy=Douyin_API()
        try:
            
            #print('video_silder_released......')
            if self.player.state() != 0:
                self.player.setPosition(self.video_slider.value())
                self.player.play()
            else: #如果视频是停止状态，则拖动进度条无效
                self.video_slider.setValue(0) 
        except Exception as e:
            dy.write_log(traceback.format_exc()) 

    def video_silder_pressed(self):
        dy=Douyin_API()
        try:
            if self.player.state != 0:
                self.player.pause()
        except Exception as e:
            dy.write_log(traceback.format_exc())   
            
    def playerStatusChanged(self, status):
        dy=Douyin_API()
        try:    
            self.player_status = status
            if status == 7:
                dy=Douyin_API()
                self.load_Next_Video(1)
        except Exception as e:
            dy.write_log(traceback.format_exc())   

            
    #响应视频界面上滑或下滑来切换视频
    def video_Slide_change(self,sinal,x,y):
        dy=Douyin_API()
        try:      
            if sinal==0:#发生鼠标滑动
                time_diff=(datetime.now()-self.lastTime).total_seconds()
                if time_diff>=0.3:            
                    self.lastTime=datetime.now()
                    self.lastY=-1
                    return
                
                if self.lastY==-1:
                    self.lastY=y
                elif self.lastY-y>=30:            
                    self.load_Next_Video(1)
                elif self.lastY-y<=-30:        
                    self.load_Next_Video(-1)
                else:
                    #self.setWindowTitle('滑动不足%f-%d-%d'%(time_diff,self.lastY,y)) 
                    pass
            elif sinal==1:#鼠标单击释放
                if self.player.state()==1:
                    self.player.pause()
                elif self.player.state()==2:     
                    self.player.play()
        except Exception as e:
            dy.write_log(traceback.format_exc())          
    #响应列表窗口视频点击        
    def slot_video_clicked(self,flag,vid):
        dy=Douyin_API()
        try:           
            self.vid=vid
            v_url=dy.get_video_url_by_vid(vid)
            self.player.setMedia(QMediaContent(QUrl(v_url)))  
            self.player.play()
        except Exception as e:
            dy.write_log(traceback.format_exc()) 
            
    def slot_setting_closed(self):
        dy=Douyin_API()
        try:        
            self.player.play()
        except Exception as e:
            dy.write_log(traceback.format_exc())  
            
    def open_List_Window(self): 
        self.player.pause()
        self.ls = Win_List('')
        self.ls.video_Signel.connect(self.slot_video_clicked)
        self.ls.showMaximized()
        
    def open_Setting_Window(self):
        self.player.pause()
        self.sw = Win_Setting()
        self.sw.video_Signel.connect(self.slot_setting_closed)
        self.sw.showMaximized()        
            
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Win_Play()    
    ex.showMaximized() 
    app.installEventFilter(ex)
    sys.exit(app.exec_())