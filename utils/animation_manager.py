import json
from pathlib import Path

from utils.img import Img


class AnimationManager:
    def __init__(self, piece_folder: Path):
        self.config = json.loads((piece_folder / "config.json").read_text())
        self.frames = []
        sprites_path = piece_folder / "sprites"
        for i in range(1, 6):
            self.frames.append(Img().read(sprites_path / f"{i}.png"))

        self.current_frame = 0
        self.last_update = 0
        self.fps = self.config["graphics"]["frames_per_sec"]

    def get_current_frame(self, current_time):
        speed_factor = 2.0
        frame_duration = (1000.0 / self.fps) * speed_factor

        elapsed = current_time - self.last_update

        if elapsed > frame_duration:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.last_update = current_time

        return self.frames[self.current_frame]