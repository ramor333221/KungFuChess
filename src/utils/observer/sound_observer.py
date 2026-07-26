import pygame
from pathlib import Path
from src.utils.observer.observer import Observer
from src.utils.logger.logger import setup_logger

sound_logger = setup_logger("SoundLogger", "sound_activity.log")

if not pygame.mixer.get_init():
    pygame.mixer.init()


def _load_sound_file(filename: str):
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    sound_path = project_root / "assests" / filename
    if sound_path.exists():
        sound_logger.info(f"Loaded sound file: {filename}")
        return pygame.mixer.Sound(str(sound_path))
    sound_logger.warning(f"Sound file not found at: {sound_path}")
    return None


class MoveSoundObserver(Observer):
    """Observer responsible exclusively for playing move and capture sound effects."""

    def __init__(self):
        self.move_sound = _load_sound_file("move.wav")
        self.capture_sound = _load_sound_file("capture.wav")

    def update(self, data):
        is_capture = data.get("is_capture", False) if isinstance(data, dict) else False

        if is_capture and self.capture_sound:
            self.capture_sound.play()
            sound_logger.info("Played capture sound effect.")
        elif self.move_sound:
            self.move_sound.play()
            sound_logger.info("Played move sound effect.")


class GameOverSoundObserver(Observer):
    """Observer responsible exclusively for playing game over sound effects."""

    def __init__(self):
        self.game_over_sound = _load_sound_file("game_over.wav")

    def update(self, data):
        if self.game_over_sound:
            self.game_over_sound.play()
            sound_logger.info("Played game over sound effect.")