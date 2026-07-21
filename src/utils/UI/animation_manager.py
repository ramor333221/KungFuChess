import json
from pathlib import Path

from src.utils.UI.img import Img


class AnimationManager:
    def __init__(self, piece_folder: Path):
        self.base_path = piece_folder
        self.config = json.loads((piece_folder / "config.json").read_text())
        self.state = "idle"
        self.frames = []
        self.current_frame = 0
        self.last_update = 0
        self.fps = self.config["graphics"]["frames_per_sec"]
        self._load_state_frames("idle")


    def _load_state_frames(self, state):
        """Loads frames from: piece_mine/[piece]/states/[state]/sprites/"""
        self.frames = []
        sprites_path = self.base_path / "sprites"
        if sprites_path.exists():
            for i in range(1, 6):
                file_path = sprites_path / f"{i}.png"
                if file_path.exists():
                    self.frames.append(Img().read(file_path))
        else:
            print(f"Warning: Could not find sprites for state: {state} at {sprites_path}")

    def set_state(self, new_state):
        """Updates the animation state and resets the frame counter."""
        if self.state != new_state:
            self.state = new_state
            self._load_state_frames(new_state)
            self.current_frame = 0
            self.last_update = 0

    def get_current_frame(self, current_time):
        if not self.frames:
            return None

        fps = self.fps if self.fps > 0 else 10
        speed_factor = 0.5 if self.state == "move" else 2.0
        frame_duration = (1000.0 / fps) * speed_factor

        elapsed = current_time - self.last_update

        if elapsed > frame_duration:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.last_update = current_time

        return self.frames[self.current_frame]