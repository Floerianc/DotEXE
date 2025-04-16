import PyQt5.QtWidgets as QtWidgets
from PyQt5.QtCore import (
    QTimer,
    QElapsedTimer,
)
from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import (
    QFont, 
    QBrush,
    QColor
)
import sys
import random
import utils
import time
import models
import keyboardHandler
from configParser import Config
from ui.ui_graphics import *

class Window(Ui_Frame):
    def __init__(self, form):
        super().__init__()
        self.setupUi(form)
        self.scene = QtWidgets.QGraphicsScene(0, 0, self.graphicsView.width(), self.graphicsView.height())
        self.graphicsView.setScene(self.scene)
        
        self.objects = {
            'dynamicObjects': [],
            'staticObjects': []
        }
        
        self.config = Config()
        
        self.keyboardWorker = keyboardHandler.KeyboardWorker(self.objects)
        self.keyboardWorker.moving.connect(self.movePlayer)
        self.keyboardWorker.start()
        
        self.FPStimer = QTimer()
        self.FPStimer.timeout.connect(self.displayFPS)
        self.FPStimer.start(0)
        
        self.elapsedTimer = QElapsedTimer()
        self.elapsedTimer.start()
        self.frameCount = 0
        
        self.constructUI()
    
    def constructUI(self) -> None:
        FPSLabelFont = QFont()
        FPSLabelFont.setPointSize(18)
        self.FPSLabel = QLabel("FPS:                    ")
        self.FPSLabel.setFont(FPSLabelFont)
        
        proxyLabel = self.scene.addWidget(self.FPSLabel)
    
    def displayFPS(self) -> None:
        self.frameCount += 1
        elapsedTime = self.elapsedTimer.elapsed()
        
        if elapsedTime >= 1000: # ms
            fps = self.frameCount
            self.elapsedTimer.restart()
            self.frameCount = 0
            self.FPSLabel.setText(f"FPS: {fps:,}")
    
    def addObject(self, obj):
        try:
            self.objects['dynamicObjects'].append(obj)
            self.scene.addItem(obj.graphics['rect'])
            if obj.graphics['trail']:
                self.scene.addItem(obj.graphics['trail'])
        except Exception as e:
            raise RuntimeError(f"Couldn't add Item! {e}")
    
    def movePlayer(self, XDirection: int, YDirection: int) -> None:
        self.objects['dynamicObjects'][0].move(XDirection, YDirection)
    
    def testing(self) -> None:
        point = models.DynamicPoint(650, 450, self.scene)
        ai = models.DPAI(850, 200, self.scene, QBrush(QColor(255, 0, 0)))
        self.addObject(point)
        self.addObject(ai)
    
    def testing2(self) -> None:
        rangeList = utils.rangespace(0, 50, 32)
        for value in rangeList:
            self.objects['dynamicObjects'][0].setPosition(self.objects['dynamicObjects'][0].pos[0] + value, self.objects['dynamicObjects'][0].pos[1])
            QtWidgets.QApplication.processEvents()
            time.sleep(0.05)
    
    def testing3(self) -> None:
        self.objects['dynamicObjects'][0].setPosition(self.objects['dynamicObjects'][0].pos[0] + random.randint(-10, 10), self.objects['dynamicObjects'][0].pos[1] + random.randint(-10, 10))

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QMainWindow()
    
    ui = Window(Form)
    Form.show()
    
    ui.testing()
    # ui.testing4()
    sys.exit(app.exec_())

# TODO

# TODO:     Add documentation
# TODO:     Think of some game concept
# TODO:     Create logic for the AI to follow you because why not, is probably very useful later on, right?