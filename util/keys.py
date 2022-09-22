import pygame as pg
from pygame import *


class Keys:
    """
    キーボードの状態を管理します。
    """
    
    def __init__(self):
        self.key = pg.key.get_pressed()
        self.key_past = None

        # このゲーム専用
        self.dfghjk = self.get_dfghjk_list()
        self.dfghjk_pressing = self.get_dfghjk_pressing_list()
    
    def update(self) -> None:
        """
        キーボードの状態を取得します。
        """
        self.key_past = self.key
        self.key = pg.key.get_pressed()
        
        self.dfghjk = self.get_dfghjk_list()
        self.dfghjk_pressing = self.get_dfghjk_pressing_list()
    
    def just_pressed(self, key_num: int) -> bool:
        """
        渡されたキーがちょうど押されたところかを返します。
        :param key_num: キーボード定数
        """
        return bool(self.key[key_num] and not self.key_past[key_num])
    
    def pressing(self, key_num: int):
        """
        渡されたキーが今押されているかを返します。
        :param key_num: キーボード定数
        """
        return self.key[key_num]

    # これより下はこのゲーム専用
    def get_dfghjk_list(self) -> list:
        """
        d, f, g, h, j, kキーがそれぞれがちょうど押されたところかを、この順番で返します。
        """
        return [self.just_pressed(k) for k in [K_d, K_f, K_g, K_h, K_j, K_k]]
    
    def get_dfghjk_pressing_list(self) -> list:
        """
        d, f, g, h, j, kキーがそれぞれが今押されているかかを、この順番で返します。
        """
        return [self.pressing(k) for k in [K_d, K_f, K_g, K_h, K_j, K_k]]
    
    @property
    def just_decided(self) -> bool:
        """
        決定を表すEnterキー、dキー、jキーのいずれかがちょうど押されたところかを返します。
        """
        return self.just_pressed(pg.K_RETURN) or self.just_pressed(pg.K_f) or self.just_pressed(pg.K_j)
    
    @property
    def just_right(self):
        return self.just_pressed(pg.K_RIGHT) or self.just_pressed(pg.K_k)

    @property
    def just_left(self):
        return self.just_pressed(pg.K_LEFT) or self.just_pressed(pg.K_d)
    