import sys
import random
import PyQt5.QtWidgets as QtWidgets
import models
import keyboardHandler
import gameMonitor
import enemyWaves
from PyQt5.QtCore import (
    QTimer,
    QElapsedTimer,
)
from PyQt5.QtWidgets import (
    QLabel, 
    QGraphicsEllipseItem
)
from PyQt5.QtGui import (
    QFont, 
    QBrush,
    QColor
)
from typing import Union
from configParser import Config
from ui.ui_graphics import *

class Window(Ui_Frame):
    """The main Window of this application

    Args:
        Ui_Frame (_type_): Application PyQt
    """
    def __init__(
        self, 
        form
    ) -> None:
        """Initiates the whole Application

        Args:
            form (_type_): Form of Application
        """
        super().__init__()
        self.setupUi(form)
        self.scene = QtWidgets.QGraphicsScene(0, 0, self.graphicsView.width(), self.graphicsView.height())
        self.graphicsView.setScene(self.scene)
        
        self.objects = {
            'dynamicObjects': [],
        }
        self.enemies = lambda: self.objects['dynamicObjects'][1:]
        self.player = None
        self.config = Config()
        
        self.keyboardWorker = keyboardHandler.KeyboardWorker(self.objects)
        self.keyboardWorker.moving.connect(self.movePlayer)
        self.keyboardWorker.start()
        
        self.gameMonitor = gameMonitor.GameMonitor(self)
        self.gameMonitor.triggerWave.connect(self.spawnWave) # triggerWave is a signal that is emitted when the game monitor wants to spawn a wave of enemies
        self.gameMonitor.start()
        
        self.enemyTimer = QTimer()
        self.enemyTimer.timeout.connect(self.gameMonitor.triggerWave.emit) # emit the signal to spawn a wave of enemies
        self.enemyTimer.start(self.config.WC)
        
        self.waves = enemyWaves.EnemyWave(self, 0, 1)
        self.waves.spawnedEnemy.connect(self.spawnEnemy) # spawnMultipleEnemies spawns all the enemies for the current wave
        self.waves.spawnCircle.connect(self.spawnCircle)
        self.waves.removeCircle.connect(self.killCircle)
        
        self.FPStimer = QTimer()
        self.FPStimer.timeout.connect(self.displayFPS)
        self.FPStimer.start(0)
        
        self.elapsedTimer = QElapsedTimer()
        self.elapsedTimer.start()
        self.frameCount = 0
        
        self.constructUI()
        self.createPlayer()
    
    def constructUI(self) -> None:
        """Constructs UI elements
        """
        label_configs = [
            {
                "name": "FPSLabel", 
                "text": "FPS:                    ", 
                "font_size": self.config.FPSLS, 
                "style": None, 
                "position": (0, 0)
            },
            {
                "name": "HPLabel", 
                "text": "HP:                    ", 
                "font_size": self.config.FPSLS, 
                "style": "color: lime; font-weight: bold; background-color: black;", 
                "position": (0, 30)
            },
            {
                "name": "enemyLabel", 
                "text": "Enemies:                    ", 
                "font_size": self.config.FPSLS, 
                "style": "color: red; font-weight: bold; background-color: black;", 
                "position": (0, 60)
            },
            {
                "name": "BGLabel", 
                "text": "0", 
                "font_size": self.config.FPSLS * 4, 
                "style": "color: white; font-weight: bold; background-color: black;", 
                "geometry": (round((self.scene.width() / 2) - 500), round((self.scene.height() / 2) - 40), 1000, 80), 
                "alignment": QtCore.Qt.AlignmentFlag.AlignCenter
            },
        ]
        
        self.labels = {}
        for config in label_configs:
            label = QLabel(config["text"])
            font = QFont()
            font.setPointSize(config["font_size"])
            label.setFont(font)
            if config.get("style"):
                label.setStyleSheet(config["style"])
            if "position" in config:
                label.move(*config["position"])
            if "geometry" in config:
                label.setGeometry(*config["geometry"])
            if "alignment" in config:
                label.setAlignment(config["alignment"])
            self.scene.addWidget(label)
            self.labels[config["name"]] = label
    
    def save(self) -> None:
        """Saves your highscore in the _player.data file
        """
        with open("_player.data", "r", encoding="UTF-8") as file:
            content = file.read().strip()
            if content == "":
                old = 0
            else:
                old = float(content)
        
        if old <= self.player.score:
            with open("_player.data", "w", encoding="UTF-8") as file:
                file.write(str(self.player.score))
    
    def displayFPS(self) -> None:
        """Counts and displays FPS if needed
        """
        self.frameCount += 1
        elapsedTime = self.elapsedTimer.elapsed()
        
        if elapsedTime >= 1000: # ms
            fps = self.frameCount
            self.elapsedTimer.restart()
            self.frameCount = 0
            self.labels['FPSLabel'].setText(f"FPS: {fps:,}")
    
    def addObject(
        self, 
        obj: Union[models.DynamicPoint, models.DPAI]
    ) -> None:
        """Adds Object to the scene and dynamicObjects section

        Args:
            obj (Union[models.DynamicPoint, models.DPAI]): All sorts of dynamic Objects

        Raises:
            RuntimeError: If it couldn't be added for some reason, call this error. Might happen
                            due to a wrong class being entered
        """
        try:
            self.objects['dynamicObjects'].append(obj)
            self.scene.addItem(obj.graphics['rect'])
            if obj.graphics['trail']:
                self.scene.addItem(obj.graphics['trail'])
        except Exception as e:
            raise RuntimeError(f"Couldn't add Item! {e}")
    
    def createPlayer(self) -> None:
        """Creates the player. The player should always be added first!
        """
        # this should always be the first object added to the scene
        player = models.Player("CENTER", "CENTER", self.objects['dynamicObjects'], self.scene)
        player.died.connect(self.killPlayer)
        self.addObject(player)
        self.player = self.objects['dynamicObjects'][0]
    
    def killPlayer(self) -> None:
        """Kills the player by removing the graphics objects and other data related to it
        """
        if self.player:
            self.save()
            self.player.active = False
            
            length = len(self.player.graphics['trail'])
            for _ in range(length):
                self.scene.removeItem(self.player.graphics['trail'][0])
                self.player.graphics['trail'].remove(self.player.graphics['trail'][0])
            
            self.scene.removeItem(self.player.graphics['rect'])
            self.player.graphics['rect'] = None
            self.objects['dynamicObjects'].remove(self.player)
            self.player = None
    
    def killEnemy(
        self, 
        enemy: models.DPAI
    ) -> None:
        """Kills a specific enemy by removing the graphics object
        and stopping timers and deleting it off of the data in the app

        Args:
            enemy (models.DPAI): AI Enemy
        """
        print(f"Removing enemy {enemy} from scene")
        enemy.destructionTimer.stop()
        enemy.timer.stop()
        
        if enemy.graphics['rect']:
            self.scene.removeItem(enemy.graphics['rect'])
            enemy.graphics['rect'] = None
        if enemy.graphics['trail']:
            for point in enemy.graphics['trail']:
                self.scene.removeItem(point)
            enemy.graphics['trail'] = []
        
        self.objects['dynamicObjects'].remove(enemy)
        del enemy
    
    def spawnCircle(
        self, 
        circle: QGraphicsEllipseItem
    ) -> None:
        """Adds a circle to the Scene

        Args:
            circle (QGraphicsEllipseItem): A certain EllipseItem
        """
        self.scene.addItem(circle)
    
    def killCircle(
        self, 
        circle: QGraphicsEllipseItem
    ) -> None:
        """Removes circle from the scene

        Args:
            circle (QGraphicsEllipseItem): A specific EllipseItem
        """
        self.scene.removeItem(circle)
    
    def spawnEnemy(
        self, 
        x: int, 
        y: int
    ) -> None:
        """Spawns an Enemy at a specific location

        Args:
            x (int): X-Position
            y (int): Y-Position

        Raises:
            RuntimeError: If the player hasn't been added yet, the enemy can't be added either!
        """
        if self.player is None:
            raise RuntimeError("Player not created yet!")
        
        ai = models.DPAI(x, y, self.scene, self.enemies(), self.player)
        ai.removeSelfSignal.connect(self.killEnemy)
        self.addObject(ai)
    
    def spawnMultipleEnemies(
        self, 
        positions: list
    ) -> None:
        """Spawns multiple enemies at certain locations

        Args:
            positions (list): List of tuples containing the position. list[tuple[int | float]]

        Raises:
            RuntimeError: If the player hasn't been added yet, the enemy can't be added either!
        """
        if self.player is None:
            raise RuntimeError("Player not created yet!")
        
        for pos in positions:
            ai = models.DPAI(pos[0], pos[1], self.scene, self.enemies(), self.player)
            self.addObject(ai)
    
    def spawnWave(self) -> None:
        """Spawns a wave of enemies
        """
        if self.waves.waveType > len(self.waves.types) - 1:
            self.waves.waveType = 0
        self.waves.start()
        
        self.waves.enemyCount += 1
        self.player.step *= 2
    
    def movePlayer(
        self, 
        XDirection: int, 
        YDirection: int
    ) -> None:
        """Moves the player graphically using a direction vector

        Args:
            XDirection (int): Direction on the x-axis
            YDirection (int): Direction on the y-axis
        """
        if XDirection == -10 and YDirection == -10: self.killPlayer()
        if self.player and self.player.active:
            self.player.playerMove(XDirection, YDirection)
    
    def testing2(self) -> None:
        for _ in range(10):
            ai = models.DPAI("RANDOM", "RANDOM", self.scene, self.enemies(), self.player)
            self.addObject(ai)
    
    def testing3(self) -> None:
        self.player.setPosition(self.player.pos[0] + random.randint(-10, 10), self.player.pos[1] + random.randint(-10, 10))

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QMainWindow()
    
    ui = Window(Form)
    
    Form.show()
    sys.exit(app.exec_())

# TODO:     Split up Config into different sections for certain files
# TODO:     Audio
# TODO:     Highscore
# TODO:     What happens after death?