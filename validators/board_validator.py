# validators/board_validator.py
from typing import List, Set, Optional
import config.constants as constants
from models.board_state import BoardState


class BoardValidator:
    def __init__(self, valid_colors: Set[str] = None, valid_pieces: Set[str] = None):
        self.valid_colors = valid_colors or constants.VALID_COLORS
        self.valid_pieces = valid_pieces or constants.VALID_PIECES

    def validate(self, raw_rows: List[List[str]]) -> Optional[BoardState]:
        """
        Validates row uniformity and token vocabulary.
        Returns a concrete BoardState data model if healthy, otherwise returns None.
        """
        if not raw_rows or not raw_rows[0]:
            print("ERROR EMPTY_BOARD")
            return None

        expected_width = len(raw_rows[0])

        for row in raw_rows:
            # Check structural matrix dimensions
            if len(row) != expected_width:
                print("ERROR ROW_WIDTH_MISMATCH")
                return None

            # Check individual string token health
            for token in row:
                if token == constants.EMPTY_CELL:
                    continue

                if (len(token) != 2 or
                        token[0] not in self.valid_colors or
                        token[1] not in self.valid_pieces):
                    print("ERROR UNKNOWN_TOKEN")
                    return None

        # Factory return: safely packages data into our Domain Model
        return BoardState(raw_rows)