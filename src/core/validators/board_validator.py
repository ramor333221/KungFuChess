# validators/board_validator.py
from typing import List, Set
from config import constants
from src.models.board_state import BoardState
from src.core.exceptions.game_exceptions import BoardValidationError

class BoardValidator:
    def __init__(self, valid_colors: Set[str] = None, valid_pieces: Set[str] = None):
        self.valid_colors = valid_colors or constants.VALID_COLORS
        self.valid_pieces = valid_pieces or constants.VALID_PIECES

    def validate(self, raw_rows: List[List[str]]) -> BoardState:
        """
        Validates row uniformity and token vocabulary.
        Raises BoardValidationError if the input is malformed.
        """
        if not raw_rows or not raw_rows[0]:
            raise BoardValidationError("EMPTY_BOARD")

        expected_width = len(raw_rows[0])

        for row in raw_rows:
            if len(row) != expected_width:
                raise BoardValidationError("ROW_WIDTH_MISMATCH")

            for token in row:
                if token is None or token == constants.EMPTY_CELL:
                    continue

                if (len(token) != 2 or
                        token[0] not in self.valid_colors or
                        token[1] not in self.valid_pieces):
                    print(f"DEBUG: Found invalid token: '{token}'")
                    raise BoardValidationError(f"UNKNOWN_TOKEN")

        return BoardState(raw_rows)