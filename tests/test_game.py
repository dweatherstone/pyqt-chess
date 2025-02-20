import unittest
from chess_game.game import GameState
from chess_game.pieces import Pawn, Rook, Bishop, Queen, King, Colour
from chess_game.move import Move


class BaseTestChessGame(unittest.TestCase):

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

    def move_piece(self, old_row: int, old_col: int, new_row: int, new_col: int):
        move = Move(old_row, old_col, new_row, new_col,
                    self.game.board[old_row][old_col].piece_type)
        self.game.move_piece(move)

    def get_moves(self, row: int, col: int):
        return self.game.get_valid_moves(row, col)

    def assert_move_possible(self, row: int, col: int, target_row: int, target_col: int):
        moves = [(move.to_row, move.to_col)
                 for move in self.get_moves(row, col)]
        self.assertIn((target_row, target_col), moves)

    def assert_move_not_possible(self, row: int, col: int, target_row: int, target_col: int):
        moves = [(move.to_row, move.to_col)
                 for move in self.get_moves(row, col)]
        self.assertNotIn((target_row, target_col), moves)

    def assert_number_of_moves(self, row: int, col: int, expected_number: int):
        moves = self.get_moves(row, col)
        self.assertEqual(len(moves), expected_number)

    def assert_piece_moved(self, start_row: int, start_col: int, target_row: int, target_col: int, piece_type, expect_checkmate: bool = False):
        moved_piece = self.game.board[start_row][start_col]
        self.assertIsNotNone(moved_piece)
        self.move_piece(start_row, start_col, target_row, target_col)
        self.assertEqual(
            self.game.board[target_row][target_col].piece_type, moved_piece.piece_type)
        self.assertIsInstance(
            self.game.board[target_row][target_col], piece_type)
        self.assertEqual(
            self.game.board[target_row][target_col].colour, moved_piece.colour)
        self.assertIsNone(self.game.board[start_row][start_col])
        self.assertEqual(self.game.is_checkmate, expect_checkmate)


