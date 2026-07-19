import sys
from typing import List, Tuple, IO
from config import constants

class TextBoardParser:
    def __init__(self, input_stream: IO = sys.stdin):
        """
        Initializes the parser with an input stream (defaults to standard input).
        """
        self._stream = input_stream

    def parse(self) -> Tuple[List[List[str]], List[str]]:
        """
        Parses the text stream into a tuple containing:
        1. A 2D list of strings representing the raw board rows.
        2. A list of raw command strings.
        """
        raw_board_rows: List[List[str]] = []
        raw_commands: List[str] = []

        is_board_section = False
        is_command_section = False

        for line in self._stream:
            line = line.strip()
            if not line:
                continue

            if line.startswith(constants.BOARD_HEADER):
                is_board_section = True
                is_command_section = False
                continue
            elif line.startswith(constants.COMMANDS_HEADER):
                is_board_section = False
                is_command_section = True
                continue

            if is_board_section:
                tokens = line.split()
                if tokens:
                    raw_board_rows.append(tokens)
            elif is_command_section:
                raw_commands.append(line)

        return raw_board_rows, raw_commands