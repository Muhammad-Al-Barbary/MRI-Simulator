from phantominator import shepp_logan, mr_ellipsoid_parameters
import matplotlib.pyplot as plt 
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib.patches as patches
from matplotlib.animation import ArtistAnimation
import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QFileDialog, QGraphicsScene
import pyqtgraph as pg
import sys



location = []

class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, PD , T1 , T2, allowdrawpoints, parent=None, width=5, height=4, dpi=100):

        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        self.fig.set_facecolor('#e1e1e1')
        self.PD , self.T1 , self.T2 = PD , T1, T2
        super(MplCanvas, self).__init__(self.fig)

        if(allowdrawpoints):
            self.mpl_connect("button_press_event", self.on_press)


    def on_press(self, event):
        rect = patches.Rectangle((event.xdata, event.ydata),2,2)
        self.axes.add_patch(rect)
        self.draw()
        xpos , ypos = int(event.xdata) , int(event.ydata)
        self.axes.set_title(f"PD = {self.PD[xpos][ypos]} , T1 = {self.T1[xpos][ypos]} , T2 = {self.T2[xpos][ypos]}")


class MainWindow(QtWidgets.QMainWindow,QMouseEvent):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        uic.loadUi(r'GUI.ui', self)

        self.phantomButton.clicked.connect(lambda : self.phantom_show())
        self.phantomSize.activated[str].connect(lambda : self.sizeChanged())
        self.tissueType.activated[str].connect(lambda : self.tissueChanged())
        

        self.size = int(self.phantomSize.currentText())
        self.tissueProp = self.tissueType.currentText()
        self.PD , self.T1 , self.T2 = [] , [] , []

        self.graph = pg.PlotItem()
        self.graph.hideAxis('left')
        self.graph.hideAxis('bottom')

        # Intiating canvas
        self.imageView.setCentralItem(self.graph)
        self.imageView.setBackground(QtGui.QColor('#e1e1e1'))

        self.imageView.scene().sigMouseClicked.connect(self.on_press)

        
    def on_press(self,evt):
        scene_coords = evt.scenePos()
        # print(scene_coords)
        # self.tissueParam.setText(f"PD = {self.PD[evt,location[1]]} , T1 = {self.T1[location[0],location[1]]} , T2 = {self.T2[location[0],location[1]]}")


    def sizeChanged(self):
        self.size = int(self.phantomSize.currentText())
        self.phantom_show()
    
    def tissueChanged(self):
        self.tissueProp = self.tissueType.currentText()
        self.phantom_show()

    def phantom_show(self):
        E = mr_ellipsoid_parameters()

        E[:5, 7] = np.linspace(.1, .9, 5)
        # print(E.shape)

        self.PD, self.T1, self.T2 = shepp_logan(
                (self.size, self.size, 1), MR=True, E=E, zlims=(-.25, -.25))
        
        
        self.originalCanvas = MplCanvas(self.PD , self.T1 , self.T2 ,True, self.imageView,  width=5.5, height=4.5, dpi=90)
        self.originalCanvas.axes.axis('off')
        self.originalLayout = QtWidgets.QVBoxLayout()
        self.originalLayout.addWidget(self.originalCanvas)
        self.originalCanvas.draw()
    
        if self.tissueProp == 'PD':
            self.originalCanvas.axes.imshow(self.PD,cmap='gray')
        elif self.tissueProp == 'T1':
            self.originalCanvas.axes.imshow(self.T1,cmap='gray')
        elif self.tissueProp == 'T2':
            self.originalCanvas.axes.imshow(self.T2,cmap='gray')
        self.originalCanvas.draw()
        self.imageView.setCentralItem(self.graph)
        self.imageView.setLayout(self.originalLayout)
    



def main():
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
