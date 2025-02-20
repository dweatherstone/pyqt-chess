from enum import Enum


class Colour(Enum):
    WHITE = "White"
    BLACK = "Black"

    def __str__(self):
        return self.value


class PieceType(Enum):
    KING = "King"
    QUEEN = "Queen"
    ROOK = "Rook"
    BISHOP = "Bishop"
    KNIGHT = "Knight"
    PAWN = "Pawn"
