import pygame as pg


class Particle:
    
    def __init__(self, image: pg.Surface, pos: list,
                 center: bool = False, close_up: bool = False,
                 disappearing_speed: float = 1, zoom_scale: float = 1):
        self.image = image
        self.alpha = 255
        self.disappearing_speed = disappearing_speed * 10
        self.close_up = close_up
        self.center = center
        self.pos = pos
        self.zoom = 1
        self.zoom_scale = zoom_scale
    
    def calc_image(self) -> pg.Surface:
        self.alpha -= self.disappearing_speed
        alpha_image = self.image.copy()
        if self.close_up:
            self.zoom *= 1.01 ** self.zoom_scale
            alpha_image = pg.transform.rotozoom(alpha_image, 0, self.zoom)
        alpha_image.set_alpha(self.alpha)
        return alpha_image
    
    def is_disappeared(self) -> bool:
        return self.alpha <= 0
    
    def get_pos(self):
        return [self.pos[0] - self.image.get_width()/2*self.zoom, self.pos[1] - self.image.get_height()/2*self.zoom] \
            if self.center else self.pos
