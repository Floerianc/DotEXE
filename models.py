from PyQt5.QtWidgets import (
    QGraphicsRectItem,
    QGraphicsScene
)
from PyQt5.QtGui import (
    QColor, 
    QBrush,
)
from PyQt5.QtCore import QTimer
from configParser import Config
from itertools import repeat

class Position:
    def __init__(self, x: float, y: float) -> None:
        self.pos = [x, y]

class DynamicPoint(Position):
    def __init__(
        self, 
        x, 
        y, 
        scene: QGraphicsScene,
        brush: QBrush = QBrush(QColor(255, 255, 255))
    ):
        super().__init__(x, y)
        
        self.config = Config()
        self.scene = scene
        
        self.speed = [0, 0]
        self.maxSpeed = self.config.MS
        self.acceleration = self.config.ACC
        self.frictionAmplifier = self.config.FA # 50%
        self.brush = brush
        
        self.graphics = {
            'rect': QGraphicsRectItem(0, 0, self.config.SIZE, self.config.SIZE),
            'trail': []
        }
        self.graphics['rect'].setBrush(self.brush)
        
        # the lambda evaluates the values even when they change
        self.debugstring = lambda: f"DynamicPoint: {self.pos[0]}, {self.pos[1]} | Velocity: {self.speed[0]}, {self.speed[1]}, Trail-Position: {self.pos[0] - (self.speed[0] * 10)}, {self.pos[1] - (self.speed[1] * 10)}"
        self.setGraphicsitem()
    
    def setSpeed(self, newX: float, newY: float) -> list:
        return [newX - self.pos[0], newY - self.pos[1]]
    
    def setPosition(self, x: float, y: float):
        self.speed = self.setSpeed(x, y)
        self.pos = [x, y]
        self.setGraphicsitem()
    
    def validate_speed(self, x_dir: int, y_dir: int) -> list:
        xVel = max(-self.maxSpeed, min(self.speed[0] + x_dir * self.acceleration, self.maxSpeed))
        yVel = max(-self.maxSpeed, min(self.speed[1] + y_dir * self.acceleration, self.maxSpeed))
        return xVel, yVel
    
    def slowDownPlayer(self) -> None:
        if self.speed[0] > 0:
            self.speed[0] -= self.frictionAmplifier
        elif self.speed[0] < 0:
            self.speed[0] += self.frictionAmplifier
        
        if self.speed[1] > 0:
            self.speed[1] -= self.frictionAmplifier
        elif self.speed[1] < 0:
            self.speed[1] += self.frictionAmplifier
        
        if abs(self.speed[0]) < self.config.MST:
            self.speed[0] = 0
        if abs(self.speed[1]) < self.config.MST:
            self.speed[1] = 0
        
        self.setGraphicsitem()
    
    def applyFriction(self, rawXDirection: float, rawYDirection: float) -> tuple:
        if rawXDirection == 0 and rawYDirection == 0:
            self.slowDownPlayer()
            return 0, 0
        
        frictionX = rawXDirection - self.frictionAmplifier
        frictionY = rawYDirection - self.frictionAmplifier
        return frictionX, frictionY
    
    def calculateMovementSpeed(self, XDirection: int, YDirection: int) -> list:
        # fixedXDirection, fixedYDirection = self.applyFriction(XDirection, YDirection)
        if XDirection == 0 and YDirection == 0:
            self.slowDownPlayer()
            return self.speed[0], self.speed[1]
        return self.validate_speed(XDirection, YDirection)
    
    def move(self, x_direction: int, y_direction: int) -> None:
        # [0, -1]
        xVel, yVel = self.calculateMovementSpeed(x_direction, y_direction)
        
        newX = self.pos[0] + xVel
        newY = self.pos[1] + yVel
        
        self.speed[0] = xVel
        self.speed[1] = yVel
        
        self.pos = [newX, newY]
        self.addTrajectory()
        self.setGraphicsitem()
    
    def setGraphicsitem(self) -> None:
        self.graphics['rect'].setPos(self.pos[0], self.pos[1])
        self.graphics['rect'].update()
        self.renderTrajectory()
        # print(self.debugstring(), end="\r")
    
    def addTrajectory(self) -> None:
        x, y = self.pos
        
        TP = QGraphicsRectItem(x, y, self.config.SIZE, self.config.SIZE) # TP = trajectory point
        TP.setBrush(self.brush)
        
        if len(self.graphics['trail']) >= 26:
            deprecatedPoint = self.graphics['trail'].pop(0)
            self.scene.removeItem(deprecatedPoint)
        
        self.graphics['trail'].append(TP)
        self.scene.addItem(TP)
    
    def renderTrajectory(self) -> None:
        for point in self.graphics['trail']:
            point.update()

class DPAI(DynamicPoint):   # dynamic point artificial intelligence
    def __init__(self, x, y, scene, brush = QBrush(QColor(255, 255, 255))):
        super().__init__(x, y, scene, brush)
        self.timer = QTimer()
        self.timer.timeout.connect(lambda: self.move(-1, 0))
        self.timer.start(125)
    
    def testing(self) -> None:
        pass

class Line:
    def __init__(self, size: int):
        self.size = size
        self.graphicsItem = None
        assert size > 0 and isinstance(size, int), "Size must be a positive integer!"

if __name__ == "__main__":
    point = DynamicPoint(10, 10)
    
    print(point.calculateMovementSpeed(-1, -1))
    print(point.calculateMovementSpeed(0, 0))
    print(point.calculateMovementSpeed(1, 1))