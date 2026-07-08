# https://github.com/ramor333221/KungFuChess

import sys
from BoardParser import BoardParser
from BoardValidator import BoardValidator
from ChessGame import ChessGame


def main():
    parser = BoardParser(sys.stdin)
    raw_rows, command_lines = parser.parse_input()

    validator = BoardValidator()
    board_representation = validator.validate(raw_rows)
    if not board_representation:
        return

    raw_grid = board_representation._matrix

    # כעת נעביר את המטריצה הגולמית ל-ChessGame כפי שהוא מצפה לקבל
    game = ChessGame(raw_grid)

    for command in command_lines:
        parts = command.split()
        if not parts:
            continue

        cmd_type = parts[0]

        if cmd_type == "click" and len(parts) == 3:
            try:
                x = int(parts[1])
                y = int(parts[2])
                game.click(x, y)
            except ValueError:
                continue
        elif cmd_type == "wait" and len(parts) == 2:
            try:
                ms = int(parts[1])
                game.wait(ms)
            except ValueError:
                continue
        elif command == "print board":
            game.print_board()


if __name__ == "__main__":
    main()