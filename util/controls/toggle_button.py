import pygame as pg
import util
from data_loader import *


class ToggleButton(util.InputControl):
	
	def __init__(self, resources: Resources):
		super().__init__()
		self.value: bool = False
		self.focused: bool = False
		self.corner_radius: int = 4
		self.hole_color: util.Color = util.GRAY
		self.off_color: util.Color = util.SYSTEM_GRAY
		self.on_color: util.Color = util.SYSTEM_BLUE
		self.rs = resources
		self.on_mark = self.rs.font(ARIAL_SMALL2_FONT).render("✓", True, util.WHITE)
		self.off_mark = self.rs.font(ARIAL_SMALL2_FONT).render("✗", True, util.GRAY)

	def update(self, keys, mouse):
		if self.value:
			self.focused = mouse.in_rect(self.x + self.x_offset, self.y + self.y_offset, int(self.width/2), self.height)
		else:
			self.focused = mouse.in_rect(self.x + self.x_offset + int(self.width / 2), self.y + self.y_offset,
			                             int(self.width / 2), self.height)
		if self.focused and mouse.just_pressed(0):
			self.value = not self.value
	
	def render(self, parent):
		if parent is None:
			return
		pg.draw.rect(parent, self.hole_color,
		             [self.x + self.width / 8, self.y + self.height / 3, self.width - self.width / 4, self.height / 3],
		             border_radius=self.corner_radius)
		if self.value:
			pg.draw.rect(parent, self.on_color, [self.x, self.y, self.width/2, self.height], border_radius=self.corner_radius)
			parent.blit(self.on_mark, [self.x + (self.width/2 - self.on_mark.get_width())/2,
			                           self.y + (self.height - self.on_mark.get_height())/2])
		else:
			pg.draw.rect(parent, self.off_color, [self.x + self.width / 2, self.y, self.width / 2, self.height],
			             border_radius=self.corner_radius)
			parent.blit(self.off_mark, [self.x + self.width / 2 + (self.width / 2 - self.off_mark.get_width()) / 2,
			                            self.y + (self.height - self.off_mark.get_height()) / 2])
