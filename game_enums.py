from enum import Enum, auto


class Index(Enum):
    START = auto()
    MODE_SELECT = auto()
    SETTING = auto()
    SONG_SELECT = auto()
    PLAY = auto()
    PAUSE = auto()
    RESULT = auto()


class Judge(Enum):
    PERFECT = auto()
    GOOD = auto()
    MISS = auto()
    LONG_PRESSING = auto()
    
    def better_than(self, value):
        if self == Judge.LONG_PRESSING or value == Judge.LONG_PRESSING:
            raise ValueError("LONG_PRESSING is unable to compare")
        return self.value < value.value


class NoteType(Enum):
    TAP = "1"
    EX_TAP = "2"
    LONG = auto()
    FUZZY = "5"


class Difficulty(Enum):
    EASY = 0
    HARD = 1
    IMP = 2


class GameMode(Enum):
    SONG_SELECT = 0
    CHALLENGE = 1
    SETTING = 2
    EXIT = 3

    def get_next(self):
        for gm in GameMode:
            if gm.value == (self.value + 1) % len(GameMode):
                return gm

    def get_past(self):
        for gm in GameMode:
            if gm.value == (self.value - 1) % len(GameMode):
                return gm


class ClearCondition(Enum):
    ALL_PERFECT = auto()
    FULL_COMBO = auto()
    CLEAR = auto()
    FAILED = auto()
