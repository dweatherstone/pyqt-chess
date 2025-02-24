import unittest
from chess_game.game import GameState
from chess_game.pieces import Pawn, Rook, Knight, Queen, King, Colour
from chess_game.move import Move
from chess_game.enums import PieceType


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
        moves = self.game.get_valid_moves(old_row, old_col)
        for move in moves:
            if move.to_row == new_row and move.to_col == new_col:
                self.game.move_piece(move)

    def get_moves(self, row: int, col: int):
        return self.game.get_valid_moves(row, col)

    def get_move_from_target(self, from_row: int, from_col: int, to_row: int, to_col: int) -> Move:
        moves = self.game.get_valid_moves(from_row, from_col)
        return Move.get_move_from_list(moves, to_row, to_col)

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

    def test_en_passant_capture(self):
        # Test that en passant capture works correctly
        self.empty_board()
        self.game.board[6][4] = Pawn(Colour.WHITE, 6, 4)
        self.game.board[4][3] = Pawn(Colour.BLACK, 4, 3)
        # White pawn moves e2 -> e4
        self.move_piece(6, 4, 4, 4)
        # Black pawn should have en passant as a possible move
        self.assert_move_possible(4, 3, 5, 4)
        # Black pawn captures en passant
        self.assert_piece_moved(4, 3, 5, 4, Pawn)
        # White pawn should be removed from e4
        self.assertIsNone(self.game.board[4][4])
        # Black pawn should be on e3
        self.assertEqual(self.game.board[5][4].colour, Colour.BLACK)

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

    def test_castling_rights_after_king_move(self):
        # Remove the Bishop and Knight stopping the ability to castle kingside, and the queen (so that the king can move left)
        self.game.board[7][5] = None
        self.game.board[7][6] = None
        self.game.board[7][3] = None
        # Make sure that castling kingside is possible
        self.assert_move_possible(7, 4, 7, 6)
        # Move the white king
        self.move_piece(7, 4, 7, 3)
        # Move a black pawn (so that it is white's move)
        self.move_piece(1, 0, 2, 0)
        # Ensure that castling kingside is no longer a possible move
        self.assert_move_not_possible(7, 3, 7, 6)
        # Check that white has no castling rights
        self.assertFalse(self.game.castling_rights[Colour.WHITE]['kingside'])
        self.assertFalse(self.game.castling_rights[Colour.WHITE]['queenside'])
        # Check that black does still have castling rights
        self.assertTrue(self.game.castling_rights[Colour.BLACK]['kingside'])
        self.assertTrue(self.game.castling_rights[Colour.BLACK]['queenside'])

    def test_castling_rights_after_rook_move(self):
        # Remove all pieces other than rooks and king from the 7th row, so that king can castle either side
        self.game.board[7][1] = None
        self.game.board[7][2] = None
        self.game.board[7][3] = None
        self.game.board[7][5] = None
        self.game.board[7][6] = None
        # Check that white has both castling rights
        self.assertTrue(self.game.castling_rights[Colour.WHITE]['kingside'])
        self.assertTrue(self.game.castling_rights[Colour.WHITE]['queenside'])
        # Check that white king's moves include castling either side
        self.assert_move_possible(7, 4, 7, 2)
        self.assert_move_possible(7, 4, 7, 6)
        # Move queenside rook
        self.move_piece(7, 0, 7, 1)
        self.game.swap_turn()
        # Ensure that White can still castle Kingside, but not Queenside
        self.assert_move_not_possible(7, 4, 7, 2)
        self.assert_move_possible(7, 4, 7, 6)
        self.assertTrue(self.game.castling_rights[Colour.WHITE]['kingside'])
        self.assertFalse(self.game.castling_rights[Colour.WHITE]['queenside'])

    def test_castle_kingside(self):
        # Remove pieces preventing castling
        self.game.board[7][5] = None
        self.game.board[7][6] = None
        # Perform castle kingside
        self.assert_piece_moved(7, 4, 7, 6, King)
        # Ensure that the Rook has also moved
        self.assertIsNone(self.game.board[7][7])
        self.assertIsInstance(self.game.board[7][5], Rook)

    def test_castle_queenside(self):
        # Remove pieces preventing castling
        self.game.board[7][1] = None
        self.game.board[7][2] = None
        self.game.board[7][3] = None
        # Perform castle kingside
        self.assert_piece_moved(7, 4, 7, 2, King)
        # Ensure that the Rook has also moved
        self.assertIsNone(self.game.board[7][0])
        self.assertIsInstance(self.game.board[7][3], Rook)

    def test_pawn_promotion(self):
        self.empty_board(6, 4, 1, 4)
        self.game.board[1][0] = Pawn(Colour.WHITE, 1, 0)
        self.game.board[6][0] = Pawn(Colour.BLACK, 6, 0)
        self.game.board[7][1] = Knight(Colour.WHITE, 7, 1)
        # Test that a plain Queen promotion works for the White pawn
        move = Move(1, 0, 0, 0, PieceType.PAWN)
        moves = self.get_moves(1, 0)
        self.assertIn(move, moves)
        move = self.get_move_from_target(1, 0, 0, 0)
        self.assertIsNotNone(move)
        self.assertTrue(self.game.is_promotion_move(move))
        promotion_piece = PieceType.from_name("Queen")
        self.assertEquals(promotion_piece, PieceType.QUEEN)
        move.promotion = promotion_piece
        # self.move_piece(1, 0, 0, 0)
        self.game.move_piece(move)
        self.assertEqual(self.game.board[0][0].piece_type, PieceType.QUEEN)
        self.assertIsInstance(self.game.board[0][0], Queen)
        self.assertEqual(self.game.board[0][0].colour, Colour.WHITE)
        self.assertIsNone(self.game.board[1][0])
        self.assertFalse(self.game.is_checkmate)

        # Test that a promotion to a queen and capture is possible
        move = Move(6, 0, 7, 1, PieceType.PAWN,
                    captured_piece=self.game.board[7][1])
        moves = self.get_moves(6, 0)
        self.assertIn(move, moves)
        move = self.get_move_from_target(6, 0, 7, 1)
        self.assertIsNotNone(move)
        self.assertTrue(self.game.is_promotion_move(move))
        promotion_piece = PieceType.from_name("Queen")
        self.assertEquals(promotion_piece, PieceType.QUEEN)
        move.promotion = promotion_piece
        # self.move_piece(6, 0, 7, 1)
        self.game.move_piece(move)
        self.assertEqual(self.game.board[7][1].piece_type, PieceType.QUEEN)
        self.assertIsInstance(self.game.board[7][1], Queen)
        self.assertEqual(self.game.board[7][1].colour, Colour.BLACK)
        self.assertIsNone(self.game.board[6][0])
        self.assertFalse(self.game.is_checkmate)
