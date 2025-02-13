from PyQt6.QtGui import QPixmap
from chess_game.enums import Colour, PieceType


class Piece:
    def __init__(self, colour: Colour, piece_type: PieceType, row: int, col: int):
        self.colour = colour
        self.piece_type = piece_type
        self.row = row
        self.col = col
        self.image_path = f"assets/{self.colour.value}-{self.piece_type.value}.png"

    def __str__(self):
        return f"{self.colour.value[0].upper()}{self.symbol()}"

    def __repr__(self):
        return f"{self.colour.value} {self.piece_type.value} at ({self.row},{self.col})"

    def get_pixmap(self) -> QPixmap:
        """Returns the QPixmap of the piece for UI display"""
        return QPixmap(self.image_path).scaled(75, 75)

    def symbol(self) -> str:
        symbols = {
            PieceType.PAWN: 'P',
            PieceType.ROOK: 'R',
            PieceType.KNIGHT: 'N',
            PieceType.BISHOP: 'B',
            PieceType.QUEEN: 'Q',
            PieceType.KING: 'K'
        }
        return symbols[self.piece_type]

    def set_position(self, row: int, col: int) -> None:
        self.row = row
        self.col = col


class Pawn(Piece):
    def __init__(self, colour, row, col):
        super().__init__(colour, PieceType.PAWN, row, col)


class Bishop(Piece):
    def __init__(self, colour, row, col):
        super().__init__(colour, PieceType.BISHOP, row, col)


class Knight(Piece):
    def __init__(self, colour, row, col):
        super().__init__(colour, PieceType.KNIGHT, row, col)


class Rook(Piece):
    def __init__(self, colour, row, col):
        super().__init__(colour, PieceType.ROOK, row, col)


class Queen(Piece):
    def __init__(self, colour, row, col):
        super().__init__(colour, PieceType.QUEEN, row, col)


class King(Piece):
    def __init__(self, colour, row, col):
        super().__init__(colour, PieceType.KING, row, col)
