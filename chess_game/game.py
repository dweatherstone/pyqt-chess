from chess_game.enums import Colour, PieceType
from chess_game.pieces import Piece, Pawn, Bishop, Knight, Rook, Queen, King


class GameState:
    def __init__(self):
        self.board = self.create_initial_board()
        self.turn = Colour.WHITE
        self.enpassant_square = None
        self.in_check = None
        self.is_checkmate = False
        self.castling_rights = {
            Colour.WHITE: {"kingside": True, "queenside": True},
            Colour.BLACK: {"kingside": True, "queenside": True},
        }
        self.king_positions = {
            Colour.WHITE: (7, 4),
            Colour.BLACK: (0, 4),
        }

    def create_initial_board(self) -> list:
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

    def swap_turn(self) -> None:
        """Swaps the current player turn after a move is made."""
        self.turn = Colour.BLACK if self.turn == Colour.WHITE else Colour.WHITE

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
