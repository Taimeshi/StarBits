import pygame as pg
import os
import sys
from PIL import Image, ImageFilter

import util
from game_enums import *


def find_data_file():
    if getattr(sys, "frozen", False):
        # The application is frozen
        return os.path.dirname(sys.executable)
    # The application is not frozen
    # Change this bit to match where you store your data files:
    return os.path.dirname(__file__)


# PROJ_PATH = os.path.dirname(os.path.abspath(__file__))
PROJ_PATH = find_data_file()
RESOURCES_PATH = os.path.join(PROJ_PATH, "resources")

pg.init()  # set_mode後にしかconvert_alphaは使えない
pg.display.set_caption("starbits")
sc = pg.display.set_mode((900, 700), pg.SRCALPHA)


def blur_surface(surface: pg.Surface, radius: int = 6):
    """
    Surfaceをぼかします。処理が少し重いかもしれません。
    :param surface: 元となるSurface
    :param radius: ぼかしの半径
    :return: ぼかされたSurface
    """
    pil_string_image = pg.image.tostring(surface, "RGBA", False)
    pil_image = Image.frombytes("RGBA", surface.get_size(), pil_string_image)
    pil_image = pil_image.filter(ImageFilter.GaussianBlur(radius=radius))
    # noinspection PyTypeChecker
    result = pg.image.fromstring(pil_image.tobytes("raw", "RGBA"), surface.get_size(), "RGBA")
    return result


TITLE_FILENAME = "0. title"
SELECT_FILENAME = "1. select"
GAME_FILENAME = "2. game"
RESULT_FILENAME = "3. result"
TRAILBLAZER_FILENAME = "4. trailblazer"


class ResourceCategory(Enum):
    GRAPHICS = auto()
    SE = auto()
    BGM_PATH = auto()
    FONTS = auto()
    
    def get_next(self):
        if self == ResourceCategory.GRAPHICS:
            return ResourceCategory.SE
        elif self == ResourceCategory.SE:
            return ResourceCategory.BGM_PATH
        elif self == ResourceCategory.BGM_PATH:
            return ResourceCategory.FONTS
        else:
            return None


LOGO_IMG = "logo"
TAP_TO_START_IMG = "tap_to_start"
TINY_STAR_IMG = "tiny_star"
TITLE_TRI_IMG = "title_tri"
SETTING_PLATE_IMG = "setting_plate"
SELECT_BACKGROUND_IMG = "select_background"
SONG_SELECT_PLATE_IMG = "song_select_plate"
SONG_SELECT_PLATE_LIGHT_IMG = "song_select_plate_light"
TITLE_UNDERBAR_IMG = "title_underbar"
AUTO_ICON_IMG = "auto_icon"
DIF_BASE_IMG = "dif_base"
NOTE_SPEED_BTN_IMG = "note_speed_button"
NOTE_SPEED_BTN_PRESSED_IMG = "note_speed_button_pressed"
OPTION_IMG = "option"
CHANGE_SCENE_IMG = "change_scene"
CHANGE_SCENE2_IMG = "change_scene2"
GAME_BACKGROUND_IMG = "game_background"
GAME_BACKGROUND_BASE_IMG = "game_background_base"
MISS_GRADATION_IMG = "miss_gradation"
LONG_TEXTURES = "long_textures"
AUTO_JUDGE = "auto_judge"
GAUGE_IMG = "gauge"
GAUGE_FULL_IMG = "gauge_full"
GAUGE_FRAME_IMG = "gauge_frame"
JUDGE_BAR_IMG = "judge_bar"
ALL_PERFECT_IMG = "all_perfect"
FULL_COMBO_IMG = "full_combo"
LEVEL_CLEAR_IMG = "level_clear"
LEVEL_FAILED_IMG = "level_failed"
COMBO_IMG = "combo"
EASY_LANE_DISABLE_IMG = "easy_lane_disable"
TAP_PARTICLES_IMG = "tap_particles"
TAP_PARTICLE2_IMG = "tap_particle2"
RELOAD_IMG = "reload"
RETURN_IMG = "return"
ARROW_IMG = "arrow"
CLICK_EFFECT_IMG = "click_effect"
COLLECT_EFFECT_IMG = "collect_effect"
GAME_DETAILS_IMG = "game_details"
CLEAR_PARTICLE_IMAGES = "clear_particles"
TRAILBLAZER_BG_IMG = "background"
TOOLBAR_HIGHLIGHT_IMG = "toolbar_highlight"
MENU_HIGHLIGHT_IMG = "menu_highlight"
PLOT_FOCUSING_HIGHLIGHT_IMG = "plot_focusing_highlight"
PLOT_SELECTING_HIGHLIGHT_IMG = "plot_selecting_highlight"

