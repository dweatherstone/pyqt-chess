from enum import Enum


class Colour(Enum):
    WHITE = "white"
    BLACK = "black"

    def __str__(self):
        return self.value


class PieceType(Enum):
    KING = "king"
    QUEEN = "queen"
    ROOK = "rook"
    BISHOP = "bishop"
    KNIGHT = "knight"
    PAWN = "pawn"
