import pygame as pg
import util
from data_loader import *


class TextBox(util.InputControl):
    
    def __init__(self, resources: Resources):
        super().__init__()
        self._type: type = str
        self._value = ""
        self._value_tmp = ""
        self.focused: bool = False
        self.selecting: bool = False
        self.corner_radius: int = 4
        self.background: util.Color = util.SYSTEM_GRAY
        self.border_color: util.Color = util.GRAY
        self.border_color_focused: util.Color = util.SYSTEM_BLUE
        self.rs = resources
        self.font = self.rs.font(ARIAL_SMALL2_FONT)
    
    @property
    def type(self):
        return self._type
    
    @type.setter
    def type(self, value: type):
        self._type = value
        self.value = self.type(self.value)
    
    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, value):
        try:
            self._value = self.type(value)
        except ValueError:
            return
    
    def init_value(self, value):
        self._type = type(value)
        self.value = value
    
    def update(self, keys, mouse):
        self.focused = mouse.in_rect(*self.rect_on_display)
        if mouse.just_pressed(0):
            if self.focused and not self.selecting:
                self.selecting = True
                self._value_tmp = str(self.value)
            elif not self.focused and self.selecting:
                self.selecting = False
                self.value = self._value_tmp  # 変換に失敗したらそのまま
        if keys.just_pressed(pg.K_RETURN) and self.selecting:
            self.selecting = False
            self.value = self._value_tmp
        
        if self.selecting:
            if keys.just_pressed(pg.K_BACKSPACE):
                self._value_tmp = self._value_tmp[:-1]
            keys_name = "1234567890qwertyuiopasdfghjklzxcvbnm"
            for k in keys_name:
                if eval(f"keys.just_pressed(pg.K_{k})"):
                    self._value_tmp += k
            if keys.just_pressed(pg.K_PERIOD):
                self._value_tmp += "."
    
    def render(self, parent):
        if parent is None:
            return
        pg.draw.rect(parent, self.background, self.rect, border_radius=self.corner_radius)
        text_sf = self.font.render(str(self._value_tmp if self.selecting else self.value),
                                   True, util.BLACK)
        parent.blit(text_sf, [self.x + self.corner_radius, self.y + (self.height - text_sf.get_height()) / 2],
                    [0, 0, self.width - self.corner_radius * 2, 100])
        if self.focused or self.selecting:
            now_border_color = self.border_color_focused if self.selecting else self.border_color
            pg.draw.rect(parent, now_border_color, self.rect, width=2 + int(self.selecting),
                         border_radius=self.corner_radius)
