
# -*- coding: utf-8 -*-
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import Qt,pyqtSignal
class VideoWidget(QVideoWidget):
    mouse_Signal = pyqtSignal(int,int,int)  # 创建双击信号
    def __init__(self,parent=None):
        super(QVideoWidget,self).__init__(parent)

    def mouseMoveEvent(self, e):  
        self.mouse_Signal.emit(0,e.x(),e.y())
        #print("鼠标移动",e.x(),e.y())  # 响应测试语句
    def mouseReleaseEvent(self,e):
        if e.button()==Qt.LeftButton:
            self.mouse_Signal.emit(1,e.x(),e.y())