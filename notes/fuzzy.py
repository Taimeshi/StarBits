import notes


class Fuzzy(notes.Tap):
    
    def __init__(self, column: int, second_to_line: float, speed,
                 right_disable: bool = False, left_disable: bool = False):
        super().__init__(column, second_to_line, speed, right_disable, left_disable)
        self.pressed_before = False
        self.temp_judge = None
