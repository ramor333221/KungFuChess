from typing import List, Set, Optional

BOARD_HEADER = "Board:"
COMMANDS_HEADER = "Commands:"

class BoardParser:
    def __init__(self, input_stream):
        self.stream = input_stream

    def parse_raw_rows(self) -> List[List[str]]:
        raw_rows = []
        board_started = False

        for line in self.stream:
            line = line.strip()
            if not line:
                continue
            if line.startswith(BOARD_HEADER):
                board_started = True
                continue
            if line.startswith(COMMANDS_HEADER):
                break

            if board_started:
                tokens = line.split()
                if tokens:
                    raw_rows.append(tokens)

        return raw_rows