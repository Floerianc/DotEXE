from configparser import ConfigParser

class Config(ConfigParser):
    """Loads the config of the configfile

    Args:
        ConfigParser (_type_): uhh.. it's a Configparser
    """
    def __init__(self) -> None:
        super().__init__()
        self.read("_player.cfg")
        
        self.FPSLS = self.getint("UI", "FPS_LABEL_FONT_SIZE", fallback=16)
        self.MS = self.getint("Player", "MAX_SPEED", fallback=15)
        self.ACC = self.getfloat("Player", "ACCELERATION", fallback=1.6)
        self.FA = self.getfloat("Player", "FRICTION_AMPLIFIER", fallback=0.5)
        self.SIZE = self.getint("Player", "SIZE", fallback=6)
        self.MST = self.getfloat("Player", "MIN_SPEED_THRESHOLD", fallback=0.01)
        self.TL = self.getint("Player", "TRAIL_LENGTH", fallback=3)
        self.TA = self.getint("Player", "TRAIL_AMOUNT", fallback=25)
        self.TOUT = self.getfloat("Input", "TIMEOUT", fallback=0.05)
        self.HP = self.getint("Player", "HP", fallback=100)
        self.MHP = self.getint("Player", "MAX_HP", fallback=100)
        
        self.EMS = self.getint("Enemy", "MAX_SPEED", fallback=10)
        self.EA = self.getfloat("Enemy", "ACCELERATION", fallback=1.2)
        self.ES = self.getint("Enemy", "SIZE", fallback=10)
        
        self.DC = self.getfloat("Game", "DAMAGE_COOLDOWN", fallback=0.25)
        self.WC = self.getint("Game", "WAVE_COOLDOWN", fallback=10000)
        self.IE = self.getint("Game", "INITIAL_ENEMIES", fallback=1)
        self.IW = self.getint("Game", "INITIAL_WAVE", fallback=0)