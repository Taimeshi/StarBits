from abc import ABCMeta, abstractmethod

import util
from data_loader import *


COLUMN_HEIGHT = 55


class Setting:
	
	def __init__(self, setting_dict: dict, resources: Resources):
		self.origin_content = SettingCategory("<Setting>", setting_dict, 0, None, resources)
		self._scroll = 0
		self.rs = resources
	
	@property
	def scroll(self):
		return self._scroll
	
	@scroll.setter
	def scroll(self, value):
		self._scroll = value
		self._scroll = min(0, self._scroll)
		self._scroll = max(-self.origin_content.count_contents()*COLUMN_HEIGHT + 700, self._scroll)
	
	def get_surface(self) -> pg.Surface:
		"""
		項目を描画したSurfaceを返します。
		"""
		setting_sf = SettingSurface(self.origin_content.count_contents())
		self.origin_content.draw(setting_sf, self._scroll)
		return setting_sf.surface
	
	def update(self, keys: util.Keys, mouse: util.Mouse) -> None:
		self.origin_content.update(keys, mouse)
	
	def get_as_dict(self) -> dict:
		k, result = self.origin_content.get_as_dict()
		return result


class SettingSurface:
	
	def __init__(self, contents_count: int):
		self.index = 0
		self.surface = pg.surface.Surface((900, COLUMN_HEIGHT * contents_count), pg.SRCALPHA)
	
	def draw(self, surface: pg.Surface):
		self.surface.blit(surface, [0, COLUMN_HEIGHT * self.index])
		self.index += 1
	
	def get_current_pos(self) -> list[int, int]:
		return [0, COLUMN_HEIGHT * self.index]


class SettingContentBase(metaclass=ABCMeta):
	"""
	設定の要素です。
	"""
	def __init__(self, text: str, indent: int, parent, resources: Resources):
		self.text: str = text
		self.indent: int = indent
		self.parent: SettingContentBase | Setting = parent
		self.rs = resources
	
	def get_origin(self):
		return self.parent.get_origin() if self.parent is not None else self
	
	@abstractmethod
	def print(self) -> None:
		"""
		この要素より下の要素をすべて書き出します。
		すべての要素に連鎖的に実行されます。
		"""
		pass
	
	@abstractmethod
	def count_contents(self) -> int:
		"""
		この要素より下の要素の数を取得します。
		すべての要素に連鎖的に実行されます。
		"""
		pass
	
	@abstractmethod
	def draw(self, setting_sf: SettingSurface, scroll: int) -> None:
		"""
		SettingSurfaceに、この要素とこの項目より下の要素を描画します。
		すべての要素に連鎖的に実行されます。
		:param setting_sf: 描画するSettingSurface
		:param scroll: スクロール
		"""
		pass
	
	@abstractmethod
	def update(self, keys: util.Keys, mouse: util.Mouse) -> None:
		"""
		コントロールなどの処理を行います。
		すべての要素に連鎖的に実行されます。
		:param keys: Keysオブジェクト
		:param mouse: Mouseオブジェクト
		"""
		pass
	
	@abstractmethod
	def get_as_dict(self) -> list[object, object]:
		pass


class SettingContent(SettingContentBase):
	"""
	設定の項目です。
	"""
	
	def __init__(self, text: str, value, indent: int, parent, resources: Resources):
		super().__init__(text, indent, parent, resources)
		self.value = value
		self.input: util.InputControl
		if type(self.value) in (str, int, float):
			self.input = util.TextBox(self.rs)
			self.input.init_value(self.value)
			self.input.rect = [500, (COLUMN_HEIGHT - 40)/2, 150, 40]
		elif type(self.value) == bool:
			self.input = util.ToggleButton(self.rs)  # 仮
			self.input.value = self.value
			self.input.rect = [500, (COLUMN_HEIGHT - 50)/2, 150, 50]
	
	def print(self):
		print("-" * self.indent + self.text + ": " + str(self.value))
	
	def count_contents(self):
		return 1
	
	def draw(self, setting_sf, scroll):
		column_sf = pg.surface.Surface((900, COLUMN_HEIGHT), pg.SRCALPHA)
		key_sf = self.rs.font(ARIAL_SMALL_FONT).render(self.text, True, util.WHITE)
		column_sf.blit(key_sf, [10 + self.indent * 40, (COLUMN_HEIGHT - key_sf.get_height())/2])
		self.input.offset = [setting_sf.get_current_pos()[0], setting_sf.get_current_pos()[1] + scroll]
		self.input.render(column_sf)
		setting_sf.draw(column_sf)
	
	def update(self, keys, mouse):
		self.input.update(keys, mouse)
	
	def get_as_dict(self):
		return self.text, self.input.value
	

class SettingCategory(SettingContentBase):
	"""
	設定のカテゴリです。
	"""
	
	def __init__(self, key: str, setting_dict: dict, indent: int, parent, resources: Resources):
		super().__init__(key, indent, parent, resources)
		self.contents: list[SettingContentBase] = []
		for key in setting_dict:
			value = setting_dict[key]
			if type(value) is dict:
				self.contents.append(SettingCategory(key, value, self.indent + 1, self, self.rs))
			else:
				self.contents.append(SettingContent(key, value, self.indent + 1, self, self.rs))
	
	def print(self):
		print("-" * self.indent + self.text)
		for c in self.contents:
			c.print()
	
	def count_contents(self):
		count = 1
		for c in self.contents:
			count += c.count_contents()
		return count
	
	def draw(self, setting_sf, scroll):
		column_sf = pg.surface.Surface((900, COLUMN_HEIGHT), pg.SRCALPHA)
		category_sf = self.rs.font(ARIAL_SMALL_FONT).render(self.text, True, util.WHITE)
		column_sf.blit(category_sf, [5 + self.indent, (COLUMN_HEIGHT - category_sf.get_height()) / 2])
		setting_sf.draw(column_sf)
		for c in self.contents:
			c.draw(setting_sf, scroll)
	
	def update(self, keys, mouse):
		for c in self.contents:
			c.update(keys, mouse)
	
	def get_as_dict(self):
		result = {}
		for c in self.contents:
			k, v = c.get_as_dict()
			result[k] = v
		return self.text, result
