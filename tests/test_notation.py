import unittest
from utils.notation import to_algebraic_notation
from chess_game.game import GameState
from chess_game.game import Move
from chess_game.enums import Colour, PieceType
from chess_game.pieces import King, Rook, Queen, Pawn, Bishop


class BaseTestNotation(unittest.TestCase):

    def setUp(self):
        self.game = GameState()

    def empty_board(self, white_king_row: int = 7, white_king_col: int = 4, black_king_row: int = 0, black_king_col: int = 4):
        for row in range(8):
            for col in range(8):
                self.game.board[row][col] = None
        self.game.board[white_king_row][white_king_col] = King(
            Colour.WHITE, white_king_row, white_king_col)
        self.game.board[black_king_row][black_king_col] = King(
            Colour.BLACK, black_king_row, black_king_col)

    def get_move_from_target(self, from_row: int, from_col: int, to_row: int, to_col: int):
        moves = self.game.get_valid_moves(from_row, from_col)
        return Move.get_move_from_list(moves, to_row, to_col)

    def move_piece(self, old_row: int, old_col: int, new_row: int, new_col: int):
        moves = self.game.get_valid_moves(old_row, old_col)
        move = Move.get_move_from_list(moves, new_row, new_col)
        self.assertIsNotNone(move)
        self.game.move_piece(move)

    def assert_move_notation(self, from_row: int, from_col: int, to_row: int, to_col: int, expected_notation: str, promote_to: PieceType = None, print_notation: bool = False):
        move = self.get_move_from_target(from_row, from_col, to_row, to_col)
        self.assertIsNotNone(move)
        if promote_to:
            move.promotion = promote_to
        notation = to_algebraic_notation(move, self.game)
        if print_notation:
            print()
            print(notation)
        self.assertEqual(notation, expected_notation)
        return move

    def assert_move_notation_and_move(self, from_row: int, from_col: int, to_row: int, to_col: int, expected_notation: str, promote_to: PieceType = None, print_notation: bool = False):
        move = self.assert_move_notation(
            from_row, from_col, to_row, to_col, expected_notation, promote_to, print_notation)
        self.game.move_piece(move)

    def setup_disambiguation_board(self, print_board: bool = False):
        self.empty_board(1, 1, 6, 3)
        self.game.board[3][0] = Rook(Colour.WHITE, 3, 0)
        self.game.board[7][0] = Rook(Colour.WHITE, 7, 0)
        self.game.board[0][3] = Rook(Colour.BLACK, 0, 3)
        self.game.board[0][7] = Rook(Colour.BLACK, 0, 7)
        self.game.board[4][4] = Queen(Colour.WHITE, 4, 4)
        self.game.board[4][7] = Queen(Colour.WHITE, 4, 7)
        self.game.board[7][7] = Queen(Colour.WHITE, 7, 7)
        if print_board:
            print()
            self.game.print_board()


class TestToAlgebraicNotation(BaseTestNotation):

    def test_initial_pawn_push(self):
        self.assert_move_notation(6, 1, 5, 1, "b3")

    def test_initial_knight_jump(self):
        self.assert_move_notation(7, 1, 5, 2, "Nc3")

    def test_disambiguation_file(self):
        self.setup_disambiguation_board()
        self.assert_move_notation(7, 0, 5, 0, "R1a3")

    def test_disambiguation_rank(self):
        self.setup_disambiguation_board()
        self.game.swap_turn()
        self.assert_move_notation(0, 3, 0, 5, "Rdf8")

    def test_disambiguation_double(self):
        self.setup_disambiguation_board()
        self.assert_move_notation(4, 7, 7, 4, "Qh4e1#")

    def test_disambiguation_double_with_capture(self):
        self.setup_disambiguation_board()
        self.game.board[7][4] = Rook(Colour.BLACK, 7, 4)
        self.assert_move_notation(4, 7, 7, 4, "Qh4xe1#")

    def test_piece_capture(self):
        self.empty_board()
        self.game.board[3][4] = Pawn(Colour.BLACK, 3, 4)
        self.game.board[7][0] = Bishop(Colour.WHITE, 7, 0)
        self.assert_move_notation(7, 0, 3, 4, "Bxe5")

    def test_pawn_capture(self):
        self.empty_board()
        self.game.board[3][3] = Pawn(Colour.BLACK, 3, 3)
        self.game.board[4][4] = Pawn(Colour.WHITE, 4, 4)
        self.assert_move_notation(4, 4, 3, 3, "exd5")

    def test_en_passant_capture(self):
        # Test that en passant capture works correctly
        self.empty_board()
        self.game.board[6][4] = Pawn(Colour.WHITE, 6, 4)
        self.game.board[4][3] = Pawn(Colour.BLACK, 4, 3)
        # White pawn moves e2 -> e4
        self.move_piece(6, 4, 4, 4)
        # Black pawn should have en passant as a possible move
        self.assert_move_notation(4, 3, 5, 4, "dxe3")

    def test_pawn_promotions(self):
        self.empty_board(4, 0, 4, 7)
        for col in range(2):
            self.game.board[1][col] = Pawn(Colour.WHITE, 1, col)
            self.game.board[6][col] = Pawn(Colour.BLACK, 6, col)
        self.assert_move_notation(
            1, 0, 0, 0, "a8=Q", promote_to=PieceType.QUEEN)
        self.assert_move_notation(
            1, 1, 0, 1, "b8=N", promote_to=PieceType.KNIGHT)
        self.game.swap_turn()
        self.assert_move_notation(
            6, 0, 7, 0, "a1=R+", promote_to=PieceType.ROOK)
        self.assert_move_notation(
            6, 1, 7, 1, "b1=B", promote_to=PieceType.BISHOP)

    def test_castling(self):
        for col in range(1, 4):
            self.game.board[7][col] = None
        for col in range(5, 7):
            self.game.board[7][col] = None
        self.assert_move_notation(7, 4, 7, 6, "O-O")
        self.assert_move_notation(7, 4, 7, 2, "O-O-O")

    def test_check(self):
        self.empty_board()
        self.game.board[4][0] = Rook(Colour.WHITE, 4, 0)
        self.assert_move_notation(4, 0, 4, 4, "Re4+")

    def test_checkmate(self):
        self.empty_board()
        self.game.board[5][0] = Bishop(Colour.WHITE, 5, 0)
        self.game.board[1][0] = Queen(Colour.WHITE, 1, 0)
        self.assert_move_notation(1, 0, 1, 4, "Qe7#")

    def test_scholars_mate(self):
        self.assert_move_notation_and_move(6, 4, 4, 4, "e4")
        self.assert_move_notation_and_move(1, 4, 3, 4, "e5")
        self.assert_move_notation_and_move(7, 5, 4, 2, "Bc4")
        self.assert_move_notation_and_move(0, 1, 2, 2, "Nc6")
        self.assert_move_notation_and_move(7, 3, 3, 7, "Qh5")
        self.assert_move_notation_and_move(0, 6, 2, 5, "Nf6")
        self.assert_move_notation_and_move(3, 7, 1, 5, "Qxf7#")
