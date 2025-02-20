from chess_game.enums import Colour, PieceType
from chess_game.move import Move
from chess_game.pieces import Piece, Pawn, Bishop, Knight, Rook, Queen, King
from typing import Optional, List, Tuple


class GameState:
    def __init__(self):
        self.board: List[List[Optional[Piece]]] = self.create_initial_board()
        self.turn: Colour = Colour.WHITE
        self.enpassant_square: Optional[Tuple[int, int]] = None
        self.in_check: Optional[Colour] = None
        self.is_checkmate: bool = False
        self.castling_rights = {
            Colour.WHITE: {"kingside": True, "queenside": True},
            Colour.BLACK: {"kingside": True, "queenside": True},
        }
        self.king_positions = {
            Colour.WHITE: (7, 4),
            Colour.BLACK: (0, 4),
        }

    def create_initial_board(self) -> List[List[Optional[Piece]]]:
        """Initialises the board with Piece objects."""
        board = [[None for _ in range(8)] for _ in range(8)]

        # Create pieces and place them in starting positions
        piece_setup = [
            (PieceType.ROOK, PieceType.KNIGHT, PieceType.BISHOP, PieceType.QUEEN,
             PieceType.KING, PieceType.BISHOP, PieceType.KNIGHT, PieceType.ROOK),
            [PieceType.PAWN] * 8,
        ]
        for col in range(8):
            board[0][col] = self.create_piece(
                Colour.BLACK, piece_setup[0][col], 0, col)
            board[1][col] = self.create_piece(
                Colour.BLACK, piece_setup[1][col], 1, col)
            board[6][col] = self.create_piece(
                Colour.WHITE, piece_setup[1][col], 6, col)
            board[7][col] = self.create_piece(
                Colour.WHITE, piece_setup[0][col], 7, col)

        return board

    def create_piece(self, colour: Colour, piece_type: PieceType, row: int, col: int) -> Piece:
        """Factory method to create a piece instance based on type."""
        piece_map = {
            PieceType.PAWN: Pawn,
            PieceType.BISHOP: Bishop,
            PieceType.KNIGHT: Knight,
            PieceType.ROOK: Rook,
            PieceType.QUEEN: Queen,
            PieceType.KING: King
        }

        # Create and return the piece instance based on type
        piece_class = piece_map.get(piece_type)
        if piece_class:
            return piece_class(colour, row, col)
        else:
            return ValueError(f"Unknown piece type: {piece_type}")

    def is_active_piece(self, row: int, col: int) -> bool:
        """Returns True if the square contains a piece of the current player's colour."""
        return self.board[row][col] and self.board[row][col].colour == self.turn

    def get_valid_moves(self, row: int, col: int) -> List[Move]:
        """Returns a list of valid moves for a selected piece."""
        piece = self.board[row][col]
        if not piece or piece.colour != self.turn:
            return []
        return piece.get_valid_moves(self.board)

    def move_piece(self, move: Move) -> None:
        piece = self.board[move.from_row][move.from_col]
        if piece and piece.colour == self.turn:
            # Move piece to new position
            self.board[move.to_row][move.to_col] = piece
            self.board[move.from_row][move.from_col] = None
            piece.set_position(move.to_row, move.to_col)

            # Is opponent in check?
            opponent = Colour.BLACK if self.turn == Colour.WHITE else Colour.WHITE
            if self.is_king_in_check(opponent):
                self.in_check = opponent
            else:
                self.in_check = None

            # Switch turn
            self.swap_turn()

            # Check if the opponent is in checkmate
            if self.is_checkmate_position(self.turn):
                self.is_checkmate = True

    def swap_turn(self) -> None:
        """Swaps the current player turn after a move is made."""
        self.turn = Colour.BLACK if self.turn == Colour.WHITE else Colour.WHITE

    def is_king_in_check(self, colour: Colour) -> bool:
        """Returns whether the `colour` player is currently in check."""
        king_position = None

        # Find the king on the board
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and isinstance(piece, King) and piece.colour == colour:
                    king_position = (row, col)
                    break

        if not king_position:
            raise ValueError("There is no position found for the king")

        # See if any opponent piece can attack the king's position
        opponent_colour = Colour.BLACK if colour == Colour.WHITE else Colour.WHITE
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.colour == opponent_colour:
                    if Move.contains_move(self.get_valid_moves(row, col), king_position[0], king_position[1]):
                        return True
        return False

    def is_checkmate_position(self, colour: Colour) -> bool:
        """Returns True if the given color is in checkmate, False otherwise."""
        if not self.is_king_in_check(colour):
            return False

        # Check if the player has any legal moves left
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                # Any valid moves?
                if self.get_valid_moves(row, col):
                    return False
        return True

    def print_board(self) -> None:
        """Prints the board to the terminal. For debugging purposes."""
        for row in self.board:
            print(' '.join([str(piece) if piece else '--' for piece in row]))

    def print_in_check(self) -> None:
        """Prints which player is in check, if any, to the terminal. For debugging purposes."""
        if self.in_check:
            print("In check:", self.in_check)
        else:
            print("Nobody in check")
