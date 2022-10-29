import os
import json
import time
import pygame as pg
import re

import notes
from game_enums import Judge, NoteType, Difficulty
import util
from data_loader import PROJ_PATH, blur_surface, AP_SMALL_IMG, FC_SMALL_IMG, LC_SMALL_IMG, LF_SMALL_IMG


SONGS_PATH = os.path.join(PROJ_PATH, "songs")  # 楽曲ファイルのパス


class Song:
    """
    楽曲のデータを持っていたり、楽曲に関する計算を行ったりします。
    """
    
    def __init__(self, folder_name: str, config: dict,
                 jacket_frame_color: list[int, int, int] | tuple[int, int, int] | pg.Color):
        """
        :param folder_name: フォルダの名前
        :param config: ゲームの設定データ
        """
        self.dir = os.path.join(SONGS_PATH, folder_name)  # この楽曲フォルダの完全パス
        with open(os.path.join(self.dir, "info.json"), "r", encoding="utf-8_sig") as j:
            self.info = json.load(j)  # 楽曲の情報を読み込む

        # 最初はジャケットなどのみを読み込む
        self.tap_data: [notes.Tap] = []
        self.ex_tap_data: [notes.ExTap] = []
        self.long_data: [notes.Long] = []
        self.fuzzy_data: [notes.Fuzzy] = []
        self.speed_changes: [notes.SpeedChange] = []
        
        self.proj_config = config
        self.started_time: float = 0  # 曲が始まった時間(ゲーム起動からの時間)
        self.jacket = pg.image.load(self.get_jacket_path()).convert_alpha()
        self.jacket = pg.transform.smoothscale(self.jacket, [256, 256])  # ジャケット画像
        self.jacket_bg: pg.Surface = pg.surface.Surface((900, 700), pg.SRCALPHA)  # ジャケットをぼかした背景
        jacket_tmp = pg.transform.rotozoom(self.jacket, 0, 900 / 256)
        jacket_tmp = blur_surface(jacket_tmp, radius=15)
        self.jacket_bg.blit(jacket_tmp, [0, -100])
        pg.draw.rect(self.jacket, jacket_frame_color, [0, 0, 256, 256], width=4)  # ジャケットの外枠
        self.started: bool = False
        
        self.paused_time: float = 0  # ポーズ画面を開いていた時間
        
        self.gauge_total: int = 0  # ゲージの最大値
        self.gauge: float = 0  # 現在のゲージ
        self.judge_counter: dict = {Judge.PERFECT: 0, Judge.GOOD: 0, Judge.MISS: 0}  # 判定のカウント
        self.combo: int = 0  # 現在のコンボ
        self.remaining_combo: int = 0  # 残りのコンボ
        self.max_combo: int = 0  # 最高コンボ
        self.gauge_base: float = 0  # ゲージの量を判定するうえの数値
        self.score: int = 0  # 現在のスコア
        
        self.judge_bar_num: float = 0
    
    def load_plots(self, dif: Difficulty) -> None:
        """
        ノーツのデータを初期化し、新たに読み込みます。
        :param dif: 選択中の難易度
        """

        # 初期化
        self.tap_data = []
        self.ex_tap_data = []
        self.long_data = []
        self.fuzzy_data = []
        self.speed_changes = []

        with open(self.get_snp_path(dif), "r") as p:
            plot_txt = p.read()
        plot_txt = plot_txt.replace(" ", "")
        plot_txt = plot_txt.replace("\n", "")

        plot_txt = plot_txt.rstrip(".")  # 終点の.を削除(splitで最後からのリストができるのを防ぐ)
        plot_tmp = plot_txt.split(".")  # 小節で区切った
        plot_as_text = []  # すべての拍を文字列("100100"など)の形で格納
        for bar_i, bar_txt in enumerate(plot_tmp):
            plot_as_text.append([])
            for beat_i, beat_text in enumerate(bar_txt.split(",")):
                notes_list = []
                for c_i in range(0, 6):
                    if len(beat_text) - 1 < c_i:  # 不足
                        notes_list.append(0)
                    else:
                        notes_list.append(beat_text[c_i])
                plot_as_text[-1].append(notes_list)
                if len(beat_text) >= 7:
                    commands = []
                    for ch in beat_text[6:]:
                        cmd_rp = re.compile("^[a-z]$")
                        num_rp = re.compile("[0-9]")
                        if cmd_rp.match(ch):
                            commands.append([ch, ""])
                        elif commands and num_rp.match(ch):
                            commands[-1][1] += ch
                    for cmd in commands:
                        if cmd[0] == "s":
                            if cmd[1].isdecimal():
                                self.speed_changes.append(
                                    notes.SpeedChange(round(int(cmd[1]) / 10, 1), bar_i, beat_i))
        long_start_data = []
        long_end_data = []
        
        def right_adjoin(bt: list, clm: int):
            if clm == 5:
                return False
            return bt[clm+1] != "0"
        
        def left_adjoin(bt: list, clm: int):
            if clm == 0:
                return False
            return bt[clm-1] != "0"
        
        second_per_bar = self.get_time() * 60 / self.get_bpm()  # 小節あたりの秒数
        note_extra_speed = 1  # 現在の速度変化
        for bar_num, bar in enumerate(plot_as_text):
            bar_second = bar_num * second_per_bar  # 計算の簡略化のため
            second_per_beat = second_per_bar / len(bar)  # 一拍あたりの秒数 小節によって変わる(4分音符、8分音符など)
            for beat_num, beat in enumerate(bar):
                beat_second = beat_num * second_per_beat
                
                for s in self.speed_changes:
                    if s.bar == bar_num and s.beat == beat_num:
                        note_extra_speed = s.speed
                
                if beat == ["0"] * 6:  # 空白ならスキップ(時間短縮)
                    continue
                for column, note in enumerate(beat):  # レーンごとに
                    if note == "0":
                        continue
                    elif note == "1":
                        self.tap_data.append(notes.Tap(column, bar_second + beat_second, note_extra_speed,
                                                       right_adjoin(beat, column), left_adjoin(beat, column)))
                    elif note == "2":
                        self.ex_tap_data.append(notes.ExTap(column, bar_second + beat_second, note_extra_speed,
                                                            right_adjoin(beat, column), left_adjoin(beat, column)))
                    elif note == "3":
                        long_start_data.append([column, bar_second + beat_second, note_extra_speed,
                                                right_adjoin(beat, column), left_adjoin(beat, column)])
                    elif note == "4":
                        long_end_data.append([column, bar_second + beat_second])
                    elif note == "5":
                        self.fuzzy_data.append(notes.Fuzzy(column, bar_second + beat_second, note_extra_speed,
                                                           right_adjoin(beat, column), left_adjoin(beat, column)))
        
        for i_s, s in enumerate(long_start_data):
            for i_e, e in enumerate(long_end_data):
                if s[0] == e[0] and s[1] < e[1]:  # 始点と終点の数が合わない場合はスキップされる
                    self.long_data.append(notes.Long(s[0], [s[1], e[1]], s[2], s[3], s[4]))
                    break
            long_start_data = long_start_data[1:]
        
        self.gauge_total = len(self.tap_data) + len(self.ex_tap_data)*3 + len(self.long_data)*2 + len(self.fuzzy_data)
        self.remaining_combo = len(self.tap_data) + len(self.ex_tap_data) + len(self.long_data)*2 + len(self.fuzzy_data)
    
    def calc_drawing_data(self, keys: util.Keys, note_sizes: dict, auto_play: bool) -> tuple:
        """
        ノーツごとに、何Pixel上に表示するか計算します。毎Tick呼び出す必要があります。
        :param keys: Keysクラス
        :param note_sizes: ノーツの画像の大きさを格納した辞書
        :param auto_play: オートプレイが有効かどうか
        """
        
        if not self.started:
            return [], []
        
        notes_drawing_data = []
        long_drawing_data = []
        
        second_now = time.perf_counter() - self.started_time - self.paused_time  # 曲開始から何秒たったか
        
        pixel_per_second = 1000 / 10 * self.proj_config["game"]["note_speed"]  # 速さ10で 700pxを0.7秒
        second_per_pixel = 1 / pixel_per_second
        
        tap_poped_after = []
        for i, t in enumerate(self.tap_data):
            remains_second = t.second_to_line - second_now
            if remains_second > second_per_pixel / t.speed * 1000:  # 画面外(上)
                break
            if remains_second < second_per_pixel / t.speed * -200:  # 画面外(下)
                if t.already_missed:
                    tap_poped_after.append(i)
                continue
            notes_drawing_data.append([200 - note_sizes[NoteType.TAP][0] / 2 + t.column * 100,
                                       610 - note_sizes[NoteType.TAP][1] / 2 -
                                       remains_second * pixel_per_second * t.speed, NoteType.TAP,
                                       remains_second])
            # x座標、y座標、判定ラインまでの時間(デバッグ用)
        
        util.pops(self.tap_data, tap_poped_after)
        
        ex_tap_poped_after = []
        for i, ext in enumerate(self.ex_tap_data):
            remains_second = ext.second_to_line - second_now
            if remains_second > second_per_pixel / ext.speed * 1000:
                break
            if remains_second < second_per_pixel / ext.speed * -200:
                if ext.already_missed:
                    ex_tap_poped_after.append(i)
                continue
            notes_drawing_data.append([200 - note_sizes[NoteType.EX_TAP][0] / 2 + ext.column * 100,
                                       610 - note_sizes[NoteType.EX_TAP][1] / 2 -
                                       remains_second * pixel_per_second * ext.speed, NoteType.EX_TAP,
                                       remains_second])
            # 上と同じ

        util.pops(self.ex_tap_data, ex_tap_poped_after)

        fuzzy_poped_after = []
        for i, f in enumerate(self.fuzzy_data):
            remains_second = f.second_to_line - second_now
            if remains_second > second_per_pixel / f.speed * 1000:  # 画面外(上)
                break
            if remains_second < second_per_pixel / f.speed * -200:  # 画面外(下)
                if f.already_missed:
                    fuzzy_poped_after.append(i)
                continue
            notes_drawing_data.append([200 - note_sizes[NoteType.FUZZY][0] / 2 + f.column * 100,
                                       610 - note_sizes[NoteType.FUZZY][1] / 2 -
                                       remains_second * pixel_per_second * f.speed, NoteType.FUZZY,
                                       remains_second])

        util.pops(self.fuzzy_data, fuzzy_poped_after)

        long_poped_after = []
        for i, l in enumerate(self.long_data):
            start_remains_second = l.start_second_to_line - second_now
            end_remains_second = l.end_second_to_line - second_now
            if start_remains_second > second_per_pixel / l.speed * 1000:
                break
            if end_remains_second < second_per_pixel / l.speed * -200:
                if l.already_missed:
                    long_poped_after.append(i)
                continue
            long_color = 0
            if start_remains_second < self.proj_config["game"]["judge"]["miss"] \
                    and -self.proj_config["game"]["judge"]["miss"] < end_remains_second \
                    and keys.get_dfghjk_pressing_list()[l.column]:
                long_color = 1
            if start_remains_second < self.proj_config["game"]["judge"]["auto_perfect"] \
                    and -self.proj_config["game"]["judge"]["auto_perfect"] < end_remains_second \
                    and auto_play:
                long_color = 1
            if l.already_missed:
                long_color = 2
            long_drawing_data.append([200 - note_sizes[NoteType.LONG][0] / 2 + l.column * 100,
                                      610 - note_sizes[NoteType.LONG][1] / 2 -
                                      start_remains_second * pixel_per_second * l.speed,
                                      610 - note_sizes[NoteType.LONG][1] / 2 -
                                      end_remains_second * pixel_per_second * l.speed,
                                      long_color, start_remains_second, end_remains_second])
            # x座標、始点のy座標、終点のy座標、ロングのいろ(0:そのまま、1:押された、2:グレー)、判定ラインまでの時間(デバッグ用)

        util.pops(self.long_data, long_poped_after)
        
        return notes_drawing_data, long_drawing_data
    
    def calc_tap_judge(self, keys: util.Keys, space_pressed: bool, auto_play: bool) -> list:
        """
        ノーツの判定を行います。
        一部のキーボードでは複数キー同時押しが認識できない可能性があります。
        :param keys: 現在のキーボードの状態を表すKeysクラス
        :param space_pressed: スペースキーが押されているか
        :param auto_play: オートプレイが有効かどうか
        :return: 判定のリスト
        """
        
        if not self.started:
            return []
        second_now = time.perf_counter() - self.started_time - self.paused_time
        judges = []
        key_pressed = keys.get_dfghjk_list()
        key_pressing = keys.get_dfghjk_pressing_list()
        
        perfect_range = self.proj_config["game"]["judge"]["perfect"]
        auto_perfect_range = self.proj_config["game"]["judge"]["auto_perfect"]
        good_range = self.proj_config["game"]["judge"]["good"]
        miss_range = self.proj_config["game"]["judge"]["miss"]
        
        def get_judge(remaining_sec: float) -> Judge:
            if abs(remaining_sec) < perfect_range:
                return Judge.PERFECT
            elif abs(remaining_sec) < good_range:
                return Judge.GOOD
            else:
                return Judge.MISS
        
        def set_judge_bar(remaining_sec: float):
            if abs(remaining_sec) < good_range:
                self.judge_bar_num = remaining_sec
        
        tap_poped_after = []  # pop(削除)するべきノーツのindexを記録(forループ中に触るとループが崩れるため)
        for i, t in enumerate(self.tap_data):
            if t.already_missed:
                continue
            
            remaining_second = t.second_to_line - second_now
            if remaining_second > miss_range:  # まだ早すぎる
                break  # 早い順に読み込まれるため、もう切り上げる
            if remaining_second < -miss_range:  # 遅すぎる(通り過ぎた)
                judges.append([Judge.MISS, t.column, NoteType.TAP])
                self.remaining_combo -= 1
                t.already_missed = True
                continue
            
            if auto_play and remaining_second < auto_perfect_range:
                key_pressed[t.column] = True
            
            if key_pressed[t.column]:
                key_pressed[t.column] = False  # 多重反応を防ぐ
                judges.append([get_judge(remaining_second), t.column, NoteType.TAP])
                self.remaining_combo -= 1
                set_judge_bar(remaining_second)
                tap_poped_after.append(i)
        
        util.pops(self.tap_data, tap_poped_after)
        
        # タップとほぼ同じ
        ex_tap_poped_after = []
        for i, ext in enumerate(self.ex_tap_data):
            if ext.already_missed:
                continue
            
            remaining_second = ext.second_to_line - second_now
            if remaining_second > miss_range:
                break
            if remaining_second < -miss_range:
                judges.append([Judge.MISS, ext.column, NoteType.EX_TAP])
                self.remaining_combo -= 1
                ext.already_missed = True
                continue
            
            if auto_play and remaining_second < auto_perfect_range:
                key_pressed[ext.column] = True
                space_pressed = True
            
            if ext.condition == notes.ExTapCondition.NEITHER:  # どちらもまだ押されていない状態
                if key_pressed[ext.column]:  # 先にキーを押した場合
                    ext.condition = notes.ExTapCondition.ONLY_KEY
                    key_pressed[ext.column] = False
                elif space_pressed:  # 先にスペースキーを押した場合
                    ext.condition = notes.ExTapCondition.ONLY_SPACE
            if ext.condition != notes.ExTapCondition.NEITHER:  # 万が一ぴったり同じタイミングで押したときのため、elseは使わない
                ext.latency += 1
                if ext.latency > 20:  # 2つのキーの押すタイミングがズレすぎたとき
                    judges.append([Judge.MISS, ext.column, NoteType.EX_TAP])
                    self.remaining_combo -= 1
                    ext.already_missed = True
                    continue
                
                if ext.condition == notes.ExTapCondition.ONLY_KEY and space_pressed or \
                        ext.condition == notes.ExTapCondition.ONLY_SPACE and key_pressed[ext.column]:
                    judges.append([get_judge(remaining_second), ext.column, NoteType.EX_TAP])
                    self.remaining_combo -= 1
                    set_judge_bar(remaining_second)
                    ex_tap_poped_after.append(i)
                    
                    if ext.condition == notes.ExTapCondition.ONLY_SPACE and key_pressed[ext.column]:
                        key_pressed[ext.column] = False
                    continue

        util.pops(self.ex_tap_data, ex_tap_poped_after)
        
        long_poped_after = []
        for i, l in enumerate(self.long_data):
            if l.already_missed:
                continue
            start_remaining_second = l.start_second_to_line - second_now
            end_remaining_second = l.end_second_to_line - second_now
            if start_remaining_second > miss_range:
                continue
            
            if not l.start_tapped:  # 始点の判定が終わっていない
                if start_remaining_second < -miss_range:  # 始点が通り過ぎた
                    l.start_tapped = True
                    judges.append([Judge.MISS, l.column, NoteType.LONG])
                    self.remaining_combo -= 1
                    continue
                
                if auto_play and start_remaining_second < auto_perfect_range:
                    key_pressed[l.column] = True
                
                if key_pressed[l.column]:
                    judges.append([get_judge(start_remaining_second), l.column, NoteType.LONG])
                    self.remaining_combo -= 1
                    set_judge_bar(start_remaining_second)
                    l.start_tapped = True
                    key_pressed[l.column] = False
            else:  # 始点の反応が終わった
                if auto_play:
                    key_pressing[l.column] = end_remaining_second > auto_perfect_range
                
                if not key_pressing[l.column]:  # 指を離したとき
                    if end_remaining_second > miss_range:  # 終点の処理には早すぎる
                        judges.append([Judge.MISS, l.column, NoteType.LONG])
                        self.remaining_combo -= 1
                        l.already_missed = True
                        continue
                    judges.append([get_judge(end_remaining_second), l.column, NoteType.LONG])
                    self.remaining_combo -= 1
                    set_judge_bar(end_remaining_second)
                    long_poped_after.append(i)
                else:
                    if key_pressing[l.column]:
                        judges.append([Judge.LONG_PRESSING, l.column, NoteType.LONG])
                    if end_remaining_second < -auto_perfect_range:  # そのまま押し続けていた
                        judges.append([Judge.PERFECT, l.column, NoteType.LONG])
                        self.remaining_combo -= 1
                        long_poped_after.append(i)
        
        util.pops(self.long_data, long_poped_after)
        
        fuzzy_poped_after = []
        for i, f in enumerate(self.fuzzy_data):
            if f.already_missed:
                continue
            
            remaining_second = f.second_to_line - second_now
            if remaining_second > miss_range:  # まだ早すぎる
                break  # 早い順に読み込まれるため、もう切り上げる
            if remaining_second < -miss_range:  # 遅すぎる(通り過ぎた)
                if f.temp_judge:
                    judges.append([f.temp_judge, f.column, NoteType.FUZZY])
                    self.remaining_combo -= 1
                    fuzzy_poped_after.append(i)
                    continue
                judges.append([Judge.MISS, f.column, NoteType.FUZZY])
                self.remaining_combo -= 1
                f.already_missed = True
                continue
            
            if auto_play and abs(remaining_second) < miss_range:
                key_pressing[f.column] = True
            
            if key_pressing[f.column]:
                # ちょうど真ん中で押している
                if abs(remaining_second) < auto_perfect_range:
                    judges.append([Judge.PERFECT, f.column, NoteType.FUZZY])
                    self.remaining_combo -= 1
                    fuzzy_poped_after.append(i)
                else:
                    if remaining_second > auto_perfect_range:  # 真ん中より前
                        f.temp_judge = get_judge(remaining_second)
                    else:  # 真ん中より後 -> これ以上判定が良くならない
                        judges.append([get_judge(remaining_second), f.column, NoteType.FUZZY])
                        self.remaining_combo -= 1
                        set_judge_bar(remaining_second)
                        fuzzy_poped_after.append(i)
            
            else:
                # 真ん中を通る前に一回押して離した
                if abs(remaining_second) < auto_perfect_range and f.temp_judge:
                    judges.append([f.temp_judge, f.column, NoteType.FUZZY])
                    self.remaining_combo -= 1
                    fuzzy_poped_after.append(i)
        
        util.pops(self.fuzzy_data, fuzzy_poped_after)
        
        for j in judges:
            if j[0] in self.judge_counter.keys():
                self.judge_counter[j[0]] += 1
            ex_boost = 1
            if j[2] == NoteType.EX_TAP:
                ex_boost = self.proj_config["game"]["score"]["ex_boost"]
            if j[2] == NoteType.LONG:
                ex_boost = self.proj_config["game"]["score"]["long_boost"]
            if j[0] == Judge.MISS:
                self.combo = 0
                self.gauge_base -= 6
            elif j[0] == Judge.GOOD:
                self.combo += 1
                self.gauge_base += 0.3 * ex_boost
                self.score += self.proj_config["game"]["score"]["good"] * ex_boost
            elif j[0] == Judge.PERFECT:
                self.combo += 1
                self.gauge_base += 1 * ex_boost
                self.score += self.proj_config["game"]["score"]["perfect"] * ex_boost
            elif j[0] == Judge.LONG_PRESSING:
                pass
        self.gauge_base = min(self.gauge_total / 1.2, self.gauge_base)
        self.gauge_base = max(0.0, self.gauge_base)
        if self.combo > self.max_combo:
            self.max_combo = self.combo
        
        return judges
    
    def start_song(self):
        self.started_time = time.perf_counter() + 2 + self.get_offset()
        self.started = True
    
    def quit_song(self):
        """
        再生中の曲を強制的に初期化します。
        通常使われません。曲を最後までスキップするわけではないことに注意してください。
        :return:
        """
        self.paused_time = 0
        self.gauge_total = 0
        self.gauge = 0
        self.judge_counter = {Judge.PERFECT: 0, Judge.GOOD: 0, Judge.MISS: 0}
        self.combo = 0
        self.max_combo = 0
        self.gauge_base = 0
        self.score = 0
        self.started = False
    
    def get_title(self) -> str:
        return self.info["title"]
    
    def get_level(self, dif) -> int:
        return self.info["level"][dif.value]
    
    def get_bpm(self) -> float:
        return self.info["bpm"]
    
    def get_time(self) -> int:
        return self.info["time"] if "time" in self.info else 4
    
    def get_offset(self) -> int:
        return self.info["offset"]
    
    def get_music_path(self) -> str:
        return os.path.join(self.dir, self.info["music"])
    
    def get_jacket_path(self) -> str:
        return os.path.join(self.dir, self.info["jacket"])
    
    def get_jacket(self) -> pg.Surface:
        return self.jacket
    
    def get_snp_path(self, dif: Difficulty) -> str:
        return os.path.join(self.dir, self.info["snp"][dif.value])
    
    def get_whose_request(self) -> str:
        return self.info["request"] if "request" in self.info else ""

    def get_demo_start(self) -> float:
        return self.info["demo"][0] if "demo" in self.info else 0

    def get_demo_end(self) -> float:
        return self.info["demo"][1] if "demo" in self.info else 100000000

    def song_finished(self):
        return self.tap_data + self.ex_tap_data + self.long_data + self.fuzzy_data == [] and self.started
    
    def get_combo(self):
        return self.combo
    
    def get_max_combo(self):
        return self.max_combo
    
    def get_sp_clear_num(self):
        if self.judge_counter[Judge.MISS] > 0:
            return 0
        if self.judge_counter[Judge.GOOD] > 0:
            return 1
        return 2
    
    def get_judge_count(self, judge: Judge):
        return self.judge_counter[judge]
    
    def get_gauge_rate(self):
        return min(self.gauge_base / self.gauge_total * 120, 100)
    
    def is_gauge_full(self):
        return self.get_gauge_rate() == 100
    
    def is_level_clear(self):
        return self.get_gauge_rate() >= 70
    
    def get_score(self):
        return self.score
    
    def get_rank(self, dif: Difficulty):
        return min(int(self.get_score() / self.info["rank_max"][dif.value] * 5), 5)
    
    def get_judge_bar_bar(self):
        bar_bar_rate = self.judge_bar_num**2 / self.proj_config["game"]["judge"]["good"]**2
        return int(824 + 65 * bar_bar_rate)
    
    def get_clear_condition(self) -> util.ClearCondition:
        if self.get_sp_clear_num() == 2:
            return util.ClearCondition.ALL_PERFECT
        if self.get_sp_clear_num() == 1:
            return util.ClearCondition.FULL_COMBO
        if self.is_level_clear():
            return util.ClearCondition.CLEAR
        return util.ClearCondition.FAILED
    
    def get_accuracy(self) -> float:
        if self.judge_counter[Judge.PERFECT] + self.judge_counter[Judge.GOOD] + self.judge_counter[Judge.MISS] == 0:
            return 0
        return (self.judge_counter[Judge.PERFECT] + self.judge_counter[Judge.GOOD] * 0.3) / \
               (self.judge_counter[Judge.PERFECT] + self.judge_counter[Judge.GOOD] + self.judge_counter[Judge.MISS])*100

    def get_cl_cnd_mini_img(self):
        if self.get_clear_condition() == util.ClearCondition.ALL_PERFECT:
            return AP_SMALL_IMG
        if self.get_clear_condition() == util.ClearCondition.FULL_COMBO:
            return FC_SMALL_IMG
        if self.get_clear_condition() == util.ClearCondition.CLEAR:
            return LC_SMALL_IMG
        if self.get_clear_condition() == util.ClearCondition.FAILED:
            return LF_SMALL_IMG
