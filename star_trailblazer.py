import math
from tkinter import filedialog, messagebox

import pygame as pg
import tkinter as tk

from trailblazer_plots import *


def main():
    # 初期化
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
    long_start_tmp: list | None = None
    speed_changes: list[SpeedChangeData] = []
    scroll = 0
    scroll_goal = 0
    pixel_per_measure = 600
    file_path = ""
    selecting_type = NoteType.TAP
    selecting_plots: list[PlotData] = []
    dragging_plot: bool = False
    
    splitting_box = util.TextBox(rs)
    ex_speed_box = util.TextBox(rs)
    splitting_box.init_value(8)
    ex_speed_box.init_value(2.0)
    splitting_box.rect = [97, 463, 123, 25]
    ex_speed_box.rect = [144, 512, 76, 26]
    splitting_box.font = rs.font(ARIAL_TINY2_FONT)
    ex_speed_box.font = rs.font(ARIAL_TINY2_FONT)
    
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
        for m_i3, measure_txt in enumerate(text_tmp):
            for b_i, beat_txt in enumerate(measure_txt.split(",")):
                for c_i in range(6):
                    note_txt = "0"
                    if len(beat_txt) - 1 >= c_i:
                        note_txt = beat_txt[c_i]
                    if note_txt == "1":
                        plots.append(PlotData(NoteType.TAP, c_i, m_i3, b_i, len(measure_txt.split(","))))
                    if note_txt == "2":
                        plots.append(PlotData(NoteType.EX_TAP, c_i, m_i3, b_i, len(measure_txt.split(","))))
                    if note_txt == "3":
                        long_start_loaded.append([c_i, m_i3, b_i, len(measure_txt.split(","))])
                    if note_txt == "4":
                        long_end_loaded.append([c_i, m_i3, b_i, len(measure_txt.split(","))])
                    if note_txt == "5":
                        plots.append(PlotData(NoteType.FUZZY, c_i, m_i3, b_i, len(measure_txt.split(","))))
                if len(beat_txt) >= 8:
                    if beat_txt[6] == "s":
                        if beat_txt[7:].isdecimal():
                            speed_changes.append(SpeedChangeData(round(int(beat_txt[7:]) / 10, 1),
                                                                 m_i3, b_i, len(measure_txt.split(","))))
        for ls in long_start_loaded:
            for le in long_end_loaded:
                if ls[1] + ls[2] / ls[3] < le[1] + le[2] / le[3] and ls[0] == le[0]:
                    longs.append(LongData(ls[0], [ls[1], le[1]], [ls[2], le[2]], [ls[3], le[3]]))
                    long_end_loaded.remove(le)
                    break
    
    def save(path: str = ""):  # 保存
        nonlocal file_path
        if not path:
            path = file_path
        if not os.path.exists(path):
            save_as()
            return
        file_path = path
        text = []
        plots_copy = plots + sum([ln2.points_as_plot() for ln2 in longs], [])
        for m_i2 in range(1000):  # 小節の番号
            if not plots_copy:  # 空になったら
                break
            plots_in_measure = []  # 小節にあるノーツ
            plots_poped_after = []
            for p_i2, p2 in enumerate(plots_copy):
                if p2.measure == m_i2:
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
            
                for sp2 in speed_changes:
                    if sp2.measure == m_i and sp2.beat * beat_split_lcm / sp2.splitting == b_i:
                        plot_text_tmp += f"s{int(sp2.speed * 10)}"
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
            defaultextension=".snp", title="譜面データを保存",
            initialfile="plots.snp", filetypes=[("Starbit Note Plots", ".snp")])
        if not path or not os.path.exists(path):
            messagebox.showerror("保存に失敗しました", f"このパスは無効です: {path}")
            return
        save(path)
    
    def calc_note_pos(offset: list[float, float] = None):
        """
        マウスの座標からレーン、小節、拍を返します。
        :return: レーン、小節、拍
        """
        if offset is None:
            offset = [0, 0]
        d = 610 - (mouse.y - offset[1]) + scroll
        clm = int(((mouse.x - offset[0]) - 250) / 100)
        int_ms = int(d / pixel_per_measure)
        tmp = d - int_ms * pixel_per_measure
        bt = 0
        for b_i2 in range(splitting_box.value + 1):
            if abs(b_i2 / splitting_box.value * pixel_per_measure - tmp) <= \
                    pixel_per_measure / (2 * splitting_box.value):
                if b_i2 < splitting_box.value:
                    bt = b_i2
                else:
                    int_ms += 1
                    bt = 0
                break
        return clm, int_ms, bt
    
    def calc_rounded_mouse_pos():
        clm, int_ms, bt = calc_note_pos()
        return [250 + clm * 100 + 50, 600 + scroll - (int_ms + bt / splitting_box.value) * pixel_per_measure]
    
    def cancel_plot_selecting():
        nonlocal selecting_plots
        for p2 in plots:
            p2.selecting = False
        for lp in sum([ln2.points_as_plot() for ln2 in longs], []):
            lp.selecting = False
        selecting_plots = []
    
    def select_plot(plot: PlotData):
        nonlocal clicked_any_plots, dragging_plot
        if not keys.ctrl_clicking:
            cancel_plot_selecting()
        plot.selecting = True
        selecting_plots.append(plot)
        clicked_any_plots = True
        dragging_plot = True
        for slp in selecting_plots:
            d_tmp = slp.measure_as_float * pixel_per_measure
            slp.selecting_offset = [mouse.x - (250 + 50 + slp.column * 100),
                                    mouse.y - (610 + scroll - d_tmp)]
    
    while True:
        tmr += 1
        for e in pg.event.get():
            if e.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if e.type == pg.MOUSEBUTTONDOWN:  # スクロールの終点の設定
                if e.button == 4:  # 上
                    if pg.key.get_pressed()[pg.K_LCTRL]:
                        pixel_per_measure -= 100
                        pixel_per_measure = max(100, pixel_per_measure)
                    else:
                        scroll_goal += 100
                        if keys.shift_clicking:
                            scroll_goal += 400
                elif e.button == 5:  # 下
                    if pg.key.get_pressed()[pg.K_LCTRL]:
                        pixel_per_measure += 100
                    else:
                        scroll_goal -= 100
                        if keys.shift_clicking:
                            scroll_goal -= 400
                        scroll_goal = max(0, scroll_goal)
        
        # 色々更新
        mouse.update()
        keys.update()
        splitting_box.update(keys, mouse)
        ex_speed_box.update(keys, mouse)
        
        sc.blit(rs.graphic(TRAILBLAZER_BG_IMG), [0, 0])
        splitting_box.render(sc)
        ex_speed_box.render(sc)
        
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
        
        # 小節線の描画
        for m_i in range(10000):
            bar_y = 610 + scroll - m_i * (pixel_per_measure / splitting_box.value)
            if -5 < bar_y < 700 + 5:
                pg.draw.line(sc, util.WHITE, [260, bar_y], [840, bar_y])
                if m_i % splitting_box.value == 0:
                    pg.draw.line(sc, util.YELLOW, [260, bar_y], [840, bar_y], width=4)
            elif -5 > bar_y:
                break
        
        # speed changeの描画
        speed_changes_poped_after = []
        for s_i, s in enumerate(speed_changes):
            distance = s.measure_as_float * pixel_per_measure
            pg.draw.line(sc, util.LIGHT_GREEN, [305, 610 + scroll - distance], [848, 610 + scroll - distance], width=3)
            speed_num_sf = rs.font(ARIAL_SMALL_FONT).render(str(s.speed), True, util.LIGHT_GREEN)
            sc.blit(speed_num_sf, [260, 585 + scroll - distance])
            if pg.key.get_pressed()[pg.K_e] and abs(700 + scroll - distance - mouse.y) < 25:
                speed_changes_poped_after.append(s_i)
        speed_changes_poped_after.reverse()
        for s_i in speed_changes_poped_after:
            speed_changes.pop(s_i)
        
        clicked_any_plots = False
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
            end_distance = ln.end.measure_as_float * pixel_per_measure
            note = rs.graphic(NOTE_IMAGES)[NoteType.LONG]
            p_y = 610 + scroll - start_distance - note.get_height() / 2
            if -127 < p_y < 700 + 127:
                sc.blit(note, [250 + 50 + ln.column * 100 - note.get_width() / 2,
                               610 + scroll - start_distance - note.get_height() / 2])
            
            # 始点の選択
            if ln.start.selecting:
                sc.blit(rs.graphic(PLOT_SELECTING_HIGHLIGHT_IMG),
                        [250 + 50 + ln.start.column * 100 - rs.graphic(PLOT_SELECTING_HIGHLIGHT_IMG).get_width() / 2,
                         610 + scroll - start_distance - rs.graphic(PLOT_SELECTING_HIGHLIGHT_IMG).get_height() / 2])
            
            # 始点のフォーカス
            if ln.start.mouse_on_plots(mouse, scroll, pixel_per_measure):
                if not ln.start.selecting:
                    sc.blit(rs.graphic(PLOT_FOCUSING_HIGHLIGHT_IMG),
                            [250 + 50 + ln.column * 100 - rs.graphic(PLOT_FOCUSING_HIGHLIGHT_IMG).get_width() / 2,
                             610 + scroll - start_distance - rs.graphic(PLOT_FOCUSING_HIGHLIGHT_IMG).get_height() / 2])
                if mouse.just_pressed(0):
                    select_plot(ln.start)
            
            # 終点の選択
            if ln.end.selecting:
                sc.blit(rs.graphic(PLOT_SELECTING_HIGHLIGHT_IMG),
                        [250 + 50 + ln.end.column * 100 - rs.graphic(PLOT_SELECTING_HIGHLIGHT_IMG).get_width() / 2,
                         610 + scroll - end_distance - rs.graphic(PLOT_SELECTING_HIGHLIGHT_IMG).get_height() / 2])
            # 終点のフォーカス
            if ln.end.mouse_on_plots(mouse, scroll, pixel_per_measure):
                if not ln.end.selecting:
                    sc.blit(rs.graphic(PLOT_FOCUSING_HIGHLIGHT_IMG),
                            [250 + 50 + ln.column * 100 - rs.graphic(PLOT_FOCUSING_HIGHLIGHT_IMG).get_width() / 2,
                             610 + scroll - end_distance - rs.graphic(PLOT_FOCUSING_HIGHLIGHT_IMG).get_height() / 2])
                # 選択
                if mouse.just_pressed(0):
                    select_plot(ln.end)
        
        # Plotの描画  メモ: 判定バーの中心y座標は610
        for p_i, p in enumerate(plots):
            distance = p.measure_as_float * pixel_per_measure
            note = rs.graphic(NOTE_IMAGES)[p.note_type]
            p_y = 610 + scroll - distance - note.get_height() / 2
            if -note.get_height() < p_y < 700 + note.get_height():
                sc.blit(note, [250 + 50 + p.column * 100 - note.get_width() / 2,
                               610 + scroll - distance - note.get_height() / 2])
            
            # 選択中
            if p.selecting:
                sc.blit(rs.graphic(PLOT_SELECTING_HIGHLIGHT_IMG),
                        [250 + 50 + p.column * 100 - rs.graphic(PLOT_SELECTING_HIGHLIGHT_IMG).get_width() / 2,
                         610 + scroll - distance - rs.graphic(PLOT_SELECTING_HIGHLIGHT_IMG).get_height() / 2])

            # フォーカス
            if p.mouse_on_plots(mouse, scroll, pixel_per_measure):
                if not p.selecting:
                    sc.blit(rs.graphic(PLOT_FOCUSING_HIGHLIGHT_IMG),
                            [250 + 50 + p.column * 100 - rs.graphic(PLOT_FOCUSING_HIGHLIGHT_IMG).get_width() / 2,
                             610 + scroll - distance - rs.graphic(PLOT_FOCUSING_HIGHLIGHT_IMG).get_height() / 2])
                # 選択
                if mouse.just_pressed(0):
                    select_plot(p)
        
        if mouse.just_pressed(0) and not clicked_any_plots:
            cancel_plot_selecting()
        
        if dragging_plot and not mouse.pressing(0):
            dragging_plot = False
        
        if dragging_plot and not selecting_plots:
            dragging_plot = False
        
        # ノーツの移動
        if dragging_plot:
            for sp in selecting_plots:
                sp.move_plot(*calc_note_pos(sp.selecting_offset), splitting_box.value)
        
        # 設置中のロング
        if long_start_tmp:
            sc.blit(rs.graphic(NOTE_IMAGES)[NoteType.LONG],
                    [250 + 50 + long_start_tmp[0] * 100 - rs.graphic(NOTE_IMAGES)[NoteType.LONG].get_width() / 2,
                     610 + scroll - (long_start_tmp[1] + long_start_tmp[3] / long_start_tmp[2]) * pixel_per_measure
                     - rs.graphic(NOTE_IMAGES)[NoteType.LONG].get_height() / 2])
            
            y1 = 610 + scroll - (long_start_tmp[1] + long_start_tmp[3] / long_start_tmp[2]) * pixel_per_measure
            y2 = calc_rounded_mouse_pos()[1]
            if y2 > y1:
                y1, y2 = y2, y1
            pg.draw.rect(sc, util.LONG_COLORS[0][0], [250 + long_start_tmp[0] * 100, y2,
                                                      100, y1 - y2])
        
        # ノーツの削除
        if selecting_plots:
            if keys.just_pressed(pg.K_BACKSPACE) or keys.just_pressed(pg.K_DELETE):
                plots_removed = selecting_plots
                cancel_plot_selecting()
                for pr in plots_removed:
                    if pr.note_type != NoteType.LONG:
                        plots.remove(pr)
                    else:
                        for ln in longs:
                            if pr in ln.points_as_plot():
                                longs.remove(ln)
                                break
        
        # ノーツの設置
        if mouse.just_pressed(2):
            column, int_measure, beat = calc_note_pos()
            if selecting_type != NoteType.LONG:
                plots.append(PlotData(selecting_type, column, int_measure, beat, splitting_box.value))
            else:
                if long_start_tmp:
                    long_end_tmp = [long_start_tmp[0], int_measure, splitting_box.value, beat]
                    if long_start_tmp[1] + long_start_tmp[3] / long_start_tmp[2] > \
                            long_end_tmp[1] + long_end_tmp[3] / long_end_tmp[2]:
                        long_start_tmp, long_end_tmp = long_end_tmp, long_start_tmp
                    longs.append(LongData(long_start_tmp[0], [long_start_tmp[1], long_end_tmp[1]],
                                          [long_start_tmp[3], long_end_tmp[3]], [long_start_tmp[2], long_end_tmp[2]]))
                    long_start_tmp = None
                else:
                    long_start_tmp = [column, int_measure, splitting_box.value, beat]
        
        # 右のツールバー
        toolbar_cmd = [load_from_snp, save, save_as]
        for ti_i in range(3):
            if mouse.in_rect(850, ti_i*50, 50, 50):
                sc.blit(rs.graphic(TOOLBAR_HIGHLIGHT_IMG), [850, ti_i*50])
                if mouse.just_pressed(0):
                    toolbar_cmd[ti_i]()
        
        # 左のメニュー
        note_types = [NoteType.TAP, NoteType.EX_TAP, NoteType.LONG, NoteType.FUZZY]
        for nt_i in range(4):
            note_img = rs.graphic(NOTE_IMAGES)[note_types[nt_i]]
            if note_types[nt_i] == selecting_type:
                sc.blit(rs.graphic(MENU_HIGHLIGHT_IMG), [25, 50 + 100 * nt_i + 3])
            else:
                note_img.set_alpha(100)
            sc.blit(note_img, [125 - note_img.get_width()/2, 100 + 100 * nt_i - note_img.get_height()/2])
            if mouse.in_rect(25, 50 + 100 * nt_i, 200, 100) and mouse.just_pressed(0):
                selecting_type = note_types[nt_i]
            note_img.set_alpha(255)
        
        pg.display.update()
        cl.tick(60)


if __name__ == '__main__':
    pg.display.set_caption("Star Trailblazer")
    sc = pg.display.set_mode((900, 700), pg.SRCALPHA)
    from data_loader import *
    
    root = tk.Tk()
    root.withdraw()
    main()
