# main.py
import sys
from io_layers.text_board_parser import TextBoardParser
from io_layers.board_printer import BoardPrinter
from validators.board_validator import BoardValidator
from models.game_status import GameStatus
from engine.chess_rules_engine import ChessRulesEngine
from engine.game_status_manager import GameStatusManager
from controllers.choice_piece_controller import ChoicePieceController
from utils.board_mapper import BoardMapper
import config.constants as constants


def main():
    parser = TextBoardParser(sys.stdin)
    raw_matrix, raw_commands = parser.parse()

    validator = BoardValidator()
    board_state = validator.validate(raw_matrix)

    if board_state is None:
        return

    game_status = GameStatus()
    rules_engine = ChessRulesEngine()
    status_manager = GameStatusManager(board_state, game_status)
    controller = ChoicePieceController(board_state, game_status, rules_engine, status_manager)
    mapper = BoardMapper()

    for command in raw_commands:
        parts = command.split()
        if not parts:
            continue

        action = parts[0].lower()

        if action == "click" and len(parts) == 3:
            try:
                x = int(parts[1])
                y = int(parts[2])
                row, col = mapper.pixel_to_grid(x, y)
                controller.handle_cell_interaction(row, col)
            except ValueError:
                continue

        elif action == "jump" and len(parts) == 3:
            try:
                x = int(parts[1])
                y = int(parts[2])
                row, col = mapper.pixel_to_grid(x, y)

                # פקודת jump היא מהלך זינוק אנכי מיידי במקום של הכלי למשך 1000ms
                piece_token = board_state.get_token(row, col)
                if piece_token != constants.EMPTY_CELL:
                    # איפוס בחירה קודמת כדי למנוע קונפליקטים
                    game_status.selected_pos = None
                    status_manager.add_airborne_movement((row, col), (row, col), piece_token)
            except ValueError:
                continue

        elif action == "wait" and len(parts) == 2:
            try:
                ms_elapsed = int(parts[1])
                status_manager.process_time_tick(ms_elapsed)
            except ValueError:
                continue


        elif action == "print":
            BoardPrinter.print_board(board_state.matrix)


if __name__ == "__main__":
    main()