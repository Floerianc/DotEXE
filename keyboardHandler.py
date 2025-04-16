from PyQt5.QtCore import (
    QThread,
    pyqtSignal
)
import keyboard
import time
from configParser import Config

class KeyboardWorker(QThread):
    moving = pyqtSignal(int, int)
    
    def __init__(self, objects: list):
        super().__init__()
        self.config = Config()
        self.objects = objects
    
    def run(self):
        while True:
            direction = [0, 0]
            
            if not self.objects['dynamicObjects']:
                time.sleep(0.05)
                continue
            
            if keyboard.is_pressed("w"):
                direction[1] -= 1
            if keyboard.is_pressed("s"):
                direction[1] += 1
            if keyboard.is_pressed("a"):
                direction[0] -= 1
            if keyboard.is_pressed("d"):
                direction[0] += 1
            
            self.moving.emit(direction[0], direction[1])
            time.sleep(self.config.TOUT)