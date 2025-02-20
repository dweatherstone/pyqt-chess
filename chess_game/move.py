# from chess_game.pieces import Piece
from chess_game.enums import PieceType
from typing import List, Optional


class Move:
    def __init__(self, from_row: int, from_col: int, to_row: int, to_col: int, piece_type: PieceType,
                 captured_piece=None, en_passant: bool = False, castling=None, promotion=None):
        """
        Represents a move in the game.

        :param from_row: The starting row of the piece.
        :param from_col: The starting column of the piece.
        :param to_row: The destination row.
        :param to_col: The destination column.
        :param piece: The piece that is moving.
        :param captured_piece: The piece that was captured (if any).
        :param en_passant: Whether this move is an en passant capture.
        :param castling: "kingside" or "queenside" if castling, else None.
        :param promotion: The piece type the pawn promotes to (if applicable).
        """
        self.from_row = from_row
        self.from_col = from_col
        self.to_row = to_row
        self.to_col = to_col
        self.piece_type = piece_type
        self.captured_piece = captured_piece  # can be None
        self.en_passant = en_passant  # True if en passant capture
        self.castling = castling  # "kingside", "queenside", or None
        self.promotion = promotion  # PieceType

    def __repr__(self):
        return f"Move({self.from_row}, {self.from_col}) -> ({self.to_row}, {self.to_col})"

    def is_equal(self, row: int, col: int) -> bool:
        return self.to_row == row and self.to_col == col

    @staticmethod
    def contains_move(moves: List['Move'], row: int, col: int) -> bool:
        return any(move.to_row == row and move.to_col == col for move in moves)

    @staticmethod
    def get_move_from_list(moves: List['Move'], row: int, col: int) -> Optional['Move']:
        if Move.contains_move(moves, row, col):
            for move in moves:
                if move.is_equal(row, col):
                    return move
        return None
