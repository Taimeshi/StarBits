from game_enums import *


class PlotData:
    
    def __init__(self, note_type: NoteType, column: int, measure: int, beat: int, splitting: int):
        self.note_type = note_type
        self.column = column
        self.measure = measure
        self.beat = beat
        self.splitting = splitting
    
    @property
    def measure_as_float(self) -> float:
        return self.measure + self.beat / self.splitting


class LongPointData(PlotData):
    
    def __init__(self, column: int, measure: int, beat: int, splitting: int, is_end: bool):
        super().__init__(NoteType.LONG, column, measure, beat, splitting)
        self.is_end = int(is_end)


class LongData:
    
    def __init__(self, column, measure: [int, int], beat: [int, int], splitting: [int, int]):
        self.start = LongPointData(column, measure[0], beat[0], splitting[0], False)
        self.end = LongPointData(column, measure[1], beat[1], splitting[1], True)
        self.column = column
    
    def points_as_plot(self):
        return [self.start, self.end]


class LongStartData(PlotData):
    
    def __init__(self, column: int, measure: int, beat: int, splitting: int):
        super().__init__(NoteType.LONG, column, measure, beat, splitting)
    
    def connect_long(self, end_measure: int, end_beat: int, end_splitting: int) -> LongData:
        return LongData(self.column, [self.measure, end_measure], [self.beat, end_beat],
                        [self.splitting, end_splitting])


class SpeedChangeData:
    
    def __init__(self, speed: float, measure: int, beat: int, splitting: int):
        self.speed = speed
        self.measure = measure
        self.beat = beat
        self.splitting = splitting
