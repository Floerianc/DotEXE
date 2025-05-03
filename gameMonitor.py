import time
from PyQt5.QtCore import (
    QThread,
    pyqtSignal
)
from typing import TYPE_CHECKING
from configParser import Config

if TYPE_CHECKING:
    from main import Window

class GameMonitor(QThread):
    """This class controls some of the GUI elements for the cool UI :)

    Args:
        QThread (QObject): It's another seperate QThread
    """
    triggerWave = pyqtSignal()
    
    def __init__(
        self, 
        window: 'Window'
    ) -> None:
        """Initiates the GameMonitor

        Args:
            window (Window): The Window class to access GUI elements
        """
        super().__init__()
        self.config = Config()
        self.window = window
    
    def run(self) -> None:
        """This is what the game constantly runs in the background
        """
        time.sleep(1) # delay
        while True:
            if self.window.player:
                self.window.labels['HPLabel'].setText(f"HP: {self.window.player.hp}/{self.window.player.maxHP}")
                self.window.labels['BGLabel'].setText(f"{str(self.window.player.score)}")
                self.window.player.score = round(self.window.player.score + self.window.player.step, 2)
            else:
                self.window.labels['HPLabel'].setText("Player died")
            self.window.labels['enemyLabel'].setText(f"Enemies: {len(self.window.objects['dynamicObjects']) - 1}")
            time.sleep(0.25)