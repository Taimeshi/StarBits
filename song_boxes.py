import pygame.gfxdraw
from data_loader import *
from song import Song
import util


prepared_box = 6


class SongBoxes:
	
	def __init__(self, config: dict, difficulty: Difficulty, resources: Resources):
		self.songs: list[Song] = []
		self.selecting_num: int = 0
		self.displaying_songs: list[Song] = []
		self.proj_config: dict = config
		self.scroll: int = 0
		self.song_selected: bool = False
		self.tmr_to_game: int = 0
		self.tmr_standby: int = 0
		self.tmr: int = 0
		self.difficulty: Difficulty = difficulty
		self.rs = resources
	
	def load_songs(self):
		self.song_selected = False
		self.tmr = 0
		self.tmr_standby = 0
		self.tmr_to_game = 0
		songs_path = os.listdir(os.path.join(PROJ_PATH, "songs"))
		self.songs = [Song(p, self.proj_config) for p in songs_path]
		self.displaying_songs = []
		self.update_selecting_around()
	
	def update_selecting_around(self):
		self.displaying_songs = []
		for b_i2 in range(-prepared_box, prepared_box + 1):
			self.displaying_songs.append(self.songs[(self.selecting_num + b_i2) % self.song_number])
	
	def update(self, keys: util.Keys):
		# タイマー
		self.tmr += 1
		if self.song_selected:
			self.tmr_to_game += 1
		self.tmr_standby += 1
		
		# 移動
		if not self.song_selected:
			if keys.just_left and self.scroll > -300:
				self.selecting_num = (self.selecting_num - 1) % self.song_number
				self.scroll -= 100
				self.update_selecting_around()
				self.tmr_standby = 0
			if keys.just_right and self.scroll < 300:
				self.selecting_num = (self.selecting_num + 1) % self.song_number
				self.scroll += 100
				self.update_selecting_around()
				self.tmr_standby = 0
			
		# スクロール
		if self.scroll != 0:
			if self.scroll > 15:
				self.scroll -= 15
			elif self.scroll < -15:
				self.scroll += 15
			else:
				self.scroll = 0
			if self.scroll == 0:
				self.rs.se(CURSOR_SE).play()
	
	def get_surface(self):
		boxes_surface = pg.surface.Surface((900, 700), pg.SRCALPHA)
		boxes_surface.fill(util.CLEAR)
		
		now_box: pg.Surface
		box_pos: [int, int]
		box_polygon: tuple[tuple[int, int], tuple[int, int], tuple[int, int], tuple[int, int]]
		title: pg.Surface
		title_pos = [int, int]
		title_clip_rect: [int, int]
		level_sf: pg.Surface
		level_pos: [int, int]
		
		def draw_box():
			nonlocal box_polygon, now_box, title_pos, title_clip_rect, level_sf, level_pos
			pg.gfxdraw.textured_polygon(boxes_surface, box_polygon, self.rs.graphic(SELECTING_BLUR_BG_IMG), 0, 0)
			boxes_surface.blit(now_box, box_pos)
			boxes_surface.blit(title, title_pos, title_clip_rect)
			boxes_surface.blit(level_sf, level_pos)
		
		box_offset = 0
		if self.song_selected:
			box_offset = -0.469 * (self.tmr_to_game - 5)**2 + 20
		elif self.tmr <= 60:
			box_offset = -0.8 * (self.tmr - 55)**2 + 20

		for b_i, s in enumerate(self.displaying_songs):
			if self.tmr_to_game > 60:
				break
			if b_i == 6 and self.scroll == 0:
				continue
			now_box = self.rs.graphic(BOX_IMAGES)[self.difficulty]
			box_pos = [30 + box_offset, (b_i - 3) * 100 + self.scroll]
			box_pos[0] -= int(abs(300 - box_pos[1] + 50) / 10)  # カーブをつける
			if -400 < box_pos[0] < 900 and -100 < box_pos[1] < 700:
				box_polygon = ((box_pos[0], box_pos[1]), (box_pos[0] + 360, box_pos[1]),
				               (box_pos[0] + 400, box_pos[1] + 99),
				               (box_pos[0] + 40, box_pos[1] + 99))
			else:
				continue
			title = self.rs.font(ARIAL_SMALL_FONT).render(s.get_title()[:17], True, util.WHITE)
			title_pos = [box_pos[0] + 30, box_pos[1] + (100 - title.get_height()) / 2]
			title_clip_rect = pg.Rect(0, 0, 360, title.get_height())
			level_sf = self.rs.font(MOLOT_SMALL2_FONT).render(str(s.get_level(self.difficulty)), True, util.WHITE)
			level_pos = [box_pos[0] + 400 - 15 - level_sf.get_width() / 2,
			             box_pos[1] + 100 - 15 - level_sf.get_height() / 2]
			draw_box()
		
		if self.scroll == 0:  # 中央のボックス
			box_pos = [10 + 10, 300 + self.scroll - 10]
			now_box = pg.transform.smoothscale(self.rs.graphic(BOX_IMAGES)[self.difficulty], [420, 120])
			box_polygon = ((box_pos[0], box_pos[1]), (box_pos[0] + 378, box_pos[1]),
			               (box_pos[0] + 419, box_pos[1] + 119), (box_pos[0] + 45, box_pos[1] + 119))
			title_tmp = self.rs.font(ARIAL_REGULAR_FONT).render(s.get_title()[:14], True, util.WHITE)
			if title_tmp.get_width() > 400:
				title = pg.surface.Surface((title_tmp.get_width() * 2 + 50, title_tmp.get_height()),
				                           pg.SRCALPHA)
				title.blit(title_tmp, [0, 0])
				title.blit(title_tmp, [title_tmp.get_width() + 50, 0])
				title_pos = [box_pos[0] + 30, box_pos[1] + (120 - title_tmp.get_height()) / 2]
				title_clip_rect = pg.Rect(self.tmr_standby % (title_tmp.get_width() + 50), 0, 350,
				                          title_tmp.get_height())
			
			else:
				title = title_tmp
				title_pos = [box_pos[0] + 30, box_pos[1] + (120 - title_tmp.get_height()) / 2]
				title_clip_rect = [0, 0, *title.get_size()]
			
			level_sf = self.rs.font(MOLOT_REGULAR_FONT).render(str(s.get_level(self.difficulty)), True, util.WHITE)
			level_pos = [box_pos[0] + 420 - 25 - level_sf.get_width() / 2,
			             box_pos[1] + 120 - 25 - level_sf.get_height() / 2]
			draw_box()
		
		return boxes_surface
	
	@property
	def song_number(self) -> int:
		return len(self.songs)
	
	@property
	def selecting_song(self) -> Song:
		return self.songs[self.selecting_num]
