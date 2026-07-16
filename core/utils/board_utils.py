from typing import List, Tuple
import core.config.constants as constants


class BoardUtils:
    """
    Provides utility functions for analyzing board geometry and piece interactions.
    """

    @staticmethod
    def is_path_clear(matrix: List[List[str]], from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> bool:
        """
        Determines if the path between two positions is unobstructed by other pieces.

        Calculates the step-wise increments for rows and columns and iterates
        along the path, ensuring each intermediate cell is empty.
        """
        r1, c1 = from_pos
        r2, c2 = to_pos

        # Calculate unit direction vector
        dr = (r2 - r1) // max(1, abs(r2 - r1)) if r1 != r2 else 0
        dc = (c2 - c1) // max(1, abs(c2 - c1)) if c1 != c2 else 0

        current_r, current_c = r1 + dr, c1 + dc

        # Iterate until the target position is reached
        while (current_r, current_c) != to_pos:
            if matrix[current_r][current_c] != constants.EMPTY_CELL:
                return False
            current_r += dr
            current_c += dc

        return True