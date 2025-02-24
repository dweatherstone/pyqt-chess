from PyQt6.QtWidgets import QWidget, QGridLayout, QLabel, QMessageBox, QDialog, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QMouseEvent, QIcon
from typing import Optional, Tuple, List
from chess_game.game import GameState
from chess_game.move import Move
from chess_game.pieces import Piece, Queen, Rook, Bishop, Knight
from chess_game.enums import PieceType


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
                            if self.game_state.is_promotion_move(move):
                                if not self.choose_promotion_piece(move):
                                    return
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

    def choose_promotion_piece(self, move: Move):
        # print("Do something to choose a promotion piece")
        dialog = PromotionDialog(self, colour=self.game_state.turn)
        result = dialog.exec()  # Show the dialog

        if result == QDialog.DialogCode.Accepted:
            chosen_piece = dialog.get_selected_piece()
            piece_type = PieceType.from_name(chosen_piece)
            if piece_type:
                move.promotion = piece_type
                return True
            else:
                raise ValueError("Could not find the piece type!")
        else:
            print("Player cancelled the promotion")
            return False

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


class PromotionDialog(QDialog):
    def __init__(self, parent=None, colour=None):
        super().__init__(parent)
        self.setWindowTitle("Pawn Promotion")
        # Makes this dialog block interactions with the main window
        self.setModal(True)
        self.setFixedSize(500, 200)

        self.selected_piece = None  # Store the selected piece type

        # Layout
        layout = QVBoxLayout(self)
        label = QLabel("Choose a piece for promotion:")
        layout.addWidget(label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Horizontal layout for the buttons
        button_layout = QHBoxLayout()

        # Create buttons with images for each promotion option
        self.pieces = {
            "Queen": Queen(colour, 0, 0),
            "Rook": Rook(colour, 0, 0),
            "Bishop": Bishop(colour, 0, 0),
            "Knight": Knight(colour, 0, 0)
        }

        for name, piece in self.pieces.items():
            btn = QPushButton()
            btn.setIcon(QIcon(piece.get_pixmap()))
            btn.setIconSize(piece.get_pixmap().size())
            btn.setFixedSize(100, 100)
            btn.setStyleSheet(
                "QPushButton { border: 2px solid black; }")
            # Capture piece type
            btn.clicked.connect(lambda checked, p=name: self.select_piece(p))
            button_layout.addWidget(btn)

        layout.addLayout(button_layout)

        # Cancel button
        cancel_btn = QPushButton("Cancel")
        # Closes dialog without selection
        cancel_btn.clicked.connect(self.reject)
        layout.addWidget(cancel_btn, alignment=Qt.AlignmentFlag.AlignHCenter)

    def select_piece(self, piece_name):
        """Set the selected piece type and close dialog."""
        self.selected_piece = piece_name
        self.accept()

    def get_selected_piece(self):
        """Return the chosen piece type."""
        return self.selected_piece