TITLE_START_SE = "title_start"
MODE_SCROLL_SE = "mode_scroll"
CLICK_SE = "click"
TAP_PERF_SE = "tap_perf"
TAP_GOOD_SE = "tap_good"
FUZZY_SE = "fuzzy"
EXTAP_SE = "extap"
SPACE_SE = "space"
CURSOR_SE = "cursor"
OPEN_PAUSE_MENU_SE = "open_pause_menu"
CLOSE_PAUSE_MENU_SE = "close_pause_menu"
SONG_SELECTED_SE = "song_selected"
COUNT_NUMBER_SE = "count_number"
RANK_SE = "rank"
CLEAR_SE = "clear"
FAILED_SE = "failed"

RESULT_BGM = "result"
TITLE_BGM = "title"

ARIAL_TINY_FONT = "arial_tiny"
ARIAL_TINY2_FONT = "arial_tiny2"
ARIAL_SMALL_FONT = "arial_small"
ARIAL_SMALL2_FONT = "arial_small2"
ARIAL_REGULAR_FONT = "arial_regular"
ARIAL_HUGE_FONT = "arial_huge"
MOLOT_TINY_FONT = "molot_tiny"
MOLOT_SMALL1_FONT = "molot_small1"
MOLOT_SMALL2_FONT = "molot_small2"
MOLOT_REGULAR_FONT = "molot_regular"
MOLOT_BIG_FONT = "molot_big"

SELECTING_BLUR_BG_IMG = "selecting_blur_bg"
RESULT_BACKGROUNDS = "result_backgrounds"
GAME_MODE_IMAGES = "game_mode_images"
BOX_IMAGES = "box_images"
DIFFICULTY_IMAGES = "difficulty_images"
NOTE_IMAGES = "note_images"
JUDGE_IMAGES = "judge_images"
AP_SMALL_IMG = "ap_small_img"
FC_SMALL_IMG = "fc_small_img"
LC_SMALL_IMG = "lc_small_img"
LF_SMALL_IMG = "lf_small_img"
RANK_IMAGES = "rank_images"
RANK_BASE_IMAGES = "rank_base_images"
RANK_PATTERN_IMAGES = "rank_pattern_images"

