import pygame as pg
import random
import math

import util


class SpreadingParticle(util.Particle):
    
    def __init__(self, pos: list, particle_image, colorful: bool):
        size = random.randint(16, 24)
        tmp_sf = pg.surface.Surface((64, 64), pg.SRCALPHA)
        p_num = random.randint(0, 3) if colorful else 0
        tmp_sf.blit(particle_image, [0, 0], pg.Rect(p_num * 64, 0, 64, 64))
        tmp_sf = pg.transform.smoothscale(tmp_sf, [size, size])
        super().__init__(tmp_sf, pos, close_up=True, disappearing_speed=1.3, center=True)
        self.spread_angle = math.radians(random.randint(0, 359))
        self.speed = random.random() * 8
    
    def calc_image(self):
        self.pos[0] += math.cos(self.spread_angle) * self.speed
        self.pos[1] += math.sin(self.spread_angle) * self.speed
        return super().calc_image()
