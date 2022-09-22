import pygame as pg
from util import Particle
import util


class Particles:
    def __init__(self, surface_size: [int, int]):
        self.particles: [Particle] = []
        self.surface_to_draw: pg.Surface = pg.surface.Surface(surface_size, pg.SRCALPHA)

    def draw(self):
        """
        パーティクルを再描画します。
        get_surface関数でもデフォルトで再描画されるので、
        通常は呼び出す必要はありません。
        :return:
        """
        self.surface_to_draw.fill(util.CLEAR)
        particles_poped_after = []
        for p_i, p in enumerate(self.particles):
            self.surface_to_draw.blit(p.calc_image(), p.get_pos())
            if p.is_disappeared():
                particles_poped_after.append(p_i)
        particles_poped_after.reverse()
        for p_i in particles_poped_after:
            self.particles.pop(p_i)

    def add(self, particle: Particle) -> None:
        self.particles.append(particle)

    def add_effect(self, image: pg.Surface, center_pos: [int, int],
                   disappearing_speed: float = 1, zoom_scale: float = 1) -> None:
        """
        指定された座標を中心に、拡大しながら消えていくパーティクルを生成します。
        """
        self.particles.append(
            Particle(image, center_pos, center=True, close_up=True,
                     disappearing_speed=disappearing_speed, zoom_scale=zoom_scale))

    def get_surface(self, update_particles: bool = True):
        """
        パーティクルが描画されたSurfaceを返します。
        デフォルトでパーティクルの再描画も行います。
        :param update_particles: パーティクルを再描画するか
        :return: Surface
        """
        if update_particles:
            self.draw()
        return self.surface_to_draw
