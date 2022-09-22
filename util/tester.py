import time


class BurdenChecker:
    
    def __init__(self, default_fps: int):
        self.fps = default_fps
        self.started_count = 0
    
    def start(self) -> None:
        self.started_count = time.perf_counter()
    
    def end(self) -> None:
        time_taken = time.perf_counter() - self.started_count
        burden_in_fps = time_taken / (1 / self.fps)
        text = "No Problem"
        if burden_in_fps > 0.1:
            text = "Maybe Problem"
        if burden_in_fps > 0.4:
            text = "Serious Problem!"
        if burden_in_fps > 0.8:
            text = "Quite Serious Problem!!"
        print(f"burden in fps: {round(burden_in_fps, 5)}  ({text})")
