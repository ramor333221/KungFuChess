import sys
from typing import List, Tuple
import constants




class BoardParser:
    def __init__(self, input_stream=sys.stdin):
        self.stream = input_stream

    def parse_input(self) -> Tuple[List[List[str]], List[str]]:
        board_rows = []
        command_lines = []

        is_board_section = False
        is_command_section = False

        for line in self.stream:
            line = line.strip()
            if not line:
                continue
            if line.startswith(constants.BOARD_HEADER):
                is_board_section = True
                is_command_section = False
                continue
            if line.startswith(constants.COMMANDS_HEADER):
                is_board_section = False
                is_command_section = True
                continue

            if is_board_section:
                tokens = line.split()
                if tokens:
                    board_rows.append(tokens)
            elif is_command_section:
                command_lines.append(line)

        return board_rows, command_lines