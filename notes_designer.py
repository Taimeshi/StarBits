import pygame as pg
import sys
from tkinter import filedialog
import tkinter as tk
import math
import json
import util
import itertools

"""
操作方法
sキー　保存
z、xキー　拍数の変更
q, wキー　ソフランスピ変更
shift +　右クリ ソフラン追加
shift + e ソフラン削除

shift + o 一拍挿入
shift + p 一拍削除

"""


def get_beat_sum(pl: list):
    return pl[2] + pl[4] / pl[3]


def main():
    pg.display.set_caption("starbits notes designer")
    cl = pg.time.Clock()
    with open(os.path.join(PROJ_PATH, "config.json"), "r", encoding="utf-8_sig") as j:
        config: dict = json.load(j)
    tmr = 0
    rs = Resources(config)
    rs.start_load()
    tmp_font = pg.font.Font(None, 30)
    while rs.loading:
        sc.fill(util.BLACK)
        pg.draw.rect(sc, util.WHITE, [150, 350, 600, 50], 2)
        pg.draw.rect(sc, util.GREEN, [155, 355, 590 / 100 * rs.update(), 40])
        sc.blit(tmp_font.render(rs.loading_category.name.lower(), True, util.WHITE), [150, 320])
        pg.display.update()
    scroll = -100
    splitting = 4
    note_type_current = NoteType.TAP
    plots = []
    long_plots_old = {"start": [], "end": []}
    long_plots = []
    long_start_tmp = None
    long_extending = False
    speed_changes = []
    mouse_l_clicked = 0
    mouse_r_clicked = 0
    m_x, m_y = 0, 0
    speed_num = 2
    
    pixel_per_measure = 600
    measure_per_pixel = 1 / pixel_per_measure
    
    # 復元
    file_load_path = filedialog.askopenfilenames(filetypes=[("Starbit Note Plots", ".snp")], initialdir="./")
    if not file_load_path:
        pg.exit()
        sys.exit()
    if not os.path.exists(file_load_path[0]):
        pg.quit()
        sys.exit()
    
    # 読み込み
    with open(file_load_path[0], "r") as f:
        text = f.read()
    text = text.replace(" ", "")
    text = text.replace("\n", "")
    text = text.rstrip(".")
    text_tmp = text.split(".")
    long_start_loaded = []
    long_end_loaded = []
    for m_i, measure_txt in enumerate(text_tmp):
        for b_i, beat_txt in enumerate(measure_txt.split(",")):
            for c_i in range(6):
                note_txt = "0"
                if len(beat_txt) - 1 >= c_i:
                    note_txt = beat_txt[c_i]
                if note_txt == "1":
                    plots.append([NoteType.TAP, c_i, m_i, len(measure_txt.split(",")), b_i])
                if note_txt == "2":
                    plots.append([NoteType.EX_TAP, c_i, m_i, len(measure_txt.split(",")), b_i])
                if note_txt == "3":
                    long_start_loaded.append([NoteType.LONG, c_i, m_i, len(measure_txt.split(",")), b_i, 0])
                if note_txt == "4":
                    long_end_loaded.append([NoteType.LONG, c_i, m_i, len(measure_txt.split(",")), b_i, 1])
                if note_txt == "5":
                    plots.append([NoteType.FUZZY, c_i, m_i, len(measure_txt.split(",")), b_i])
            if len(beat_txt) >= 8:
                if beat_txt[6] == "s":
                    if beat_txt[7:].isdecimal():
                        speed_changes.append([round(int(beat_txt[7:]) / 10, 1), m_i, b_i, len(measure_txt.split(","))])
    for ls in long_start_loaded:
        for le in long_end_loaded:
            if get_beat_sum(ls) < get_beat_sum(le) and ls[1] == le[1]:
                long_plots.append([ls, le])
                long_end_loaded.remove(le)
                break

    # マウスの座標からレーン、小節、拍を計算します。
    def calc_pos():
        d = 700 - m_y + scroll
        c = int((m_x - 150) / 100)
        int_m = int(d * measure_per_pixel)
        tmp = d - int_m * pixel_per_measure
        be = 0
        for b_i2 in range(splitting + 1):
            if abs(b_i2 / splitting * pixel_per_measure - tmp) <= pixel_per_measure / (2 * splitting):
                if b_i2 < splitting:
                    be = b_i2
                else:
                    int_m += 1
                    be = 0
                break
        return c, int_m, be
    
    while True:
        tmr += 1
        
        for e in pg.event.get():
            if e.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if e.type == pg.MOUSEBUTTONDOWN:  # スクロール
                if e.button == 4:
                    if pg.key.get_pressed()[pg.K_LCTRL]:
                        pixel_per_measure -= 100
                        pixel_per_measure = max(100, pixel_per_measure)
                        measure_per_pixel = 1 / pixel_per_measure
                    else:
                        scroll += 100
                        if shift_clicking:
                            scroll += 900
                elif e.button == 5:
                    if pg.key.get_pressed()[pg.K_LCTRL]:
                        pixel_per_measure += 100
                        measure_per_pixel = 1 / pixel_per_measure
                    else:
                        scroll -= 100
                        if shift_clicking:
                            scroll -= 900
                        scroll = max(-100, scroll)
            
            if e.type == pg.KEYDOWN:
                if e.key == pg.K_n:  # ノーツの種類
                    note_types = [n for n in NoteType]
                    if note_type_current == NoteType.LONG:
                        long_start_tmp = None
                    note_type_current = note_types[(note_types.index(note_type_current) + 1) % len(note_types)]
                
                if e.key == pg.K_z:  # 拍数
                    splitting -= 1
                    splitting = max(1, splitting)
                if e.key == pg.K_x:  # 拍数
                    splitting += 1
                
                if e.key == pg.K_q:  # ソフラン
                    if speed_num == int(speed_num):
                        speed_num += 1
                    else:
                        speed_num += 0.2
                        speed_num = round(speed_num, 1)
                        if speed_num == int(speed_num):
                            speed_num = int(speed_num)
                if e.key == pg.K_w:  # ソフラン
                    if speed_num == int(speed_num) and speed_num > 1:
                        speed_num -= 1
                    else:
                        speed_num -= 0.2
                        speed_num = round(speed_num, 1)
                        speed_num = max(0.2, speed_num)
                
                if e.key == pg.K_o:  # 一拍追加
                    _, m, b = calc_pos()
                    
                    for p in plots:
                        # 0type, 1column, 2measure, 3splitting, 4beat
                        if m + b / splitting <= p[2] + p[4] / p[3]:
                            new_s = math.lcm(splitting, p[3])
                            p[3] = new_s
                            p[4] += new_s / splitting
                            while p[4] >= p[3]:
                                p[2] += 1
                                p[4] -= p[3]
                    
                    for ln in itertools.chain.from_iterable(long_plots):
                        # 0type, 1column, 2measure, 3splitting, 4beat
                        if m + b / splitting <= ln[2] + ln[4] / ln[3]:
                            new_s = math.lcm(splitting, ln[3])
                            ln[3] = new_s
                            ln[4] += new_s / splitting
                            while ln[4] >= ln[3]:
                                ln[2] += 1
                                ln[4] -= ln[3]

                if e.key == pg.K_p:  # 一拍削除
                    _, m, b = calc_pos()
                    
                    for p in plots:
                        # 0type, 1column, 2measure, 3splitting, 4beat
                        if m + b / splitting <= p[2] + p[4] / p[3]:
                            new_s = math.lcm(splitting, p[3])
                            p[3] = new_s
                            p[4] -= new_s / splitting
                            while p[4] < 0:
                                p[2] -= 1
                                if p[2] < 0:
                                    p[2] = 0
                                p[4] += p[3]
                    
                    for ln in itertools.chain.from_iterable(long_plots):
                        # 0type, 1column, 2measure, 3splitting, 4beat
                        if m + b / splitting <= ln[2] + ln[4] / ln[3]:
                            new_s = math.lcm(splitting, ln[3])
                            ln[3] = new_s
                            ln[4] -= new_s / splitting
                            while ln[4] < 0:
                                ln[2] -= 1
                                if ln[2] < 0:
                                    ln[2] = 0
                                ln[4] += ln[3]
                
                if e.key == pg.K_s:  # 保存
                    text = []
                    plots_copy = plots.copy() + sum(long_plots, [])  # itertools.chain.from_iterable(long_plots)
                    for m_i in range(100):  # 小節の番号
                        if not plots_copy:  # 空になったら
                            break
                        plots_in_measure = []  # 小節にあるノーツ
                        plots_poped_after = []
                        for p_i, p in enumerate(plots_copy):
                            if p[2] == m_i:
                                plots_in_measure.append(p)
                                plots_poped_after.append(p_i)
                        
                        plots_poped_after.reverse()
                        for p_i in plots_poped_after:
                            plots_copy.pop(p_i)
                        
                        # 最小公倍数に合わせる
                        beat_split_lcm = math.lcm(*[p[3] for p in plots_in_measure])
                        text.append([])
                        for p_i, p in enumerate(plots_in_measure):
                            p[4] *= beat_split_lcm / p[3]
                            p[3] = beat_split_lcm
                        
                        for b_i in range(beat_split_lcm):  # 拍ごとに
                            plots_in_beat = []
                            for p in plots_in_measure:
                                if p[4] == b_i:
                                    plots_in_beat.append(p)
                            plots_columns = ["0"] * 6
                            for p in plots_in_beat:
                                if p[0] != NoteType.LONG:
                                    plots_columns[p[1]] = p[0].value
                                else:
                                    plots_columns[p[1]] = str(3 + p[5])
                            plot_text_tmp = "".join(plots_columns)
                            
                            for s in speed_changes:
                                if s[1] == m_i and s[2] * beat_split_lcm / s[3] == b_i:
                                    plot_text_tmp += f"s{int(s[0] * 10)}"
                                    break
                            text[-1].append(plot_text_tmp)
                    
                    file_save_path = filedialog.asksaveasfilename(
                        defaultextension=".snp", title="譜面データを保存", filetypes=[("Starbit Note Plots", ".snp")],
                        initialdir=file_load_path)
                    if not os.path.exists(file_save_path):
                        pg.quit()
                        sys.exit()
                    with open(file_save_path, "w") as f:
                        for m in text:
                            for b_i, b in enumerate(m):
                                f.write(b)
                                f.write("," if b_i + 1 < len(m) else ".")
        
        m_x, m_y = pg.mouse.get_pos()
        sc.fill(util.BLACK)
        if pg.mouse.get_pressed()[0]:
            mouse_l_clicked += 1
        else:
            mouse_l_clicked = 0
        if pg.mouse.get_pressed()[2]:
            mouse_r_clicked += 1
        else:
            mouse_r_clicked = 0
        
        shift_clicking = bool(pg.key.get_pressed()[pg.K_LSHIFT])
        
        for l_i in range(7):
            # 242 16
            pg.draw.rect(sc, util.WHITE, [142 + l_i * 100, 0, 16, 700])
        if mouse_l_clicked == 1:
            column, int_measure, beat = calc_pos()
            if note_type_current != NoteType.LONG:
                plots.append([note_type_current, column, int_measure, splitting, beat])
            else:
                if long_start_tmp:
                    long_end = [note_type_current, long_start_tmp[1], int_measure, splitting, beat, 1]
                    if long_start_tmp[2] + long_start_tmp[4] / long_start_tmp[3] > \
                            long_end[2] + long_end[4] / long_end[3]:
                        long_start_tmp, long_end = long_end, long_start_tmp
                    long_plots.append([long_start_tmp, long_end])
                    long_start_tmp = None
                else:
                    long_start_tmp = [note_type_current, column, int_measure, splitting, beat, 0]
                    long_extending = not long_extending
        
        if shift_clicking and mouse_r_clicked == 1:
            speed_changes.append([speed_num, *calc_pos()[1:], splitting])
        
        for m_i in range(10000):
            bar_y = 700 + scroll - m_i * (pixel_per_measure / splitting)
            if -5 < bar_y < 700 + 5:
                pg.draw.line(sc, util.WHITE, [150, bar_y], [750, bar_y])
                if m_i % splitting == 0:
                    pg.draw.line(sc, util.YELLOW, [150, bar_y], [750, bar_y], width=4)
            elif -5 > bar_y:
                break
        
        speed_changes_poped_after = []
        for s_i, s in enumerate(speed_changes):
            distance = (s[1] + s[2] / s[3]) * pixel_per_measure
            pg.draw.line(sc, util.LIGHT_GREEN, [150, 700 + scroll - distance], [750, 700 + scroll - distance], width=3)
            speed_num_sf = rs.font(ARIAL_SMALL_FONT).render(str(s[0]), True, util.LIGHT_GREEN)
            sc.blit(speed_num_sf, [120, 680 + scroll - distance])
            if pg.key.get_pressed()[pg.K_e] and abs(700 + scroll - distance - m_y) < 25:
                speed_changes_poped_after.append(s_i)
        speed_changes_poped_after.reverse()
        for s_i in speed_changes_poped_after:
            speed_changes.pop(s_i)
        
        long_plots_poped_after = []
        for ln_i, ln in enumerate(long_plots):
            end_y = 700 + scroll - (ln[1][2] + ln[1][4] / ln[1][3]) * pixel_per_measure
            start_y = 700 + scroll - (ln[0][2] + ln[0][4] / ln[0][3]) * pixel_per_measure

            # 線の描画
            for y in range(int(start_y), int(end_y), -1):
                if not (0 <= y < 700):
                    continue
                texture = rs.graphic(LONG_TEXTURES)[0]
                if int(end_y) - y < 35:
                    texture.set_alpha(int(255 - (35 - (y - int(end_y))) * 255 / 35))
                sc.blit(texture, [150 + ln[0][1] * 100, y])
            
            # 始点の描画
            distance = (ln[0][2] + ln[0][4] / ln[0][3]) * pixel_per_measure
            note = rs.graphic(NOTE_IMAGES)[ln[0][0]]
            p_y = 700 + scroll - distance - note.get_height() / 2
            if -127 < p_y < 700 + 127:
                sc.blit(note, [150 + ln[0][1] * 100 - note.get_width() / 2 + 50,
                               700 + scroll - distance - note.get_height() / 2])
            
            # 削除
            if pg.mouse.get_pressed()[2] and not shift_clicking:
                if pg.Rect(150 + ln[0][1] * 100 - 50 + 50, 700 + scroll - distance - 10, 100, 20).collidepoint(
                        m_x, m_y):
                    long_plots_poped_after.append(ln_i)
                elif pg.Rect(150 + ln[1][1] * 100 - 50 + 50, 700 + scroll - distance - 10, 100, 20).collidepoint(
                        m_x, m_y):
                    long_plots_poped_after.append(ln_i)
        
        plots_poped_after = []
        for p_i, p in enumerate(plots):
            distance = (p[2] + p[4] / p[3]) * pixel_per_measure
            note = rs.graphic(NOTE_IMAGES)[p[0]]
            p_y = 700 + scroll - distance - note.get_height() / 2
            if -127 < p_y < 700 + 127:
                sc.blit(note,
                        [150 + p[1] * 100 - note.get_width() / 2 + 50, 700 + scroll - distance - note.get_height() / 2])
            if pg.mouse.get_pressed()[2] and not shift_clicking:
                if pg.Rect(150 + p[1] * 100 - 50 + 50, 700 + scroll - distance - 10, 100, 20).collidepoint(m_x, m_y):
                    plots_poped_after.append(p_i)
        
        if long_start_tmp:
            distance = get_beat_sum(long_start_tmp) * pixel_per_measure
            note = rs.graphic(NOTE_IMAGES)[long_start_tmp[0]]
            p_y = 700 + scroll - distance - note.get_height() / 2
            if -127 < p_y < 700 + 127:
                sc.blit(note,
                        [150 + long_start_tmp[1] * 100 - note.get_width() / 2 + 50,
                         700 + scroll - distance - note.get_height() / 2])

        plots_poped_after.reverse()
        long_plots_poped_after.reverse()
        for p_i in plots_poped_after:
            plots.pop(p_i)
        for p_i in long_plots_poped_after:
            long_plots.pop(p_i)
        
        sc.blit(rs.graphic(NOTE_IMAGES)[note_type_current],
                [m_x - rs.graphic(NOTE_IMAGES)[note_type_current].get_width() / 2,
                 m_y - rs.graphic(NOTE_IMAGES)[note_type_current].get_height() / 2])
        split_num_sf = rs.font(MOLOT_REGULAR_FONT).render(str(splitting), True, util.WHITE)
        sc.blit(split_num_sf, [800, 600])
        
        current_speed_num_sf = rs.font(MOLOT_REGULAR_FONT).render(str(speed_num), True, util.LIGHT_GREEN)
        sc.blit(current_speed_num_sf, [800, 500])
        
        pg.display.update()
        cl.tick(60)


if __name__ == '__main__':
    pg.display.set_caption("notes designer")
    sc = pg.display.set_mode((900, 700), pg.SRCALPHA)
    from data_loader import *
    
    root = tk.Tk()
    root.withdraw()
    main()
