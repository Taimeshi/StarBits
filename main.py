import sys
import json
import random
import time
import math
import pygame.gfxdraw

import song
from setting import *

from ctypes import windll, Structure, wintypes, pointer

from song_boxes import SongBoxes

SWP_NO_MOVE = 0x0002
SWP_NO_OWNERZORDER = 0x0200
SWP_NO_SIZE = 0x0001


class Rect(Structure):
    _fields_ = [
        ("left", wintypes.LONG),
        ("top", wintypes.LONG),
        ("right", wintypes.LONG),
        ("bottom", wintypes.LONG),
    ]


def get_window_rect(hwnd=None):
    if hwnd is None:
        hwnd = pygame.display.get_wm_info()["window"]
    r = Rect(0, 0, 0, 0)
    windll.user32.GetWindowRect(hwnd, pointer(r))
    return pygame.Rect(r.left, r.top, r.right - r.left, r.bottom - r.top)


def move_window_abs(x, y, hwnd=None):
    if hwnd is None:
        hwnd = pygame.display.get_wm_info()["window"]
    windll.user32.SetWindowPos(hwnd, 0, x, y, 0, 0, SWP_NO_SIZE | SWP_NO_OWNERZORDER)


def main():
    # 初期化(set_modeまではload_data側で実行)
    cl = pg.time.Clock()
    tmr = 0
    
    # システム
    with open(os.path.join(PROJ_PATH, "config.json"), "r", encoding="utf-8_sig") as j:
        config: dict = json.load(j)
    rs = Resources(config)
    rs.start_load()
    tmp_font = pg.font.Font(None, 30)
    while rs.loading:
        sc.fill(util.BLACK)
        pg.draw.rect(sc, util.WHITE, [150, 350, 600, 50], 2)
        pg.draw.rect(sc, util.GREEN, [155, 355, 590 / 100 * rs.update(), 40])
        sc.blit(tmp_font.render(rs.loading_category.name.lower(), True, util.WHITE), [150, 320])
        pg.display.update()
    
    setting_data: Setting = Setting(config, rs)
    mode_select_sf = pg.surface.Surface((900, 700), pg.SRCALPHA)
    selecting_info_sf = pg.surface.Surface((900, 700), pg.SRCALPHA)
    notes_sf = pg.surface.Surface((900, 700), pg.SRCALPHA)
    game_data_sf = pg.surface.Surface((900, 700), pg.SRCALPHA)
    pause_background = pg.surface.Surface((900, 700), pg.SRCALPHA)
    pause_gradation = pg.surface.Surface((900, 700), pg.SRCALPHA)
    pause_gradation.fill((0, 0, 0, 150))
    
    keys = util.Keys()
    mouse = util.Mouse()
    
    # その他
    difficulty: Difficulty = Difficulty.EASY
    song_boxes = SongBoxes(config, difficulty, rs)
    playing_song: song.Song
    combo_effect: int = 0
    finished_timer: int = 0
    past_rank = 0
    result_timer = 0
    selecting_game_mode = GameMode.SONG_SELECT
    selecting_gm_ang = 0
    tiny_stars = []
    dif_scroll = 0
    select_option = False
    to_select_timer = 0
    game_timer: int = 0
    pause_from = 0
    restart_timer = 0
    back_select_timer = 0
    restart_countdown = False
    auto_play = config["game"]["auto_play"]
    window_original_pos: list[int, int] = []
    window_vib_timer: int = 0
    window_vib_busy: bool = False
    miss_gr_timer: int = 0
    game_clear_particles = util.Particles((900, 700))
    
    note_sizes = {}
    for t in NoteType:
        note_sizes[t] = (rs.graphic(NOTE_IMAGES)[t].get_width(), rs.graphic(NOTE_IMAGES)[t].get_height())
    scene_changer = util.SceneChanger(sc.get_size(), Index.START, rs)
    
    particles: util.Particles = util.Particles(sc.get_size())
    
    pg.mixer.music.load(rs.bgm_path(TITLE_BGM))
    pg.mixer.music.play(-1)
    
    def close_song():
        """
        楽曲の情報をリセットし、楽曲選択画面に移ります。
        """
        nonlocal back_select_timer, result_timer
        back_select_timer = 0
        result_timer = 0
        song_boxes.load_songs()
        pg.mixer.music.stop()
    
    def draw_title_bg():
        """
        タイトルの背景を描画します。
        """
        # 星の追加
        if random.randint(1, 5) == 1:
            star_pos_tmp = random.random() * 2 - 1
            # x座標、y座標、スピード、サイズ
            tiny_stars.append([900 + star_pos_tmp * 340, star_pos_tmp * 440,
                               random.randint(4, 10), random.randint(1, 3) / 2])
        
        # 背景のグラデーションの描画
        gr_start = [ce * (math.sin(tmr / 40) / 4 + 1) for ce in util.GR_START_BASE]
        gr_end = [ce * (math.sin(tmr / 40) / 4 + 1) for ce in util.GR_END_BASE]
        rect_time = int(900 / util.GR_QUALITY) + 1
        gr_between = [(gr_end[e_i] - gr_start[e_i]) / rect_time for e_i in range(3)]
        
        for g_i in range(rect_time):
            pg.draw.rect(sc, [gr_start[e_i] + gr_between[e_i] * g_i for e_i in range(3)],
                         [0, g_i * util.GR_QUALITY, 900, util.GR_QUALITY])
        
        # 星の描画
        tiny_stars_poped_after = []
        for t_i2, ts in enumerate(tiny_stars):
            sc.blit(pg.transform.rotozoom(rs.graphic(TINY_STAR_IMG), 0, ts[3]), ts[:2])
            ts[0] -= ts[2] * math.cos(0.66) * (math.sin(tmr / 80) + 2) * 0.5
            ts[1] += ts[2] * math.sin(0.66) * (math.sin(tmr / 80) + 2) * 0.5
            if ts[0] < -50 or ts[1] > 750:
                tiny_stars_poped_after.append(t_i2)
        tiny_stars_poped_after.reverse()
        for t_i2 in tiny_stars_poped_after:
            tiny_stars.pop(t_i2)
    
    def get_ellipse_x(angle: float):
        """
        モード選択での楕円のx座標を取得します。
        :param angle: 度数法で、"傾いた楕円の長軸を始点とした"角度
        :return: 楕円の点のx座標
        """
        rad_ang = math.radians(angle)
        rad_15 = math.radians(-15)
        return 300 * math.cos(rad_15) * math.cos(rad_ang) - 100 * math.sin(rad_15) * math.sin(rad_ang) + 420
    
    def get_ellipse_y(angle: float):
        """
        モード選択での楕円のy座標を取得します。
        :param angle: 度数法で、"傾いた楕円の長軸を始点とした"角度
        :return: 楕円の点のy座標
        """
        rad_ang = math.radians(angle)
        rad_15 = math.radians(-15)
        return 300 * math.sin(rad_15) * math.cos(rad_ang) + 100 * math.cos(rad_15) * math.sin(rad_ang) + 500
    
    def raise_note_speed():
        """
        ノーツの速度を一つ上げます。
        """
        config["game"]["note_speed"] %= 15
        config["game"]["note_speed"] += 1
        with open(os.path.join(PROJ_PATH, "config.json"), "w", encoding="utf-8_sig") as c:
            json.dump(config, c, indent=4)
    
    def start_game_play():
        pg.mixer.music.load(playing_song.get_music_path())
        pg.mixer.music.play()
        playing_song.start_song()
    
    def save_setting():
        nonlocal setting_data, config
        with open(os.path.join(PROJ_PATH, "config.json"), "w", encoding="utf-8_sig") as jw:
            json.dump(setting_data.get_as_dict(), jw, indent=4, ensure_ascii=False)
        with open(os.path.join(PROJ_PATH, "config.json"), "r", encoding="utf-8_sig") as jr:
            config = json.load(jr)
        setting_data = Setting(config, rs)
    
    while True:
        
        tmr += 1
        
        sc.fill(util.BLACK)
        
        for e in pg.event.get():
            if e.type == pg.QUIT:
                pg.quit()
                sys.exit()
            elif e.type == pg.MOUSEBUTTONDOWN:
                if scene_changer.index == Index.SETTING:
                    if e.button == 4:
                        setting_data.scroll += 30
                    if e.button == 5:
                        setting_data.scroll -= 30
        window_vib_timer -= 1
        window_vib_timer = max(0, window_vib_timer)
        
        # ウィンドウの振動
        if config["game"]["window_vibration"] and window_vib_busy and \
                window_vib_timer >= 0 and window_vib_timer % 3 == 0:
            pos = [op + random.randint(-window_vib_timer, window_vib_timer)
                   for op in window_original_pos]
            move_window_abs(*pos)
            if window_vib_timer == 0:
                window_vib_busy = False
        
        keys.update()
        mouse.update()
        scene_changer.update()
        
        if scene_changer.index == Index.START:  # スタート画面
            
            if to_select_timer > 0:
                to_select_timer += 1
            
            draw_title_bg()
            
            rs.graphic(TAP_TO_START_IMG).set_alpha(min(abs(math.sin(tmr / 80)) * 150 + 100,
                                                       255 - (to_select_timer / 120 * 255)))
            rs.graphic(TITLE_TRI_IMG).set_alpha(abs(math.sin(tmr / 80)) * 150 + 100)
            
            sc.blit(rs.graphic(LOGO_IMG), [145, 161 - min(to_select_timer ** 2, 50 ** 2) / 20])
            sc.blit(rs.graphic(TAP_TO_START_IMG), [180, 502])
            sc.blit(rs.graphic(TITLE_TRI_IMG), [723 + to_select_timer ** 2 / 2 + math.sin(tmr / 20) * 15, 513])
            
            sc.blit(pg.transform.flip(rs.graphic(TITLE_TRI_IMG), True, False),
                    [130 - to_select_timer ** 2 / 2 - math.sin(tmr / 20) * 15, 513])
            
            if keys.just_decided and to_select_timer == 0:
                rs.se(TITLE_START_SE).play()
                to_select_timer += 1
            
            if to_select_timer >= 120:
                scene_changer.index = Index.MODE_SELECT
                to_select_timer = 0
        
        elif scene_changer.index == Index.MODE_SELECT:
            mode_select_sf.fill(util.CLEAR)
            
            if to_select_timer < 60:
                to_select_timer += 1
            
            draw_title_bg()
            sc.blit(rs.graphic(LOGO_IMG), [145, 36])
            
            for ang in range(0, 360, 4):
                pg.draw.circle(mode_select_sf, (255, 255, 255, (2 - abs(math.sin((tmr + ang) / 50) * 2)) * 75 + 50),
                               [get_ellipse_x(ang), get_ellipse_y(ang)], 2)
            
            for i in range(4):
                now_angle = 45 + i * 90 + selecting_gm_ang
                pg.draw.circle(mode_select_sf,
                               (255, 255, 255, (2 - abs(math.sin((tmr + now_angle * 4) / 50) * 2)) * 75 + 50),
                               [get_ellipse_x(now_angle), get_ellipse_y(now_angle)], 8)
            
            drawing_mode: GameMode = selecting_game_mode.get_past()
            
            for i in range(4):
                now_angle = i * 90 + selecting_gm_ang
                drawing_mode = drawing_mode.get_next()
                now_image = rs.graphic(GAME_MODE_IMAGES)[drawing_mode]
                now_pos = [get_ellipse_x(now_angle),
                           get_ellipse_y(now_angle)]
                
                distance = int(math.sqrt((now_pos[0] - 709) ** 2 + (now_pos[1] - 422) ** 2))
                now_image.set_alpha(255 - distance / 3)  # 708 ,578
                now_image = pg.transform.rotozoom(now_image, 0, round(1 - distance / 1200, 3))
                mode_select_sf.blit(now_image,
                                    [now_pos[0] - now_image.get_width() / 2, now_pos[1] - now_image.get_height() / 2])
            mode_select_sf.set_alpha(min(int(to_select_timer * 255 / 60), 255))
            
            if keys.just_left and not scene_changer.is_busy():
                selecting_gm_ang += 90
                selecting_game_mode = selecting_game_mode.get_next()
            if keys.just_right and not scene_changer.is_busy():
                selecting_gm_ang -= 90
                selecting_game_mode = selecting_game_mode.get_past()
            if selecting_gm_ang != 0:
                if selecting_gm_ang > 5:
                    selecting_gm_ang -= 5
                elif selecting_gm_ang < -5:
                    selecting_gm_ang += 5
                else:
                    selecting_gm_ang = 0
                if selecting_gm_ang == 0:
                    rs.se(CURSOR_SE).play()
            
            if (keys.just_pressed(pg.K_RETURN) or keys.just_pressed(pg.K_f) or keys.just_pressed(pg.K_j)) \
                    and not scene_changer.is_busy():
                if selecting_game_mode != GameMode.CHALLENGE:
                    if selecting_game_mode == GameMode.SONG_SELECT:
                        scene_changer.add_event(Index.SONG_SELECT, 120, song_boxes.load_songs)
                    elif selecting_game_mode == GameMode.CHALLENGE:
                        pass
                    elif selecting_game_mode == GameMode.SETTING:
                        scene_changer.add_event(Index.SETTING, 60)
                    elif selecting_game_mode == GameMode.EXIT:
                        pg.quit()
                        sys.exit()
        
        elif scene_changer.index == Index.SETTING:
            sc.fill(util.CLEAR)
            setting_data.update(keys, mouse)
            sc.blit(setting_data.get_surface(), [0, setting_data.scroll])
            
            sc.blit(rs.graphic(SETTING_PLATE_IMG), [544, 625])
            if mouse.in_rect(544 + 289, 625, 67, 67):
                sc.blit(rs.graphic(SONG_SELECT_PLATE_LIGHT_IMG), [544 + 289, 625])
                if mouse.just_pressed(0):
                    scene_changer.add_event \
                        (Index.MODE_SELECT, 60, save_setting)
        
        elif scene_changer.index == Index.SONG_SELECT:
            selecting_info_sf.fill(util.CLEAR)
            sc.blit(rs.graphic(SELECT_BACKGROUND_IMG), [0, 0])
            sc.blit(rs.graphic(TITLE_UNDERBAR_IMG), [480, 450])
            song_boxes.update(keys)
            sc.blit(song_boxes.get_surface(), [0, 0])
            
            # 楽曲情報の描画
            selecting_info_sf.blit(song_boxes.selecting_song.get_jacket(), [550, 100])
            info_title = rs.font(ARIAL_SMALL_FONT).render(song_boxes.selecting_song.get_title(), True, util.WHITE)
            selecting_info_sf.blit(info_title, [480 + 198 - info_title.get_width() / 2, 400])
            selecting_info_sf.blit(
                rs.font(ARIAL_SMALL_FONT).render(f"リクエスト: {song_boxes.selecting_song.get_whose_request()}",
                                                 True, util.WHITE), [500, 500])
            if keys.just_pressed(pg.K_F1):
                select_option = not select_option
            
            # オートプレイの表示
            if auto_play:
                selecting_info_sf.blit(rs.graphic(AUTO_ICON_IMG), [720, 580])
            if keys.just_pressed(pg.K_F2):
                auto_play = not auto_play
            
            # 右下のやつ
            selecting_info_sf.blit(rs.graphic(SONG_SELECT_PLATE_IMG), [544, 625])
            if not song_boxes.song_selected and mouse.in_rect(544 + 289, 625, 67, 67):
                selecting_info_sf.blit(rs.graphic(SONG_SELECT_PLATE_LIGHT_IMG), [544 + 289, 625])
                if mouse.just_pressed(0):
                    scene_changer.add_event \
                        (Index.MODE_SELECT, 120,
                         lambda: [
                             pg.mixer.music.load(rs.bgm_path(TITLE_BGM)),
                             pg.mixer.music.play(-1)])
            
            # 簡易メニュー
            if select_option:
                selecting_info_sf.blit(rs.graphic(OPTION_IMG), [600, 50])
                option_texts = {"note_speed": [
                    rs.font(ARIAL_SMALL_FONT).render(f'note speed: {config["game"]["note_speed"]}', True, util.WHITE),
                    raise_note_speed]}
                for t_i, t in enumerate(option_texts.values()):
                    selecting_info_sf.blit(t[0], [600 + 10, 50 + 50 + 25 + 60 * t_i - t[0].get_height() / 2])
                    if mouse.just_pressed(0) and mouse.in_rect(600, 50 + 50 + 60 * t_i, 280, 50) and t[1]:
                        t[1]()
                        rs.se(SPACE_SE).play()
            
            # 難易度のプレートの描画
            selecting_info_sf.blit(rs.graphic(DIF_BASE_IMG), [830 - 3, 50 - 3])
            selecting_info_sf.blit(rs.graphic(DIFFICULTY_IMAGES)[difficulty], [830, 50 + dif_scroll])
            for d_i, d in enumerate([d for d in Difficulty]):
                if difficulty == d or dif_scroll != 0:
                    continue
                if not song_boxes.song_selected and mouse.in_rect(830, 50 + 60 * d_i, 50, 60) and mouse.just_pressed(0):
                    dif_scroll = 60 * (difficulty.value - d.value)
                    difficulty = d
                    rs.se(SPACE_SE).play()
                    song_boxes.difficulty = difficulty
            if dif_scroll > 0:
                dif_scroll -= 10
            if dif_scroll < 0:
                dif_scroll += 10
            
            # ノーツスピードの簡易変更
            selecting_info_sf.blit(rs.graphic(NOTE_SPEED_BTN_IMG), [500 - 6, 20 - 5])
            speed_selecting = 3
            if config["game"]["note_speed"] == 2:
                speed_selecting = 0
            if config["game"]["note_speed"] == 5:
                speed_selecting = 1
            if config["game"]["note_speed"] == 8:
                speed_selecting = 2
            selecting_info_sf.blit(rs.graphic(NOTE_SPEED_BTN_PRESSED_IMG),
                                   [500 + 75 * speed_selecting, 20], [75 * speed_selecting, 0, 75, 60])
            for s_i in range(3):
                if mouse.in_rect(500 + 75 * s_i, 20, 75, 60) and mouse.just_pressed(0):
                    config["game"]["note_speed"] = [2, 5, 8][s_i]
                    with open(os.path.join(PROJ_PATH, "config.json"), "w", encoding="utf-8_sig") as f:
                        json.dump(config, f, indent=4)
                    rs.se(CURSOR_SE).play()
            
            # 決定
            if keys.just_decided and not song_boxes.song_selected:
                song_boxes.song_selected = True
                selected_effect = pg.surface.Surface((256, 256), pg.SRCALPHA)
                pg.draw.rect(selected_effect, util.YELLOW, [0, 0, 256, 256])
                particles.add_effect(selected_effect, [550 + 128, 100 + 128], 0.6)
                rs.se(SONG_SELECTED_SE).play()
            
            # 楽曲の試聴
            if not song_boxes.song_selected:
                if song_boxes.tmr_standby == 60:
                    pg.mixer.music.load(song_boxes.selecting_song.get_music_path())
                    pg.mixer.music.play(start=song_boxes.selecting_song.get_demo_start(), fade_ms=500)
                elif song_boxes.tmr_standby == 0:
                    pg.mixer.music.stop()
                if song_boxes.tmr_standby > 60:
                    if not pg.mixer.music.get_busy():
                        pg.mixer.music.load(song_boxes.selecting_song.get_music_path())
                        pg.mixer.music.play(start=song_boxes.selecting_song.get_demo_start(), fade_ms=500)
                    if pg.mixer.music.get_pos() >= song_boxes.selecting_song.get_demo_end() * 100:
                        pg.mixer.music.fadeout(800)
            else:
                pg.mixer.music.fadeout(1000)
            
            # ゲームへ移る
            if song_boxes.tmr_to_game == 60:
                playing_song = song_boxes.selecting_song
                playing_song.load_plots(difficulty)
                finished_timer = 0
                game_timer = 0
                scene_changer.add_event(Index.PLAY, 180)
        
        # ゲーム
        elif scene_changer.index == Index.PLAY:
            notes_sf.fill(util.CLEAR)
            game_data_sf.fill(util.CLEAR)
            game_timer += 1
            if game_timer == 120:
                start_game_play()
            if playing_song.song_finished() and not scene_changer.is_busy() and game_timer > 120:
                finished_timer += 1
            if finished_timer == 1:
                pg.mixer.music.fadeout(1000)
            if miss_gr_timer > 0:
                miss_gr_timer -= 1
            
            # リザルトへ
            if finished_timer == 220:
                scene_changer.add_event(Index.RESULT, 120,
                                        lambda: [pg.mixer.music.load(rs.bgm_path(RESULT_BGM)),
                                                 pg.mixer.music.play(-1)])
                finished_timer = 221
            
            # 背景
            sc.blit(playing_song.jacket_bg, [0, 0])
            sc.blit(rs.graphic(GAME_BACKGROUND_BASE_IMG), [0, 0])
            
            # 難易度Easyの6レーン無効化
            if difficulty == Difficulty.EASY:
                sc.blit(rs.graphic(EASY_LANE_DISABLE_IMG), [0, -700 + (tmr * 5 % 700)])
                sc.blit(rs.graphic(EASY_LANE_DISABLE_IMG), [0, (tmr * 5 % 700)])
            
            # ノーツの描画
            notes, long = playing_song.calc_drawing_data(keys, note_sizes, auto_play)
            for ln in long:
                long_start_y = min(ln[1], 546 if ln[3] == 1 else ln[1])
                long_end_y = ln[2]
                
                if int(long_end_y) < 546:
                    for y in range(int(long_start_y), int(long_end_y), -1):
                        texture = rs.graphic(LONG_TEXTURES)[ln[3]]
                        if int(long_end_y) - y < 35:
                            texture.set_alpha(int(255 - (35 - (y - int(long_end_y))) * 255 / 35))
                        notes_sf.blit(texture,
                                      [ln[0] + note_sizes[NoteType.LONG][0] / 2 - 50,
                                       y + note_sizes[NoteType.LONG][1] / 2])
                
                notes_sf.blit(rs.graphic(NOTE_IMAGES)[NoteType.LONG], [ln[0], long_start_y])
                
                if config["general"]["debug"]:
                    notes_sf.blit(rs.font(ARIAL_REGULAR_FONT).render(str(ln[3])[:4], True, util.WHITE),
                                  [ln[0], long_start_y])
                    notes_sf.blit(rs.font(ARIAL_REGULAR_FONT).render(str(ln[4])[:4], True, util.WHITE), [ln[0], ln[2]])
            
            for n in notes:
                notes_sf.blit(rs.graphic(NOTE_IMAGES)[n[2]], n[:2])
                if config["general"]["debug"]:
                    notes_sf.blit(rs.font(ARIAL_REGULAR_FONT).render(str(n[3])[:4], True, util.WHITE), n[:2])
            
            # 叩いたときのレーンが光るやつと効果音
            for k_i, k in enumerate(keys.get_dfghjk_list()):
                if difficulty == Difficulty.EASY and k_i in [0, 5]:
                    continue
                if k:
                    particles.add(util.Particle(rs.graphic(CLICK_EFFECT_IMG), [150 + k_i * 100, 0]))
                    rs.se(CLICK_SE).play()
            if keys.just_pressed(pg.K_SPACE):
                rs.se(SPACE_SE).play()
            
            # ポーズ
            if keys.just_pressed(pg.K_F1):
                scene_changer.index = Index.PAUSE
                sc.blit(notes_sf, [0, 0])
                sc.blit(game_data_sf, [0, 0])
                sc.blit(particles.get_surface(), [0, 0])
                pause_background = sc.copy()
                pause_from = time.perf_counter()
                pg.mixer.music.pause()
                rs.se(OPEN_PAUSE_MENU_SE).play()
            
            # ノーツの判定
            judges = playing_song.calc_tap_judge(keys, keys.just_pressed(pg.K_SPACE), auto_play)
            for j in judges:
                if j[0] == Judge.PERFECT or j[0] == Judge.GOOD:
                    combo_effect = 8
                    particles.add(util.Particle(rs.graphic(JUDGE_IMAGES)[j[0]], [450, 500], center=True))
                    if auto_play:
                        particles.add(util.Particle(rs.graphic(AUTO_JUDGE), [450, 460], center=True))
                    particles.add(util.Particle(rs.graphic(COLLECT_EFFECT_IMG),
                                                [150 + j[1] * 100 + 50, 610], center=True))
                    
                    for _ in range(8 if j[0] == Judge.PERFECT else 5):
                        particles.add(util.SpreadingParticle
                                      ([random.randint(150 + j[1] * 100, 150 + j[1] * 100 + 100),
                                        random.randint(600, 620)],
                                       rs.graphic(TAP_PARTICLES_IMG), j[0] == Judge.PERFECT))
                    particles.add_effect(rs.graphic(TAP_PARTICLE2_IMG), [150 + j[1] * 100 + 50, 610],
                                         disappearing_speed=1, zoom_scale=4)
                    
                    if j[2] == NoteType.EX_TAP:
                        rs.se(EXTAP_SE).play()
                    elif j[2] == NoteType.FUZZY:
                        rs.se(FUZZY_SE).play()
                    else:
                        if j[0] == Judge.PERFECT:
                            rs.se(TAP_PERF_SE).play()
                        else:
                            rs.se(TAP_GOOD_SE).play()
                elif j[0] == Judge.MISS:
                    particles.add(util.Particle(rs.graphic(JUDGE_IMAGES)[Judge.MISS], [450, 500], center=True))
                    window_vib_timer = 15
                    window_vib_busy = True
                    window_original_pos = [get_window_rect().x, get_window_rect().y]
                    miss_gr_timer = 60
                elif j[0] == Judge.LONG_PRESSING:
                    if random.randint(0, 3) == 0:
                        particles.add(util.SpreadingParticle
                                      ([random.randint(150 + j[1] * 100, 150 + j[1] * 100 + 100),
                                        random.randint(600, 620)],
                                       rs.graphic(TAP_PARTICLES_IMG), True))
            
            # コンボの描画
            combo_effect = max(0, combo_effect - 2)
            if playing_song.get_combo() != 0 and finished_timer <= 40:
                combo_sf = rs.font(MOLOT_BIG_FONT).render \
                     (str(playing_song.get_combo()), True, util.WHITE
                      if playing_song.get_combo() < 10 * (difficulty.value + 1) ** 2 else util.GOLD)
                game_data_sf.blit(rs.graphic(COMBO_IMG),
                                  [450 - rs.graphic(COMBO_IMG).get_width() / 2, 285 - combo_effect])
                game_data_sf.blit(combo_sf, [450 - combo_sf.get_width() / 2, 300 - combo_effect])
            
            # スコアの描画
            if playing_song.get_score() != 0 and finished_timer <= 40:
                score_sf = rs.font(ARIAL_SMALL_FONT).render(str(playing_song.get_score()), True, util.TRANS_WHITE)
                game_data_sf.blit(score_sf, [450 - score_sf.get_width() / 2, 375])
            
            # ゲージの描画
            gauge_long = int(5 * playing_song.get_gauge_rate())
            game_data_sf.blit(rs.graphic(GAUGE_FULL_IMG) if playing_song.is_level_clear()
                              else rs.graphic(GAUGE_IMG), [76, 142],
                              pg.Rect(0, 0, 58, gauge_long))
            game_data_sf.blit(rs.graphic(GAUGE_FRAME_IMG), [66, 159])
            
            # ランクの描画
            rank_sf = rs.graphic(RANK_IMAGES)[playing_song.get_rank(difficulty)]
            rank_sf2 = rs.graphic(RANK_BASE_IMAGES)[playing_song.get_sp_clear_num()]
            game_data_sf.blit(rank_sf, [10, 10])
            game_data_sf.blit(rs.graphic(RANK_PATTERN_IMAGES)[playing_song.get_rank(difficulty)], [10, 10])
            game_data_sf.blit(rank_sf2, [10, 10])
            if playing_song.get_rank(difficulty) != past_rank:
                particles.add_effect(rank_sf2, [10 + rank_sf2.get_width() / 2, 10 + rank_sf2.get_height() / 2])
            past_rank = playing_song.get_rank(difficulty)
            
            # 判定ゲージの描画
            game_data_sf.blit(rs.graphic(JUDGE_BAR_IMG), [750, 395])
            cursor_color = rs.graphic(JUDGE_BAR_IMG).get_at((playing_song.get_judge_bar_bar() - 759, 9))
            pg.draw.polygon(game_data_sf, cursor_color, ((playing_song.get_judge_bar_bar()-10, 388),
                                                         (playing_song.get_judge_bar_bar()+10, 388),
                                                         (playing_song.get_judge_bar_bar(), 401)))
            judge_bar_text = rs.font(ARIAL_TINY_FONT).render(str(playing_song.judge_bar_num)[:5], True, util.WHITE)
            game_data_sf.blit(judge_bar_text,
                              [playing_song.get_judge_bar_bar() - judge_bar_text.get_width() / 2, 367])
            
            # ミスしたときの赤いやつ
            rs.graphic(MISS_GRADATION_IMG).set_alpha(int(miss_gr_timer / 60 * 255))
            game_data_sf.blit(rs.graphic(MISS_GRADATION_IMG), [0, 0])
            
            # 右下の曲詳細
            game_data_sf.blit(rs.graphic(GAME_DETAILS_IMG), [756, 446])
            detail_max_cmb = rs.font(MOLOT_SMALL1_FONT).render(str(playing_song.get_max_combo()), True, util.WHITE)
            game_data_sf.blit(detail_max_cmb, [756 + 119 - detail_max_cmb.get_width(), 446 + 44])
            detail_remaining_cmb = rs.font(MOLOT_SMALL1_FONT).render\
                (str(playing_song.remaining_combo), True, util.WHITE)
            game_data_sf.blit(detail_remaining_cmb, [756 + 119 - detail_remaining_cmb.get_width(), 446 + 84])
            for j_i, j in enumerate(list(Judge)):
                if j == Judge.LONG_PRESSING:
                    continue
                detail_judge = rs.font(MOLOT_TINY_FONT).render(str(playing_song.judge_counter[j]), True, util.WHITE)
                game_data_sf.blit(detail_judge, [756 + 119 - detail_judge.get_width(), 446 + 129 + j_i * 20])
            detail_accuracy = rs.font(MOLOT_SMALL1_FONT).render\
                (str(round(playing_song.get_accuracy(), 1)), True, util.WHITE)
            game_data_sf.blit(detail_accuracy, [756 + 104 - detail_accuracy.get_width(), 446 + 209])
            
            # FC・APの表示
            if finished_timer > 40:
                # クリア時
                if playing_song.get_clear_condition() != util.ClearCondition.FAILED:
                    # パーティクル表示
                    p1 = rs.graphic(CLEAR_PARTICLE_IMAGES) \
                        [0 if playing_song.get_clear_condition() == util.ClearCondition.CLEAR else 1]
                    if finished_timer - 40 < 56:
                        tmp_ang = math.radians(90 - ((finished_timer - 40) / 4) ** 2)
                        game_clear_particles.add(
                            util.Particle(p1,
                                          [450 + 100 * math.cos(tmp_ang), 350 + 100 * math.sin(tmp_ang)]))
                        game_clear_particles.add(
                            util.Particle(p1,
                                          [450 + 100 * math.cos(tmp_ang + math.pi),
                                           350 + 100 * math.sin(tmp_ang + math.pi)]))
                    elif finished_timer - 40 - 56 < 40:
                        tmp_scr = ((finished_timer - 40 - 56) / 4) ** 2
                        game_clear_particles.add(
                            util.Particle(p1, [450, 350 - 100 + tmp_scr]))
                        game_clear_particles.add(
                            util.Particle(p1, [450, 350 + 100 - tmp_scr]))
                    elif finished_timer - 40 - 56 - 40 < 70:
                        tmp1 = 70 - (finished_timer - 40 - 56 - 40)
                        tmp2 = (tmp1 / 4) ** 2
                        tmp_r = 306.25 - tmp2
                        if playing_song.get_clear_condition() == util.ClearCondition.ALL_PERFECT:
                            tmp_num = 10
                        elif playing_song.get_clear_condition() == util.ClearCondition.FULL_COMBO:
                            tmp_num = 8
                        else:
                            tmp_num = 6
                        for i in range(tmp_num):
                            if playing_song.get_clear_condition() == util.ClearCondition.ALL_PERFECT:
                                tmp_p = rs.graphic(CLEAR_PARTICLE_IMAGES)[i]
                            elif playing_song.get_clear_condition() == util.ClearCondition.FULL_COMBO:
                                tmp_p = rs.graphic(CLEAR_PARTICLE_IMAGES)[1]
                            else:
                                tmp_p = rs.graphic(CLEAR_PARTICLE_IMAGES)[0]
                            tmp_ang = math.radians(360 / tmp_num * i)
                            game_clear_particles.add(
                                util.Particle(tmp_p, [450 + tmp_r * math.cos(tmp_ang),
                                                      350 + tmp_r * math.sin(tmp_ang)]))
                    
                    # 文字表示
                    if 40 + 56 + 40 < finished_timer:
                        tmp = finished_timer - 40 - 56 - 40
                        if playing_song.get_clear_condition() == util.ClearCondition.ALL_PERFECT:
                            ap_image_z = pg.transform.rotozoom(rs.graphic(ALL_PERFECT_IMG), 0,
                                                               (min(20, tmp) / 20) ** 2)
                            game_data_sf.blit(ap_image_z,
                                              [450 - ap_image_z.get_width() / 2, 350 - ap_image_z.get_height() / 2])
                            if tmp == 20:
                                particles.add_effect(rs.graphic(ALL_PERFECT_IMG), [450, 350], 0.7)
                        elif playing_song.get_clear_condition() == util.ClearCondition.FULL_COMBO:
                            fc_image_z = pg.transform.rotozoom(rs.graphic(FULL_COMBO_IMG), 0,
                                                               (min(10, tmp) / 10) ** 2)
                            game_data_sf.blit(fc_image_z,
                                              [450 - fc_image_z.get_width() / 2, 350 - fc_image_z.get_height() / 2])
                            if tmp == 10:
                                particles.add_effect(rs.graphic(FULL_COMBO_IMG), [450, 350], 0.7)
                        else:
                            cl_image_z = pg.transform.rotozoom(rs.graphic(LEVEL_CLEAR_IMG), 0,
                                                               (min(10, tmp) / 10) ** 2)
                            game_data_sf.blit(cl_image_z,
                                              [450 - cl_image_z.get_width() / 2, 350 - cl_image_z.get_height() / 2])
                            if tmp == 10:
                                particles.add_effect(rs.graphic(LEVEL_CLEAR_IMG), [450, 350], 0.7)
                
                else:  # 失敗
                    rs.graphic(LEVEL_FAILED_IMG).set_alpha(int(min(finished_timer - 40, 30) * 255 / 30))
                    game_data_sf.blit(rs.graphic(LEVEL_FAILED_IMG),
                                      [450 - rs.graphic(LEVEL_FAILED_IMG).get_width() / 2,
                                       350 - rs.graphic(LEVEL_FAILED_IMG).get_height() / 2])
            
            if playing_song.is_level_clear() or playing_song.get_sp_clear_num():
                if finished_timer == 136:
                    rs.se(CLEAR_SE).play()
            elif finished_timer == 50:
                rs.se(FAILED_SE).play()
        
        elif scene_changer.index == Index.PAUSE:
            game_data_sf.fill(util.CLEAR)
            sc.blit(pause_background, [0, 0])
            sc.blit(pause_gradation, [0, 0])
            
            if not restart_countdown and not scene_changer.is_busy():
                for i_i, icon in enumerate([rs.graphic(RETURN_IMG), rs.graphic(RELOAD_IMG), rs.graphic(ARROW_IMG)]):
                    if mouse.in_rect(320 + 130 * i_i - icon.get_width() / 2, 350 - icon.get_height() / 2,
                                     icon.get_width(), icon.get_height()):
                        icon.set_alpha(min(220, icon.get_alpha() + 5))
                        if mouse.just_pressed(0):
                            if icon == rs.graphic(RETURN_IMG):
                                scene_changer.add_event(Index.SONG_SELECT, 120, close_song)
                            elif icon == rs.graphic(RELOAD_IMG):
                                playing_song.quit_song()
                                playing_song.load_plots(difficulty)
                                finished_timer = 0
                                game_timer = 0
                                scene_changer.add_event(Index.PLAY, 180)
                            else:
                                restart_timer = 60 * 3
                                restart_countdown = True
                    else:
                        icon.set_alpha(max(150, icon.get_alpha() - 5))
                
                sc.blit(rs.graphic(RETURN_IMG), [320 - rs.graphic(RETURN_IMG).get_width() / 2,
                                                 350 - rs.graphic(RETURN_IMG).get_height() / 2])
                sc.blit(rs.graphic(RELOAD_IMG), [450 - rs.graphic(RELOAD_IMG).get_width() / 2,
                                                 350 - rs.graphic(RELOAD_IMG).get_height() / 2])
                sc.blit(rs.graphic(ARROW_IMG), [580 - rs.graphic(ARROW_IMG).get_width() / 2,
                                                350 - rs.graphic(ARROW_IMG).get_height() / 2])
                
                if keys.just_pressed(pg.K_F1):
                    restart_timer = 60 * 3
                    restart_countdown = True
            
            if restart_countdown:
                if restart_timer == 0:
                    restart_countdown = False
                    scene_changer.index = Index.PLAY
                    playing_song.paused_time += time.perf_counter() - pause_from
                    pg.mixer.music.unpause()
                    rs.se(CLOSE_PAUSE_MENU_SE).play()
                else:
                    if restart_timer % 60 == 0:
                        rs.se(CLICK_SE).play()
                    count_text = rs.font(ARIAL_HUGE_FONT).render(str(-(-restart_timer // 60)), True, util.WHITE)
                    sc.blit(count_text, [450 - count_text.get_width() / 2, 350 - count_text.get_height() / 2])
                restart_timer -= 1
        
        elif scene_changer.index == Index.RESULT:
            game_data_sf.fill(util.CLEAR)
            sc.blit(rs.graphic(RESULT_BACKGROUNDS)[difficulty], [0, 0])
            title_sf = rs.font(ARIAL_REGULAR_FONT).render(playing_song.get_title(), True, util.WHITE)
            game_data_sf.blit(title_sf, [60, 21])
            result_timer += 1
            if back_select_timer > 0:
                back_select_timer += 1
            if result_timer >= 60:
                
                score_result_sf = rs.font(MOLOT_BIG_FONT).render(
                    str(min(playing_song.get_score(), (result_timer - 60) * 10000)).zfill
                    (len(str(playing_song.get_score()))), True, util.WHITE)
                if playing_song.get_score() >= (result_timer - 60) * 10000 and tmr % 5 == 0:
                    rs.se(COUNT_NUMBER_SE).play()
                game_data_sf.blit(score_result_sf, [310, 170])
                
                for j_i, j in enumerate([Judge.PERFECT, Judge.GOOD, Judge.MISS]):
                    judge_count_sf = rs.font(ARIAL_SMALL_FONT).render(
                        str(min(playing_song.get_judge_count(j), result_timer * 2)), True, util.WHITE)
                    
                    game_data_sf.blit(judge_count_sf, [301 + j_i * 164 + (164 - judge_count_sf.get_width())/2,
                                                       365])
                    if playing_song.get_judge_count(j) >= result_timer * 2 and tmr % 5 == 0:
                        rs.se(COUNT_NUMBER_SE).play()
                
                max_combo_sf = rs.font(MOLOT_BIG_FONT).render \
                    (str(min(playing_song.get_max_combo(), (result_timer - 60) * 2))
                     .zfill(len(str(playing_song.get_max_combo()))), True, util.WHITE)
                game_data_sf.blit(rs.graphic(COMBO_IMG), [140 - rs.graphic(COMBO_IMG).get_width() / 2, 440])
                game_data_sf.blit(max_combo_sf,
                                  [140 - max_combo_sf.get_width() / 2, 500 - max_combo_sf.get_height() / 2])
                accuracy_sf = rs.font(MOLOT_SMALL2_FONT).render\
                    (str(round(playing_song.get_accuracy(), 1)), True, util.WHITE)
                game_data_sf.blit(accuracy_sf, [135, 559])
                
                if playing_song.get_max_combo() >= (result_timer - 60) * 2 and tmr % 5 == 0:
                    rs.se(COUNT_NUMBER_SE).play()
            
            if result_timer >= 240:
                rank_sf = rs.graphic(RANK_IMAGES)[playing_song.get_rank(difficulty)]
                rank_sf2 = rs.graphic(RANK_BASE_IMAGES)[playing_song.get_sp_clear_num()]
                game_data_sf.blit(rank_sf, [50, 150])
                game_data_sf.blit(rs.graphic(RANK_PATTERN_IMAGES)[playing_song.get_rank(difficulty)], [50, 150])
                game_data_sf.blit(rank_sf2, [50, 150])
                if result_timer == 240:
                    particles.add_effect(rank_sf2, [140, 240], 0.7)
                    rs.se(RANK_SE).play()
                if playing_song.get_sp_clear_num():
                    condition_image = rs.graphic(playing_song.get_cl_cnd_mini_img())
                    game_data_sf.blit(condition_image, [300, 270])
                    if result_timer == 240:
                        particles.add_effect(condition_image, [300 + condition_image.get_width() / 2,
                                                               270 + condition_image.get_height() / 2])
            
            if keys.just_decided:
                if result_timer >= 300 and not scene_changer.is_busy():
                    scene_changer.add_event(Index.SONG_SELECT, 180, close_song)
                elif result_timer < 300:
                    result_timer = 10000
        
        if scene_changer.index == Index.SONG_SELECT:
            sc.blit(selecting_info_sf, [0, 0])
        elif scene_changer.index == Index.PLAY:
            sc.blit(notes_sf, [0, 0])
            sc.blit(game_clear_particles.get_surface(), [0, 0])
            sc.blit(game_data_sf, [0, 0])
        elif scene_changer.index == Index.RESULT:
            sc.blit(game_data_sf, [0, 0])
        elif scene_changer.index == Index.MODE_SELECT:
            sc.blit(mode_select_sf, [0, 0])
        
        sc.blit(particles.get_surface(), [0, 0])
        sc.blit(scene_changer.get_surface(), [0, 0])
        if config["general"]["debug"]:
            fps_text = rs.font(ARIAL_SMALL_FONT).render("FPS: " + str(int(cl.get_fps())), True, util.WHITE)
            sc.blit(fps_text, [0, 0])
        
        pg.display.update()
        cl.tick(60)


if __name__ == '__main__':
    main()
