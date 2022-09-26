import pygame as pg


class Mouse:
    
    def __init__(self):
        self.pos = pg.mouse.get_pos()
        self.pressed = pg.mouse.get_pressed()
        self.pressed_past = None
    
    def update(self):
        self.pressed_past = self.pressed
        self.pos = pg.mouse.get_pos()
        self.pressed = pg.mouse.get_pressed()
    
    def in_rect(self, x: int, y: int, width: int, height: int):
        return pg.Rect(x, y, width, height).collidepoint(*self.pos)
    
    def just_pressed(self, num: int):
        return bool(self.pressed[num] and not self.pressed_past[num])
    
    def pressing(self, num: int):
        return self.pressed[num]
    
    @property
    def x(self):
        return self.pos[0]
    
    @property
    def y(self):
        return self.pos[1]
