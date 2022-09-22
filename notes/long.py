
class Long:
    
    def __init__(self, column: int, second_to_line: [float, float], speed,
                 right_disable: bool = False, left_disable: bool = False):
        self.column = column
        self.start_second_to_line = second_to_line[0]
        self.end_second_to_line = second_to_line[1]
        self.already_missed = False
        self.start_tapped = False
        self.speed = speed
        self.right_disable = right_disable
        self.left_disable = left_disable
