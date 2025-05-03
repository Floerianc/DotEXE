import random
import math
from typing import Union
from PyQt5.QtWidgets import (
    QGraphicsRectItem,
    QGraphicsScene,
)
from PyQt5.QtGui import (
    QColor, 
    QBrush,
)
from PyQt5.QtCore import (
    QTimer, 
    QObject,
    pyqtSignal
)
from configParser import Config

class Position:
    """This is a goofy little class to save a position in a list
    """
    def __init__(
        self, 
        x: float, 
        y: float
    ) -> None:
        self.pos = [x, y]

class DynamicPoint(Position):
    """This is what the Player-class is based on.
    A point, which inherits the position variable,
    which is able to move, apply forces on like friction and other
    stuff which could be beneficial for a player.

    Args:
        Position (Position): Position class
    """
    def __init__(
        self, 
        x: int,
        y: int,
        scene: QGraphicsScene,
        brush: QBrush = QBrush(QColor(255, 255, 255)),
        trailBrush: QBrush = QBrush(QColor(120, 120, 120, 120))
    ) -> None:
        """This initiates the DynamicPoint class

        Args:
            x (int): X-Position
            y (int): Y-Position
            scene (QGraphicsScene): Graphicsscene it should be added to
            brush (QBrush, optional): Color of the square. Defaults to QBrush(QColor(255, 255, 255)).
            trailBrush (QBrush, optional): Color of the trail. Defaults to QBrush(QColor(120, 120, 120, 120)).
        """
        self.config = Config()
        self.scene = scene
        
        self.speed = [0, 0]
        
        self.size = self.config.SIZE
        self.maxSpeed = self.config.MS
        self.acceleration = self.config.ACC
        self.frictionAmplifier = self.config.FA
        self.minimumSpeed = self.config.MST
        
        self.brush = brush
        self.trailBrush = trailBrush
        
        self.graphics = {
            'rect': QGraphicsRectItem(0, 0, self.size, self.size),
            'trail': [],
        }
        self.graphics['rect'].setBrush(self.brush)
        
        super().__init__(x, y)
        if isinstance(x, str):
            self.interpretPosition(x)
        elif isinstance(y, str):
            self.interpretPosition(y)
        
        # the lambda evaluates the values even when they change
        self.debugstring = lambda: f"DynamicPoint: {self.pos[0]}, {self.pos[1]} | Velocity: {self.speed[0]}, {self.speed[1]}, Trail-Position: {self.pos[0] - (self.speed[0] * 10)}, {self.pos[1] - (self.speed[1] * 10)}"
    
    def interpretPosition(
        self, 
        types: str
    ) -> None:
        """Interprets the position if it's not a numerical value
        
        It is able to interpret different strings as a specific position
        usually relative to the Graphicsscene.
        
        Supported types:
        
        - CENTER
        - TOPLEFT
        - TOPRIGHT
        - BOTTOMLEFT
        - BOTTOMRIGHT
        - RANDOM

        Args:
            types (str): String to be interpreted
        """
        positions = {
            "CENTER": (
                self.scene.width() / 2 - self.size / 2,
                self.scene.height() / 2 - self.size / 2
            ),
            "TOPLEFT": (
                0, 
                0
            ),
            "TOPRIGHT": (
                self.scene.width() - self.size,
                0
            ),
            "BOTTOMLEFT": (
                0,
                self.scene.height() - self.size
            ),
            "BOTTOMRIGHT": (
                self.scene.width() - self.size,
                self.scene.height() - self.size
            ),
            "RANDOM": (
                random.randint(0, int(self.scene.width())) - self.size,
                random.randint(0, int(self.scene.height())) - self.size
            )
        }
        x, y = positions.get(types)
        self.pos = [x, y]
    
    def setPosition(
        self, 
        x: float, 
        y: float
    ) -> None:
        """Sets the position of the Point and its 
        graphical equivalent

        Args:
            x (float): X-Position
            y (float): Y-Position
        """
        self.pos = [x, y]
        self.setGraphicsitem()
    
    def validate_speed(
        self, 
        x_dir: int, 
        y_dir: int
    ) -> list:
        """Validates the speed: is it higher/lower than the maximum/minimum?

        Args:
            x_dir (int): Direction on the x-axis
            y_dir (int): Direction on the y-axis

        Returns:
            list: List of speeds on the x- and y-axis
        """
        xVel = max(-self.maxSpeed, min(self.speed[0] + x_dir * self.acceleration, self.maxSpeed))
        yVel = max(-self.maxSpeed, min(self.speed[1] + y_dir * self.acceleration, self.maxSpeed))
        return xVel, yVel
    
    def slowDownPlayer(self) -> None:
        """This slows down the player if there's no direction vector given.
        
        This can happen when the player is not pressing any keys.
        
        This prevents the DynamicPoint to just drift off when you press nothing.
        Therefore, it slows itself down to stand still.
        
        This automatically updates the graphics item.
        """
        if self.speed[0] > 0:
            self.speed[0] -= self.frictionAmplifier
        elif self.speed[0] < 0:
            self.speed[0] += self.frictionAmplifier
        
        if self.speed[1] > 0:
            self.speed[1] -= self.frictionAmplifier
        elif self.speed[1] < 0:
            self.speed[1] += self.frictionAmplifier
        
        if abs(self.speed[0]) < self.minimumSpeed:
            self.speed[0] = 0
        if abs(self.speed[1]) < self.minimumSpeed:
            self.speed[1] = 0
        
        self.setGraphicsitem()
    
    def applyFriction(
        self, 
        rawXDirection: float, 
        rawYDirection: float
    ) -> tuple:
        """Applies friction to the raw direction vector values

        Args:
            rawXDirection (float): Direction on the x-axis
            rawYDirection (float): Direction on the y-axis

        Returns:
            tuple: Direction in x- and y
        """
        if rawXDirection == 0 and rawYDirection == 0:
            self.slowDownPlayer()
            return 0, 0
        
        frictionX = rawXDirection - self.frictionAmplifier
        frictionY = rawYDirection - self.frictionAmplifier
        return frictionX, frictionY
    
    def calculateMovementSpeed(
        self, 
        XDirection: int, 
        YDirection: int
    ) -> list:
        """Calculates the speed of the DynamicPoint

        Args:
            XDirection (int): Direction on the x-axis
            YDirection (int): Direction on the y-axis

        Returns:
            list: [x, y] move in pixels
        """
        if XDirection == 0 and YDirection == 0:
            self.slowDownPlayer()
            return self.speed[0], self.speed[1]
        return self.validate_speed(XDirection, YDirection)
    
    def checkBounds(
        self, 
        newX: int | float, 
        newY: int | float
    ) -> list:
        """Checks if the Object is out-of-bounds (out of viewport)

        Args:
            newX (int | float): New x-position
            newY (int | float): New y-position

        Returns:
            list: Returns rounded value of new position (because fuck floats)
        """
        if newX < 0:
            newX = 0
        elif newX > self.scene.width() - self.size:
            newX = self.scene.width() - self.size
        
        if newY < 0:
            newY = 0
        elif newY > self.scene.height() - self.size:
            newY = self.scene.height() - self.size
        return [round(newX), round(newY)]
    
    def move(
        self, 
        XDirection: int, 
        YDirection: int
    ) -> None:
        """Moves the DynamicPoint with a direction vector given
        
        The direction vector allows a 8-bit movement because the
        direction on the x- and y-axis can only be either -1, 0 or 1

        Args:
            XDirection (int): _description_
            YDirection (int): _description_
        """
        xVel, yVel = self.calculateMovementSpeed(XDirection, YDirection)
        
        newX = self.pos[0] + xVel
        newY = self.pos[1] + yVel
        
        self.speed[0] = xVel
        self.speed[1] = yVel
        
        self.pos = self.checkBounds(newX, newY)
        self.addTrajectory()
        self.setGraphicsitem()
    
    def setGraphicsitem(self) -> None:
        """Updates the graphicsitem by updating the rectangle and trail
        """
        if self.graphics:
            self.graphics['rect'].setPos(self.pos[0], self.pos[1])
            self.graphics['rect'].update()
            self.renderTrajectory()
    
    def addTrajectory(self) -> None:
        """Adds a point to the trail
        """
        x, y = self.pos
        
        TP = QGraphicsRectItem(x, y, self.size, self.size) # TP = trajectory point
        TP.setBrush(self.trailBrush)
        
        if len(self.graphics['trail']) >= self.config.TA:
            deprecatedPoint = self.graphics['trail'].pop(0)
            self.scene.removeItem(deprecatedPoint)
        
        self.graphics['trail'].append(TP)
        self.scene.addItem(TP)
    
    def renderTrajectory(self) -> None:
        """Renders the trail
        """
        for point in self.graphics['trail']:
            point.update()

