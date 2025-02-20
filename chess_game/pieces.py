from PyQt6.QtGui import QPixmap
from chess_game.enums import Colour, PieceType
from chess_game.move import Move
from typing import Optional, List


class Piece:
    def __init__(self, colour: Colour, piece_type: PieceType, row: int, col: int):
        self.colour: Colour = colour
        self.piece_type: PieceType = piece_type
        self.row: int = row
        self.col: int = col
        self.image_path: str = f"assets/{self.colour.value}-{self.piece_type.value}.png"

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
    def __init__(self, colour: Colour, row: int, col: int):
        super().__init__(colour, PieceType.PAWN, row, col)

    def get_valid_moves(self, board: List[List[Optional[Piece]]]) -> List[Move]:
        moves = []
        # White moves up, black moves down
        direction = -1 if self.colour == Colour.WHITE else 1

        # Regular 1-square move
        if board[self.row + direction][self.col] is None:
            moves.append(Move(self.row, self.col, self.row +
                         direction, self.col, self.piece_type))

        # Initial 2-square move
        if (self.colour == Colour.WHITE and self.row == 6) or (self.colour == Colour.BLACK and self.row == 1):
            if board[self.row + (2 * direction)][self.col] is None and board[self.row + direction][self.col] is None:
                moves.append(Move(self.row, self.col, self.row +
                             (2 * direction), self.col, self.piece_type))

        # Captures
        if self.col > 0 and board[self.row + direction][self.col - 1] and board[self.row + direction][self.col - 1].colour != self.colour:
            moves.append(Move(self.row, self.col, self.row + direction, self.col - 1,
                         self.piece_type, captured_piece=board[self.row+direction][self.col - 1]))
        if self.col < 7 and board[self.row + direction][self.col + 1] and board[self.row + direction][self.col + 1].colour != self.colour:
            moves.append(Move(self.row, self.col, self.row + direction, self.col + 1,
                         self.piece_type, captured_piece=board[self.row + direction][self.col + 1]))

        return moves


class Bishop(Piece):
    def __init__(self, colour: Colour, row: int, col: int):
        super().__init__(colour, PieceType.BISHOP, row, col)

    def get_valid_moves(self, board: List[List[Optional[Piece]]]) -> List[Move]:
        moves = []
        # Diagonal movement
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        for direction in directions:
            r, c = self.row, self.col
            while True:
                r += direction[0]
                c += direction[1]
                if r < 0 or r >= 8 or c < 0 or c >= 8:
                    break  # Out of bounds
                # Move to an empty square
                if board[r][c] is None:
                    moves.append(
                        Move(self.row, self.col, r, c, self.piece_type))
                # Capture enemy piece
                elif board[r][c].colour != self.colour:
                    moves.append(Move(self.row, self.col, r, c,
                                 self.piece_type, captured_piece=board[r][c]))
                    break  # Cannot move further
                # Cannot move past friendly piece
                else:
                    break

        return moves


class Knight(Piece):
    def __init__(self, colour: Colour, row: int, col: int):
        super().__init__(colour, PieceType.KNIGHT, row, col)

    def get_valid_moves(self, board: List[List[Optional[Piece]]]) -> List[Move]:
        moves = []
        translations = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                        (1, -2), (1, 2), (2, -1), (2, 1)]

        for translation in translations:
            r = self.row + translation[0]
            c = self.col + translation[1]
            if r < 0 or r >= 8 or c < 0 or c >= 8:
                continue  # Out of bounds
            # Move to an empty square
            if board[r][c] is None:
                moves.append(Move(self.row, self.col, r, c, self.piece_type))
            # Capture enemy piece
            elif board[r][c].colour != self.colour:
                moves.append(Move(self.row, self.col, r, c,
                                  self.piece_type, captured_piece=board[r][c]))
            # Cannot move past friendly piece
            else:
                continue
        return moves


class Rook(Piece):
    def __init__(self, colour: Colour, row: int, col: int):
        super().__init__(colour, PieceType.ROOK, row, col)

    def get_valid_moves(self, board: List[List[Optional[Piece]]]) -> List[Move]:
        moves = []
        # Vertical and horizontal movement
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for direction in directions:
            r, c = self.row, self.col
            while True:
                r += direction[0]
                c += direction[1]
                if r < 0 or r >= 8 or c < 0 or c >= 8:
                    break  # Out of bounds
                # Move to an empty square
                if board[r][c] is None:
                    moves.append(
                        Move(self.row, self.col, r, c, self.piece_type))
                # Capture enemy piece
                elif board[r][c].colour != self.colour:
                    moves.append(Move(self.row, self.col, r, c,
                                 self.piece_type, captured_piece=board[r][c]))
                    break  # Cannot move further
                # Cannot move past friendly piece
                else:
                    break

        return moves


class Queen(Piece):
    def __init__(self, colour: Colour, row: int, col: int):
        super().__init__(colour, PieceType.QUEEN, row, col)

    def get_valid_moves(self, board: List[List[Optional[Piece]]]) -> List[Move]:
        rook_moves = Rook(self.colour, self.row,
                          self.col).get_valid_moves(board)
        bishop_moves = Bishop(self.colour, self.row,
                              self.col).get_valid_moves(board)
        return rook_moves + bishop_moves


class King(Piece):
    def __init__(self, colour: Colour, row: int, col: int):
        super().__init__(colour, PieceType.KING, row, col)

    def get_valid_moves(self, board: List[List[Optional[Piece]]]) -> List[Move]:
        moves = []
        translations = [(-1, -1), (-1, 0), (-1, 1), (0, -1),
                        (0, 1), (1, -1), (1, 0), (1, 1)]

        for translation in translations:
            r = self.row + translation[0]
            c = self.col + translation[1]
            if r < 0 or r >= 8 or c < 0 or c >= 8:
                continue  # Out of bounds
            # Move to an empty square
            if board[r][c] is None:
                moves.append(Move(self.row, self.col, r, c, self.piece_type))
            # Capture enemy piece
            elif board[r][c].colour != self.colour:
                moves.append(Move(self.row, self.col, r, c,
                                  self.piece_type, captured_piece=board[r][c]))
            # Cannot move past friendly piece
            else:
                continue
        return moves
