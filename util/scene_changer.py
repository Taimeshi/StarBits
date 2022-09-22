
from data_loader import *


class SceneChanger:
    def __init__(self, surface_size: tuple[int, int] | list[int, int], default, resources: Resources):
        """
        シーンをなめらかに変更する描画を行います。
        :param surface_size: 画面のサイズ
        :param default: 初めのシーン
        """
        self.fadeout_surface = pg.surface.Surface(surface_size, pg.SRCALPHA)
        self.event: list[SceneChangeEvent] = []
        self.index = default
        self.rs = resources

    def add_event(self, scene_to, end_tick: int, run_when_changed=None) -> None:
        """
        シーン変更のイベントを追加します。
        :param scene_to: 移動するシーン
        :param end_tick: かけるTick数
        :param run_when_changed: シーンがちょうど変わるときに実行される関数
        """
        self.event.append(SceneChangeEvent(self, self.rs, scene_to, end_tick, run_when_changed))

    def update(self) -> None:
        """
        アニメーションを1Tick進めます。
        """
        if self.event and not self.event[0].is_busy():
            self.event.pop(0)

        self.fadeout_surface.fill(util.CLEAR)
        if self.event:
            self.event[0].draw_surface(self.fadeout_surface)

    def get_surface(self) -> pg.Surface:
        return self.fadeout_surface

    def is_busy(self) -> bool:
        """
        いずれかのシーン変更が実行中かを返します。
        """
        if self.event:
            return self.event[0].is_busy()
        return False


class SceneChangeEvent:
    def __init__(self, scene_changer: SceneChanger, resources: Resources,
                 scene_to, end_tick: int, run_when_changed=None):
        self.scene_changer = scene_changer
        self.scene_to = scene_to
        self.end_tick = end_tick
        self.tick_count: int = 0
        self.run_when_changed = run_when_changed
        self.rs = resources

    def draw_surface(self, surface: pg.Surface) -> None:
        """
        渡されたSurfaceにアニメーションを描画します。
        :param surface: アニメーションを描画するSurface
        """
        if self.tick_count == int(self.end_tick / 2):
            self.scene_changer.index = self.scene_to
            if self.run_when_changed:
                self.run_when_changed()
        if self.tick_count < int(self.end_tick / 2):
            proportion = self.tick_count / int(self.end_tick / 2)
            proportion **= 3
            self.rs.graphic(CHANGE_SCENE_IMG).set_alpha(int(255 * proportion))
            surface.blit(self.rs.graphic(CHANGE_SCENE_IMG), [900 - 1200 * proportion, 0])
        else:
            proportion = (self.tick_count-int(self.end_tick / 2)) / int(self.end_tick / 2)
            proportion **= 3
            self.rs.graphic(CHANGE_SCENE2_IMG).set_alpha(int(255 - 255 * proportion))
            surface.blit(self.rs.graphic(CHANGE_SCENE2_IMG), [0 - 1200 * proportion, 0])
        self.tick_count += 1

    def is_busy(self) -> bool:
        """
        このイベントでシーン変更が実行中かを返します。
        """
        return self.tick_count <= self.end_tick
