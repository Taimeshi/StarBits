
class Tap:
    
    def __init__(self, column: int, second_to_line: float, speed,
                 right_disable: bool = False, left_disable: bool = False):
        self.column = column
        self.second_to_line = second_to_line
        self.already_missed = False
        self.speed = speed
        self.right_disable = right_disable
        self.left_disable = left_disable
