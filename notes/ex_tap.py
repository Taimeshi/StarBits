import notes
from enum import Enum, auto


class ExTapCondition(Enum):
    NEITHER = auto()
    ONLY_KEY = auto()
    ONLY_SPACE = auto()


class ExTap(notes.Tap):
    
    def __init__(self, column: int, second_to_line: float, speed,
                 right_disable: bool = False, left_disable: bool = False):
        super().__init__(column, second_to_line, speed, right_disable, left_disable)
        self.condition = ExTapCondition.NEITHER
        self.latency = 0
