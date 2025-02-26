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
        self.history: List[Move] = []

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

    def get_valid_moves(self, row: int, col: int, simulate: bool = False) -> List[Move]:
        """Returns a list of valid moves for a selected piece."""
        piece = self.board[row][col]
        if not piece or piece.colour != self.turn:
            return []
        possible_moves: List[Move] = piece.get_valid_moves(self.board)
        # Add en passant move if applicable
        if isinstance(piece, Pawn) and self.enpassant_square:
            piece.add_enpassant(
                self.board, self.enpassant_square, possible_moves)

        # Add castling move(s) if applicable
        if isinstance(piece, King) and (self.castling_rights[self.turn]['kingside'] or self.castling_rights[self.turn]['queenside']):
            piece.add_castling(
                self.board, self.castling_rights[self.turn], possible_moves)

        if simulate:
            return possible_moves

        moves = []
        # Only allow moves that do not put the current player in check
        for move in possible_moves:
            new_row, new_col = move.to_row, move.to_col
            # Simulate the move
            # Store whatever was in the destination
            original_piece = self.board[new_row][new_col]
            self.board[new_row][new_col] = piece
            self.board[row][col] = None
            piece.set_position(new_row, new_col)
            self.swap_turn()

            if not self.is_king_in_check(piece.colour):
                moves.append(move)

            # Undo the move
            self.board[row][col] = piece
            self.board[new_row][new_col] = original_piece
            piece.set_position(row, col)
            self.swap_turn()

        return moves

    def move_piece(self, move: Move) -> None:
        piece = self.board[move.from_row][move.from_col]
        if piece and piece.colour == self.turn:
            # Move piece to new position
            if move.promotion:
                new_piece = self.create_piece(
                    self.turn, move.promotion, move.to_row, move.to_col)
                self.board[move.to_row][move.to_col] = new_piece
            else:
                self.board[move.to_row][move.to_col] = piece
                piece.set_position(move.to_row, move.to_col)
            self.board[move.from_row][move.from_col] = None

            # Remove taken pawn when move is en-passant take
            if move.en_passant:
                self.board[move.from_row][move.to_col] = None

            # Update the en-passant square
            self.update_enpassant_square(move)

            # Update castling rights based on move
            self.update_castling_rights(move)

            # Move Rook if the move is a castle
            if move.piece_type == PieceType.KING and move.castling:
                self.move_castled_rook(move)

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

            self.history.append(move)

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
                    if Move.contains_move(self.get_valid_moves(row, col, simulate=True), king_position[0], king_position[1]):
                        return True
        return False

    def is_checkmate_position(self, colour: Colour) -> bool:
        """Returns True if the given color is in checkmate, False otherwise."""
        if not self.in_check and self.in_check != colour:
            return False

        # Check if the player has any legal moves left
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.colour == colour:
                    # Any valid moves?
                    if self.get_valid_moves(row, col):
                        return False
        return True

    def is_promotion_move(self, move: Move) -> bool:
        if not move.piece_type == PieceType.PAWN:
            return False
        if self.turn == Colour.WHITE:
            return move.from_row == 1
        else:
            return move.from_row == 6

    def update_enpassant_square(self, move: Move):
        if move.piece_type == PieceType.PAWN and abs(move.from_row - move.to_row) == 2:
            direction = -1 if self.turn == Colour.WHITE else 1
            self.enpassant_square = (move.from_row + direction, move.to_col)
        else:
            self.enpassant_square = None

    def update_castling_rights(self, move: Move):
        # If the King moves, then castling rights are denied
        if move.piece_type == PieceType.KING:
            self.castling_rights[self.turn]['kingside'] = False
            self.castling_rights[self.turn]['queenside'] = False
        # If the rook moves...
        elif move.piece_type == PieceType.ROOK:
            # If castling is currently allowed, but the kingside rook has moved
            if self.castling_rights[self.turn]['kingside'] and move.from_col == 7:
                # Deny right to castle kingside
                self.castling_rights[self.turn]['kingside'] = False
            # If castling is currently allowed, but the queenside rook has moved
            elif self.castling_rights[self.turn]['queenside'] and move.from_col == 0:
                # Deny right to castle queenside
                self.castling_rights[self.turn]['queenside'] = False

    def move_castled_rook(self, move: Move):
        # We know this is a King move already, and that it is a castling move.
        if move.castling == 'kingside':
            # Kingside white
            if self.turn == Colour.WHITE:
                rook = self.board[7][7]
                self.board[7][7] = None
                self.board[7][5] = rook
                rook.set_position(7, 5)
            # Kingside black
            else:
                rook = self.board[0][7]
                self.board[0][7] = None
                self.board[0][5] = rook
                rook.set_position(0, 5)
        else:
            # Queenside white
            if self.turn == Colour.WHITE:
                rook = self.board[7][0]
                self.board[7][0] = None
                self.board[7][3] = rook
                rook.set_position(7, 3)
            # Kingside black
            else:
                rook = self.board[0][0]
                self.board[0][0] = None
                self.board[0][3] = rook
                rook.set_position(0, 3)

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