class DPAI(DynamicPoint, QObject):   # dynamic point artificial intelligence
    """This is the enemy AI, it uses the DynamicPoint and QObject base
    to utilize the movement and pyqtSignals

    Args:
        DynamicPoint (DynamicPoint): DynamicPoint class
        QObject (QObject): QObject class
    """
    removeSelfSignal = pyqtSignal(object)
    
    def __init__(
        self, 
        x: int, 
        y: int, 
        scene, 
        enemies: list[DynamicPoint],
        player: DynamicPoint,
        brush: QBrush = QBrush(QColor(255, 0, 0)),
        trailBrush: QBrush = QBrush(QColor(255, 0, 0, 120))
    ) -> None:
        """Initiates the Enemy AI

        Args:
            x (int): X-Position
            y (int): Y-Position
            scene (_type_): Graphicsscene they're drawn to
            enemies (list[DynamicPoint]): other enemies
            player (DynamicPoint): player
            brush (QBrush, optional): Color of the main rect. Defaults to QBrush(QColor(255, 0, 0)).
            trailBrush (QBrush, optional): Color of the trail. Defaults to QBrush(QColor(255, 0, 0, 120)).
        """
        super().__init__(x, y, scene, brush, trailBrush)
        QObject.__init__(self)
        
        self.player = player
        self.otherEnemies = enemies
        self.maxSpeed = self.config.EMS
        self.acceleration = self.config.EA
        self.size = self.config.ES
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.chasePlayer)
        self.timer.start(25)
        
        self.destructionTimer = QTimer()
        self.destructionTimer.timeout.connect(self.removeSelf)
        self.destructionTimer.start(15000)  # 15 seconds
    
    def removeSelf(self) -> None:
        """Emits a signal to the Window class to remove 
        the Enemy entirely from the program
        """
        self.removeSelfSignal.emit(self)
    
    def getDirectionalVector(
        self, 
        targetX: int, 
        targetY: int
    ) -> list[float]:
        """Gets the direction vector to a position

        Args:
            targetX (int): X-Position
            targetY (int): Y-Position

        Returns:
            list[float]: direction vector
        """
        dx = targetX - self.pos[0]     # difference in x
        dy = targetY - self.pos[1]     # difference in y
        distance = math.hypot(dx, dy)  # distance

        if distance == 0:
            return [0.0, 0.0]
        return self.addWander(dx / distance, dy / distance)
    
    def addWander(
        self, 
        xDir: float, 
        yDir: float
    ) -> list[float]:
        """Adds a little bit of wander to the movement

        Args:
            xDir (float): Raw direction on the x-axis
            yDir (float): Raw direction on the y-axis

        Returns:
            list[float]: New x and y directions
        """
        return [xDir + random.uniform(-0.25, 0.25), yDir + random.uniform(-0.25, 0.25)]
    
    def chasePlayer(self) -> None:
        """Tells the Enemy to chase the player
        """
        xDir, yDir = self.getDirectionalVector(self.player.pos[0], self.player.pos[1])
        self.move(xDir, yDir)

