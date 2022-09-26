import pygame as pg
import tkinter as tk
import json
from tkinter import *
import os
import util


def main():
    # 初期化
    pg.display.set_caption("starbits notes designer")
    cl = pg.time.Clock()
    with open(os.path.join(PROJ_PATH, "config.json"), "r", encoding="utf-8_sig") as j:
        config: dict = json.load(j)
    tmr = 0
    rs = Resources(config)
    rs.show_loading_bar(sc)
    file_path = ""
    
    # 変数
    plots = []
    longs = []
    scroll = 0
    pixel_per_measure = 600
    
    def load_from_snp():
        pass
    
    def save():
        pass
    
    def save_as():
        pass
    
    while True:
        tmr += 1
        sc.blit(rs.graphic(TRAILBLAZER_BG_IMG), [0, 0])
        
        for e in pg.event.get():
            if e.type == pg.QUIT:
                pg.quit()
                sys.exit()

        plots_poped_after = []
        for p_i, p in enumerate(plots):
            distance = (p[2] + p[4] / p[3]) * pixel_per_measure
            note = rs.graphic(NOTE_IMAGES)[p[0]]
            p_y = 700 + scroll - distance - note.get_height() / 2
            if -127 < p_y < 700 + 127:
                sc.blit(note,
                        [150 + p[1] * 100 - note.get_width() / 2 + 50, 700 + scroll - distance - note.get_height() / 2])
        
        pg.display.update()
        cl.tick(60)


if __name__ == '__main__':
    pg.display.set_caption("star trailblazer")
    sc = pg.display.set_mode((900, 700), pg.SRCALPHA)
    from data_loader import *
    
    root = tk.Tk()
    root.withdraw()
    main()
