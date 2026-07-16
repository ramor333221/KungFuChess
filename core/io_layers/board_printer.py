# io_layers/board_printer.py
from typing import List

class BoardPrinter:
    @staticmethod
    def print_board(matrix: List[List[str]]) -> None:
        """
        Accepts a raw 2D array matrix of strings and outputs it
        to the console line-by-line with spaces separating elements.
        """
        for row in matrix:
            print(" ".join(row))