import sys

from Board.BoardParser import BoardParser
from Board.BoardValidator import BoardValidator


def main():
    parser = BoardParser(sys.stdin)
    raw_rows = parser.parse_raw_rows()

    validator = BoardValidator()
    board = validator.validate(raw_rows)

    if board is dict or not board:
        return

    print(board.to_canonical_string())

if __name__ == "__main__":
    main()