resource_members = {ResourceCategory.GRAPHICS: [
    
    [TITLE_FILENAME, LOGO_IMG],
    [TITLE_FILENAME, TAP_TO_START_IMG],
    [TITLE_FILENAME, TINY_STAR_IMG],
    [TITLE_FILENAME, TITLE_TRI_IMG],
    [TITLE_FILENAME, SETTING_PLATE_IMG],
    [SELECT_FILENAME, SELECT_BACKGROUND_IMG],
    [SELECT_FILENAME, SONG_SELECT_PLATE_IMG],
    [SELECT_FILENAME, SONG_SELECT_PLATE_LIGHT_IMG],
    [SELECT_FILENAME, TITLE_UNDERBAR_IMG],
    [SELECT_FILENAME, AUTO_ICON_IMG],
    [SELECT_FILENAME, DIF_BASE_IMG],
    [SELECT_FILENAME, NOTE_SPEED_BTN_IMG],
    [SELECT_FILENAME, NOTE_SPEED_BTN_PRESSED_IMG],
    [SELECT_FILENAME, OPTION_IMG],
    [SELECT_FILENAME, CHANGE_SCENE_IMG],
    [SELECT_FILENAME, CHANGE_SCENE2_IMG],
    [GAME_FILENAME, GAME_BACKGROUND_IMG],
    [GAME_FILENAME, GAME_BACKGROUND_BASE_IMG],
    [GAME_FILENAME, MISS_GRADATION_IMG],
    [GAME_FILENAME, AUTO_JUDGE],
    [GAME_FILENAME, GAUGE_IMG],
    [GAME_FILENAME, GAUGE_FULL_IMG],
    [GAME_FILENAME, GAUGE_FRAME_IMG],
    [GAME_FILENAME, JUDGE_BAR_IMG],
    [GAME_FILENAME, ALL_PERFECT_IMG],
    [GAME_FILENAME, FULL_COMBO_IMG],
    [GAME_FILENAME, LEVEL_CLEAR_IMG],
    [GAME_FILENAME, LEVEL_FAILED_IMG],
    [GAME_FILENAME, COMBO_IMG],
    [GAME_FILENAME, EASY_LANE_DISABLE_IMG],
    [GAME_FILENAME, TAP_PARTICLES_IMG],
    [GAME_FILENAME, TAP_PARTICLE2_IMG],
    [GAME_FILENAME, RELOAD_IMG],
    [GAME_FILENAME, RETURN_IMG],
    [GAME_FILENAME, ARROW_IMG],
    [GAME_FILENAME, CLICK_EFFECT_IMG],
    [GAME_FILENAME, COLLECT_EFFECT_IMG],
    [GAME_FILENAME, GAME_DETAILS_IMG],
    [TRAILBLAZER_FILENAME, TRAILBLAZER_BG_IMG],
    [TRAILBLAZER_FILENAME, TOOLBAR_HIGHLIGHT_IMG],
    [TRAILBLAZER_FILENAME, MENU_HIGHLIGHT_IMG],
    [TRAILBLAZER_FILENAME, PLOT_FOCUSING_HIGHLIGHT_IMG],
    [TRAILBLAZER_FILENAME, PLOT_SELECTING_HIGHLIGHT_IMG]

], ResourceCategory.SE: [
    "title_start", "mode_scroll", "click", "tap_perf", "tap_good", "fuzzy", "extap", "space",
    "cursor", "open_pause_menu", "close_pause_menu", "song_selected", "count_number", "rank",
    "clear", "failed"
], ResourceCategory.BGM_PATH: ["result", "title"],
    ResourceCategory.FONTS: [
        ["ARIALUNI.TTF", 15, "arial_tiny"],  # 判定バー
        ["ARIALUNI.TTF", 20, "arial_tiny2"],  # エディターのコントロールの文字
        ["ARIALUNI.TTF", 30, "arial_small"],  # オプション・判定カウント・スコア
        ["ARIALUNI.TTF", 35, "arial_small2"],  # コントロールの中の文字
        ["ARIALUNI.TTF", 45, "arial_regular"],  # 設定画面
        ["ARIALUNI.TTF", 200, "arial_huge"],  # カウントダウン
        ["Molot.otf", 16, "molot_tiny"],  # 曲詳細の文字(小)
        ["Molot.otf", 20, "molot_small1"],  # 曲詳細の文字(大)
        ["Molot.otf", 30, "molot_small2"],  # 曲選択場面のレベルの文字
        ["Molot.otf", 50, "molot_regular"],  # 曲選択場面のレベルの文字(中央のやつ)
        ["Molot.otf", 80, "molot_big"],  # コンボ・リザルト画面のスコア
    ]
}


