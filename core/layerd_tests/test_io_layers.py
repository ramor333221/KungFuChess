# tests/test_io_layers.py
import unittest
import io
from core.io_layers.text_board_parser import TextBoardParser
from core.io_layers.board_printer import BoardPrinter


class TestTextBoardParser(unittest.TestCase):

    def test_parse_valid_board_and_commands(self):
        """Ensures the parser properly separates board layout grid from instructions."""
        # 1. Setup simulated text-file input stream
        simulated_input = (
            "Board:\n"
            "bR bN bB bQ bK\n"
            ".  .  .  .  .\n"
            "wR wN wB wQ wK\n"
            "\n"
            "Commands:\n"
            "click 0 0\n"
            "wait 100\n"
            "print\n"
        )
        stream = io.StringIO(simulated_input)
        parser = TextBoardParser(stream)

        # 2. Execute target logic
        matrix, commands = parser.parse()

        # 3. Assert correct mapping structures
        expected_matrix = [
            ["bR", "bN", "bB", "bQ", "bK"],
            [".", ".", ".", ".", "."],
            ["wR", "wN", "wB", "wQ", "wK"]
        ]
        expected_commands = [
            "click 0 0",
            "wait 100",
            "print"
        ]

        self.assertEqual(matrix, expected_matrix)
        self.assertEqual(commands, expected_commands)

    def test_parse_empty_input(self):
        """Ensures the parser handles empty or spaces-only streams gracefully without crashing."""
        stream = io.StringIO("   \n\n   \n")
        parser = TextBoardParser(stream)

        matrix, commands = parser.parse()

        self.assertEqual(matrix, [])
        self.assertEqual(commands, [])


class TestBoardPrinter(unittest.TestCase):

    def test_print_board_formatting(self):
        """Verifies that the printer formats matrices line-by-line using standard spacing."""
        # Setup matrix data
        sample_matrix = [
            ["bR", "bN"],
            [".", "wP"]
        ]

        # Capture console stdout prints using unittest mock utilities
        from unittest.mock import patch
        with patch('sys.stdout', new=io.StringIO()) as fake_out:
            BoardPrinter.print_board(sample_matrix)
            printed_output = fake_out.getvalue()

        # Assert correct terminal alignment format output string
        expected_output = "bR bN\n. wP\n"
        self.assertEqual(printed_output, expected_output)


if __name__ == "__main__":
    unittest.main()