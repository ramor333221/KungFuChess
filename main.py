import sys
from BoardParser import BoardParser
from BoardValidator import BoardValidator
from ChessGame import ChessGame


def main():
    # 1. Parse
    parser = BoardParser(sys.stdin)
    raw_rows, command_lines = parser.parse_input()

    # 2. Validate
    validator = BoardValidator()
    board = validator.validate(raw_rows)
    if not board:
        return

    # 3. Instantiate Engine
    game = ChessGame(board)

    # 4. Process Commands
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