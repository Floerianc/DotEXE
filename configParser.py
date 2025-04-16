from configparser import ConfigParser

class Config(ConfigParser):
    def __init__(self) -> None:
        super().__init__()
        self.read("_elementary.cfg")
        
        self.FPSLS = self.getint("UI", "FPS_LABEL_FONT_SIZE", fallback=16)
        self.MS = self.getint("Player", "MAX_SPEED", fallback=15)
        self.ACC = self.getfloat("Player", "ACCELERATION", fallback=1.6)
        self.FA = self.getfloat("Player", "FRICTION_AMPLIFIER", fallback=0.5)
        self.SIZE = self.getint("Player", "SIZE", fallback=6)
        self.MST = self.getfloat("Player", "MIN_SPEED_THRESHOLD", fallback=0.01)
        self.TL = self.getint("Player", "TRAIL_LENGTH", fallback=3)
        self.TOUT = self.getfloat("Input", "TIMEOUT", fallback=0.05)