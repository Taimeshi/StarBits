import pygame as pg
from abc import ABCMeta, abstractmethod

import util


class InputControl(metaclass=ABCMeta):
	
	def __init__(self):
		self.x: int = 0  # 描画するx座標
		self.y: int = 0  # 描画するy座標
		self.width: int = 0  # 幅
		self.height: int = 0  # 高さ
		self.x_offset: int = 0  # 画面の左端とparentの左端の差のx座標
		self.y_offset: int = 0  # 画面の左端とparentの左端の差のy座標
	
	@property
	def pos(self):
		return [self.x, self.y]
	
	@pos.setter
	def pos(self, value: list[int, int] | tuple[int, int]):
		self.x, self.y = value
	
	@property
	def size(self):
		return [self.width, self.height]
	
	@size.setter
	def size(self, value: list[int, int] | tuple[int, int]):
		if min(*value) < 0:
			raise ValueError("Invalid size")
		self.width, self.height = value
	
	@property
	def offset(self):
		return [self.x_offset, self.y_offset]
	
	@offset.setter
	def offset(self, value: list[int, int] | tuple[int, int]):
		self.x_offset, self.y_offset = value
	
	@property
	def rect(self):
		return [*self.pos, *self.size]
	
	@rect.setter
	def rect(self, value: list[int, int, int, int] | tuple[int, int, int, int]):
		self.x, self.y, self.width, self.height = value
	
	@property
	def rect_on_display(self):
		return [self.x + self.x_offset, self.y + self.y_offset, self.width, self.height]
	
	@abstractmethod
	def render(self, parent: pg.Surface) -> None:
		pass
	
	@abstractmethod
	def update(self, keys: util.Keys, mouse: util.Mouse) -> None:
		pass