class Resources:
    
    def __init__(self, config: dict):
        self.proj_config = config
        self.resources: dict = {}
        self.new_resources: dict = {}
        self._texture_name = config["general"]["texture"]
        if not os.path.isdir(os.path.join(RESOURCES_PATH, self._texture_name)):
            self._texture_name = "Default"
        self._TEXTURE_PATH = os.path.join(RESOURCES_PATH, self._texture_name)
        self._DEF_TEXTURE_PATH = os.path.join("Default", self._texture_name)
        self._GRAPHICS_PATH = os.path.join(self._TEXTURE_PATH, "graphics")
        self._SE_PATH = os.path.join(self._TEXTURE_PATH, "se")
        self._BGM_PATH = os.path.join(self._TEXTURE_PATH, "bgm")
        self._FONT_PATH = os.path.join(self._TEXTURE_PATH, "font")
        self.loading: bool = False
        self.loading_category: ResourceCategory = ResourceCategory.GRAPHICS
        self.loading_iterator: int = 0
    
    def start_load(self):
        """
        テクスチャの読み込みを開始します。
        """
        self.new_resources = {ResourceCategory.GRAPHICS: {}, ResourceCategory.SE: {}, ResourceCategory.BGM_PATH: {},
                              ResourceCategory.FONTS: {}}
        self.loading = True
        self.loading_category: ResourceCategory = ResourceCategory.GRAPHICS
        self.loading_iterator = 0
    
    def _img_path(self, folder_name: str, filename: str) -> str:
        path = self._GRAPHICS_PATH
        for d in [folder_name, filename]:
            path = os.path.join(path, d)
        path += ".png"
        if not os.path.isfile(path):
            path = os.path.join(os.path.join(os.path.join(
                self._DEF_TEXTURE_PATH, "graphics"), folder_name), filename)
        return path
    
    def update(self) -> float:
        """
        テクスチャが読み込み中なら、読み込みを進め、進捗を返します。
        :return: カテゴリ毎の進捗度(0~100)
        """
        if not self.loading:
            return 100
        progressing_member = resource_members[self.loading_category][self.loading_iterator]
        if self.loading_category == ResourceCategory.GRAPHICS:
            folder_tmp = os.path.join(self._GRAPHICS_PATH, progressing_member[0])
            self.new_resources[ResourceCategory.GRAPHICS][progressing_member[1]] = \
                pg.image.load(os.path.join(folder_tmp, progressing_member[1]) + ".png").convert_alpha()
        
        elif self.loading_category == ResourceCategory.SE:
            self.new_resources[ResourceCategory.SE][progressing_member] = \
                pg.mixer.Sound(os.path.join(self._SE_PATH, progressing_member) + ".mp3")
        
        elif self.loading_category == ResourceCategory.BGM_PATH:
            self.new_resources[ResourceCategory.BGM_PATH][progressing_member] = \
                os.path.join(self._BGM_PATH, progressing_member) + ".mp3"
        
        else:
            self.new_resources[ResourceCategory.FONTS][progressing_member[2]] = \
                pg.font.Font(os.path.join(self._FONT_PATH, progressing_member[0]), progressing_member[1])
        progressive = self.loading_iterator / (len(resource_members[self.loading_category]) - 1) * 100
        
        self.loading_iterator += 1
        if self.category_all_loaded:
            if self.loading_category != ResourceCategory.FONTS:
                self.loading_category = self.loading_category.get_next()
                self.loading_iterator = 0
            else:
                # その他の画像
                self.load_others()
                self.loading = False
                self.resources = self.new_resources
        
        return progressive
    
    def change_texture(self, texture_name: str):
        """
        テクスチャを変更します。
        テクスチャをすべて読み込み直します。
        :param texture_name: テクスチャの名前
        """
        self._texture_name = texture_name
        if not os.path.isdir(os.path.join(RESOURCES_PATH, self._texture_name)):
            self._texture_name = "Default"
        self._TEXTURE_PATH = os.path.join(RESOURCES_PATH, self._texture_name)
        self._GRAPHICS_PATH = os.path.join(self._TEXTURE_PATH, "graphics")
        self._SE_PATH = os.path.join(self._TEXTURE_PATH, "se")
        self._BGM_PATH = os.path.join(self._TEXTURE_PATH, "bgm")
        self.start_load()
    
    def graphic(self, name: str):
        return self.resources[ResourceCategory.GRAPHICS][name]
    
    def se(self, name: str):
        return self.resources[ResourceCategory.SE][name]
    
    def bgm_path(self, name: str):
        return self.resources[ResourceCategory.BGM_PATH][name]
    
    def font(self, name: str):
        return self.resources[ResourceCategory.FONTS][name]
    
    def load_others(self):
        """
        その他の画像を読み込みます
        """
        selecting_blur_bg_tmp = blur_surface(self.new_resources[ResourceCategory.GRAPHICS][SELECT_BACKGROUND_IMG], 2)
        grad_tmp = pg.surface.Surface((900, 700), pg.SRCALPHA)
        grad_tmp.fill((0, 0, 0, 50))
        selecting_blur_bg_tmp.blit(grad_tmp, [0, 0])
        self.new_resources[ResourceCategory.GRAPHICS]["selecting_blur_bg"] = selecting_blur_bg_tmp
        self.new_resources[ResourceCategory.GRAPHICS]["result_backgrounds"] = {
            Difficulty.EASY: pg.image.load(self._img_path(RESULT_FILENAME, "result_bg_easy")).convert_alpha(),
            Difficulty.HARD: pg.image.load(self._img_path(RESULT_FILENAME, "result_bg_hard")).convert_alpha(),
            Difficulty.IMP: pg.image.load(self._img_path(RESULT_FILENAME, "result_bg_imp")).convert_alpha()}
        self.new_resources[ResourceCategory.GRAPHICS]["game_mode_images"] = {
            GameMode.SONG_SELECT: pg.image.load(self._img_path(TITLE_FILENAME, "song_select")).convert_alpha(),
            GameMode.CHALLENGE: pg.image.load(self._img_path(TITLE_FILENAME, "challenge")).convert_alpha(),
            GameMode.SETTING: pg.image.load(self._img_path(TITLE_FILENAME, "setting")).convert_alpha(),
            GameMode.EXIT: pg.image.load(self._img_path(TITLE_FILENAME, "exit")).convert_alpha()}
        self.new_resources[ResourceCategory.GRAPHICS]["box_images"] = {
            Difficulty.EASY: pg.image.load(self._img_path(SELECT_FILENAME, "song_box_easy")).convert_alpha(),
            Difficulty.HARD: pg.image.load(self._img_path(SELECT_FILENAME, "song_box_hard")).convert_alpha(),
            Difficulty.IMP: pg.image.load(self._img_path(SELECT_FILENAME, "song_box_imp")).convert_alpha()}
        self.new_resources[ResourceCategory.GRAPHICS]["difficulty_images"] = {
            Difficulty.EASY: pg.image.load(self._img_path(SELECT_FILENAME, "dif_easy")).convert_alpha(),
            Difficulty.HARD: pg.image.load(self._img_path(SELECT_FILENAME, "dif_hard")).convert_alpha(),
            Difficulty.IMP: pg.image.load(self._img_path(SELECT_FILENAME, "dif_imp")).convert_alpha()}
        
        self.new_resources[ResourceCategory.GRAPHICS]["note_images"] = {
            NoteType.TAP: pg.image.load(self._img_path(GAME_FILENAME, "tap")).convert_alpha(),
            NoteType.EX_TAP: pg.image.load(self._img_path(GAME_FILENAME, "ex_tap")).convert_alpha(),
            NoteType.FUZZY: pg.image.load(self._img_path(GAME_FILENAME, "fuzzy")).convert_alpha(),
            NoteType.LONG: pg.image.load(self._img_path(GAME_FILENAME, "long_tap")).convert_alpha()}
        
        self.new_resources[ResourceCategory.GRAPHICS]["long_textures"] = [
            pg.image.load(self._img_path(GAME_FILENAME, "long_texture")).convert_alpha(),
            pg.image.load(self._img_path(GAME_FILENAME, "long_texture_pressing")).convert_alpha(),
            pg.image.load(self._img_path(GAME_FILENAME, "long_texture_missed")).convert_alpha()
        ]
        
        self.new_resources[ResourceCategory.GRAPHICS]["judge_images"] = {
            Judge.PERFECT: pg.image.load(self._img_path(GAME_FILENAME, "perfect")).convert_alpha(),
            Judge.GOOD: pg.image.load(self._img_path(GAME_FILENAME, "good")).convert_alpha(),
            Judge.MISS: pg.image.load(self._img_path(GAME_FILENAME, "miss")).convert_alpha()}
        
        self.new_resources[ResourceCategory.GRAPHICS]["ap_small_img"] = \
            pg.transform.rotozoom(self.new_resources[ResourceCategory.GRAPHICS][ALL_PERFECT_IMG], 0, 0.5)
        self.new_resources[ResourceCategory.GRAPHICS]["fc_small_img"] = \
            pg.transform.rotozoom(self.new_resources[ResourceCategory.GRAPHICS][FULL_COMBO_IMG], 0, 0.5)
        self.new_resources[ResourceCategory.GRAPHICS]["lc_small_img"] = \
            pg.transform.rotozoom(self.new_resources[ResourceCategory.GRAPHICS][LEVEL_CLEAR_IMG], 0, 0.5)
        self.new_resources[ResourceCategory.GRAPHICS]["lf_small_img"] = \
            pg.transform.rotozoom(self.new_resources[ResourceCategory.GRAPHICS][LEVEL_FAILED_IMG], 0, 0.5)
        
        self.new_resources[ResourceCategory.GRAPHICS]["rank_images"] = \
            [pg.image.load(self._img_path(GAME_FILENAME, f"star{r_i}")).convert_alpha() for r_i in range(6)]
        self.new_resources[ResourceCategory.GRAPHICS]["rank_base_images"] = \
            [pg.image.load(self._img_path(GAME_FILENAME, f"star_{c}")).convert_alpha() for c in ["n", "fc", "ap"]]
        self.new_resources[ResourceCategory.GRAPHICS]["rank_pattern_images"] = \
            [pg.image.load(self._img_path(GAME_FILENAME, f"star_pt{r_i}")).convert_alpha() for r_i in range(6)]
        
        self.new_resources[ResourceCategory.GRAPHICS]["clear_particles"] = \
            [pg.surface.Surface((10, 10), pg.SRCALPHA) for _ in range(10)]
        clear_particles_base = pg.image.load(self._img_path(GAME_FILENAME, "clear_particles")).convert_alpha()
        for cp_i, cp in enumerate(self.new_resources[ResourceCategory.GRAPHICS]["clear_particles"]):
            cp.fill(util.CLEAR)
            cp.blit(clear_particles_base, [0, 0], [10 * cp_i, 0, 10, 10])
    
    @property
    def category_all_loaded(self) -> bool:
        return len(resource_members[self.loading_category]) == self.loading_iterator
    
    def show_loading_bar(self, display: pg.Surface):
        self.start_load()
        tmp_font = pg.font.Font(None, 30)
        while self.loading:
            display.fill(util.BLACK)
            pg.draw.rect(display, util.WHITE, [150, 350, 600, 50], 2)
            pg.draw.rect(display, util.GREEN, [155, 355, 590 / 100 * self.update(), 40])
            display.blit(tmp_font.render(self.loading_category.name.lower(), True, util.WHITE), [150, 320])
            pg.display.update()