class TestChessGameFlow(BaseTestChessGame):

    def test_move(self):
        # Move the pawn from A2 (6, 0) to A3 (5, 0)
        self.assert_move_possible(6, 0, 5, 0)
        self.assert_piece_moved(6, 0, 5, 0, Pawn)

    def test_capture(self):
        self.game.board[5][1] = Pawn(Colour.BLACK, 5, 1)
        self.assert_move_possible(6, 0, 5, 1)
        self.assert_piece_moved(6, 0, 5, 1, Pawn)
        self.assertIsNone(self.game.board[5][0])

    # def test_en_passant_capture(self):
    #     # Test that en passant capture works correctly
    #     self.empty_board()
    #     self.game.board[6][4] = Pawn(Colour.WHITE, 6, 4)
    #     self.game.board[4][3] = Pawn(Colour.BLACK, 4, 3)
    #     # White pawn moves e2 -> e4
    #     self.move_piece(6, 4, 4, 4)
    #     # Black pawn should have en passant as a possible move
    #     self.assert_move_possible(4, 3, 5, 4)
    #     # Black pawn captures en passant
    #     self.assert_piece_moved(4, 3, 5, 4, Pawn)
    #     # White pawn should be removed from e4
    #     self.assertIsNone(self.game.board[4][4])
    #     # Black pawn should be on e3
    #     self.assertEqual(self.game.board[5][4].colour, Colour.BLACK)

    def test_is_in_check(self):
        self.empty_board(7, 4, 2, 3)
        self.game.board[4][4] = Pawn(Colour.WHITE, 4, 4)
        # Nobody is in check
        self.assertFalse(self.game.is_king_in_check(Colour.BLACK))
        self.assertIsNone(self.game.in_check)
        # Move white pawn so that black goes into check
        self.move_piece(4, 4, 3, 4)
        # Check that black is now in check
        self.assertEqual(self.game.in_check, Colour.BLACK)
        self.game.turn = Colour.WHITE
        self.assertTrue(self.game.is_king_in_check(Colour.BLACK))

    def test_moves_out_of_check(self):
        self.empty_board(7, 4, 2, 3)
        self.game.board[4][4] = Pawn(Colour.WHITE, 4, 4)
        # Nobody is in check
        self.assertFalse(self.game.is_king_in_check(Colour.BLACK))
        self.assertIsNone(self.game.in_check)
        # Move white pawn so that black goes into check
        self.move_piece(4, 4, 3, 4)
        # Confirm that black is now in check
        self.assertEqual(self.game.in_check, Colour.BLACK)
        # Move black king to (2, 2)
        self.move_piece(2, 3, 2, 2)
        # Confirm nobody in check
        self.assertIsNone(self.game.in_check)
        # Push white pawn to (2, 4)
        self.move_piece(3, 4, 2, 4)
        # Confirm nobody in check
        self.assertIsNone(self.game.in_check)

    def test_cannot_put_yourself_in_check(self):
        self.empty_board(7, 4, 1, 3)
        self.game.board[4][4] = Pawn(Colour.WHITE, 4, 4)
        self.move_piece(4, 4, 3, 4)
        self.assertIsNone(self.game.in_check)
        # Get possible moves for the Black king
        self.assert_number_of_moves(1, 3, 7)
        # Check that the move to (2, 3) is not allowed
        self.assert_move_not_possible(1, 3, 2, 3)

    def test_can_only_move_out_of_check(self):
        self.empty_board(4, 5, 2, 3)
        self.game.board[4][4] = Queen(Colour.WHITE, 4, 4)
        self.game.board[5][1] = Queen(Colour.BLACK, 5, 1)
        # Push the pawn so Black is in check
        self.move_piece(4, 4, 3, 4)
        self.assertEqual(self.game.in_check, Colour.BLACK)
        # The Black queen should not be able to move
        self.assert_number_of_moves(4, 1, 0)
        # The black king should only have 2 moves
        self.assert_number_of_moves(2, 3, 2)
        self.assert_move_possible(2, 3, 1, 3)
        self.assert_move_possible(2, 3, 2, 2)

    def test_can_capture_checking_piece(self):
        self.empty_board(7, 4, 2, 3)
        self.game.board[4][4] = Queen(Colour.WHITE, 4, 4)
        self.game.board[6][1] = Queen(Colour.BLACK, 6, 1)
        # Push the pawn so Black is in check
        self.move_piece(4, 4, 3, 4)
        self.assertEqual(self.game.in_check, Colour.BLACK)
        # The black queen should have 1 move - to take the white queen on (3, 4)
        self.assert_number_of_moves(6, 1, 1)
        self.assert_move_possible(6, 1, 3, 4)
        # The black king should only have 2 moves
        self.assert_number_of_moves(2, 3, 3)
        self.assert_move_possible(2, 3, 1, 3)
        self.assert_move_possible(2, 3, 2, 2)
        self.assert_move_possible(2, 3, 3, 4)

    def test_scholarsmate(self):
        self.assertFalse(self.game.is_checkmate)
        # 1W e4
        self.move_piece(6, 4, 4, 4)
        self.assertFalse(self.game.is_checkmate)
        # 1B e5
        self.move_piece(1, 4, 3, 4)
        self.assertFalse(self.game.is_checkmate)
        # 2W Bc4
        self.move_piece(7, 5, 4, 2)
        self.assertFalse(self.game.is_checkmate)
        # 2B Nc6
        self.move_piece(0, 1, 2, 2)
        self.assertFalse(self.game.is_checkmate)
        # 3W Qh5
        self.move_piece(7, 3, 3, 7)
        self.assertFalse(self.game.is_checkmate)
        # 3B Nf6??
        self.move_piece(0, 6, 2, 5)
        self.assertFalse(self.game.is_checkmate)
        # 4W Qxf7#
        self.assert_piece_moved(3, 7, 1, 5, Queen, True)
        self.assertEqual(self.game.in_check, Colour.BLACK)
        self.assertTrue(self.game.is_checkmate)
        # Check that no pieces have legal moves
        for row in range(8):
            for col in range(8):
                piece = self.game.board[row][col]
                if piece and piece.colour == self.game.turn:
                    self.assert_number_of_moves(row, col, 0)

    def test_foolsmate(self):
        self.assertFalse(self.game.is_checkmate)
        # 1W. e4 -> (6, 4) -> (4, 4)
        self.move_piece(6, 4, 4, 4)
        self.assertFalse(self.game.is_checkmate)
        # 1B. g5 -> (1, 6) -> (3, 6)
        self.move_piece(1, 6, 3, 6)
        self.assertFalse(self.game.is_checkmate)
        # 2W. Nc3 -> (7, 1) -> (5, 2)
        self.move_piece(7, 1, 5, 2)
        self.assertFalse(self.game.is_checkmate)
        # 2B. f5 -> (1, 5) -> (3, 5)
        self.move_piece(1, 5, 3, 5)
        self.assertFalse(self.game.is_checkmate)
        # 3W. Qh5# -> (7, 3) -> (3, 7)
        self.assert_piece_moved(7, 3, 3, 7, Queen, True)
        # self.game.print_board()
        # Check that Black is in check
        self.assertEqual(self.game.in_check, Colour.BLACK)
        # Check that no pieces have legal moves
        for row in range(8):
            for col in range(8):
                piece = self.game.board[row][col]
                if piece and piece.colour == self.game.turn:
                    self.assert_number_of_moves(row, col, 0)
        # Ensure that the checkmate flag is now set
        self.assertTrue(self.game.is_checkmate)
