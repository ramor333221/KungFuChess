from typing import List, Set, Optional
from BoardRepresentation import BoardRepresentation

DEFAULT_VALID_COLORS = {"w", "b"}
DEFAULT_VALID_PIECES = {"K", "Q", "R", "B", "N", "P"}
EMPTY_CELL = "."

class BoardValidator:
    def __init__(self, valid_colors: Set[str] = None, valid_pieces: Set[str] = None):
        self.valid_colors = valid_colors or DEFAULT_VALID_COLORS
        self.valid_pieces = valid_pieces or DEFAULT_VALID_PIECES

    def validate(self, raw_rows: List[List[str]]) -> Optional[BoardRepresentation]:
        if not raw_rows or not raw_rows[0]:
            return None

        expected_width = len(raw_rows[0])

        for row in raw_rows:
            if len(row) != expected_width:
                print("ERROR ROW_WIDTH_MISMATCH")
                return None
            for token in row:
                if token == EMPTY_CELL:
                    continue
                if (len(token) != 2 or
                        token[0] not in self.valid_colors or
                        token[1] not in self.valid_pieces):
                    print("ERROR UNKNOWN_TOKEN")
                    return None

        return BoardRepresentation(raw_rows)