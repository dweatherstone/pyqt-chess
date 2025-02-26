from PyQt6.QtGui import QPixmap
from chess_game.enums import Colour, PieceType
from chess_game.move import Move
from typing import Optional, List, Tuple


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

    def add_enpassant(self, board: List[List[Optional[Piece]]], enpassant_square: Tuple[int, int], moves: List[Move]):
        """
        Adds the possible en-passant move for the current board state.

        :param board: The current board state
        :param enpassant_square: A tuple of (row, col) position of the current en_passant square
        :param moves: The list of Move objects to add the en-passant moves to 
        """
        # White moves up, black moves down
        direction = -1 if self.colour == Colour.WHITE else 1
        (ep_row, ep_col) = enpassant_square
        if self.row + direction == ep_row and ((self.col > 0 and self.col - 1 == ep_col) or (self.col < 7 and self.col + 1 == ep_col)):
            moves.append(Move(self.row, self.col, self.row + direction, ep_col,
                         self.piece_type, captured_piece=board[ep_row][ep_col], en_passant=True))


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
        for move in rook_moves:
            move.piece_type = PieceType.QUEEN
        bishop_moves = Bishop(self.colour, self.row,
                              self.col).get_valid_moves(board)
        for move in bishop_moves:
            move.piece_type = PieceType.QUEEN
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

    def add_castling(self, board: List[List[Optional[Piece]]], castling_rights: dict, moves: List[Move]):
        """
        Adds the possible castling moves for the current board state.

        :param board: The current board state
        :param castling_rights: A dictionary with elements 'kingside' and 'queenside' with boolean values indicating
            whether castling in that direction is available.
        :param moves: The list of Move objects to add the en-passant moves to 
        """
        row = 0 if self.colour == Colour.BLACK else 7
        possible_moves = []
        if castling_rights['kingside']:
            # Check that the pieces between the king and rook have moved
            # TODO: Check if the piece moved through check
            if board[row][5] is None and board[row][6] is None and self.row == row and self.col == 4 and board[row][7] and board[row][7].piece_type == PieceType.ROOK:
                possible_moves.append(Move(self.row, self.col, row, 6,
                                           self.piece_type, castling='kingside'))
                through_square = (self.row, 5)
        if castling_rights['queenside']:
            # Check the pieces between the king and rook have moved
            # TODO: Check if the piece moved through check
            if board[row][3] is None and board[row][2] is None and board[row][1] is None and self.row == row and self.col == 4 and board[row][0] and board[row][0].piece_type == PieceType.ROOK:
                possible_moves.append(Move(self.row, self.col, row, 2,
                                           self.piece_type, castling='queenside'))
                through_square = (self.row, 3)

        for move in possible_moves:
            try:
                for row in range(8):
                    for col in range(8):
                        piece = board[row][col]
                        if piece and piece.colour != self.colour:
                            piece_moves = piece.get_valid_moves(board)
                            move_targets = [(move.to_row, move.to_col)
                                            for move in piece_moves]
                            if through_square in move_targets:
                                raise BreakLoop
                moves.append(move)
            except BreakLoop:
                pass


class BreakLoop(Exception):
    pass
