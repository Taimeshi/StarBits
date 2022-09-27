from game_enums import *
import util


class PlotData:
    
    def __init__(self, note_type: NoteType, column: int, measure: int, beat: int, splitting: int):
        self.note_type = note_type
        self.column = column
        self.measure = measure
        self.beat = beat
        self.splitting = splitting
        self.selecting: bool = False
    
    def move_plot(self, column: int, measure: int, beat: int, splitting: int):
        self.column = column
        self.measure = measure
        self.beat = beat
        self.splitting = splitting
    
    def mouse_on_plots(self, mouse: util.Mouse, scroll: int, pixel_per_measure: int) -> bool:
        return mouse.in_rect(250 + 50 + self.column * 100 - 50,
                             610 + scroll - (self.measure_as_float * pixel_per_measure) - 20,
                             100, 40)
    
    @property
    def measure_as_float(self) -> float:
        return self.measure + self.beat / self.splitting


class LongPointData(PlotData):
    
    def __init__(self, column: int, measure: int, beat: int, splitting: int, is_end: bool):
        super().__init__(NoteType.LONG, column, measure, beat, splitting)
        self.is_end = int(is_end)
    
    def move_plot(self, _, measure: int, beat: int, splitting: int):
        self.measure = measure
        self.beat = beat
        self.splitting = splitting


class LongData:
    
    def __init__(self, column, measure: [int, int], beat: [int, int], splitting: [int, int]):
        self.start = LongPointData(column, measure[0], beat[0], splitting[0], False)
        self.end = LongPointData(column, measure[1], beat[1], splitting[1], True)
        self.column = column
    
    def points_as_plot(self):
        return [self.start, self.end]


class SpeedChangeData:
    
    def __init__(self, speed: float, measure: int, beat: int, splitting: int):
        self.speed = speed
        self.measure = measure
        self.beat = beat
        self.splitting = splitting

    @property
    def measure_as_float(self) -> float:
        return self.measure + self.beat / self.splitting
