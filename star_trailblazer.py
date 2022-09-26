import math
from tkinter import filedialog

import pygame as pg
import tkinter as tk
import json
from tkinter import *
import os
import util
from trailblazer_plots import *


def main():
    # 初期化
    pg.display.set_caption("starbits notes designer")
    cl = pg.time.Clock()
    with open(os.path.join(PROJ_PATH, "config.json"), "r", encoding="utf-8_sig") as j:
        config: dict = json.load(j)
    tmr = 0
    rs = Resources(config)
    rs.show_loading_bar(sc)
    mouse = util.Mouse()
    keys = util.Keys()
    
    # 変数
    plots: list[PlotData] = []
    longs: list[LongData] = []
    long_start_temp: LongStartData | None = None
    speed_changes = []
    scroll = 0
    scroll_goal = 0
    pixel_per_measure = 600
    file_path = ""
    
    def load_from_snp():  # 読み込み
        nonlocal plots, longs
        file_load_path = filedialog.askopenfilenames(filetypes=[("Starbit Note Plots", ".snp")])
        if not file_load_path:
            return
        if not os.path.exists(file_load_path[0]):
            return
        
        plots = []
        longs = []
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
                        plots.append(PlotData(NoteType.TAP, c_i, m_i, b_i, len(measure_txt.split(","))))
                    if note_txt == "2":
                        plots.append(PlotData(NoteType.EX_TAP, c_i, m_i, b_i, len(measure_txt.split(","))))
                    if note_txt == "3":
                        long_start_loaded.append([c_i, m_i, b_i, len(measure_txt.split(","))])
                    if note_txt == "4":
                        long_end_loaded.append([c_i, m_i, b_i, len(measure_txt.split(","))])
                    if note_txt == "5":
                        plots.append(PlotData(NoteType.FUZZY, c_i, m_i, b_i, len(measure_txt.split(","))))
                if len(beat_txt) >= 8:
                    if beat_txt[6] == "s":
                        if beat_txt[7:].isdecimal():
                            speed_changes.append(SpeedChangeData(round(int(beat_txt[7:]) / 10, 1),
                                                                 m_i, b_i, len(measure_txt.split(","))))
        for ls in long_start_loaded:
            for le in long_end_loaded:
                if ls[1] + ls[2] / ls[3] < le[1] + le[2] / le[3] and ls[0] == le[0]:
                    longs.append(LongData(ls[0], [ls[1], le[1]], [ls[2], le[2]], [ls[3], le[3]]))
                    long_end_loaded.remove(le)
                    break
    
    def save(path: str = ""):  # 保存
        if not path:
            path = file_path
        if not os.path.exists(path):
            save_as()
            return
        text = []
        plots_copy = plots + sum([ln2.points_as_plot() for ln2 in longs], [])
        for m_i in range(1000):  # 小節の番号
            if not plots_copy:  # 空になったら
                break
            plots_in_measure = []  # 小節にあるノーツ
            plots_poped_after = []
            for p_i2, p2 in enumerate(plots_copy):
                if p2.measure == m_i:
                    plots_in_measure.append(p2)
                    plots_poped_after.append(p_i2)
        
            plots_poped_after.reverse()
            for p_i2 in plots_poped_after:
                plots_copy.pop(p_i2)
        
            # 最小公倍数に合わせる
            beat_split_lcm = math.lcm(*[p3.splitting for p3 in plots_in_measure])
            text.append([])
            for p_i2, p2 in enumerate(plots_in_measure):
                p2.beat *= beat_split_lcm / p2.splitting
                p2.splitting = beat_split_lcm
        
            for b_i in range(beat_split_lcm):  # 拍ごとに
                plots_in_beat = []
                for p2 in plots_in_measure:
                    if p2.beat == b_i:
                        plots_in_beat.append(p2)
                plots_columns = ["0"] * 6
                for p2 in plots_in_beat:
                    if p2.note_type != NoteType.LONG:
                        plots_columns[p2.column] = p2.note_type.value
                    else:
                        p2_lp: LongPointData = p2
                        plots_columns[p2.column] = str(3 + p2_lp.is_end)
                plot_text_tmp = "".join(plots_columns)
            
                for s in speed_changes:
                    if s[1] == m_i and s[2] * beat_split_lcm / s[3] == b_i:
                        plot_text_tmp += f"s{int(s[0] * 10)}"
                        break
                text[-1].append(plot_text_tmp)
    
        if not os.path.exists(path):
            pg.quit()
            sys.exit()
        with open(path, "w") as f:
            for m in text:
                for b_i, b in enumerate(m):
                    f.write(b)
                    f.write("," if b_i + 1 < len(m) else ".")
    
    def save_as():  # 名前をつけて保存
        path = filedialog.asksaveasfilename(
            defaultextension=".snp", title="譜面データを保存", filetypes=[("Starbit Note Plots", ".snp")])
        if not path or not os.path.exists(path[0]):
            return
        save(path)
    
    while True:
        tmr += 1
        for e in pg.event.get():
            if e.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if e.type == pg.MOUSEBUTTONDOWN:  # スクロールの終点の設定
                if e.button == 4:
                    if pg.key.get_pressed()[pg.K_LCTRL]:
                        pixel_per_measure -= 100
                        pixel_per_measure = max(100, pixel_per_measure)
                    else:
                        scroll_goal += 100
                        if keys.shift_clicking:
                            scroll_goal += 400
                elif e.button == 5:
                    if pg.key.get_pressed()[pg.K_LCTRL]:
                        pixel_per_measure += 100
                    else:
                        scroll_goal -= 100
                        if keys.shift_clicking:
                            scroll_goal -= 400
                        scroll_goal = max(0, scroll_goal)
        
        mouse.update()
        keys.update()
        sc.blit(rs.graphic(TRAILBLAZER_BG_IMG), [0, 0])
        
        # スクロール処理
        if scroll > scroll_goal:
            if scroll - scroll_goal > 80:
                scroll -= 80
            elif scroll - scroll_goal > 10:
                scroll -= 10
            else:
                scroll = scroll_goal
        if scroll < scroll_goal:
            if scroll_goal - scroll > 80:
                scroll += 80
            elif scroll_goal - scroll > 10:
                scroll += 10
            else:
                scroll = scroll_goal
                
        # Plotの描画  メモ: 判定バーの中心y座標は610
        for p_i, p in enumerate(plots):
            distance = p.measure_as_float * pixel_per_measure
            note = rs.graphic(NOTE_IMAGES)[p.note_type]
            p_y = 700 + scroll - distance - note.get_height() / 2
            if -note.get_height() < p_y < 700 + note.get_height():
                sc.blit(note, [250 + 50 + p.column * 100 - note.get_width() / 2,
                               610 + scroll - distance - note.get_height() / 2])
        
        # longの描画
        for ln_i, ln in enumerate(longs):
            end_y = 610 + scroll - ln.end.measure_as_float * pixel_per_measure
            start_y = 610 + scroll - ln.start.measure_as_float * pixel_per_measure
    
            # 線の描画
            for y in range(int(start_y), int(end_y), -1):
                if not (0 <= y < 700):
                    continue
                texture = rs.graphic(LONG_TEXTURES)[0]
                if int(end_y) - y < 35:
                    texture.set_alpha(int(255 - (35 - (y - int(end_y))) * 255 / 35))
                sc.blit(texture, [250 + ln.column * 100, y])
    
            # 始点の描画
            start_distance = ln.start.measure_as_float * pixel_per_measure
            note = rs.graphic(NOTE_IMAGES)[NoteType.LONG]
            p_y = 700 + scroll - start_distance - note.get_height() / 2
            if -127 < p_y < 700 + 127:
                sc.blit(note, [250 + 50 + ln.column * 100 - note.get_width() / 2,
                               610 + scroll - start_distance - note.get_height() / 2])
        
        # 右のツールバー
        toolbar_cmd = [load_from_snp, save, save_as]
        for ti_i in range(3):
            if mouse.in_rect(850, ti_i*50, 50, 50):
                sc.blit(rs.graphic(TOOLBAR_HIGHLIGHT_IMG), [850, ti_i*50])
                if mouse.just_pressed(0):
                    toolbar_cmd[ti_i]()
        
        pg.display.update()
        cl.tick(60)


if __name__ == '__main__':
    pg.display.set_caption("star trailblazer")
    sc = pg.display.set_mode((900, 700), pg.SRCALPHA)
    from data_loader import *
    
    root = tk.Tk()
    root.withdraw()
    main()