class Player(DynamicPoint, QObject):
    """This is the Player: it inherits the DynamicPoint 
    and QObject to emit signals
    """
    died = pyqtSignal()
    
    def __init__(
        self, 
        x: int, 
        y: int,
        enemies: list[DPAI], 
        scene,
        brush = QBrush(QColor(255, 255, 255)),
        trailBrush = QBrush(QColor(255, 255, 255, 120))
        ):
        """Initiates the player

        Args:
            x (int): X-Position
            y (int): Y-Position
            enemies (list[DPAI]): List of enemies in the game
            scene (_type_): Graphicsscene it should be drawn to
            brush (_type_, optional): Color of the square. Defaults to QBrush(QColor(255, 255, 255)).
            trailBrush (_type_, optional): Color of the trail. Defaults to QBrush(QColor(255, 255, 255, 120)).
        """
        super().__init__(x, y, scene, brush, trailBrush)
        QObject.__init__(self)
        
        self.scene = scene
        self.enemies = lambda: enemies[1:] if len(enemies) > 1 else []
        
        self.active = True
        self.hp = self.config.HP
        self.maxHP = self.config.MHP
        self.score = 0
        self.step = 0.01
    
    def collidesWithItem(
        self, 
        item: DPAI
    ) -> bool:
        """Checks if it collides with a certain item (usually DPAIs)

        Args:
            item (DPAI): Usually DPAIs (enemy AIs)

        Returns:
            bool: True if collides, False if not
        """
        if (self.pos[0] < item.pos[0] + item.size and
            self.pos[0] + self.size > item.pos[0] and
            self.pos[1] < item.pos[1] + item.size and
            self.pos[1] + self.size > item.pos[1]):
            return True
        return False
    
    def checkCollisions(self) -> bool:
        """Checks if there any collisions with other enemies

        Returns:
            bool: True if collides, False if not
        """
        for obj in self.enemies():
            if self.collidesWithItem(obj):
                print(f"Collision detected with {obj} at {self.pos[0]}, {self.pos[1]}")
                return True
        return False
    
    def playerMove(
        self, 
        xDir: int, 
        yDir: int
    ) -> None:
        """Moves the player, respecting the check for collisions

        Args:
            xDir (int): Direction on the x-axis
            yDir (int): Direction on the y-axis
        """
        self.move(xDir, yDir)
        if self.checkCollisions():
            self.hp -= 1
            if self.hp <= 0:
                self.died.emit()

class Line:
    def __init__(
        self, 
        size: int
    ) -> None:
        self.size = size
        self.graphicsItem = None
        assert size > 0 and isinstance(size, int), "Size must be a positive integer!"

if __name__ == "__main__":
    point = DynamicPoint(10, 10, None)
    
    
    ai = DPAI(25, 25, None, [None], None)
    p = Player(10, 10, [ai], None)
    
    print(f"size ai: {ai.size}, size player: {p.size}")
    
    p.checkCollisions()