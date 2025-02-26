import unittest
from chess_game.pieces import Colour, Pawn, Rook, Bishop, Queen, King
from chess_game.game import GameState
from chess_game.move import Move


class BaseTestPieceMovement(unittest.TestCase):

    def setUp(self):
        self.game = GameState()

    def empty_board(self):
        for row in range(8):
            for col in range(8):
                self.game.board[row][col] = None

    def move_piece(self, old_row: int, old_col: int, new_row: int, new_col: int):
        move = Move(old_row, old_col, new_row, new_col,
                    self.game.board[old_row][old_col].piece_type)
        self.game.move_piece(move)

    def get_moves(self, row: int, col: int):
        return self.game.get_valid_moves(row, col)

    def assert_move_possible(self, row: int, col: int, target_row: int, target_col: int):
        moves = self.get_moves(row, col)
        move_targets = [(move.to_row, move.to_col) for move in moves]
        self.assertIn((target_row, target_col), move_targets)

    def assert_move_not_possible(self, row: int, col: int, target_row: int, target_col: int):
        moves = self.get_moves(row, col)
        move_targets = [(move.to_row, move.to_col) for move in moves]
        self.assertNotIn((target_row, target_col), move_targets)

    def assert_number_of_moves(self, row: int, col: int, expected_number: int):
        moves = self.get_moves(row, col)
        self.assertEqual(len(moves), expected_number)


class TestPawnMovement(BaseTestPieceMovement):

    def test_pawn_initial_move_white(self):
        # Test a white pawn at row 6 can move one or two squares forward
        self.assert_move_possible(6, 0, 5, 0)
        self.assert_move_possible(6, 0, 4, 0)
        self.assert_number_of_moves(6, 0, 2)

    def test_pawn_initial_move_black(self):
        # Test a black pawn at row 1 can move one or two squares forward
        self.game.turn = Colour.BLACK
        self.assert_move_possible(1, 0, 2, 0)
        self.assert_move_possible(1, 0, 3, 0)
        self.assert_number_of_moves(1, 0, 2)

    def test_pawn_cannot_move_backwards(self):
        self.move_piece(6, 0, 4, 0)
        self.game.turn = Colour.WHITE
        self.assert_move_not_possible(4, 0, 5, 0)

    def test_pawn_capture(self):
        # Test a white pawn can capture a piece diagonally
        self.game.board[5][1] = Pawn(Colour.BLACK, 5, 1)
        self.assert_move_possible(6, 0, 5, 1)
        self.assert_number_of_moves(6, 0, 3)

    def test_pawn_cannot_move(self):
        # Test a white pawn cannot move if there is a piece directly in front of it
        self.game.board[5][0] = Pawn(Colour.BLACK, 5, 0)
        self.assert_move_not_possible(6, 0, 5, 0)
        self.assert_number_of_moves(6, 0, 0)
        self.game.board[5][0] = Rook(Colour.WHITE, 5, 0)
        self.assert_move_not_possible(6, 0, 5, 0)
        self.assert_number_of_moves(6, 0, 0)

    # En-passant tests
    def test_en_passant_possible(self):
        # Test that en passant is set up correctly when a pawn moves two squares.
        self.empty_board()
        self.game.board[6][4] = Pawn(Colour.WHITE, 6, 4)
        self.game.board[4][3] = Pawn(Colour.BLACK, 4, 3)
        self.game.board[0][4] = King(Colour.BLACK, 0, 4)
        self.game.board[7][4] = King(Colour.WHITE, 7, 4)
        # White pawn moves e2 -> e4
        self.move_piece(6, 4, 4, 4)
        # En passant should now be possible at e3 (5, 4)
        self.assert_move_possible(4, 3, 5, 4)
        self.assertEqual(self.game.enpassant_square, (5, 4))

    def test_en_passant_expires(self):
        self.empty_board()
        self.game.board[6][4] = Pawn(Colour.WHITE, 6, 4)
        self.game.board[4][3] = Pawn(Colour.BLACK, 4, 3)
        self.game.board[7][0] = Pawn(Colour.WHITE, 7, 0)
        self.game.board[0][4] = King(Colour.BLACK, 0, 4)
        self.game.board[7][4] = King(Colour.WHITE, 7, 4)
        # White pawn moves e2 -> e4
        self.move_piece(6, 4, 4, 4)
        # En passant should be possible
        self.assertEqual(self.game.enpassant_square, (5, 4))
        self.assert_move_possible(4, 3, 5, 4)
        # Change player turn back to white
        self.game.turn = Colour.WHITE
        # Another move happens instead (white moves another piece)
        self.move_piece(7, 0, 6, 0)
        # En passant should expire
        self.assertIsNone(self.game.enpassant_square)
        self.assert_move_not_possible(4, 3, 5, 4)


class TestRookMovement(BaseTestPieceMovement):

    def test_rook_can_move_straight(self):
        # Rook should move straight in any direction
        self.empty_board()
        self.game.board[4][0] = Rook(Colour.WHITE, 4, 0)
        self.game.board[0][4] = King(Colour.BLACK, 0, 4)
        self.game.board[7][4] = King(Colour.WHITE, 7, 4)
        self.assert_move_possible(4, 0, 3, 0)
        self.assert_move_possible(4, 0, 5, 0)
        self.assert_move_possible(4, 0, 4, 1)
        self.assert_number_of_moves(4, 0, 14)

    def test_rook_cannot_jump(self):
        # Rook should NOT be able to jump over pieces
        self.assert_move_not_possible(7, 0, 5, 0)
        self.assert_number_of_moves(7, 0, 0)
        # Move pawn forward 2 squares
        self.move_piece(6, 0, 4, 0)
        # Make it white's turn next, and assert rook can move forward up to 2 squares
        self.game.turn = Colour.WHITE
        self.assert_move_possible(7, 0, 5, 0)
        self.assert_number_of_moves(7, 0, 2)


