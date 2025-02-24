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

    @staticmethod
    def from_name(name: str):
        map = {
            "king": PieceType.KING,
            "queen": PieceType.QUEEN,
            "rook": PieceType.ROOK,
            "bishop": PieceType.BISHOP,
            "knight": PieceType.KNIGHT,
            "pawn": PieceType.PAWN
        }
        return map.get(name.lower())
