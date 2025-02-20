from PyQt6.QtWidgets import QWidget, QGridLayout, QLabel, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QMouseEvent
from typing import Optional, Tuple, List
from chess_game.game import GameState
from chess_game.move import Move
from chess_game.pieces import Piece


class ChessBoard(QWidget):
    def __init__(self, game_state: GameState):
        super().__init__()

        # Store reference to game logic
        self.game_state = game_state

        # Set up the layout of the board
        self.gridLayoutBoard = QGridLayout(self)
        self.gridLayoutBoard.setSpacing(0)

        self.labels: List[List[QLabel]] = [
            [QLabel(self) for _ in range(8)] for _ in range(8)]
        self.selected_piece: Tuple[int, int] = None  # Track selected piece
        self.valid_moves: List[Move] = []  # Track valid moves for highlighting

        self.setup_chessboard()

    def setup_chessboard(self):
        """Draws the board and pieces based on `self.game_state` state."""
        for row in range(8):
            for col in range(8):
                label = self.labels[row][col]
                label.setFixedSize(75, 75)
                label.setStyleSheet(self.get_square_style(row, col))
                label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.gridLayoutBoard.addWidget(label, row, col)

                # If there's a piece in this position, set its image
                piece: Optional[Piece] = self.game_state.board[row][col]
                if piece:
                    label.setPixmap(piece.get_pixmap())

    def get_square_style(self, row: int, col: int, highlight: bool = False) -> str:
        """Returns the CSS style for a board square."""
        base_colour = "#DDB88C" if (row + col) % 2 == 0 else "#A66F4F"
        highlight_colour = "#77DD77"  # Light green for highlighting valid moves
        return f"background-color: {highlight_colour if highlight else base_colour};"

    def highlight_squares(self, squares: list) -> None:
        """Highlights the squares where a piece can move."""
        for row in range(8):
            for col in range(8):
                highlight = Move.contains_move(squares, row, col)
                self.labels[row][col].setStyleSheet(
                    self.get_square_style(row, col, highlight))

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Handles clicking on the board to select/move pieces."""
        label = self.childAt(event.position().toPoint())
        if not label:
            return

        # Find the row and column of the clicked QLabel
        for row in range(8):
            for col in range(8):
                if self.labels[row][col] == label:
                    # First click on a piece
                    if self.selected_piece is None:
                        self.mark_selection(row, col)
                    # If a piece is selected, check if the clicked square is a valid move
                    else:
                        # Check if the click is on a valid move
                        if Move.contains_move(self.valid_moves, row, col):
                            move = Move.get_move_from_list(
                                self.valid_moves, row, col)
                            if move is None:
                                raise ValueError(
                                    f"Move cannot be found: ({self.selected_piece[0]}, {self.selected_piece[1]}) -> ({row}, {col})")
                            # Make the move here
                            self.game_state.move_piece(move)
                            # Remove all pieces from labels
                            self.clear_labels()
                            self.clear_selection()
                            self.setup_chessboard()
                            self.update()
                            # Check if the user is now in checkmate
                            if self.game_state.is_checkmate:
                                QMessageBox.information(
                                    self, "Game Over", f"Checkmate! {self.game_state.in_check} loses.")
                            else:
                                self.mark_selection(row, col)
                        # If not a valid move, clear the selection
                        else:
                            self.clear_selection()

    def mark_selection(self, row: int, col: int) -> None:
        """Marks a piece, and highlights all valid move squares."""
        if self.game_state.is_active_piece(row, col):
            # Select the piece if it's the current player's turn
            self.selected_piece = (row, col)
            self.valid_moves = self.game_state.get_valid_moves(row, col)
            if self.valid_moves:
                self.highlight_squares(self.valid_moves)
            else:
                self.clear_selection()
        else:
            self.clear_selection()

    def clear_selection(self) -> None:
        """Clears the current selection, once a move has been made."""
        self.selected_piece = None
        self.valid_moves = []
        self.highlight_squares([])
        # self.update()

    def clear_labels(self) -> None:
        """Clears all the labels on all squares."""
        for row in range(8):
            for col in range(8):
                self.labels[row][col].clear()
