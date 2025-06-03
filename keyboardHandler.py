import keyboard
import time
from PyQt5.QtCore import (
    QThread,
    pyqtSignal
)
from configParser import Config

class KeyboardWorker(QThread):
    """This checks the keyboard's inputs

    Args:
        QThread (QObject): It's yet another seperate QThread
    """
    moving = pyqtSignal(int, int)
    
    def __init__(
        self, 
        objects: list
    ) -> None:
        """Initiates the KeyboardWorker

        Args:
            objects (list): Uses the objects to see 
                if it should even check for input
        """
        super().__init__()
        self.config = Config("player")
        self.objects = objects
    
    def run(self) -> None:
        """Checks for WASD movement and emits a 8-bit direction vector
        """
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
            if keyboard.is_pressed("q"):
                self.moving.emit(-10, -10)
            self.moving.emit(direction[0], direction[1])
            time.sleep(self.config.TOUT)