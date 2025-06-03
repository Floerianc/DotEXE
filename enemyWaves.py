import time
import random
import utils
from PyQt5.QtCore import (
    QThread,
    pyqtSignal
)
from PyQt5.QtWidgets import QGraphicsEllipseItem
from PyQt5.QtGui import (
    QBrush, 
    QColor
)
from configParser import Config
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import Window

class EnemyWave(QThread):
    """Defines all the enemy waves in the game

    Args:
        QThread (QObject): Inherits everything from QThread
    """
    spawnedEnemy = pyqtSignal(int, int) # (x, y)
    spawnCircle = pyqtSignal(object) # circle object
    removeCircle = pyqtSignal(object) # circle object
    
    def __init__(
        self, 
        window: 'Window', 
        waveType: int, 
        enemyCount: int
    ) -> None:
        """Initializes the enemy waves

        Args:
            window (Window): The window class, to access GUI elements
            waveType (int): Type of enemy wave
            enemyCount (int): Amount of enemies
        """
        super().__init__()
        self.window = window
        self.waveType = waveType
        self.enemyCount = enemyCount
        
        self.types = [self.corners, self.horizontalLine, self.center, self.top, self.seperate, self.random]
    
    def run(self) -> None:
        """Spawns a specific wave of enemies
        """
        print(f"Wave {self.waveType} started")
        self.types[self.waveType]()
        self.waveType += 1 # if we do this in the SpawnWave() function, it will increment before the wave spawns
    
    def showWarning(
        self, 
        xPositions: list[int], 
        yPositions: list[int]
    ) -> None:
        """Shows circles that warn the player of where
        enemies are going to be spawned at.

        Args:
            xPositions (list[int]): Positions on the x-axis
            yPositions (list[int]): Positions on the y-axis
        """
        circleSize = 200
        circles = []
        
        zipped = list(zip(xPositions, yPositions))
        for tup in zipped:
            x_pos = round(tup[0])
            y_pos = round(tup[1])
            
            circle = QGraphicsEllipseItem(x_pos - circleSize / 2, y_pos - circleSize / 2, circleSize, circleSize)
            circle.setBrush(QBrush(QColor(255, 0, 0, 100)))
            circles.append(circle)
            self.spawnCircle.emit(circle)
        
        time.sleep(1.5)
        for circle in circles:
            self.removeCircle.emit(circle)
    
    def corners(self) -> None:
        """Spawns enemies in the corners.
        """
        x = [0, self.window.scene.width()] * 2
        y = [0, self.window.scene.height(), self.window.scene.height(), 0]
        self.showWarning(x, y)
        
        for i in range(self.enemyCount):
            x_pos = round(x[i % len(x)])
            y_pos = round(y[i % len(y)]) # fuck floats
            print(f"Spawning enemy at ({x_pos}, {y_pos})")
            self.spawnedEnemy.emit(x_pos, y_pos)
            time.sleep(0.25)
    
    def horizontalLine(self) -> None:
        """Spawns enemies in a horizontal line in the middle of the screen
        """
        sceneWidth = self.window.scene.width()
        y = self.window.scene.height() / 2
        spacing = sceneWidth / (self.enemyCount + 1)
        
        xList = [(i + 1) * spacing for i in range(self.enemyCount)]
        yList = [y] * self.enemyCount
        
        self.showWarning(xList, yList)
        
        for x in xList:
            self.spawnedEnemy.emit(int(x), int(y))
            time.sleep(0.15)
    
    def center(self) -> None:
        """Spawns enemies in the center of the screen
        """
        x = [int(self.window.scene.width() / 2)]
        y = [int(self.window.scene.height() / 2)]
        self.showWarning(x, y)
        
        for _ in range(self.enemyCount):
            xPos = random.randint(x[0] - 100, x[0] + 100)
            yPos = random.randint(y[0] - 100, y[0] + 100)
            self.spawnedEnemy.emit(int(xPos), int(yPos))
            time.sleep(0.5)
    
    def top(self) -> None:
        """Spawns enemies at the top of the screen in a
        horizontal line
        """
        sceneWidth = self.window.scene.width()
        y = 0
        spacing = sceneWidth / (self.enemyCount + 1)
        
        xList = [(i + 1) * spacing for i in range(self.enemyCount)]
        yList = [y] * self.enemyCount
        
        self.showWarning(xList, yList)
        
        for x in xList:
            self.spawnedEnemy.emit(int(x), int(y))
            time.sleep(0.15)
    
    def seperate(self) -> None:
        """Spawns enemies in a tilted line from the top to bottom
        """
        x = utils.rangespace(self.window.scene.width() / 2 - 100, self.window.scene.width() / 2 + 100, self.enemyCount)
        y = utils.rangespace(self.window.scene.height(), 0, self.enemyCount)
        self.showWarning(x, y)
        
        for pos in list(zip(x, y)):
            self.spawnedEnemy.emit(int(pos[0]), int(pos[1]))
    
    def random(self) -> None:
        x = [random.randint(0, int(self.window.scene.width())) for i in range(self.enemyCount)] 
        y = [random.randint(0, int(self.window.scene.height())) for i in range(self.enemyCount)]
        
        self.showWarning(x, y)
        
        for pos in list(zip(x, y)):
            self.spawnedEnemy.emit(int(pos[0]), int(pos[1]))

if __name__ == "__main__":
    a = EnemyWave("", 0, 1)
    
    a.seperate()