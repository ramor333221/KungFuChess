import pygame
from pathlib import Path
from config import constants
from src.utils.observer.observer import Observer
from src.utils.logger.logger import setup_logger

sound_logger = setup_logger("SoundLogger", "sound_activity.log")

if not pygame.mixer.get_init():
    pygame.mixer.init()


class SoundObserver(Observer):
    """Observer responsible for playing different audio effects based on game events."""

    def __init__(self):
        project_root = Path(__file__).resolve().parent.parent.parent.parent
        assets_dir = project_root / "assests"

        self.sounds = {}

        sound_files = {
            "move": "move.wav",
            "capture": "capture.wav",
            "game_over": "game_over.wav"
        }

        for key, filename in sound_files.items():
            sound_path = assets_dir / filename
            try:
                if sound_path.exists():
                    self.sounds[key] = pygame.mixer.Sound(str(sound_path))
                    sound_logger.info(f"Loaded sound file: {filename}")
                else:
                    sound_logger.warning(f"Sound file not found at: {sound_path}")
            except Exception as e:
                sound_logger.warning(f"Could not load sound file {filename}: {e}")

    def update(self, event, data):
        """Triggers specific sound playback based on received game events."""
        if event == constants.EVENT_MOVE_COMPLETED:
            is_capture = data.get("is_capture", False) if isinstance(data, dict) else False

            if is_capture and "capture" in self.sounds:
                self.sounds["capture"].play()
                sound_logger.info("Played capture sound effect.")
            elif "move" in self.sounds:
                self.sounds["move"].play()
                sound_logger.info("Played move sound effect.")

        elif event == constants.EVENT_GAME_OVER:
            if "game_over" in self.sounds:
                self.sounds["game_over"].play()
                sound_logger.info("Played game over sound effect.")