class TestBishopMovement(BaseTestPieceMovement):

    def test_bishop_can_move_diagonally(self):
        self.empty_board()
        self.game.board[4][5] = Bishop(Colour.WHITE, 4, 5)
        self.game.board[0][4] = King(Colour.BLACK, 0, 4)
        self.game.board[7][4] = King(Colour.WHITE, 7, 4)
        self.assert_move_possible(4, 5, 2, 7)
        self.assert_number_of_moves(4, 5, 11)

    def test_bishop_cannot_jump(self):
        # Bishop should NOT be able to jump over pieces
        self.assert_move_not_possible(7, 2, 4, 5)
        self.assert_number_of_moves(7, 2, 0)
        # Move pawn forward 1 square
        self.move_piece(6, 3, 5, 3)
        # Make it white's turn next
        self.game.turn = Colour.WHITE
        self.assert_move_possible(7, 2, 4, 5)
        self.assert_number_of_moves(7, 2, 5)


class TestKnightMovement(BaseTestPieceMovement):

    def test_knight_can_jump(self):
        self.assert_move_possible(7, 1, 5, 2)
        self.assert_move_possible(7, 1, 5, 0)
        self.assert_number_of_moves(7, 1, 2)

    def test_knight_can_capture(self):
        self.game.board[5][2] = Pawn(Colour.BLACK, 5, 2)
        self.assert_move_possible(7, 1, 5, 2)
        self.assert_move_possible(7, 1, 5, 0)
        self.assert_number_of_moves(7, 1, 2)

    def test_knight_blocked(self):
        self.game.board[5][2] = Pawn(Colour.WHITE, 5, 2)
        self.assert_move_not_possible(7, 1, 5, 2)
        self.assert_move_possible(7, 1, 5, 0)
        self.assert_number_of_moves(7, 1, 1)


class TestQueenMovement(BaseTestPieceMovement):

    def test_queen_all_directions(self):
        self.empty_board()
        self.game.board[4][3] = Queen(Colour.WHITE, 4, 3)
        self.game.board[0][4] = King(Colour.BLACK, 0, 4)
        self.game.board[7][4] = King(Colour.WHITE, 7, 4)
        self.assert_number_of_moves(4, 3, 27)

    def test_queen_blocked(self):
        self.empty_board()
        self.game.board[4][4] = Queen(Colour.WHITE, 4, 4)
        self.game.board[3][4] = Pawn(Colour.WHITE, 3, 4)
        self.game.board[0][3] = King(Colour.BLACK, 0, 3)
        self.game.board[7][3] = King(Colour.WHITE, 7, 3)
        self.assert_number_of_moves(4, 4, 23)
        self.game.board[3][3] = Pawn(Colour.WHITE, 3, 3)
        self.assert_number_of_moves(4, 4, 19)


class TestKingMovement(BaseTestPieceMovement):

    def test_king_all_directions(self):
        self.empty_board()
        self.game.board[4][4] = King(Colour.WHITE, 4, 4)
        self.assert_number_of_moves(4, 4, 8)

    def test_king_blocked(self):
        self.empty_board()
        self.game.board[4][4] = King(Colour.WHITE, 4, 4)
        self.game.board[3][4] = Pawn(Colour.WHITE, 3, 4)
        self.assert_number_of_moves(4, 4, 7)
        self.game.board[3][3] = Pawn(Colour.WHITE, 3, 3)
        self.assert_number_of_moves(4, 4, 6)

    def test_kingside_castle(self):
        # Remove bishop and knight in the way of castling
        self.game.board[7][5] = None
        # Ensure that castling is not possible (knight in the way)
        self.assert_move_not_possible(7, 4, 7, 6)
        self.game.board[7][6] = None
        # Ensure that castling kingside is possible
        self.assert_move_possible(7, 4, 7, 6)
        # Ensure that castling queenside is not possible
        self.assert_move_not_possible(7, 4, 7, 2)

    def test_queenside_castle(self):
        # Remove queen, bishop, and knight in the way of castling
        self.game.board[7][3] = None
        # Ensure that castling is not possible (bishop and knight in the way)
        self.assert_move_not_possible(7, 4, 7, 2)
        self.game.board[7][2] = None
        # Ensure that castling is not possible (knight in the way)
        self.assert_move_not_possible(7, 4, 7, 2)
        self.game.board[7][1] = None
        # Ensure that castling queenside is possible
        self.assert_move_possible(7, 4, 7, 2)
        # Ensure that castling kingside is not possible
        self.assert_move_not_possible(7, 4, 7, 6)

    def test_cannot_castle_through_check(self):
        self.empty_board()
        self.game.board[0][4] = King(Colour.BLACK, 0, 4)
        self.game.board[7][4] = King(Colour.WHITE, 7, 4)
        # Add the rook so the white king can castle queenside
        self.game.board[7][0] = Rook(Colour.WHITE, 7, 0)
        # Check that the king can castle queenside
        self.assert_move_possible(7, 4, 7, 2)
        # Add a black rook at (4, 3), attacking (7, 3)
        self.game.board[4][3] = Rook(Colour.BLACK, 4, 3)
        # Check that queenside castling is not possible
        self.assert_move_not_possible(7, 4, 7, 2)
